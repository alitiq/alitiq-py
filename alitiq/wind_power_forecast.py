"""
alitiq's Wind Power Forecast Service SDK.

This SDK provides tools for managing and interacting with alitiq's Windpower Forecast API.

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
    FORECASTING_MODELS_TO_ALITIQ_MODEL_NAMING,
    ForecastModels,
)
from alitiq.enumerations.services import Services
from alitiq.models.wind_power_forecast import (
    CurtailmentForm,
    WindParkModel,
    WindPowerMeasurementForm,
)


class alitiqWindAPI(alitiqAPIBase):
    """
    Subclass to interact with the alitiq WindPower Forecast API.

    This class provides methods for managing Windparks (aka locations), retrieving measurements, and obtaining
    forecasts for individual locations or entire portfolios.

    Attributes:
        api_key (str): The API key used for authentication.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize the alitiqWindAPI instance.

        Args:
            api_key (str): API key for authentication.
        """
        super().__init__(Services.WIND_POWER_FORECAST, api_key)

    def create_location(
        self, locations: Union[WindParkModel, List[WindParkModel]]
    ) -> str:
        """
        Create a new location (windpark) by sending the data to the API.

        Args:
            locations (Union[WindParkModel, List[WindParkModel]]):
                A single WindParkModel instance or a list of such instances.

        Returns:
            Dict[str, Any]: API response.

        Raises:
            ValidationError: If the provided data is invalid.
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
            response = self._request(
                "POST", "wind_parks/add/", data=json.dumps(location)
            )
        return response

    def delete_location(self, location_id: str) -> str:
        """
        Delete a solar power plant location by its ID.

        Args:
            location_id (str): The ID of the location to delete.

        Returns:
            Dict[str, Any]: API response.
        """
        return self._request(
            "POST", "wind_parks/delete/", params={"location_id": location_id}
        )

    def get_measurements(
        self,
        location_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch wind power measurement data for a specific system.

        Args:
            location_id (str): The ID of the location/windpark.
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
        self,
        measurements: Union[WindPowerMeasurementForm, List[WindPowerMeasurementForm]],
    ) -> str:
        """
        Push new Wind power measurements to the API.

        Args:
            measurements (Union[WindPowerMeasurementForm, List[WindPowerMeasurementForm]]):
                A single WindPowerMeasurementForm instance or a list of such instances.

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

        self._check_for_duplicate_entries(validated_data)

        return self._request(
            "POST", "measurement/add/", data=json.dumps(validated_data)
        )

    def inspect_curtailments(
        self,
        location_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Retrieve curtailment records for a given wind park location.

        Args:
            location_id (str): The external location ID to query.
            start_date (Optional[datetime]): Start date for the time range (default: 2 days ago).
            end_date (Optional[datetime]): End date for the time range (default: now).

        Returns:
            pd.DataFrame: DataFrame containing curtailment records.
        """
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=2)

        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "curtailments/inspect/",
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

    def post_curtailments(
        self,
        curtailments: Union[CurtailmentForm, List[CurtailmentForm]],
    ) -> str:
        """
        Push curtailment records to the alitiq WindPower API.

        Args:
            curtailments (Union[CurtailmentForm, List[CurtailmentForm]]):
                A single CurtailmentForm or a list of such forms representing curtailment events.

        Returns:
            str: API response message from the server.

        Raises:
            ValidationError: If the provided data is invalid.
            requests.HTTPError: If the API request fails.
        """
        if not isinstance(curtailments, list):
            curtailments = [curtailments]

        try:
            validated_data = [
                curtailment.dict(exclude_unset=True) for curtailment in curtailments
            ]
        except ValidationError as e:
            raise ValueError(f"Validation failed for input data: {e}")

        self._check_for_duplicate_entries(validated_data)

        return self._request(
            "POST", "curtailments/add/", data=json.dumps(validated_data)
        )

    def list_locations(self) -> pd.DataFrame:
        """
        List all WindParks (locations) associated with the account.

        Returns:
            pd.DataFrame: Dataframe containing location details.
        """
        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "wind_parks/list/",
                    params={
                        "response_format": "json",
                    },
                )
            ),
            orient="split",
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
        Retrieve the power forecast for a specific WindPark.

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
        if forecast_model is None:
            forecast_model = ForecastModels.OPTIMIZED
        else:
            forecast_model = ForecastModels(forecast_model)

        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "forecast/single/",
                    params={
                        "location_id": location_id,
                        "response_format": "json",
                        "weather_model": FORECASTING_MODELS_TO_ALITIQ_MODEL_NAMING[
                            forecast_model
                        ],
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
        Retrieve the power forecast for all locations in the portfolio.

        Args:
            forecast_model (Optional[Union[str, ForecastModels]]): The forecast model to use (default: optimized model).
            dt_calc (Optional[datetime]): Calculation datetime (default: None).
            power_measure (str): Unit of power measurement (default: kW).
            timezone (str): Timezone for the forecast data (default: UTC).
            interval_in_minutes (int): Forecast interval in minutes (default: 15).
            window_boundary (str): Window boundary for forecast data (default: "end").
            portfolio_sum_column (bool): Whether to include a column summing the portfolio power (default: True).

        Returns:
            pd.DataFrame: Dataframe containing the portfolio forecast data.
        """
        if forecast_model is None:
            forecast_model = ForecastModels.OPTIMIZED
        else:
            forecast_model = ForecastModels(forecast_model)

        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "forecast/portfolio/",
                    params={
                        "response_format": "json",
                        "weather_model": FORECASTING_MODELS_TO_ALITIQ_MODEL_NAMING[
                            forecast_model
                        ],
                        "power_measure": power_measure,
                        "timezone": timezone,
                        "interval_in_minutes": interval_in_minutes,
                        "window_boundary": window_boundary,
                        "dt_calc": (
                            dt_calc.strftime("%Y-%m-%dT%H:%M:%S") if dt_calc else None
                        ),
                        "portfolio_sum_column": portfolio_sum_column,
                    },
                )
            ),
            orient="split",
        )
