"""Constants used in the API"""

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

BUS_STOP_KEYS = ("bus_stop", "school_stop")
COORDINATE_KEYS = ("latitude", "longitude")
PASSENGER_INFO_KEYS = ("legacyID", "name")
SCHEDULE_KEYS = ("scheduled", "actual")
TIME_SPANS = ("AM", "MID", "PM")
