import datetime
from abc import ABCMeta, abstractmethod

from models.history.import_history import ImportHistoryData
from mongoengine import NotUniqueError

import utils
from client import aws_client
from utils import addlogger


@addlogger
class BasePipeline(metaclass=ABCMeta):
    SAVE_ON_S3 = True

    def __init__(self, importer_id, import_history_id, code):
        self.importer_id = importer_id
        self.import_history_id = import_history_id
        self.story_count = 0
        self.code = code
        self.s3 = aws_client.get_s3_client()
        self.bucket, self.folder = aws_client.get_aws_resources()
        # self.log = utils.get_logger()

    def save_object_to_s3(self, path, obj):
        try:
            obj = str(obj)
            return self.s3.Bucket(self.bucket).put_object(Key=path, Body=obj)
        except Exception as error:
            raise error

    def save_history_to_mongodb(self, data_dict, history_data):
        try:
            history_data.save()
            self.story_count += 1
        except NotUniqueError as error:
            self.__log.warning("key_name: %s | Tried duplicate entry; Error: %s"
                               % (history_data.key_name, str(error)))

    def folder_structure_from_date(self, date):
        if date is None:
            date = datetime.datetime.utcnow()
        try:
            date_folder = date.strftime("d=%Y-%m-%d/h=%H")
            return date_folder
        except Exception as error:
            raise error

    def get_history_model(self, story, spider,
                          key_name=None, data_object_id=None):
        if key_name is None:
            key_name = spider.name

        history_data = ImportHistoryData(
            history=self.import_history_id,
            key_name=key_name,
            data_object_id=data_object_id,
            data_object=story.get(key_name)
        )
        return history_data

    @abstractmethod
    def import_history(self, item, spider):
        pass

    @abstractmethod
    def dump_story(self, item, spider):
        pass

    @abstractmethod
    def process_item(self, item, spider):
        raise NotImplemented
