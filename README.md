
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
</p>

## Overview 🛠️  (WIP)
Welcome to **alitiq's Forecasting Service SDK**, a robust Python-based SDK that simplifies interaction with alitiq’s Solar, and Engine (Demand) Forecast APIs. This SDK enables seamless data retrieval, measurements management, and forecasting for solar power plants, energy demand, and more. Built with flexibility and scalability in mind, it supports a range of features such as pushing measurements, retrieving forecasts, and managing locations.

Before you start using the SDK, you need to obtain an API key. For the engine / demand API you will receive your key and relevant information from the alitiq Team. To obtain a key for the solar power forecasting API register here: [Solar-APP](https://solar-app.alitiq.com)

This is a work in progress. We will shortly add an extensive documentation with step by step guides to use our API with python. 

---

## Features ✨  
- **Solar Power Plant Management**:  
  Manage PV system configurations and retrieve forecasts for your solar power installations.  
- **Demand Forecasting** by alitiq Engine:  
  Fetch and manage energy demand forecasts for heat, gas, and electricity demand.  
- **Pushing and Retrieving Measurements**:  
  Push new measurement data to the API and inspect historical measurement data.  
- **Robust Validation**:  
  Powered by Pydantic, ensuring data integrity for all API interactions.  

---

## Installation 📦  

1. Clone the repository:  
   ```bash
   git clone https://github.com/alitiq/alitiq-py.git
   cd alitiq-sdk
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
Example shows how to add a new Solar PV power plant
```python
from alitiq import alitiqSolarAPI, SolarPowerPlantModel

# Initialize the API client
solar_api = alitiqSolarAPI(api_key="your-api-key")

# Create a solar power plant location
plant = SolarPowerPlantModel(
    site_name="My Solar Plant",
    location_id="SP123",
    latitude=40.7128,
    longitude=-74.0060,
    installed_power=500.0,
    installed_power_inverter=480.0,
    azimuth=180.0,
    tilt=25.0,
    temp_factor=0.95,
    do_backtracking=True,
)

response = solar_api.create_location(plant)
print("Location created:", response)

# Retrieve a forecast
forecast = solar_api.get_forecast(location_id="SP123")
print(forecast)
```
Please note this docs for setting up your PV system locations: [How to setup PV systems at alitiq](https://makandracards.com/alitiq/621166-setup-pv-system-solar-power-forecast-alitiq/read)

---

## Project Structure 🏗️  

```plaintext
forecasting-sdk/
├── alitiq/
│   ├── base.py              # Base class for interacting with APIs
│   ├── solar_api.py         # Solar forecasting service SDK
│   ├── demand_api.py        # Demand forecasting service SDK
│   └── enumerations/        # Enumerations for services and forecasting models
├── models/
│   ├── solar.py             # Pydantic models for solar APIs
│   └── demand_forecast.py   # Pydantic models for demand APIs
├── tests/                   # Unit tests for the SDK
└── README.md                # Project documentation
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

### Demand Forecasting Module (`demand_forecast.py`)  
Interact with alitiq's demand forecast API for heat, gas, and electricity. Key methods:  
- `get_measurements`: Retrieve historical data for a location.  
- `post_measurements`: Push new measurement data.  
- `get_forecast`: Fetch demand forecasts for your configured location.  

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
t.b.d.
---

## Support & Contact 📧  
For any questions or issues, please contact [support@alitiq.com](mailto:support@alitiq.com).  

🌟 **Happy Forecasting!** 🌟