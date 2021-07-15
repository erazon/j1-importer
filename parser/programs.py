import logging
import os

import xmltodict
from models.history.import_history import ImportHistoryDataKeys

from parser.base import BaseParser

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class ProgramParser(BaseParser):
    name = ImportHistoryDataKeys.programs
    headers = {'content-type': "application/x-www-form-urlencoded"}
    api_action = "searchPrograms.action"

    def __init__(self, importer_id, base_url,
                 import_history_id, importer_start_time):
        super().__init__(importer_id=importer_id,
                         import_history_id=import_history_id, base_url=base_url)
        self.importer_start_time = importer_start_time
        logger.debug("base_url: {}".format(self.base_url))

    def fetch(self):
        try:
            url = os.path.join(self.base_url, self.api_action)
            logger.info("URL: {}".format(url))
            response = self.get_response(url=url)
            response = self.parse(response)
            yield response
        except Exception as error:
            yield self.errback(msg="error on starting crawling!", failure=error)

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
            programs = xmltodict.parse(selector_string)
            programs = self.get_value_from_dict(
                data=programs,
                key="response.data.Program"
            )
            result['raw'] = selector_string
            if programs is None:
                logger.warning(
                    "spider name: {} | Program got empty! url: {}".format(
                        self.name, response.url))
                return {"success": True, "data": result}

            programs = self.transform_to_list(programs)
            for program in programs:
                program_id = program.get("ProgramID")
                logger.info("Parsed - ProgramID: {}".format(program_id))
                program_item = {
                    "spider_name": self.name,
                    "program_id": program_id,
                    self.name: program
                }
                result["parsed"].append(program_item)

        except (xmltodict.expat.ExpatError, Exception) as e:
            logger.exception("Parsing error! url: {}".format(response.url))
            return self.errback(msg=response.url, failure=e)

        return {"success": True, "data": result}
