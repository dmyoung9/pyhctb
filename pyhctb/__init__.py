"""Constants used in the API"""

import logging

from .api_types import (
    BusStopKey,
    CoordinateKey,
    PassengerInfoKey,
    ScheduleKey,
    TimeSpanKey,
)

LOGGER_ID = "HCTB_API"
LOGGER = logging.getLogger(LOGGER_ID)

BASE_URL = "https://login.herecomesthebus.com"
AUTH_URL = f"{BASE_URL}/authenticate.aspx"
MAP_URL = f"{BASE_URL}/Map.aspx"
REFRESH_URL = f"{MAP_URL}/RefreshMap"

FORM_FIELDS = {
    "username": "ctl00$ctl00$cphWrapper$cphContent$tbxUserName",
    "password": "ctl00$ctl00$cphWrapper$cphContent$tbxPassword",
    "code": "ctl00$ctl00$cphWrapper$cphContent$tbxAccountNumber",
    "passenger": "ctl00$ctl00$cphWrapper$cphControlPanel$ddlSelectPassenger",
}

ACTUAL_TIME_REGEX = r"Actual:\s*(\d{2}:\d{2}\s*(?:AM|PM))"
BUS_NUMBER_REGEX = r"Bus\s*(\d+)"
BUS_PUSHPIN_REGEX = r"SetBusPushPin\(([-+]?\d*\.?\d+),\s*([-+]?\d*\.?\d+)"
TIME_REGEX = r"Scheduled: (\d{2}:\d{2} [APM]{2})(?: Actual: (\d{2}:\d{2} [APM]{2}))?"
SCHEDULED_TIME_REGEX = r"Scheduled:\s*(\d{2}:\d{2}\s*(?:AM|PM))"

DATE_PARSE_FORMAT = "%Y-%m-%d"
TIME_PARSE_FORMAT = "%I:%M %p"

BUS_STOP_KEYS = BusStopKey.__args__
COORDINATE_KEYS = CoordinateKey.__args__
PASSENGER_INFO_KEYS = PassengerInfoKey.__args__
SCHEDULE_KEYS = ScheduleKey.__args__
TIME_SPAN_KEYS = TimeSpanKey.__args__
