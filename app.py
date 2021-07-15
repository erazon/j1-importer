import argparse
import datetime
import logging
import os

from campuslibs.eventmanager import event_publisher
from models.history.import_history import ImportHistoryDataKeys
from models.importer.base import ImporterStatus, ImporterExecutionStatus

from client import mongoengine_client
from config import Config
from crawler.hr_crawler import HrCrawler
from services import mongodb_service
from utils import Json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

parser = argparse.ArgumentParser(description='Spider runner')
parser.add_argument('--importer-id', type=str, required=True,
                    help='provide importer_config ID from mongodb(Ref)')
args = parser.parse_args()


def processed_base_url(base_url):
    root_phrase = "modules/shop"
    base = base_url.split(root_phrase)
    return os.path.join(base[0], root_phrase)


def main():
    importer_id = args.importer_id
    config = Config
    importer_start_time = datetime.datetime.utcnow()
    parser_list = [
        ImportHistoryDataKeys.offerings,
        ImportHistoryDataKeys.offerings_overview,
        ImportHistoryDataKeys.sections,
        ImportHistoryDataKeys.meetings,
        ImportHistoryDataKeys.programs,
        ImportHistoryDataKeys.programs_detail
    ]

    response = {
        "success": False,
        "importer_id": None,
        "import_history_id": None,
        "msg": ""
    }

    try:
        mongoengine_client.connect_to_mongodb(config)
        importer_obj = mongodb_service.get_importer_config(importer_id=importer_id)
        importer_name = importer_obj.name
        base_url = importer_obj.base_url
        base_url = processed_base_url(base_url)
        response['importer_id'] = importer_id

        import_history_obj = mongodb_service.create_new_import_history(
            importer_obj=importer_obj, importer_name=importer_name,
            base_url=base_url,
            importer_start_time=importer_start_time)
        import_history_id = import_history_obj.id
        response['import_history_id'] = str(import_history_id)

        # update current importer status & history_id
        mongodb_service.update_importer_status(
            importer_id=importer_id,
            importer_status=ImporterStatus.RUNNING.value,
            imp_execution_status=ImporterExecutionStatus.IMPORT_STARTED.value
        )

        hrcrawler = HrCrawler(
            importer_id=importer_id,
            import_history_id=import_history_id,
            base_url=base_url,
            importer_start_time=importer_start_time,
            code=importer_obj.code
        )
        result = hrcrawler.crawl(parser_list=parser_list)
        logger.debug("FinalResult: %s" % result)

        if result.get('success'):
            # Update last import history id only when import is successful
            mongodb_service.update_importer_last_history_id(
                importer_id=importer_id,
                import_history_id=import_history_id,
            )
            response['success'] = True
            response['msg'] = result.get('msg', "")
            stats = {
                "start_time": importer_start_time,
                "end_time": datetime.datetime.utcnow(),
                'tcount': result.get('tcount', -1),
                "count": result.get('count', {})
            }
            logger.info("Stats: {}".format(Json.dumps(stats, indent=2)))
            mongodb_service.update_importer_status(
                importer_id=importer_id,
                importer_status=ImporterStatus.RUNNING.value,
                imp_execution_status=ImporterExecutionStatus.IMPORT_DONE.value
            )
            mongodb_service.insert_stats_mongodb(
                import_history_id=import_history_id, stats=stats)
        else:
            response['success'] = False
            response['msg'] = result.get('msg', "")
            mongodb_service.update_importer_status(
                importer_id=importer_id,
                importer_status=ImporterStatus.ERROR.value,
                imp_execution_status=ImporterExecutionStatus.IMPORT_DONE.value
            )
            mongodb_service.insert_error_mongodb(
                import_history_id=import_history_id,
                error_msg={"error": response.get('msg')}
            )
    except (NotImplementedError, Exception) as e:
        response['success'] = False
        response['msg'] = str(e)
        logger.exception("importer_id: %s | Error: %s" % (importer_id, e))

        mongodb_service.update_importer_status(
            importer_id=importer_id,
            importer_status=ImporterStatus.ERROR.value,
            imp_execution_status=ImporterExecutionStatus.IMPORT_DONE.value
        )
        mongodb_service.insert_error_mongodb(
            import_history_id=import_history_id,
            error_msg={"error": response.get('msg')}
        )

    finally:
        logger.info("FinalResponse: %s" % response)
        action = 'status.completed.importer'
        event_publisher.publish(
            action=action,
            data=response
        )
        mongoengine_client.disconnect_to_mongodb()
        logger.info("Done!")


if __name__ == '__main__':
    main()
