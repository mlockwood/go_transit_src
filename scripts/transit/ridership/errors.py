class ErrorManager(object):

    def __init__(self, error_type, message):
        self.error_type = error_type
        self.message = message

    def get_error_message(self):
        return self.error_type, self.message


class MissingMetadataError(ErrorManager):

    @staticmethod
    def get(meta):
        return MissingMetadataError('MissingMetadataError', 'Missing metadata for "{}"'.format(meta)
                                    ).get_error_message()


class MetadataError(ErrorManager):

    @staticmethod
    def get(meta, value):
        return MetadataError('MetadataError', 'Meta of "{}" could not process with value of "{}"'.format(meta, value)
                             ).get_error_message()


class EntryError(ErrorManager):

    @staticmethod
    def get(row, entry_type):
        return EntryError('EntryError', 'The record in row {} does not have a {}'.format(row, entry_type)
                          ).get_error_message()


class StopValidationError(ErrorManager):

    @staticmethod
    def get(entry_type, stop, row):
        return StopValidationError('StopValidationError', '{} stop of {} in row {} is not a valid stop'.format(
            entry_type, stop, row)).get_error_message()


class TimeValidationError(ErrorManager):

    @staticmethod
    def get(time, row):
        return TimeValidationError('TimeValidationError', 'Time {} in row {} is not a valid time'.format(time, row)
                                   ).get_error_message()


class CountValidationError(ErrorManager):

    @staticmethod
    def get(count, row):
        return CountValidationError('CountValidationError', 'The count of {} in row {} is not a valid count'.format(
            count, row)).get_error_message()


class WarningManager(object):

    def __init__(self, warning_type, message):
        self.warning_type = warning_type
        self.message = message

    def get_warning_message(self):
        return self.warning_type, self.message


class NamingConventionWarning(WarningManager):

    @staticmethod
    def get():
        return NamingConventionWarning('NamingConventionWarning', 'File does not have proper naming convention'
                                       ).get_warning_message()


class FileNameMismatchWarning(WarningManager):

    @staticmethod
    def get():
        return FileNameMismatchWarning('FileNameMismatchWarning', 'Year, month, and day of filename does not match ' +
                                       'metadata').get_warning_message()


class EmptyDataWarning(WarningManager):

    @staticmethod
    def get():
        return EmptyDataWarning('EmptyDataWarning', 'File does not contain any data').get_warning_message()

