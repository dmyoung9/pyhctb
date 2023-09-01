"""Type definitions for the API"""

from typing import Dict, Optional

Schedule = Dict[str, Dict[str, Optional[str]]]
AllSchedules = Dict[str, Schedule]

Coordinates = Dict[str, Optional[float]]
AllCoordinates = Dict[str, Coordinates]
