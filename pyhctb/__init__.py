BASE_URL = "https://login.herecomesthebus.com"
AUTH_URL = f"{BASE_URL}/Authenticate.aspx"
MAP_URL = f"{BASE_URL}/Map.aspx"
REFRESH_URL = f"{MAP_URL}/RefreshMap"

BUS_PUSHPIN_REGEX = r"SetBusPushPin\(([-+]?\d*\.?\d+),\s*([-+]?\d*\.?\d+)"

ELEMENTS = {
    "user": "ctl00$ctl00$cphWrapper$cphContent$tbxUserName",
    "password": "ctl00$ctl00$cphWrapper$cphContent$tbxPassword",
    "code": "ctl00$ctl00$cphWrapper$cphContent$tbxAccountNumber",
    "auth_button": "ctl00$ctl00$cphWrapper$cphContent$btnAuthenticate",
}
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
    "Content-Type": "application/json; charset=UTF-8",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Referer": MAP_URL,
    "Sec-Ch-Ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest",
}
