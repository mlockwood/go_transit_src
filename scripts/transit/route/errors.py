

class RouteError(Exception):

    def __init__(self, message):
        self.message = message


class JointHeadwayNotMatchError(RouteError):
    pass


class JointRoutesNotMatchError(RouteError):
    pass