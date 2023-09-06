"""API for getting data from Here Comes The Bus"""

import itertools
from typing import Dict, List, Optional, Union

from bs4 import BeautifulSoup
from mechanicalsoup import StatefulBrowser


from . import (
    AUTH_URL,
    FORM_FIELDS,
    LOGGER,
    REFRESH_URL,
    TIME_SPAN_KEYS,
)
from .api_types import (
    BusData,
    BusDataKey,
    Coordinates,
    PassengerInfo,
    PassengerInfoKey,
    StopData,
    TimeSpanKey,
)
from .exceptions import (
    InvalidAuthorizationException,
    NotAuthenticatedException,
    PassengerInfoException,
    UnsuccessfulRequestException,
)
from .parse import parse_bus_data


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
            **passenger,  # type: ignore
            "timeSpanId": timespan_id,
            "wait": "false",
        }

        LOGGER.info(
            "Getting response for %s at %s...", passenger["legacyID"], timespan_id
        )
        response = self.browser.post(REFRESH_URL, json=post_data)

        if not response.ok:
            raise UnsuccessfulRequestException(response.status_code)

        return response.json()["d"]

    def _get_timespan_id(self, timespan: TimeSpanKey) -> str:
        if self.soup is None and not self._perform_login():
            raise NotAuthenticatedException()

        return self.soup.find(string=timespan).parent["value"]  # type: ignore

    def _get_passenger_list(self) -> List[PassengerInfo]:
        if self.soup is None and not self._perform_login():
            raise NotAuthenticatedException()

        passenger_field = FORM_FIELDS["passenger"]
        if fields := self.soup.select(f'select[name="{passenger_field}"]'):  # type: ignore
            return (
                [
                    {"legacyID": passenger["value"], "name": passenger.text}
                    for passenger in passengers
                ]
                if (passengers := [o for o in fields[0].children if o != "\n"])
                else []
            )

        raise PassengerInfoException()

    def authenticate(self) -> bool:
        """Authenticate and retrieve cookies from HCTB."""
        try:
            return self._perform_login()
        except InvalidAuthorizationException as iae:
            LOGGER.error(iae)

        return False

    def get_passenger_info(self) -> Optional[Union[PassengerInfo, List[PassengerInfo]]]:
        """Get passenger info from HCTB."""
        try:
            passengers = self._get_passenger_list()
        except NotAuthenticatedException as nae:
            LOGGER.error(nae)
        except PassengerInfoException as pie:
            LOGGER.error(pie)

        return passengers

    def get_scheduled_stops(
        self,
        timespan: Optional[TimeSpanKey] = None,
        passenger_info: Optional[PassengerInfo] = None,
    ) -> Optional[List[BusData]]:
        try:
            passengers = self._get_passenger_list()
            timespan_ids = (
                [self._get_timespan_id(timespan)]
                if timespan is not None
                else [self._get_timespan_id(span) for span in TIME_SPAN_KEYS]
            )
        except NotAuthenticatedException as nae:
            LOGGER.error(nae)
        except PassengerInfoException as pie:
            LOGGER.error(pie)

        schedules: List[
            Dict[Union[PassengerInfoKey, BusDataKey], Union[str, StopData]]
        ] = []
        for passenger, timespan_id in itertools.product(passengers, timespan_ids):
            try:
                response = self._get_response(passenger, timespan_id)
            except UnsuccessfulRequestException as ure:
                LOGGER.error(ure)
                return None

            bus_data = parse_bus_data(response)

            if bus_data is not None:
                for schedule in schedules:
                    if (passenger["legacyID"], bus_data["bus_number"]) == (
                        schedule["legacyID"],
                        schedule["bus_number"],
                    ):
                        schedule["stops"].extend(bus_data["stops"])
                        break
                else:
                    schedules.append(
                        {
                            **passenger,  # type: ignore
                            "bus_number": bus_data["bus_number"],
                            "stops": bus_data["stops"],
                        }
                    )

        if passenger_info is None:
            return schedules

        return next(
            (s for s in schedules if s["legacyID"] == passenger_info["legacyID"]),
            None,
        )

    def get_bus_coordinates(self, timespan: TimeSpanKey):
        try:
            passengers = self._get_passenger_list()
            timespan_id = self._get_timespan_id(timespan)
        except NotAuthenticatedException as nae:
            LOGGER.error(nae)
        except PassengerInfoException as pie:
            LOGGER.error(pie)

        coordinates: Dict[str, Coordinates] = {}
        for passenger in passengers:
            try:
                response = self._get_response(passenger, timespan_id)
            except UnsuccessfulRequestException as ure:
                LOGGER.error(ure)
                return None

            bus_data = parse_bus_data(response)

            if bus_data is not None:
                if coordinates.get(bus_data["bus_number"]) is None:
                    coordinates[bus_data["bus_number"]] = bus_data["coordinates"]
                else:
                    continue

        return coordinates
