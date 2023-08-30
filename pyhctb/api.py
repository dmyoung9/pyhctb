import re
from typing import Optional, Tuple, Union

import requests

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.options import ArgOptions

from . import AUTH_URL, BUS_PUSHPIN_REGEX, ELEMENTS, HEADERS, REFRESH_URL
from .exceptions import InvalidAuthorizationException, PassengerDataException


def _build_browser_options() -> ArgOptions:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-logging")
    options.add_argument("--log-level=3")

    return options


def _build_webdriver(options: ArgOptions) -> WebDriver:
    return webdriver.Chrome(options=options)


class HctbApi:
    def __init__(self, username: str, password: str, code: str):
        self.username = username
        self.password = password
        self.code = code

        self.browser_options = _build_browser_options()
        self.headers = HEADERS

    def _perform_login(self, driver: WebDriver):
        driver.get(AUTH_URL)

        driver.find_element(By.NAME, ELEMENTS["user"]).send_keys(self.username)
        driver.find_element(By.NAME, ELEMENTS["password"]).send_keys(self.password)
        driver.find_element(By.NAME, ELEMENTS["code"]).send_keys(self.code)

        driver.find_element(By.NAME, ELEMENTS["auth_button"]).click()
        driver.implicitly_wait(10)

        return {cookie["name"]: str(cookie["value"]) for cookie in driver.get_cookies()}

    def _update_headers_with_cookies(self, cookies: dict[str, str]) -> None:
        cookie_str = "; ".join([f"{name}={value}" for name, value in cookies.items()])
        self.headers["cookie"] = cookie_str

    def _get_passenger_data(self, driver: WebDriver) -> Optional[dict]:
        selected_options = driver.find_elements(
            By.CSS_SELECTOR, 'option[selected="selected"]'
        )

        if len(selected_options) >= 3:
            name = selected_options[1].get_attribute("innerHTML")
            person = selected_options[1].get_attribute("value")
            time = selected_options[2].get_attribute("value")

            return {
                "legacyID": person,
                "name": name,
                "timeSpanId": time,
                "wait": "false",
            }

        return None

    @staticmethod
    def _parse_coordinates(
        response_data: str,
    ) -> Union[Tuple[str, str], Tuple[None, None]]:
        if "SetBusPushPin" in response_data:
            return re.findall(BUS_PUSHPIN_REGEX, response_data)[0]
        return None, None

    def _get_api_response(self, passenger_data) -> dict:
        response = requests.post(REFRESH_URL, headers=self.headers, json=passenger_data)

        passenger_data.pop("wait", None)

        if response.ok:
            response_json = response.json()
            latitude, longitude = HctbApi._parse_coordinates(response_json["d"])

            return passenger_data | {
                "latitude": latitude,
                "longitude": longitude,
            }

        return {
            "success": False,
            "error": f"Request unsuccessful: {response.status_code}",
        }

    def authenticate(self, driver: Optional[WebDriver] = None):
        if driver is not None:
            cookies = self._perform_login(driver)
        else:
            with _build_webdriver(options=self.browser_options) as driver:
                cookies = self._perform_login(driver)

        if ".ASPXFORMSAUTH" not in cookies:
            raise InvalidAuthorizationException()

        return cookies

    def get_bus_data(self) -> dict:
        with _build_webdriver(options=self.browser_options) as driver:
            cookies = self.authenticate(driver)
            if cookies is None:
                raise InvalidAuthorizationException()

            self._update_headers_with_cookies(cookies)

            passenger_data = self._get_passenger_data(driver)
            if passenger_data is None:
                raise PassengerDataException()

        return self._get_api_response(passenger_data)
