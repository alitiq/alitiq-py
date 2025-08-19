
<p align="center">
  <a href="https://www.alitiq.com"><img src="https://alitiq.com/wp-content/uploads/2022/08/Logo-1.png" alt="alitiq Forecasting Energy"></a>
</p>
<p align="center">
    <em>alitiq-py , high performance, easy to use, ready for production python software development kit </em>
</p>
<p align="center">
<a href="" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/fastapi.svg?color=%2334D058" alt="Supported Python versions">
</a>
<a href="https://docs.alitiq.com">
    <img src="https://img.shields.io/badge/Documentation-here-blue">
</a>
</p>

## Overview 🛠️
Welcome to **alitiq's Forecasting Service SDK**, a robust Python-based SDK that simplifies interaction with alitiq’s Solar, Wind and Load Forecast APIs. This SDK enables seamless data retrieval, measurements management, and forecasting for solar power plants, energy demand, and more. Built with flexibility and scalability in mind, it supports a range of features such as pushing measurements, retrieving forecasts, and managing locations.

Before you start using the SDK, you need to obtain an API key. For the engine / load API you will receive your key and relevant information from the alitiq Team. To obtain a key for the solar power forecasting API register here: [Solar-APP](https://solar-app.alitiq.com)

This is a work in progress. We will shortly add an extensive documentation with step by step guides to use our API with python. 

---

## Features ✨  
- **Solar Power Plant Management**:  
  Manage PV system configurations and retrieve forecasts for your solar power installations. 
- **WindPark Management**:  
  Manage WindPark configurations and retrieve forecasts for your portfolio. 
- **Load Forecasting** by alitiq Engine:  
  Fetch and manage energy load forecasts for heat, gas, and electricity demand.  
- **Pushing and Retrieving Measurements**:  
  Push new measurement data to the API and inspect historical measurement data.  
- **Robust Validation**:  
  Powered by Pydantic, ensuring data integrity for all API interactions.  

---

## Installation 📦  
With pip: 
```bash
pip install alitiq
```

Or check out locally:
1. Clone the repository:  
   ```bash
   git clone https://github.com/alitiq/alitiq-py.git
   cd alitiq-py
   ```
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Install the SDK locally:  
   ```bash
   pip install .
   ```


---

## Quickstart 🚀  
Example shows how to add a new Solar PV power plant, retrieve most recent forecast and push measurements for a given location. 
```python
from datetime import datetime
from alitiq import alitiqSolarAPI, SolarPowerPlantModel, PvMeasurementForm

# Initialize the API client
solar_api = alitiqSolarAPI(api_key="your-api-key")

# Create a solar power plant location
plant = SolarPowerPlantModel(
    site_name="My Solar Plant",
    location_id="SP123",
    latitude=48.160170,
    longitude=10.55907,
    installed_power=500.0,
    installed_power_inverter=480.0,
    azimuth=180.0,
    tilt=25.0,
)

response = solar_api.create_location(plant)
print("Location created:", response)

# Retrieve a forecast ( after 1-6 hours after creation available)
forecast = solar_api.get_forecast(location_id="SP123")
print(forecast)

# Post measurements 
pv_measurements = [
    PvMeasurementForm(
        location_id="SP123",
        dt=datetime(2024, 6, 10, 10).isoformat(),
        power=120.5,
        power_measure="kW",
        timezone="UTC",
        interval_in_minutes=15,
    ),
    PvMeasurementForm(
        location_id="SP123",
        dt=datetime(2024, 6, 10, 10, 15).isoformat(),
        power=90.8,
        power_measure="kW",
        timezone="UTC",
        interval_in_minutes=15,
    ),
    PvMeasurementForm(
        location_id="SP123",
        dt=datetime(2024, 6, 10, 10, 30).isoformat(),
        power=150.0,
        power_measure="kW",
        timezone="UTC",
        interval_in_minutes=15,
    ),
]

response = solar_api.post_measurements(pv_measurements)
print(response)

```

### Setup a load location


```python
from alitiq.models.load_forecast import LoadLocationForm

# Example
api = alitiqLoadAPI(api_key="your-key")

location = LoadLocationForm(
    site_name="HQ Campus",
    location_id="HQ-001",
    latitude=52.52,
    longitude=13.405,
    service=Services.ELECTRICITY_LOAD,
)

resp = api.create_location(location)
print(resp)


```
Please go to our docs for detailed information [alitiq-Docs](https://docs.alitiq.com)

---

## Project Structure 🏗️  

```plaintext
alitiq/
│── enumerations/
│   │── __init__.py
│   │── forecast_models.py
│   │── services.py
│
│── models/
│   │── __init__.py
│   │── load_forecast.py
│   │── solar_power_forecast.py
│   │── wind_power_forecast.py
│
│── __init__.py
│── base.py
│── load_forecast.py
│── solar_power_forecast.py
│── wind_power_forecast.py

```

---

## Key Modules 📚  

### Solar Forecasting Module (`solar_power_forecast.py`)  
Manage PV systems and retrieve solar power forecasts. Key methods:  
- `create_location`: Add new PV system configurations.
- `list_locations`: List current portfolio
- `delete_location`: Deletes one location from portfolio
- `get_forecast`: Retrieve solar power forecasts for a specific location.  
- `get_forecast_portfolio`: Retrieve solar power forecasts for the whole portfolio.  
- `push_measurements`: Submit real-time measurements for your solar plant.  
- `get_measurements`: Retrieve historical data for a location.  

### Wind Forecasting Module (`wind_power_forecast.py`)  
Manage WindParks and retrieve wind power forecasts. Key methods:  
- `create_location`: Add new WindPark configurations.
- `list_locations`: List current portfolio
- `delete_location`: Deletes one location from portfolio
- `get_forecast`: Retrieve wind power forecasts for a specific location.  
- `get_forecast_portfolio`: Retrieve wind power forecasts for the whole portfolio.  
- `push_measurements`: Submit real-time measurements for your WindPark.  
- `get_measurements`: Retrieve historical data for a location.  

### Load Forecasting Module (`load_forecast.py`)  
Interact with alitiq's load forecast API for heat, gas, and electricity. Key methods:  
- `get_measurements`: Retrieve historical data for a location.  
- `post_measurements`: Push new measurement data.  
- `get_forecast`: Fetch load forecasts for your configured location.  

---

## Contributing 🤝  
We welcome contributions! To contribute:  
1. Fork the repository.  
2. Create a new branch:  
   ```bash
   git checkout -b feature/new-feature
   ```
3. Commit your changes:  
   ```bash
   git commit -m "Add a new feature"
   ```
4. Push to your branch and submit a pull request.  

---

## License 📜  

MIT License, see attached LICENSE

---

## Developer Notes

Run `python3 -m build` to build the package and then upload with twine: `twine upload -r pypi dist/*`  

---

## Support & Contact 📧  
For any questions or issues, please contact [support@alitiq.com](mailto:support@alitiq.com).  

🌟 **Happy Forecasting!** 🌟