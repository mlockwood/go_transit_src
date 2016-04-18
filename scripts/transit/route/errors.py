

class RouteError(Exception):

    def __init__(self, message):
        self.message = message


class UnknownStopPointError(RouteError):
    pass


class DuplicateTimingSpreadError(RouteError):
    pass


class JointHeadwayNotMatchError(RouteError):
    pass


class JointRoutesNotMatchError(RouteError):
    pass