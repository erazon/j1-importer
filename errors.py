class ImporterException(Exception):
    pass


class SpiderException(ImporterException):
    pass


class CourseidMissingException(SpiderException):
    pass


class MongodbException(ImporterException):
    pass


class ParseException(SpiderException):
    pass


class MongoNotFoundException(MongodbException):
    pass


class MongoSaveException(MongodbException):
    pass
