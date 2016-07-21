class ErrorManager(object):


    def __init__(self, file, error_type, message):
        self.file = file
        self.error_type = error_type
        self.message = message

    def get_error_message(self):
        return [self.file, self.error_type, self.message]


class MissingMetadataError(ErrorManager):

    @staticmethod
    def get(file):
        return MissingMetadataError(file, 'MissingMetadataError', 'Missing corresponding metadata row in metadata.csv'
                                    ).get_error_message()


class MissingDatasheetError(ErrorManager):

    @staticmethod
    def get(file):
        return MissingDatasheetError(file, 'MissingDatasheetError', 'Missing corresponding datasheet CSV'
                                     ).get_error_message()


class MissingMetaValueError(ErrorManager):

    @staticmethod
    def get(file, meta):
        return MissingMetadataError(file, 'MissingMetadataError', 'Missing meta value for "{}"'.format(meta)
                                    ).get_error_message()


class EntryError(ErrorManager):

    @staticmethod
    def get(file, row, entry_type):
        return EntryError(file, 'EntryError', 'The record in row {} does not have a {}'.format(row, entry_type)
                          ).get_error_message()


class StopValidationError(ErrorManager):

    @staticmethod
    def get(file, entry_type, stop, row):
        return StopValidationError(file, 'StopValidationError', '{} stop of {} in row {} is not a valid stop'.format(
            entry_type, stop, row)).get_error_message()


class TimeValidationError(ErrorManager):

    @staticmethod
    def get(file, time, row):
        return TimeValidationError(file, 'TimeValidationError', 'Time {} in row {} is not a valid time'.format(time,
                                                                                                               row)
                                   ).get_error_message()


class CountValidationError(ErrorManager):

    @staticmethod
    def get(file, count, row):
        return CountValidationError(file, 'CountValidationError',
                                    'The count of {} in row {} is not a valid count'.format(count, row)
                                    ).get_error_message()


class StopUnavailableForRouteError(ErrorManager):

    @staticmethod
    def get(file, stop, route):
        return StopUnavailableForRouteError(file, 'StopUnavailableForRouteError',
                                            'The stop {} is not a part of any routes within joint route {}'.format(
                                                stop, route)).get_error_message()


class WarningManager(object):

    def __init__(self, file, warning_type, message):
        self.file = file
        self.warning_type = warning_type
        self.message = message

    def get_warning_message(self):
        return [self.file, self.warning_type, self.message]


class EmptyDataWarning(WarningManager):

    @staticmethod
    def get(file):
        return EmptyDataWarning(file, 'EmptyDataWarning', 'File does not contain any data').get_warning_message()
