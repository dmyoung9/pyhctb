class InvalidAuthorizationException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Invalid authorization!")


class PassengerDataException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__("Couldn't parse passenger data!")
