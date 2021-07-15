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


class MeetingsParser(BaseParser):
    name = ImportHistoryDataKeys.meetings
    headers = {'content-type': "application/x-www-form-urlencoded"}
    api_action = "sectionSchedule.action?SectionID={}"

    def __init__(self, importer_id, base_url,
                 import_history_id, importer_start_time):
        super().__init__(importer_id=importer_id,
                         import_history_id=import_history_id, base_url=base_url)
        self.importer_start_time = importer_start_time
        logger.debug("base_url: {}".format(self.base_url))

    def fetch(self):
        try:
            for section in mongodb_service.get_history_data(
                    import_history_id=self.import_history_id,
                    key_name=ImportHistoryDataKeys.sections,
            ):
                section = section.data_object
                section_id = section.get("SectionID")
                logger.info("SectionID: {}".format(section_id))

                url = os.path.join(
                    self.base_url,
                    self.api_action.format(section_id)
                )
                logger.info("URL: {}".format(url))
                response = self.get_response(url)
                response = self.parse(response)
                yield response
        except Exception as error:
            yield self.errback(msg="error on start crawling!", failure=error)

    def parse(self, response):
        logger.debug("ParseNode - URL: {}".format(response.url))
        result = {
            "importer_start_time": self.importer_start_time,
            "parsed": [],
            "raw": None,
            "url": response.url
        }
        try:
            selector_string = response.text
            meetings = xmltodict.parse(selector_string)
            meetings = self.get_value_from_dict(
                data=meetings, key="response.data.Meeting")
            result['raw'] = selector_string

            if meetings is None:
                logger.warning(
                    "meeting got empty! url: {}".format(response.url))
                return {"success": True, "data": result}

            meetings = self.transform_to_list(meetings)
            for meeting in meetings:
                meeting_id = meeting.get("ScheduleID")
                logger.info("Parsed - MeetingID: {}".format(meeting_id))
                meeting_item = {
                    "meeting_id": meeting_id,
                    self.name: meeting
                }
                result["parsed"].append(meeting_item)
        except (xmltodict.expat.ExpatError, Exception) as e:
            logger.exception("Parsing error! url: {}".format(response.url))
            return self.errback(msg=response.url, failure=e)

        return {"success": True, "data": result}
