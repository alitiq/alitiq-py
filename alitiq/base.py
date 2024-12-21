"""
A base module for interacting with alitiq's REST APIs.

This module defines the `alitiqAPIBase` abstract base class, which provides the foundational methods
for API interaction and serves as a blueprint for specific service integrations.

author: Daniel Lassahn, CTO, alitiq GmbH
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, Union

import pandas as pd
import requests

from alitiq.enumerations.forecast_models import ForecastModels
from alitiq.enumerations.services import Services


class alitiqAPIBase(ABC):
    """
    A base class for interacting with alitiq's REST APIs.

    This class serves as a foundation for subclasses that interact with specific services provided by alitiq.
    It handles API authentication, request execution, and error handling.

    Attributes:
        base_url_mapping (dict): A mapping of service names to their respective base URLs.
        service (Services): The service being accessed.
        base_url (str): The base URL for the service.
        api_key (str): API key for authentication.
        session (requests.Session): A persistent HTTP session with pre-configured headers.
    """

    base_url_mapping = {
        # Services.WEATHER: "https://api.alitiq.com",
        Services.SOLAR_POWER_FORECAST: "https://solar.alitiq.com",
        Services.DEMAND_FORECAST: "https://engine.alitiq.com",
    }

    def __init__(self, service: Union[str, Services], api_key: str):
        """
        Initialize the alitiqAPIBase instance.

        Args:
            service (Union[str, Services]): The name or enum of the service being accessed.
            api_key (str): API key for authenticating API requests.
        """
        self.service = Services(service)
        self.base_url = self.base_url_mapping[service]
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"x-api-key": self.api_key})
        logging.basicConfig(level=logging.INFO)

    def _request(self, method: str, endpoint: str, **kwargs) -> str:
        """
        Execute an HTTP request and handle common error scenarios.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            endpoint (str): The API endpoint path (relative to the base URL).
            **kwargs: Additional parameters passed to the `requests.Session.request` method.

        Returns:
            str: The response text from the API.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request returns a client or server error.
            Exception: For any other unexpected errors during the request.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, verify=True, **kwargs)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise

    @abstractmethod
    def get_measurements(
        self,
        location_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """
        Fetch measurement data for a specific location.

        Args:
            location_id (str): The ID of the location for which measurements are fetched.
            start_date (Optional[datetime]): The start date for the data range. Defaults to None.
            end_date (Optional[datetime]): The end date for the data range. Defaults to None.

        Returns:
            pd.DataFrame: A dataframe containing the measurement data.
        """
        pass

    @abstractmethod
    def post_measurements(
        self,
        measurement: Any,
    ) -> pd.DataFrame:
        """
        Push measurements (Engine or PV power) to the API.

        Args:
            measurements  Any:

        Returns:
            str: The response from the API as a string.
            Typically contains status, message, and any additional response data.

        Raises:
            ValueError: If the provided measurement data fails validation.
            requests.HTTPError: If the HTTP request to the API encounters an error.
        """
        pass

    @abstractmethod
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
        Retrieve the forecast for a specific location.

        Args:
            location_id (str): The ID of the location.
            forecast_model (Optional[Union[str, ForecastModels]]): The forecast model to use. Defaults to optimized
                model.
            dt_calc (Optional[datetime]): Calculation datetime for the forecast. Defaults to None.
            power_measure (str): The unit of power measurement (e.g., 'kW'). Defaults to 'kW'.
            timezone (str): The timezone for the forecast data. Defaults to 'UTC'.
            interval_in_minutes (int): Forecast interval in minutes. Defaults to 15.
            window_boundary (str): Window boundary for forecast data. Defaults to 'end'.

        Returns:
            pd.DataFrame: A dataframe containing the forecast data.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def list_locations(self) -> pd.DataFrame:
        """
        Fetch the list of all available locations (Solar and Wind).

        Returns:
            pd.DataFrame: A dataframe containing details of all locations.
        """
        pass

    @abstractmethod
    def create_location(self, location_data: Any) -> str:
        """
        Create a new location (Solar or Wind).

        Args:
            location_data (Any): The data for the new location.

        Returns:
            str: The response from the API.
        """
        pass

    @abstractmethod
    def delete_location(self, location_id: str) -> str:
        """
        Delete a location by its ID. Only valid for Wind and SolarPV services.

        Args:
            location_id (str): The ID of the location to delete.

        Returns:
            str: The response from the API.
        """
        pass
