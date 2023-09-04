"""API for getting data from Here Comes The Bus"""

from typing import List, Optional, Union

from bs4 import BeautifulSoup
from mechanicalsoup import StatefulBrowser

from . import (
    AUTH_URL,
    FORM_FIELDS,
    LOGGER,
    REFRESH_URL,
)
from .api_types import PassengerInfo, TimeSpanKey
from .exceptions import (
    InvalidAuthorizationException,
    NotAuthenticatedException,
    PassengerInfoException,
    UnsuccessfulRequestException,
)


class HctbApi:
    """API client class for Here Comes The Bus"""

    def __init__(self, username: str, password: str, code: str):
        self.credentials = {
            "username": username,
            "password": password,
            "code": code,
        }

        self.authenticated = False
        self.browser = StatefulBrowser()
        self.soup: Optional[BeautifulSoup] = None

    def _perform_login(self) -> bool:
        self.browser.open(AUTH_URL)
        self.browser.select_form()

        for key, cred in self.credentials.items():
            self.browser[FORM_FIELDS[key]] = cred

        self.browser.submit_selected()

        cookies = {c.name: str(c.value) for c in self.browser.get_cookiejar()}
        self.authenticated = ".ASPXFORMSAUTH" in cookies

        if not self.authenticated:
            raise InvalidAuthorizationException()

        map_page = self.browser.get(REFRESH_URL)
        self.soup = BeautifulSoup(map_page.content, "html.parser")
        return self.authenticated

    def _get_response(self, passenger: PassengerInfo, timespan_id: str) -> str:
        if not self.authenticated and not self._perform_login():
            raise NotAuthenticatedException()

        post_data = {
            **passenger,
            "timeSpanId": timespan_id,
            "wait": "false",
        }

        response = self.browser.post(REFRESH_URL, json=post_data)

        if not response.ok:
            raise UnsuccessfulRequestException(response.status_code)

        return response.json()["d"]

    def _get_timespan_id(self, timespan: TimeSpanKey) -> str:
        if self.soup is None and not self._perform_login():
            raise NotAuthenticatedException()

        return self.soup.find(string=timespan).parent["value"]

    def _get_passenger_list(self) -> List[PassengerInfo]:
        if self.soup is None and not self._perform_login():
            raise NotAuthenticatedException()

        passenger_field = FORM_FIELDS["passenger"]
        if fields := self.soup.select(f'select[name="{passenger_field}"]'):
            return (
                [
                    {"legacyID": passenger["value"], "name": passenger.text}
                    for passenger in passengers
                ]
                if (passengers := [o for o in fields[0].children if o != "\n"])
                else []
            )

        raise PassengerInfoException()

    # def _get_time_data(self, time_span_id: str) -> ScheduleData:
    #     response_data = self._get_api_response(time_span_id)
    #     return re.findall(TIME_REGEX, response_data)

    # def _get_coordinate_data(self, time_span_id: str) -> CoordinateData:
    #     response_data = self._get_api_response(time_span_id)
    #     return re.findall(BUS_PUSHPIN_REGEX, response_data)

    # def _parse_time_span(
    #     self, span: Optional[str] = None
    # ) -> Union[Schedule, AllSchedules,]:
    #     time_spans: AllSchedules = {
    #         span: dict.fromkeys(BUS_STOP_KEYS, {}) for span in TIME_SPAN_KEYS
    #     }

    #     def process_span(span: str):
    #         time_span_id = self._get_time_span_id(span)
    #         time_span_matches = self._get_time_data(time_span_id)
    #         if not time_span_matches:
    #             return

    #         today = datetime.now()
    #         bus, school = (
    #             time_span_matches[:2] if span == "AM" else time_span_matches[:2][::-1]
    #         )

    #         time_spans[span].update(
    #             dict(
    #                 zip(
    #                     BUS_STOP_KEYS,
    #                     (
    #                         convert_to_timestamp(bus, today),
    #                         convert_to_timestamp(school, today),
    #                     ),
    #                 )
    #             )
    #         )

    #     if span is not None:
    #         process_span(span)
    #         return time_spans[span]

    #     for span in TIME_SPAN_KEYS:
    #         if span == "MID":  # Skip, as we don't have data for this yet
    #             continue
    #         process_span(span)

    #     return time_spans

    # def _parse_coordinates(
    #     self, span: Optional[str]
    # ) -> Union[Coordinates, AllCoordinates]:
    #     coordinates: AllCoordinates = {
    #         span: dict.fromkeys(COORDINATE_KEYS) for span in TIME_SPAN_KEYS
    #     }

    #     def process_span(span: str):
    #         time_span_id = self._get_time_span_id(span)
    #         coordinate_matches = self._get_coordinate_data(time_span_id)
    #         if not coordinate_matches:
    #             return

    #         converted_coordinates = convert_coordinates(coordinate_matches[0])
    #         coordinates[span].update(converted_coordinates)

    #     if span is not None:
    #         process_span(span)
    #         return coordinates[span]

    #     for span in TIME_SPAN_KEYS:
    #         if span == "MID":  # Skip, as we don't have data for this yet
    #             continue
    #         process_span(span)

    #     return coordinates

    def authenticate(self) -> bool:
        """Authenticate and retrieve cookies from HCTB."""
        try:
            return self._perform_login()
        except InvalidAuthorizationException as iae:
            LOGGER.error(iae)

    def get_passenger_info(
        self, passenger: Optional[PassengerInfo] = None
    ) -> Optional[Union[PassengerInfo, List[PassengerInfo]]]:
        """Get passenger info from HCTB."""
        try:
            passengers = self._get_passenger_list()
        except NotAuthenticatedException as nae:
            LOGGER.error(nae)
        except PassengerInfoException as pie:
            LOGGER.error(pie)

        if passenger is None:
            return passengers

        return next(
            (p for p in passengers if p == passenger),
            None,
        )

    # def get_bus_schedule(
    #     self, passenger_id: Optional[str] = None, time_span: Optional[str] = None
    # ) -> Optional[Union[Schedule, AllSchedules]]:
    #     """Get bus schedule from HCTB."""
    #     pass

    # def get_bus_coordinates(
    #     self, time_span: Optional[str] = None
    # ) -> Optional[Union[Coordinates, AllCoordinates]]:
    #     """Get bus coordinates from HCTB."""

    #     if not self.authenticated:
    #         raise NotAuthenticatedException()

    #     try:
    #         return self._parse_coordinates(time_span)
    #     except UnsuccessfulRequestException:
    #         return None
