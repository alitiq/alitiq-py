"""
alitiq's engine based Demand forecasting Service SDK.

This SDK provides tools for managing and interacting with alitiq's Engine API.

author: Daniel Lassahn, CTO, alitiq GmbH
"""

import json
from datetime import datetime, timedelta
from io import StringIO
from typing import List, Optional, Union

import pandas as pd
from pydantic import ValidationError

from alitiq.base import alitiqAPIBase
from alitiq.enumerations.forecast_models import (
    ForecastModels,
)
from alitiq.enumerations.services import Services
from alitiq.models.load_forecast import LoadLocationForm, LoadMeasurementForm


class alitiqLoadAPI(alitiqAPIBase):
    """
    Subclass to interact with the alitiq Engine Forecast API.

    This class provides methods for managing retrieving measurements, and obtaining
    forecasts for individual locations

    Attributes:
        api_key (str): The API key used for authentication.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the alitiqDemandAPI instance.

        Args:
            api_key (str): API key for authentication.
        """
        super().__init__(Services.LOAD_FORECAST, api_key)

    def get_measurements(
        self,
        location_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch solar measurement data for a specific system.

        Args:
            location_id (str): The ID of the location.
            start_date (Optional[datetime]): Start date for the data range (default: 2 days before today).
            end_date (Optional[datetime]): End date for the data range (default: today).

        Returns:
            pd.DataFrame: Dataframe containing the measurement data.
        """
        if end_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=2)

        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "measurement/inspect/",
                    params={
                        "location_id": location_id,
                        "response_format": "json",
                        "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "end_date": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    },
                )
            ),
            orient="split",
        )

    def post_measurements(
        self, measurements: Union[LoadMeasurementForm, List[LoadMeasurementForm]]
    ) -> str:
        """
        Push new Engine measurements to the API.

        Args:
            measurements (Union[LoadMeasurementForm, List[EngineMeasurementForm]]):
                A single EngineMeasurementForm instance or a list of such instances.

        Returns:
            Dict[str, Any]: The API response.

        Raises:
            ValidationError: If the provided data is invalid.
            requests.HTTPError: If the API request fails.
        """
        if not isinstance(measurements, list):
            measurements = [measurements]

        try:
            validated_data = [
                measurement.dict(exclude_unset=True) for measurement in measurements
            ]
        except ValidationError as e:
            raise ValueError(f"Validation failed for input data: {e}")

        return self._request(
            "POST", "measurement/add/", data=json.dumps(validated_data)
        )

    def get_forecast(
        self,
        location_id: str,
        forecast_model: Optional[Union[str, ForecastModels]] = None,
        dt_calc: Optional[datetime] = None,
        power_measure: str = "kW",
        timezone: str = "UTC",
        interval_in_minutes: int = 15,
        window_boundary: str = "end",
    ) -> pd.DataFrame:
        """
        Retrieve the power forecast for a specific Engine location. That could be a heat, gas  or electricity
        demand forecast.

        Args:
            location_id (str): The ID of the location.
            forecast_model (Optional[Union[str, ForecastModels]]): The forecast model to use (default: optimized model).
            dt_calc (Optional[datetime]): Calculation datetime (default: None).
            power_measure (str): Unit of power measurement (default: kW).
            timezone (str): Timezone for the forecast data (default: UTC).
            interval_in_minutes (int): Forecast interval in minutes (default: 15).
            window_boundary (str): Window boundary for forecast data (default: "end").

        Returns:
            pd.DataFrame: Dataframe containing the forecast data.
        """
        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "forecast/",
                    params={
                        "location_id": location_id,
                        "response_format": "json",
                        "power_measure": power_measure,
                        "timezone": timezone,
                        "interval_in_minutes": interval_in_minutes,
                        "window_boundary": window_boundary,
                        "dt_calc": (
                            dt_calc.strftime("%Y-%m-%dT%H:%M:%S") if dt_calc else None
                        ),
                    },
                )
            ),
            orient="split",
        )

    def get_forecast_portfolio(
        self,
        forecast_model: Optional[Union[str, ForecastModels]] = None,
        dt_calc: Optional[datetime] = None,
        power_measure: str = "kW",
        timezone: str = "UTC",
        interval_in_minutes: int = 15,
        window_boundary: str = "end",
        portfolio_sum_column: bool = True,
    ) -> pd.DataFrame:
        """
        Retrieve the forecast for all locations in the portfolio.

        Args:
            forecast_model (Optional[Union[str, ForecastModels]]): The forecast model to use. Defaults to optimized
                model.
            dt_calc (Optional[datetime]): Calculation datetime for the forecast. Defaults to None.
            power_measure (str): The unit of power measurement (e.g., 'kW'). Defaults to 'kW'.
            timezone (str): The timezone for the forecast data. Defaults to 'UTC'.
            interval_in_minutes (int): Forecast interval in minutes. Defaults to 15.
            window_boundary (str): Window boundary for forecast data. Defaults to 'end'.
            portfolio_sum_column (bool): Whether to include a portfolio summary column. Defaults to True.

        Returns:
            pd.DataFrame: A dataframe containing the portfolio forecast data.
        """
        raise NotImplementedError

    def list_locations(self) -> pd.DataFrame:
        """
        Fetch the list of all available locations (Solar and Wind).

        Returns:
            pd.DataFrame: A dataframe containing details of all locations.
        """
        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "load/location/list/",
                    params={"response_format": "json"},
                )
            ),
            orient="split",
        )

    def create_location(
        self, locations: Union[LoadLocationForm, List[LoadLocationForm]]
    ) -> str:
        """
        Create a new load location .

        Args:
            location_data (Any): The data for the new location.

        Returns:
            str: The response from the API.
        """
        if not isinstance(locations, list):
            locations = [locations]
        try:
            validated_data = [
                location.dict(exclude_unset=True) for location in locations
            ]
        except ValidationError as e:
            raise ValueError(f"Validation failed for input data: {e}")
        response = None
        for location in validated_data:
            response = self._request("POST", "location/add", data=json.dumps(location))
        return response

    def delete_location(self, location_id: str) -> str:
        """
        Delete a location by its ID. Only valid for Wind and SolarPV services.

        Args:
            location_id (str): The ID of the location to delete.

        Returns:
            str: The response from the API.
        """
        raise NotImplementedError
