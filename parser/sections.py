import logging
import os

import xmltodict
from models.history.import_history import ImportHistoryDataKeys

from parser.base import BaseParser
from services import mongodb_service

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class SectionsParser(BaseParser):
    name = ImportHistoryDataKeys.sections
    headers = {'content-type': "application/x-www-form-urlencoded"}
    api_action = "defaultSections.action?OfferingID={}"

    def __init__(self, importer_id, base_url,
                 import_history_id, importer_start_time):
        super().__init__(importer_id=importer_id,
                         import_history_id=import_history_id, base_url=base_url)
        self.importer_start_time = importer_start_time
        logger.debug("base_url: {}".format(self.base_url))

    def fetch(self):
        try:
            for offering in mongodb_service.get_history_data(
                    import_history_id=self.import_history_id,
                    key_name=ImportHistoryDataKeys.offerings
            ):
                offering = offering.data_object
                offering_id = offering.get("OfferingID")
                logger.info("OfferingID: {}".format(offering_id))

                url = os.path.join(
                    self.base_url,
                    self.api_action.format(offering_id)
                )
                logger.info("URL: {}".format(url))
                response = self.get_response(url)
                response = self.parse(response)
                yield response
        except Exception as error:
            yield self.errback(msg="error on start crawling!", failure=error)
        pass

    def parse(self, response):
        result = {
            "importer_start_time": self.importer_start_time,
            "parsed": [],
            "raw": None,
            "url": response.url
        }

        try:
            selector_string = response.text
            sections = xmltodict.parse(selector_string)
            sections = self.get_value_from_dict(
                data=sections, key="response.data.Section"
            )
            result['raw'] = selector_string
            if sections is None:
                logger.warning(
                    "sections got empty! url: {}".format(response.url))
                return {"success": True, "data": result}

            sections = self.transform_to_list(sections)
            for section in sections:
                section_id = section.get("SectionID")
                logger.info("Parsed - SectionID: {}".format(section_id))
                section_item = {
                    "section_id": section_id,
                    self.name: section
                }
                result["parsed"].append(section_item)
        except (xmltodict.expat.ExpatError, Exception) as e:
            logger.exception("Parsing error! url: {}".format(response.url))
            return self.errback(msg=response.url, failure=e)

        return {"success": True, "data": result}
