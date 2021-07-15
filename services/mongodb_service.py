import bson
from models.history.import_history import ImportHistory, ImportHistoryData
from models.importer import BaseImporterConfig
from mongoengine import DoesNotExist

from client import mongoengine_client
from errors import MongoSaveException


def get_importer_config(importer_id):
    try:
        importer_obj = BaseImporterConfig.objects(id=importer_id).get()
        return importer_obj
    except DoesNotExist as e:
        raise e
    except Exception as e:
        raise e


def create_new_import_history(importer_obj, importer_name, base_url,
                              importer_start_time):
    try:
        import_history = ImportHistory(
            importer_name=importer_name,
            base_url=base_url,
            importer_config=importer_obj.id,
            importer_start_time=importer_start_time,
            importer_config_sanpshot=importer_obj.to_mongo(),
            updated_at=importer_start_time,
            created_at=importer_start_time
        )
        import_history.save()
        return import_history
    except Exception as e:
        raise MongoSaveException(
            "error on creating new import_history %s " % e)


def update_importer_status(importer_id, importer_status, imp_execution_status):
    try:
        importer_obj = get_importer_config(importer_id=importer_id)
        importer_obj.status = importer_status
        importer_obj.execution_status = imp_execution_status
        importer_obj.save()
    except Exception as error:
        raise error


def update_importer_last_history_id(importer_id, import_history_id):
    try:
        importer_obj = get_importer_config(importer_id=importer_id)
        importer_obj.last_import_history = import_history_id
        importer_obj.save()
    except Exception as error:
        raise error


def insert_error_mongodb(import_history_id, error_msg):
    try:
        importer_history_obj = ImportHistory.objects(id=import_history_id).get()
        importer_history_obj.error = error_msg
        importer_history_obj.save()
        return importer_history_obj
    except DoesNotExist as e:
        raise e
    except Exception as e:
        raise e


def insert_stats_mongodb(import_history_id, stats):
    try:
        importer_history_obj = ImportHistory.objects(id=import_history_id).get()
        importer_history_obj.stats = stats
        importer_history_obj.save()
        return importer_history_obj
    except DoesNotExist as e:
        raise e
    except Exception as e:
        raise e


def get_history_data(import_history_id, key_name, data_object_id=None):
    try:
        importer_history_obj = ImportHistoryData.objects(
            history=bson.ObjectId(import_history_id),
            key_name=key_name,
            # data_object_id=data_object_id
        )
        return importer_history_obj
    except DoesNotExist as e:
        raise e
    except Exception as e:
        raise e


def test():
    from config import Config as config
    mongoengine_client.connect_to_mongodb(config)
    hid = "5e316b89cb6f26adc9e5a27f"
    key_name = "offerings"

    for obj in get_history_data(hid, key_name):
        print(obj)
        print("==========")

# test()
