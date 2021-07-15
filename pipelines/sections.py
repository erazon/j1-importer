import logging
import os

from pipelines.base import BasePipeline

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class SectionPipeline(BasePipeline):
    def __init__(self, importer_id, import_history_id, code):
        super().__init__(importer_id, import_history_id, code)

    def import_history(self, item, spider):
        try:
            data = item.get("parsed", [])
            for section in data:
                data_dict = section
                history_data = self.get_history_model(
                    story=data_dict,
                    spider=spider,
                    key_name=spider.name,
                    data_object_id=data_dict.get("section_id")
                )
                self.save_history_to_mongodb(
                    data_dict=data_dict,
                    history_data=history_data
                )
        except Exception as e:
            raise e

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

    def process_item(self, item, spider):
        try:
            self.dump_story(item, spider)
            self.import_history(item, spider)
        except Exception as e:
            raise e
