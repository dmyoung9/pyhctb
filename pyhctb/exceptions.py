"""Exceptions that can occur from the API"""


class InvalidAuthorizationException(Exception):
    """Raised when invalid credentials are used to attempt to authenticate."""

    def __init__(self, *args, **kwargs):
        super().__init__("Invalid authorization!")


class PassengerDataException(Exception):
    """Raised when passenger data cannot be parsed."""

    def __init__(self, *args, **kwargs):
        super().__init__("Couldn't parse passenger data!")


class UnsuccessfulRequestException(Exception):
    """Raised when a connection cannot be established."""

    def __init__(self, status_code, *args, **kwargs):
        super().__init__(f"Request unsuccessful: {status_code}")
