"""
pydantic models to pass relevant data to SDK functions

author: Daniel Lassahn, CTO, alitiq GmbH
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, validator


class LoadMeasurementForm(BaseModel):
    """
    Represents the data structure for load/demand measurements.

    Attributes:
        id_location (str): Unique identifier for the location.
        dt (str): Timestamp of the measurement.
        power (float): Measured power in the specified unit.
        power_measure (str): Unit of power measurement (e.g., 'kW', 'MW').
        timezone (str): Timezone of the measurement. Defaults to 'UTC'.
        interval_in_minutes (int): Interval duration in minutes. Required when `window_boundary` is not 'end'.
        window_boundary (str): Boundary type for interval-based measurements. Options: 'begin', 'center', 'end'.
    """

    id_location: str = Field(..., description="Unique identifier for the location")
    dt: str = Field(
        ...,
        description="Timestamp of the measurement in the form: 2019-01-09T22:15:00.000 or in ISO 8601 format",
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


class LoadLocationForm(BaseModel):
    """
    Pydantic model for creating a new load forecasting location.
    Matches the API schema for /load/location/add/
    """

    site_name: str = Field(..., description="Display name of the location")
    location_id: Optional[str] = Field(
        None,
        description="Optional external location ID. If omitted, the API assigns one automatically.",
    )
    latitude: float = Field(
        ..., ge=-90.0, le=90.0, description="Latitude in decimal degrees"
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0, description="Longitude in decimal degrees"
    )
    service: str = Field(
        default="electricity-load",
        description="Service type (electricity-load, district-heating, gas_load, etc.)",
    )

    @field_validator("site_name")
    @classmethod
    def validate_site_name(cls, v: str) -> str:
        """validate site name not empty"""
        if not v.strip():
            raise ValueError("site_name cannot be empty")
        return v
