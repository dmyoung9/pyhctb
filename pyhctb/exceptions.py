"""Exceptions that can occur from the API"""


class InvalidAuthorizationException(Exception):
    """Raised when invalid credentials are used to attempt to authenticate."""

    def __init__(self):
        super().__init__("Invalid authorization!")


class NotAuthenticatedException(Exception):
    """Raised when not authenticated."""

    def __init__(self):
        super().__init__("Not authenticated!")


class PassengerInfoException(Exception):
    """Raised when passenger info cannot be parsed."""

    def __init__(self):
        super().__init__("Couldn't parse passenger info!")


class UnsuccessfulRequestException(Exception):
    """Raised when a connection cannot be established."""

    def __init__(self, status_code):
        super().__init__(f"Request unsuccessful! - {status_code}")
