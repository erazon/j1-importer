import logging
import os

from models.history.import_history import ImportHistoryDataKeys
from mongoengine import NotUniqueError

from pipelines.base import BasePipeline

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class OfferingOverviewPipeline(BasePipeline):
    def __init__(self, importer_id, import_history_id, code):
        super().__init__(importer_id, import_history_id, code)

    def import_history(self, item, spider):
        try:
            data_dict = item.get('parsed')
            history_data = self.get_history_model(
                story=data_dict,
                spider=spider,
                key_name=spider.name,
                data_object_id=data_dict.get("offering_id")
            )
            self.save_history_to_mongodb(
                data_dict=data_dict,
                history_data=history_data
            )

            offering = data_dict.get(spider.name)
            requisitie = offering.get("Requisities", None)
            if requisitie:
                logger.info("Requisitie found on story! OfferingID: {}".format(
                    data_dict.get("offering_id")))

                offering_id = offering.get("OfferingID")
                spider_name = spider.name
                importer_start_time = data_dict.get("importer_start_time")

                new_requisitie = {
                    "spider_name": spider_name,
                    "importer_start_time": importer_start_time,
                    ImportHistoryDataKeys.requisities: requisitie,
                    "offering_id": offering_id
                }
                key_name = ImportHistoryDataKeys.requisities
                history_data = self.get_history_model(
                    story=new_requisitie,
                    spider=spider,
                    key_name=key_name,
                    data_object_id=new_requisitie.get("offering_id")
                )
                try:
                    history_data.save()
                except NotUniqueError as e:
                    logger.warning("Requisities got duplicate entry | "
                                   "Offering_id: %s | key_name: %s" %
                                   (offering_id, key_name))

        except Exception as e:
            raise e
        pass

    def dump_story(self, item, spider):
        try:
            data = item.get('raw')
            url = item.get('url')
            key = url.split("?")[-1] + ".xml"
            date_folder = self.folder_structure_from_date(
                item.get('importer_start_time'))
            action = spider.api_action.split("?")[0]
            story_path = os.path.join(self.folder, self.code,
                                      date_folder, action, key)
            logger.debug("Story Path: {}".format(story_path))
            if self.SAVE_ON_S3:
                self.save_object_to_s3(path=story_path, obj=data)

        except Exception as e:
            raise e
        pass

    def process_item(self, item, spider):
        try:
            self.dump_story(item, spider)
            self.import_history(item, spider)
        except Exception as e:
            raise e
