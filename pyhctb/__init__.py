"""Constants used in the API"""

from enum import Enum

BASE_URL = "https://login.herecomesthebus.com"
AUTH_URL = f"{BASE_URL}/authenticate.aspx"
MAP_URL = f"{BASE_URL}/Map.aspx"
REFRESH_URL = f"{MAP_URL}/RefreshMap"

FORM_FIELDS = {
    "username": "ctl00$ctl00$cphWrapper$cphContent$tbxUserName",
    "password": "ctl00$ctl00$cphWrapper$cphContent$tbxPassword",
    "code": "ctl00$ctl00$cphWrapper$cphContent$tbxAccountNumber",
}

BUS_PUSHPIN_REGEX = r"SetBusPushPin\(([-+]?\d*\.?\d+),\s*([-+]?\d*\.?\d+)"
TIME_REGEX = r"Scheduled: (\d{2}:\d{2} [APM]{2})(?: Actual: (\d{2}:\d{2} [APM]{2}))?"
TIME_PARSE_FORMAT = "%I:%M %p"


class BusStopKey(str, Enum):
    """Keys for types of bus stops"""

    BUS_STOP = "bus_stop"
    SCHOOL_STOP = "school_stop"


class CoordinateKey(str, Enum):
    """Keys for coordinate segments"""

    LATITUDE = "latitude"
    LONGITUDE = "longitude"


class PassengerKey(str, Enum):
    """Keys for passenger info"""

    LEGACY_ID = "legacyID"
    NAME = "name"


class ScheduleKey(str, Enum):
    """Keys for stop times"""

    ACTUAL = "actual"
    SCHEDULED = "scheduled"


class TimeSpanKey(str, Enum):
    """Keys for time spans"""

    AM = "AM"
    MID = "MID"
    PM = "PM"


BUS_STOP_KEYS = tuple(key.value for key in BusStopKey)
COORDINATE_KEYS = tuple(key.value for key in CoordinateKey)
PASSENGER_INFO_KEYS = tuple(key.value for key in PassengerKey)
SCHEDULE_KEYS = tuple(key.value for key in ScheduleKey)
TIME_SPAN_KEYS = tuple(key.value for key in TimeSpanKey)
