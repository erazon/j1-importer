from models.history.import_history import ImportHistoryDataKeys

from parser.meetings import MeetingsParser
from parser.offerings import OfferingParser
from parser.offerings_overview import OfferingOverviewParser
from parser.program_details import ProgramDetailParser
from parser.programs import ProgramParser
from parser.sections import SectionsParser


class ParserFactory:
    def __init__(self, importer_id, import_history_id, base_url,
                 importer_start_time):
        self.importer_id = importer_id
        self.import_history_id = import_history_id
        self.base_url = base_url
        self.importer_start_time = importer_start_time

    def get_parser(self, name):
        if name == ImportHistoryDataKeys.offerings:
            return OfferingParser(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                base_url=self.base_url,
                importer_start_time=self.importer_start_time
            )
        elif name == ImportHistoryDataKeys.offerings_overview:
            return OfferingOverviewParser(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                base_url=self.base_url,
                importer_start_time=self.importer_start_time
            )

        elif name == ImportHistoryDataKeys.sections:
            return SectionsParser(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                base_url=self.base_url,
                importer_start_time=self.importer_start_time
            )

        elif name == ImportHistoryDataKeys.meetings:
            return MeetingsParser(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                base_url=self.base_url,
                importer_start_time=self.importer_start_time
            )
        elif name == ImportHistoryDataKeys.programs:
            return ProgramParser(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                base_url=self.base_url,
                importer_start_time=self.importer_start_time
            )
        elif name == ImportHistoryDataKeys.programs_detail:
            return ProgramDetailParser(
                importer_id=self.importer_id,
                import_history_id=self.import_history_id,
                base_url=self.base_url,
                importer_start_time=self.importer_start_time
            )
        else:
            raise NotImplemented()
