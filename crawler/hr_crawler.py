import logging

from parser import ParserFactory
from pipelines import PipelineFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class HrCrawler:
    def __init__(self, importer_id, base_url,
                 import_history_id, importer_start_time, code):
        self.importer_id = importer_id
        self.base_url = base_url
        self.import_history_id = import_history_id
        self.importer_start_time = importer_start_time
        self.code = code

    def __run(self, parser, pipeline):
        try:
            for response in parser.fetch():
                success = response.get('success')
                if not success:
                    return response
                data = response.get('data', None)
                if data:
                    pipeline.process_item(data, parser)
            return {"success": True, "msg": "Smile"}
        except Exception as error:
            logger.exception(error)
            return {
                "success": False,
                "msg": "error on parserName: %s | Error: %s" % (
                    parser.name, str(error))}

    def crawl(self, parser_list=None):
        if parser_list is None:
            return {"success": False, "msg": "parser_list undefined"}

        parser_factory = ParserFactory(
            importer_id=self.importer_id,
            import_history_id=self.import_history_id,
            base_url=self.base_url,
            importer_start_time=self.importer_start_time
        )
        pipeline_factory = PipelineFactory(
            importer_id=self.importer_id,
            import_history_id=self.import_history_id,
            code=self.code
        )
        total_story_count = 0
        count_story = {}
        for name in parser_list:
            logger.info("Starting spider - Name: %s" % name)
            parser = parser_factory.get_parser(name)
            pipeline = pipeline_factory.get_pipeline(name)
            response = self.__run(parser, pipeline)
            success = response.get('success')
            if not success:
                return response
            else:
                logger.info("ParserName: {} | StoryCount: {}\n".format(
                    parser.name, pipeline.story_count))
                total_story_count += pipeline.story_count
                count_story[parser.name] = pipeline.story_count
            pass

        result = {
            "success": True,
            "msg": "Smile",
            "tcount": total_story_count,
            "count": count_story
        }
        return result
