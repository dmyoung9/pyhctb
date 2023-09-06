# ./pyhctb/utils.py
"""Utility methods to manipulate data from the API"""

from datetime import datetime
import time
from typing import List

import pytz  # type: ignore

from . import (
    DATE_PARSE_FORMAT,
    TIME_PARSE_FORMAT,
)


def time_to_unix_timestamp(time_str: str, date_str: str, timezone) -> int:
    """Converts date and time strings to an integer Unix timestamp"""

    dt_str = f"{date_str} {time_str}"
    dt_obj = datetime.strptime(dt_str, f"{DATE_PARSE_FORMAT} {TIME_PARSE_FORMAT}")
    local_tz = pytz.timezone(timezone)
    localized_dt = local_tz.localize(dt_obj)
    return int(localized_dt.timestamp())


def get_local_timezone() -> str:
    """Retrieves the user's system timezone as GMT+OFFSET"""

    offset_hour = (time.altzone if time.daylight else time.timezone) / 3600

    return f"Etc/GMT{int(offset_hour):+d}"


def clean_data_string(data: str) -> str:
    """Returns a 'clean' version of the data, with
    escaped characters and whitespace fixed"""

    return (
        data.replace("\r\n", "")
        .replace("\u0027", "'")
        .replace("\\u00A0", " ")
        .replace("\\u0026", "&")
        .replace('"', "")
        .replace("'", '"')
    )


def extract_parenthesis_content(string: str) -> str:
    """Extracts string contained between parentheses"""

    stack = []
    start = 0
    end = 0
    for i, char in enumerate(string):
        if char == "(":
            stack.append(i)
        elif char == ")":
            if stack:
                start = stack.pop()
                if not stack:
                    end = i
                    break
    return string[start + 1 : end]


def split_args(string: str) -> List[str]:
    """Split the arguments from a function-like string,
    taking into account quotes and parentheses."""

    args = []
    arg = ""
    quote = None
    depth = 0
    quote_chars = ('"', "'")

    for char in string:
        if char in quote_chars:
            if quote is None:  # Start of quoted string
                quote = char
            elif quote == char:  # End of quoted string
                quote = None
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1

        if all((char == ",", quote is None, depth == 0)):
            args.append(arg.strip())
            arg = ""
        else:
            arg += char

    if arg:
        args.append(arg.strip())

    return args
