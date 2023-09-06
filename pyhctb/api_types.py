"""Type definitions for the API"""

from typing import Dict, Literal, Optional, Union

BusStopKey = Literal["bus_stop", "school_stop"]
BusDataKey = Literal["bus_number", "stops", "coordinates"]
CoordinateKey = Literal["latitude", "longitude"]
PassengerInfoKey = Literal["legacyID", "name"]
ScheduleKey = Literal["actual", "scheduled"]
StopDataKeys = Literal["type", "name", "timespan", "schedule", "coordinates"]
TimeSpanKey = Literal["AM", "MID", "PM"]

PassengerInfo = Dict[PassengerInfoKey, str]
Coordinates = Dict[CoordinateKey, Optional[float]]
Schedule = Dict[ScheduleKey, Optional[int]]
StopData = Dict[StopDataKeys, Union[Optional[str], Schedule, Coordinates]]

BusData = Dict[BusDataKey, Union[str, StopData, Coordinates]]
BusCoordinates = Dict[str, Coordinates]
