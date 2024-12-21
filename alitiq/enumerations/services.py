""" enumeration class for alitiq Services """

from enum import Enum


class Services(Enum):
    """alitiq forecasting API's"""

    DEMAND_FORECAST = "demand"
    # WIND_POWER_FORECAST = "wind"  t.b.a
    SOLAR_POWER_FORECAST = "solar"
    # WEATHER = "weather" t.b.a.
