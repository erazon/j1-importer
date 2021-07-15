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


class OfferingParser(BaseParser):
    name = ImportHistoryDataKeys.offerings
    api_action = "searchOfferings.action?startPosition={}&pageSize={}"

    BATCH_SIZE = 50
    LIMIT = 2000

    def __init__(self, importer_id, base_url,
                 import_history_id, importer_start_time):
        super().__init__(importer_id=importer_id,
                         import_history_id=import_history_id, base_url=base_url)
        self.importer_start_time = importer_start_time
        logger.debug("base_url: {}".format(self.base_url))

    def fetch(self):
        try:
            for url in self.get_paginated_urls():
                logger.info("URL: {}".format(url))
                response = self.get_response(url=url)
                response = self.parse(response)
                if 'data' in response:
                    yield response
                else:
                    return response
        except Exception as error:
            yield self.errback(msg="error on starting crawling!", failure=error)

    def is_empty_node(self, offering_dict):
        check = self.get_value_from_dict(
            data=offering_dict,
            key="response.data",
            default=None
        )
        check = not bool(check)
        logger.debug("Check: {}".format(check))
        return check

    def get_paginated_urls(self):
        for start_position in range(0, self.LIMIT, self.BATCH_SIZE):
            url = os.path.join(
                self.base_url,
                self.api_action.format(start_position, self.BATCH_SIZE))
            yield url

    def parse(self, response):
        logger.debug("ParseNode - URL: {}".format(response.url))
        result = {
            "parsed": [],
            "raw": None,
            "importer_start_time": self.importer_start_time,
            "url": response.url
        }
        try:
            offering_str = response.text
            result['raw'] = offering_str

            data = xmltodict.parse(offering_str)
            if self.is_empty_node(data):
                logger.info("ParserName: %s In The END! | LastURL: "
                            "%s" % (self.name, response.url))
                return {"success": True}

            offerings = self.get_value_from_dict(
                data, "response.data.Offering", [])

            offerings = self.transform_to_list(offerings)

            for offering in offerings:
                offering_id = offering.get("OfferingID")
                logger.info("Parsed - OfferingID: {}".format(offering_id))
                offering_item = {
                    "offering_id": offering_id,
                    self.name: offering
                }
                result['parsed'].append(offering_item)
        except xmltodict.expat.ExpatError as e:
            logger.exception("Parsing error")
            return self.errback(msg=response.url, failure=e)

        return {"success": True, "data": result}
