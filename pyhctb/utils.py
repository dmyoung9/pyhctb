"""Utility methods to manipulate data from the API"""

from datetime import datetime
from typing import Dict, Optional, Tuple

from . import COORDINATE_KEYS, SCHEDULE_KEYS, TIME_PARSE_FORMAT


def convert_to_timestamp(
    time_tuple: Tuple[str, str], today: datetime
) -> Dict[str, Optional[str]]:
    """Converts a tuple of time strings into datetimes."""
    scheduled, actual = time_tuple
    scheduled_time = datetime.combine(
        today, datetime.strptime(scheduled, TIME_PARSE_FORMAT).time()
    )
    actual_time = (
        datetime.combine(today, datetime.strptime(actual, TIME_PARSE_FORMAT).time())
        if actual
        else None
    )
    return dict(
        zip(
            SCHEDULE_KEYS,
            (
                str(scheduled_time),
                str(actual_time) if actual_time else None,
            ),
        )
    )


def convert_coordinates(coordinate_tuple) -> Dict[str, Optional[float]]:
    """Converts a tuple of coordinates into latitude and longitude."""
    return dict(
        zip(
            COORDINATE_KEYS,
            (float(coord) if coord else coord for coord in coordinate_tuple),
        )
    )
