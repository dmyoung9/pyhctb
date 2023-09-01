"""API for getting data from Here Comes The Bus"""

from datetime import datetime
import re
from typing import Dict, List, Optional, Tuple, Union

from bs4 import BeautifulSoup
from mechanicalsoup import StatefulBrowser

from . import (
    AUTH_URL,
    BUS_PUSHPIN_REGEX,
    COORDINATE_KEYS,
    FORM_FIELDS,
    PASSENGER_INFO_KEYS,
    REFRESH_URL,
    TIME_REGEX,
    TIME_SPANS,
    BUS_STOP_KEYS,
)
from .api_types import AllCoordinates, AllSchedules, Coordinates, Schedule
from .exceptions import (
    InvalidAuthorizationException,
    NotAuthenticatedException,
    PassengerInfoException,
    UnsuccessfulRequestException,
)
from .utils import convert_to_timestamp, convert_coordinates


class HctbApi:
    """API client class for Here Comes The Bus"""

    def __init__(self, username: str, password: str, code: str):
        self.authenticated = False
        self.credentials = {
            "username": username,
            "password": password,
            "code": code,
        }
        self.passenger_info = dict.fromkeys(PASSENGER_INFO_KEYS, "")
        self.time_spans: AllSchedules = {
            span: dict.fromkeys(BUS_STOP_KEYS, {}) for span in TIME_SPANS
        }

        self.browser = StatefulBrowser()
        self.soup: Optional[BeautifulSoup] = None

    def _perform_login(self) -> None:
        self.browser.open(AUTH_URL)
        self.browser.select_form()

        for key, cred in self.credentials.items():
            self.browser[FORM_FIELDS[key]] = cred

        self.browser.submit_selected()

        cookies = {c.name: str(c.value) for c in self.browser.get_cookiejar()}
        if ".ASPXFORMSAUTH" not in cookies:
            self.authenticated = False
            raise InvalidAuthorizationException()

        map_page = self.browser.get(REFRESH_URL)
        self.soup = BeautifulSoup(map_page.content, "html.parser")

        self.passenger_info = self._parse_passenger_info()
        self.authenticated = True

    def _parse_passenger_info(self) -> Dict[str, str]:
        if self.soup is None:
            raise NotAuthenticatedException()

        selected_options = self.soup.select('option[selected="selected"]')

        passenger_info = dict.fromkeys(PASSENGER_INFO_KEYS, "")
        if len(selected_options) < 1:
            raise PassengerInfoException()

        name = selected_options[1].text
        person = selected_options[1]["value"]

        passenger_info = dict(zip(PASSENGER_INFO_KEYS, (person, name)))
        return passenger_info

    def _get_api_response(self, time_span_id: str) -> str:
        response = self.browser.post(
            REFRESH_URL,
            json={**self.passenger_info, "timeSpanId": time_span_id, "wait": "false"},
            timeout=5,
        )

        if not response.ok:
            raise UnsuccessfulRequestException(response.status_code)

        return response.json()["d"]

    def _get_time_span_id(self, span: str) -> str:
        if self.soup is None:
            raise NotAuthenticatedException()

        return self.soup.find(string=span).parent["value"]

    def _get_time_data(self, time_span_id: str) -> List[Tuple[str, str]]:
        response_data = self._get_api_response(time_span_id)
        return re.findall(TIME_REGEX, response_data)

    def _get_coordinate_data(self, time_span_id: str) -> List[Tuple[str, str]]:
        response_data = self._get_api_response(time_span_id)
        return re.findall(BUS_PUSHPIN_REGEX, response_data)

    def _parse_time_span(
        self, span: Optional[str] = None
    ) -> Union[Schedule, AllSchedules,]:
        time_spans: AllSchedules = {
            span: dict.fromkeys(BUS_STOP_KEYS, {}) for span in TIME_SPANS
        }

        def process_span(span: str):
            time_span_id = self._get_time_span_id(span)
            time_span_matches = self._get_time_data(time_span_id)
            if not time_span_matches:
                return

            today = datetime.now()
            bus, school = (
                time_span_matches[:2] if span == "AM" else time_span_matches[:2][::-1]
            )

            time_spans[span].update(
                dict(
                    zip(
                        BUS_STOP_KEYS,
                        (
                            convert_to_timestamp(bus, today),
                            convert_to_timestamp(school, today),
                        ),
                    )
                )
            )

        if span is not None:
            process_span(span)
            return time_spans[span]

        for span in TIME_SPANS:
            if span == "MID":  # Skip, as we don't have data for this yet
                continue
            process_span(span)

        return time_spans

    def _parse_coordinates(
        self, span: Optional[str]
    ) -> Union[Coordinates, AllCoordinates]:
        coordinates: AllCoordinates = {
            span: dict.fromkeys(COORDINATE_KEYS) for span in TIME_SPANS
        }

        def process_span(span: str):
            time_span_id = self._get_time_span_id(span)
            coordinate_matches = self._get_coordinate_data(time_span_id)
            if not coordinate_matches:
                return

            converted_coordinates = convert_coordinates(coordinate_matches[0])
            coordinates[span].update(converted_coordinates)

        if span is not None:
            process_span(span)
            return coordinates[span]

        for span in TIME_SPANS:
            if span == "MID":  # Skip, as we don't have data for this yet
                continue
            process_span(span)

        return coordinates

    def authenticate(self) -> bool:
        """Authenticate and retrieve cookies from HCTB."""
        try:
            self._perform_login()
        except InvalidAuthorizationException:
            return False
        except PassengerInfoException:
            return False

        return self.authenticated

    def get_passenger_info(self) -> dict[str, str]:
        """Get passenger info from HCTB."""
        if not self.authenticated:
            raise NotAuthenticatedException()

        info = self.passenger_info.copy()
        info.pop("legacyID", None)

        return info

    def get_bus_schedule(
        self, time_span: Optional[str] = None
    ) -> Optional[Union[Schedule, AllSchedules]]:
        """Get bus schedule from HCTB."""
        if not self.authenticated:
            raise NotAuthenticatedException()

        try:
            return self._parse_time_span(time_span)
        except UnsuccessfulRequestException:
            return None

    def get_bus_coordinates(
        self, time_span: Optional[str] = None
    ) -> Optional[Union[Coordinates, AllCoordinates]]:
        """Get bus coordinates from HCTB."""

        if not self.authenticated:
            raise NotAuthenticatedException()

        try:
            return self._parse_coordinates(time_span)
        except UnsuccessfulRequestException:
            return None
