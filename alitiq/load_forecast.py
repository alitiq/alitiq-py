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
    FORECASTING_MODELS_TO_ALITIQ_MODEL_NAMING,
    ForecastModels,
)
from alitiq.enumerations.services import Services
from alitiq.models.load_forecast import EngineMeasurementForm


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
        super().__init__(Services.DEMAND_FORECAST, api_key)

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
                    "measurement/inspect",
                    params={
                        "id_location": location_id,
                        "response_format": "json",
                        "start_date": start_date.strftime("%Y-%m-%dT%H:%M:%S"),
                        "end_date": end_date.strftime("%Y-%m-%dT%H:%M:%S"),
                    },
                )
            ),
            orient="split",
        )

    def post_measurements(
        self, measurements: Union[EngineMeasurementForm, List[EngineMeasurementForm]]
    ) -> str:
        """
        Push new Engine measurements to the API.

        Args:
            measurements (Union[EngineMeasurementForm, List[EngineMeasurementForm]]):
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

        return self._request("POST", "measurement/add", data=json.dumps(validated_data))

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
        if forecast_model is None:
            forecast_model = ForecastModels.ICON_EU
        else:
            forecast_model = ForecastModels(forecast_model)

        return pd.read_json(
            StringIO(
                self._request(
                    "GET",
                    "forecast",
                    params={
                        "id_location": location_id,
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
