"""Type definitions for the API"""

from typing import Dict, List, Optional, Tuple

Schedule = Dict[str, Dict[str, Optional[str]]]
AllSchedules = Dict[str, Schedule]
ScheduleData = List[Tuple[str, str]]

Coordinates = Dict[str, Optional[float]]
AllCoordinates = Dict[str, Coordinates]
CoordinateData = List[Tuple[str, str]]

PassengerInfo = Dict[str, str]
