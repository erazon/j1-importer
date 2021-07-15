import ssl
from abc import ABCMeta, abstractmethod

import requests
from requests import HTTPError, Timeout, adapters
from urllib3 import poolmanager


class TLSAdapter(adapters.HTTPAdapter):

    def init_poolmanager(self, connections, maxsize, block=False):
        """Create and initialize the urllib3 PoolManager."""
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = False
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_context=ctx
        )


class BaseParser(metaclass=ABCMeta):
    headers = {'content-type': "application/x-www-form-urlencoded"}

    def __init__(self, importer_id, import_history_id, base_url):
        self.importer_id = importer_id
        self.import_history_id = import_history_id
        self.base_url = base_url
        self.session = requests.Session()
        self.session.mount('https://', TLSAdapter())

    def get_response(self, url):
        try:
            response = self.session.get(
                url=url,
                headers=self.headers,
                timeout=300
            )
            response.raise_for_status()
            return response
        except HTTPError as http_err:
            raise http_err
        except Timeout as tout:
            raise tout
        except Exception as err:
            raise err

    def errback(self, msg, failure):
        return {
            "success": False,
            "msg": msg + " Error: " + str(failure)
        }

    def get_value_from_dict(self, data, key, default=None):
        try:
            result = data
            tokens = key.split(".")
            for token in tokens:
                result = result.get(token, None)
                if result is None:
                    return default
            return result
        except Exception as error:
            raise error

    def transform_to_list(self, data):
        data = [] if data is None else data
        data = [data] if isinstance(data, dict) else data
        return data

    @abstractmethod
    def fetch(self):
        pass

    @abstractmethod
    def parse(self, response):
        pass
