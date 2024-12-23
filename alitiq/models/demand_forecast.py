"""
pydantic models to pass relevant data to SDK functions

author: Daniel Lassahn, CTO, alitiq GmbH
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field, validator


class EngineMeasurementForm(BaseModel):
    """
    Represents the data structure for engine/demand measurements.

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
