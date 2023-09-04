"""Type definitions for the API"""

from typing import Dict, Literal, Optional, Union

BusStopKey = Literal["bus_stop", "school_stop"]
CoordinateKey = Literal["latitude", "longitude"]
PassengerInfoKey = Literal["legacyID", "name"]
ScheduleKey = Literal["actual", "schedule"]
StopDataKeys = Literal["type", "name", "schedule", "coordinates"]
TimeSpanKey = Literal["AM", "MID", "PM"]

PassengerInfo = Dict[PassengerInfoKey, str]
Coordinates = Dict[CoordinateKey, Optional[float]]
Schedule = Dict[ScheduleKey, Optional[int]]
StopData = Dict[StopDataKeys, Union[Optional[str], Schedule, Coordinates]]
