"""enumeration class for alitiq Services"""

from enum import Enum


class Services(Enum):
    """alitiq forecasting API's"""

    LOAD_FORECAST = "load"
    WIND_POWER_FORECAST = "wind"
    SOLAR_POWER_FORECAST = "solar"
    # WEATHER = "weather" t.b.a.
