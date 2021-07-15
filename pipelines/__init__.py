from models.history.import_history import ImportHistoryDataKeys

from pipelines.meetings import MeetingPipeline
from pipelines.offerings import OfferingPipeline
from pipelines.offerings_overview import OfferingOverviewPipeline
from pipelines.programs import ProgramPipeline
from pipelines.programs_detail import ProgramDetailPipeline
from pipelines.sections import SectionPipeline


class PipelineFactory:
    def __init__(self, importer_id, import_history_id, code):
        self.importer_id = importer_id
        self.import_history_id = import_history_id
        self.code = code

    def get_pipeline(self, name):
        if name == ImportHistoryDataKeys.offerings:
            return OfferingPipeline(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                code=self.code
            )
        elif name == ImportHistoryDataKeys.offerings_overview:
            return OfferingOverviewPipeline(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                code=self.code
            )

        elif name == ImportHistoryDataKeys.sections:
            return SectionPipeline(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                code=self.code
            )

        elif name == ImportHistoryDataKeys.meetings:
            return MeetingPipeline(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                code=self.code
            )
        elif name == ImportHistoryDataKeys.programs:
            return ProgramPipeline(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                code=self.code
            )
        elif name == ImportHistoryDataKeys.programs_detail:
            return ProgramDetailPipeline(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                code=self.code
            )
        else:
            raise NotImplementedError
