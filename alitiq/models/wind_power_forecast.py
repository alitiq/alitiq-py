"""
pydantic models to pass relevant data to SDK functions

author: Daniel Lassahn, CTO, alitiq GmbH
"""

from datetime import time
from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class WindPowerMeasurementForm(BaseModel):
    """
    Represents the data structure for posting Windpower measurements.

    Attributes:
        location_id (str): Unique identifier for the location.
        dt (str): Timestamp of the measurement.
        power (float): Measured power in the specified unit.
        power_measure (str): Unit of power measurement (e.g., 'kW', 'MW').
        timezone (str): Timezone of the measurement. Defaults to 'UTC'.
        interval_in_minutes (int): Interval duration in minutes. Required when `window_boundary` is not 'end'.
        window_boundary (str): Boundary type for interval-based measurements. Options: 'begin', 'center', 'end'.
    """

    location_id: str = Field(..., description="Unique identifier for the location")
    dt: str = Field(
        ...,
        description="Timestamp of the measurement in the form: 2019-01-09T22:15:00.000",
    )
    power: float = Field(..., description="Measured power in the specified unit")
    power_measure: Literal["W", "kW", "MW", "kWh", "Wh", "MWh"] = Field(
        "kW",
        description="Unit of power measurement. Supported: 'W', 'kW', 'MW', 'kWh', 'Wh', 'MWh'",
    )
    timezone: str = Field(
        "UTC", description="Timezone of the measurement. Defaults to 'UTC'."
    )
    interval_in_minutes: Optional[int] = Field(
        None,
        description="Interval duration in minutes. Required for 'begin' or 'center' boundaries.",
    )
    window_boundary: Literal["begin", "center", "end"] = Field(
        "end",
        description="Boundary type for interval-based measurements. Options: 'begin', 'center', 'end'.",
    )

    @validator("interval_in_minutes", always=True)
    def validate_interval(cls, value, values):
        """Validates that `interval_in_minutes` is provided when `window_boundary` is 'begin' or 'center'."""
        if values.get("window_boundary") in {"begin", "center"} and value is None:
            raise ValueError(
                "interval_in_minutes is required when window_boundary is 'begin' or 'center'."
            )
        return value


class LocationBaseSchema(BaseModel):
    """location for wind parks base schema"""

    location_id: str
    altitude: Optional[float] = None
    latitude: float
    longitude: float
    site_name: str
    zip_code: Optional[str] = None
    country: Optional[str] = None
    tso_area: Optional[str] = None
    nighttime_curtailment: Optional[bool] = None
    start_nighttime_curtailment: Optional[time] = None
    end_nighttime_curtailment: Optional[time] = None
    curtailment_level: Optional[float] = None
    time_zone_curtailment: Optional[str] = None
    mrl_power: Optional[float] = None
    eeg_key: Optional[str] = None

    class Config:
        """subclass config from attributes"""

        from_attributes = True


class WindTurbineSchema(BaseModel):
    """wind park specific base schema"""

    hub_height: float
    rotor_diameter: Optional[float] = None
    turbine_type: str
    installed_power: Optional[float] = None

    class Config:
        """subclass config from attributes"""

        from_attributes = True


class WindParkModel(LocationBaseSchema):
    """WindPark model form with all location information as well as list of wind turbines"""

    wind_turbines: Optional[list[WindTurbineSchema]] = []


class CurtailmentForm(BaseModel):
    """Form data to post curtailments to db"""

    location_id: str
    dt: str  # isoformat '2024-06-10T10:15:00'
    level: float
    timezone: str = "UTC"
    interval_in_minutes: int = 15
    window_boundary: str = "end"  # begin | center | end
