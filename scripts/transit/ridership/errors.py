

class RidershipError(Exception):

    def __init__(self, message):
        self.message = message

class FileDoesNotMatchError(RidershipError):
    pass