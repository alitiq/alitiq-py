"""
pydantic models to pass relevant data to SDK functions

author: Daniel Lassahn, CTO, alitiq GmbH
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class PvMeasurementForm(BaseModel):
    """
    Represents the data structure for posting photovoltaic (PV) measurements.

    Attributes:
        location_id (str): Unique identifier for the location.
        dt (str): Timestamp of the measurement.
        power (float): Measured power in the specified unit.
        irradiance (float): Measured irradiance (optional, defaults to -1.0 if unknown).
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
    irradiance: float = Field(
        -1.0, description="Measured irradiance. Defaults to -1.0 if unknown."
    )
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


class SolarPowerPlantModel(BaseModel):
    """
    Represents the data structure for a solar power plant, compatible with the PvSystemsForm used in the API.

    Note:
        - A PV system consists of 1 to n subsystems.
        - The number of subsystems is defined by the unique combinations of azimuth and tilt of the power plant.
        - Provide the same `location_id` for all subsystems to group them under the same location.

    Attributes:
        site_name (str): The name of the solar power plant.
        location_id (str): The internal identifier for the location.
        latitude (float): Latitude coordinate of the site.
        longitude (float): Longitude coordinate of the site.
        installed_power (float): Total installed power in kW (must be greater than 0).
        installed_power_inverter (float): Total installed power of the inverter in kW (must be greater than 0).
        azimuth (float): Azimuth angle of the panels (0-360, where 180 is South).
        tilt (float): Tilt angle of the panels (0-90 degrees).
        temp_factor (Optional[float]): Optional temperature factor affecting system performance.
        mover (Optional[int]): Type of tracking system (e.g., 0 for fixed, 1 for single-axis tracking).
        max_rotation_angle (Optional[float]): Maximum rotation angle for tracking systems.
        row_distance (Optional[float]): Distance between rows in meters.
        do_backtracking (Optional[bool]): Whether the system uses backtracking.
        table_length (Optional[float]): Length of each table in meters.
    """

    site_name: str
    location_id: str  # your internal identifier
    latitude: float
    longitude: float
    installed_power: float = Field(..., gt=0, description="Installed power in kW")
    installed_power_inverter: float = Field(
        ..., gt=0, description="Installed power of the inverter in kW"
    )
    azimuth: float = Field(
        ..., ge=0, le=360, description="Azimuth angle (180 is South)"
    )
    tilt: float = Field(..., ge=0, le=90, description="Tilt angle of the panels")
    temp_factor: Optional[float] = Field(
        default=0.0033,
        description="Temperature factor (optional). 0.0033 for free mounting, "
        "0.004 for roof mounted, 0.005 for roof integrated",
    )
    mover: Optional[int] = Field(
        default=1, description="Tracking type (e.g., 1 for fixed, 2 for single-axis)"
    )
    max_rotation_angle: Optional[float] = Field(
        None, description="Maximum rotation angle for tracking systems"
    )
    row_distance: Optional[float] = Field(
        None, description="Distance between rows in meters"
    )
    do_backtracking: Optional[bool] = Field(
        False, description="Whether the system performs backtracking"
    )
    table_length: Optional[float] = Field(
        None, description="Length of each table in meters"
    )

    class Config:
        """pydantic scheme example"""

        schema_extra = {
            "example": {
                "site_name": "Desert Solar Plant",
                "location_id": "12345",
                "latitude": 35.1234,
                "longitude": -115.1234,
                "installed_power": 5000.0,
                "installed_power_inverter": 4800.0,
                "azimuth": 180.0,
                "tilt": 25.0,
                "temp_factor": 0.95,
                "mover": 1,
                "max_rotation_angle": 45.0,
                "row_distance": 5.0,
                "do_backtracking": True,
                "table_length": 30.0,
            }
        }
