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


class OfferingOverviewParser(BaseParser):
    name = ImportHistoryDataKeys.offerings_overview
    headers = {'content-type': "application/x-www-form-urlencoded"}
    api_action = "offeringOverview.action?OfferingID={}"

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
                    key_name=ImportHistoryDataKeys.offerings,
            ):
                offering = offering.data_object
                offering_id = offering.get("OfferingID")
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

    def parse(self, response):
        logger.debug("ParseNode - URL: {}".format(response.url))
        result = {
            "importer_start_time": self.importer_start_time,
            "parsed": None,
            "raw": None,
            "url": response.url
        }
        try:
            offering_str = response.text
            offering = xmltodict.parse(offering_str)
            logger.debug("data:  %s" % offering)
            offering = self.get_value_from_dict(
                data=offering,
                key='response.data.Offering'
            )
            offering_id = offering.get("OfferingID")
            logger.info("Parsed - OfferingID: {}".format(offering_id))
            offering_item = {
                "offering_id": offering_id,
                self.name: offering
            }
            result['parsed'] = offering_item
            result['raw'] = offering_str
        except xmltodict.expat.ExpatError as e:
            logger.exception("Parsing error")
            return self.errback(msg=response.url, failure=e)

        return {"success": True, "data": result}
