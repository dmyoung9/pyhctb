"""Command-line tool for the Here Comes The Bus API"""

import argparse
import json
from typing import Optional, Tuple

from .api import HctbApi
from .exceptions import InvalidAuthorizationException


ARGS = (
    ("-u", "--username", True, "Username"),
    ("-p", "--password", True, "Password"),
    ("-c", "--code", True, "School Code"),
    ("-t", "--time", False, "Timespan"),
)


def _parse_cli_args() -> Tuple[str, str, str, Optional[str]]:
    parser = argparse.ArgumentParser()
    for arg in ARGS:
        parser.add_argument(*arg[:2], required=arg[2], help=arg[3])

    args = parser.parse_args()

    username = str(args.username)
    password = str(args.password)
    code = str(args.code)
    time_span = str(args.time) if args.time is not None else None

    return (username, password, code, time_span)


def cli() -> None:
    """Defines the CLI."""
    username, password, code, time_span = _parse_cli_args()
    api = HctbApi(username, password, code)
    if not api.authenticate():
        raise InvalidAuthorizationException()

    passenger_info = api.get_passenger_info()
    bus_schedule = api.get_bus_schedule(time_span)
    bus_coordinates = api.get_bus_coordinates(time_span)

    print("Passenger Info:", json.dumps(passenger_info, indent=4))
    print("Bus Schedule:", json.dumps(bus_schedule, indent=4))
    print("Bus Coordinates:", json.dumps(bus_coordinates, indent=4))


if __name__ == "__main__":
    cli()
