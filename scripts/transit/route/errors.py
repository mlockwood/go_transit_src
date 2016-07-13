

class RouteError(Exception):

    def __init__(self, message):
        self.message = message


class DuplicateServiceSheetError(RouteError):
    pass


class UnknownStopPointError(RouteError):
    pass


class DuplicateTimingSpreadError(RouteError):
    pass


class JointHeadwayNotMatchError(RouteError):
    pass


class JointRouteMismatchedDriverCount(RouteError):
    pass


class IncongruentSchedulesError(RouteError):
    pass


class MismatchedJointSchedulesTimingError(RouteError):
    pass


class LaxConstraintFailureError(RouteError):
    pass