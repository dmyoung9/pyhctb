"""Functions for parsing response data from the API"""

from datetime import datetime
import re
from typing import Optional, Tuple

from api_types import Coordinates, Schedule, StopData

from . import (
    ACTUAL_TIME_REGEX,
    BUS_NUMBER_REGEX,
    COORDINATE_KEYS,
    DATE_PARSE_FORMAT,
    SCHEDULE_KEYS,
    SCHEDULED_TIME_REGEX,
)
from .utils import (
    clean_data_string,
    extract_parenthesis_content,
    get_local_timezone,
    split_args,
    time_to_unix_timestamp,
)


def parse_stop_data(
    stop_info: Optional[str],
    stop_times: Optional[str],
    stop_coordinates: Tuple[Optional[str], Optional[str]],
) -> StopData:
    """Parses data about a single bus stop"""

    stop_type, stop_name, timespan = (
        extract_stop_attributes(stop_info)
        if stop_info is not None
        else (None, None, None)
    )

    if None in (stop_type, stop_name, timespan):
        return None

    times = extract_stop_times(stop_times)
    coordinates = format_coordinates(stop_coordinates)

    return {
        "type": stop_type,
        "name": stop_name,
        "timespan": timespan,
        "schedule": times,
        "coordinates": coordinates,
    }


def extract_stop_attributes(
    stop: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Parses type and name of bus stop"""

    if stop is None:
        return None, None

    split_stop = stop.split(":")

    if len(split_stop) < 2:
        return None, None, None

    stop_type = (
        split_stop[0].strip('"').strip().lower().replace(" ", "_")
        if split_stop is not None
        else None
    )
    stop_name = split_stop[1].split("(")[0].strip() if split_stop is not None else None

    timespan_match = re.search(r"\((.*?)\)", stop)
    timespan = timespan_match[1] if timespan_match else None

    return stop_type, stop_name, timespan


def extract_stop_times(stop_times_str: Optional[str]) -> Schedule:
    """Parses bus stop times from a string,
    returning them as a dictionary of Unix timestamps."""

    if stop_times_str is None:
        return dict.fromkeys(SCHEDULE_KEYS)

    current_date_str = datetime.now().strftime(DATE_PARSE_FORMAT)
    user_timezone = get_local_timezone()

    scheduled_match = re.search(SCHEDULED_TIME_REGEX, stop_times_str.strip('"'))
    actual_match = re.search(ACTUAL_TIME_REGEX, stop_times_str.strip('"'))

    return dict(
        zip(
            SCHEDULE_KEYS,
            (
                time_to_unix_timestamp(
                    match[1],
                    current_date_str,
                    user_timezone,
                )
                if match
                else None
                for match in (actual_match, scheduled_match)
            ),
        )
    )


def format_coordinates(coordinates: Tuple[Optional[str], Optional[str]]) -> Coordinates:
    """Formats a pair of coordinates from strings into floats"""

    return dict(
        zip(
            COORDINATE_KEYS,
            (
                float(coordinates[0].strip())  # type: ignore
                if coordinates[0] not in ("0", None)
                else None,
                float(coordinates[1].strip())  # type: ignore
                if coordinates[1] not in ("0", None)
                else None,
            ),
        )
    )


def extract_bus_number(bus_string: str) -> Optional[str]:
    """Extracts bus number"""

    bus_match = re.search(BUS_NUMBER_REGEX, bus_string)
    return bus_match[1] if bus_match else None


def parse_bus_data(data: str):
    """Parses bus data from a response, including bus number,
    stop types, names, and coordinates"""

    clean_data = clean_data_string(data)

    if stops_info_str := extract_parenthesis_content(
        clean_data.split("UpdateControlPanel")[-1]
    ):
        stops_args = split_args(stops_info_str)

        first_stop = parse_stop_data(
            stop_info=stops_args[0] if len(stops_args) > 0 else None,
            stop_times=stops_args[3] if len(stops_args) > 3 else None,
            stop_coordinates=(
                stops_args[5] if len(stops_args) > 5 else None,
                stops_args[6] if len(stops_args) > 6 else None,
            ),
        )
        last_stop = parse_stop_data(
            stop_info=stops_args[1] if len(stops_args) > 1 else None,
            stop_times=stops_args[4] if len(stops_args) > 4 else None,
            stop_coordinates=(
                stops_args[7] if len(stops_args) > 7 else None,
                stops_args[8] if len(stops_args) > 8 else None,
            ),
        )

        bus_number = extract_bus_number(stops_args[2])
        stops = [stop for stop in (first_stop, last_stop) if stop is not None]

        return {
            "bus_number": bus_number,
            "stops": stops,
            "coordinates": parse_bus_coordinates(data),
        }

    return None


def parse_bus_coordinates(data: str) -> Coordinates:
    """Parse bus coordinates from a response"""

    clean_data = clean_data_string(data)

    if bus_str := (
        extract_parenthesis_content(clean_data.split("SetBusPushPin")[-1])
        if "SetBusPushPin" in clean_data
        else None
    ):
        bus_args = split_args(bus_str)

        return format_coordinates(
            (
                bus_args[0] if len(bus_args) > 0 else None,
                bus_args[1] if len(bus_args) > 1 else None,
            )
        )
