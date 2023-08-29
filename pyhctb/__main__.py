import argparse
import json
from typing import Tuple

from .api import HctbApi


ARGS = (
    ("-u", "--username", True, "Username"),
    ("-p", "--password", True, "Password"),
    ("-c", "--code", True, "School Code"),
)


def _parse_cli_args() -> Tuple[str, str, str]:
    parser = argparse.ArgumentParser()
    for arg in ARGS:
        parser.add_argument(*arg[:2], required=arg[2], help=arg[3])

    args = parser.parse_args()

    username = args.username
    password = args.password
    code = args.code

    return (username, password, code)


def cli() -> None:
    username, password, code = _parse_cli_args()
    api = HctbApi(username, password, code)

    bus_data = api.get_bus_data()
    print(json.dumps(bus_data, indent=4))


if __name__ == "__main__":
    cli()
