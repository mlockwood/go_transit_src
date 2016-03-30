
class RidershipError(Exception):

    def __init__(self, message):
        self.message = message


class NotExistVersionNumberError(RidershipError):
    pass


class MissingMetadataError(RidershipError):
    pass


class MetadataError(RidershipError):
    pass


class EntryError(RidershipError):
    pass

class StopValidationError(RidershipError):
    pass


class RidershipWarnings(object):

    def __init__(self, message):
        self.message = message
        self.alert()

    def alert(self):
        print('Warning: {}'.format(self.message))


class NamingConventionWarning(RidershipWarnings):
    pass


class FileNameMismatchWarning(RidershipWarnings):
    pass