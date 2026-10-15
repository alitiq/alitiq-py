<p align="center">
  <a href="https://alitiq.com"><img src="https://alitiq.com/lovable-uploads/ccbd17e8-5cac-4432-87dc-4adff0f65e46.png" alt="alitiq – solar, wind and load forecasting"></a>
</p>

<h1 align="center">alitiq-py: Python SDK for solar PV, wind power and load forecasting</h1>

<p align="center">
  <a href="https://pypi.org/project/alitiq/"><img src="https://img.shields.io/pypi/v/alitiq.svg?color=%2334D058" alt="PyPI version"></a>
  <a href="https://pypi.org/project/alitiq/"><img src="https://img.shields.io/pypi/pyversions/alitiq.svg?color=%2334D058" alt="Supported Python versions"></a>
  <a href="https://docs.alitiq.com"><img src="https://img.shields.io/badge/docs-docs.alitiq.com-blue" alt="Documentation"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT"></a>
</p>

`alitiq` is the official Python client for the [alitiq](https://alitiq.com) forecasting API. Use it to get
**solar power forecasts (PV forecasts)**, **wind power forecasts** and **energy load forecasts**
(electricity, heat and gas demand) as pandas DataFrames. You can also push live measurements and
curtailments, manage your portfolio of PV systems and wind parks, and simulate the output of any PV
system from satellite irradiance.

The forecasts run operationally on alitiq's side and combine several numerical weather prediction
models (ICON, ICON-D2, HARMONIE, ARPEGE, GFS, …), satellite data and machine learning trained on your
measurements. You don't have to run any weather or ML infrastructure yourself: the SDK only does the
HTTP calls and validates your input with Pydantic.

```python
from alitiq import alitiqSolarAPI

solar_api = alitiqSolarAPI(api_key="your-api-key")
forecast = solar_api.get_forecast(location_id="SP123")  # pandas DataFrame, 15-minute steps
```

> **API key:** You need an alitiq API key to use the SDK. Request one at [alitiq.com/en/contact](https://alitiq.com/en/contact)
> or email [sales@alitiq.com](mailto:sales@alitiq.com).

---

## Contents

- [Features](#features)
- [Installation](#installation)
- [Solar PV power forecast](#solar-pv-power-forecast)
- [Simulate a PV system from satellite irradiance](#simulate-a-pv-system-from-satellite-irradiance)
- [Wind power forecast](#wind-power-forecast)
- [Load forecast (electricity, heat, gas)](#load-forecast-electricity-heat-gas)
- [Check when your API key expires](#check-when-your-api-key-expires)
- [API reference](#api-reference)
- [Further reading](#further-reading)
- [Contributing](#contributing)

---

## Features

| | Solar PV | Wind power | Load |
|---|:---:|:---:|:---:|
| Create, list and delete locations | ✅ | ✅ | ✅ |
| Forecast for a single location | ✅ | ✅ | ✅ |
| Forecast for the whole portfolio | ✅ | ✅ | ✅ |
| Choose the weather model (`ForecastModels`) | ✅ | ✅ | – |
| Push and read measurements | ✅ | ✅ | ✅ |
| Push and read curtailments | ✅ | ✅ | – |
| Simulate power from satellite irradiance | ✅ | – | – |

All clients also share:

- **pandas output**: forecasts and measurements come back as `pd.DataFrame`.
- **Flexible units and time handling**: `power_measure` (W, kW, MW, Wh, kWh, MWh), `timezone`,
  `interval_in_minutes` and `window_boundary` (`begin` / `center` / `end`).
- **Input validation**: Pydantic models catch invalid configurations and duplicate measurements before
  anything is sent to the API.
- **API key status**: `get_token_expiration()` tells you when your key expires.

What the forecast services cover:
[Solar PV forecast](https://alitiq.com/en/products/solar-pv) ·
[Wind power forecast](https://alitiq.com/en/products/wind-power) ·
[Energy load forecast](https://alitiq.com/en/products/energyload) ·
[Weather API](https://alitiq.com/en/products/weather-api)

---

## Installation

```bash
pip install alitiq
```

Requires Python 3.10+. Dependencies: `pandas`, `pydantic` (v2), `requests`.

To install from source:

```bash
git clone https://github.com/alitiq/alitiq-py.git
cd alitiq-py
pip install .
```

---

## Solar PV power forecast

Add a PV system, get its power forecast and push measurements so the forecast can learn from your
plant's real output.

```python
from datetime import datetime
from alitiq import alitiqSolarAPI, SolarPowerPlantModel, PvMeasurementForm

solar_api = alitiqSolarAPI(api_key="your-api-key")

# Register a PV system
plant = SolarPowerPlantModel(
    site_name="My Solar Plant",
    location_id="SP123",
    latitude=48.160170,
    longitude=10.55907,
    installed_power=500.0,           # kWp
    installed_power_inverter=480.0,  # kW
    azimuth=180.0,                   # 180 = south
    tilt=25.0,
    temp_factor=0.03,
)
solar_api.create_location(plant)

# Get the forecast (available 1–6 hours after the location was created)
forecast = solar_api.get_forecast(location_id="SP123")

# Forecast based on one specific weather model, in MW, local time
from alitiq.enumerations.forecast_models import ForecastModels

forecast_icon_d2 = solar_api.get_forecast(
    location_id="SP123",
    forecast_model=ForecastModels.ICON_D2,
    power_measure="MW",
    timezone="Europe/Berlin",
)

# Forecast for the whole PV portfolio, plus a sum column
portfolio = solar_api.get_forecast_portfolio()

# Push measurements
solar_api.post_measurements([
    PvMeasurementForm(
        location_id="SP123",
        dt=datetime(2024, 6, 10, 10, 0).isoformat(),
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
])
```

`SolarPowerPlantModel` also supports single-axis trackers (`mover`, `max_rotation_angle`,
`do_backtracking`, `row_distance`, …) and self-consumption systems (`self_consumption=True`). For
systems with several orientations, pass one model per subsystem with the same `location_id`.

New to PV forecasting? Start with [What is a solar power forecast?](https://alitiq.com/en/blog/what-is-a-solar-power-forecast)

### Simulate a PV system from satellite irradiance

`simulate_pv_power` simulates any PV system configuration on the fly from satellite irradiance
observations (CM SAF). Nothing is stored and the system doesn't have to be in your portfolio. Use it
to check a configuration, fill gaps in your measurements, or estimate the yield of a planned system.
Pass one `SolarPowerPlantModel` per subsystem.

```python
from datetime import datetime
from alitiq import alitiqSolarAPI, SolarPowerPlantModel

solar_api = alitiqSolarAPI(api_key="your-api-key")

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

simulation = solar_api.simulate_pv_power(
    plant,
    start_date=datetime(2026, 9, 1),
    end_date=datetime(2026, 9, 8),
    interpolate_to_15min=True,  # cm_saf_europe delivers 10-minute values
)
print(simulation[["power", "global_horizontal_irradiance", "air_temperature_2m"]])
```

---

## Wind power forecast

Register a wind park with its turbines and get the wind power forecast for the park or your whole
portfolio.

```python
from datetime import datetime
from alitiq import alitiqWindAPI, WindParkModel, WindPowerMeasurementForm, CurtailmentForm
from alitiq.models.wind_power_forecast import WindTurbineSchema

wind_api = alitiqWindAPI(api_key="your-api-key")

park = WindParkModel(
    site_name="My Wind Park",
    location_id="WP001",
    latitude=53.55,
    longitude=8.58,
    wind_turbines=[
        WindTurbineSchema(turbine_type="Enercon E-138 EP3", hub_height=131, rotor_diameter=138, installed_power=4200),
        WindTurbineSchema(turbine_type="Enercon E-138 EP3", hub_height=131, rotor_diameter=138, installed_power=4200),
    ],
)
wind_api.create_location(park)

# Wind power forecast for one park and for the whole portfolio
forecast = wind_api.get_forecast(location_id="WP001", power_measure="MW")
portfolio = wind_api.get_forecast_portfolio(power_measure="MW")

# Push measured power and curtailments (e.g. redispatch or nighttime curtailment)
wind_api.post_measurements([
    WindPowerMeasurementForm(
        location_id="WP001",
        dt=datetime(2026, 10, 1, 12, 0).isoformat(),
        power=5.2,
        power_measure="MW",
        interval_in_minutes=15,
    ),
])
wind_api.post_curtailments([
    CurtailmentForm(location_id="WP001", dt="2026-10-01T12:15:00", level=0.5),
])
```

`WindParkModel` also takes park-level nighttime curtailment settings
(`nighttime_curtailment`, `start_nighttime_curtailment`, `end_nighttime_curtailment`, `curtailment_level`).

More background: [What is a wind power forecast?](https://alitiq.com/en/blog/what-is-a-wind-power-forecast)

---

## Load forecast (electricity, heat, gas)

alitiq's load forecasts predict electricity, heat and gas demand, e.g. for utilities, grid operators
and energy traders.

```python
from alitiq import alitiqLoadAPI, LoadLocationForm

load_api = alitiqLoadAPI(api_key="your-api-key")

location = LoadLocationForm(
    site_name="HQ Campus",
    location_id="HQ-001",
    latitude=52.52,
    longitude=13.405,
    service="electricity-load",  # or "district-heating", "gas_load"
)
load_api.create_location(location)

forecast = load_api.get_forecast(location_id="HQ-001")
```

More background: [What is a load forecast?](https://alitiq.com/en/blog/what-is-a-load-forecast) ·
[What is a heat demand forecast?](https://alitiq.com/en/blog/what-is-a-heat-demand-forecast)

---

## Check when your API key expires

Every client can report when its API key was issued and when it expires. The same key works for all
services, so it doesn't matter which client you ask.

```python
from alitiq import alitiqSolarAPI

solar_api = alitiqSolarAPI(api_key="your-api-key")

expiration = solar_api.get_token_expiration()
print(expiration.token_expire_at)   # datetime in UTC, or None if the key never expires
print(expiration.expires_in_days)   # full days left, or None

if expiration.expires_in_days is not None and expiration.expires_in_days < 14:
    print("Time to rotate the alitiq API key")
```

An expired key is rejected with an HTTP 401/403 error, so this call only works while the key is still
valid. Run it from a scheduled job to get warned before your forecasts stop.

---

## API reference

All clients are in the `alitiq` package and take `api_key` as their only argument.

### `alitiqSolarAPI`: solar PV power forecast

| Method | Description |
|---|---|
| `create_location` | Add one or more PV systems (`SolarPowerPlantModel`) |
| `list_locations` | List your PV portfolio |
| `delete_location` | Delete a PV system |
| `get_forecast` | PV power forecast for one location |
| `get_forecast_portfolio` | PV power forecast for all locations |
| `post_measurements` | Push measured PV power (`PvMeasurementForm`) |
| `get_measurements` | Read measured PV power |
| `post_curtailments` / `inspect_curtailments` | Push and read curtailments (`CurtailmentForm`) |
| `simulate_pv_power` | Simulate any PV system from satellite irradiance |
| `get_token_expiration` | Expiration status of your API key |

### `alitiqWindAPI`: wind power forecast

| Method | Description |
|---|---|
| `create_location` | Add one or more wind parks (`WindParkModel`) |
| `list_locations` | List your wind portfolio |
| `delete_location` | Delete a wind park |
| `get_forecast` | Wind power forecast for one wind park |
| `get_forecast_portfolio` | Wind power forecast for all wind parks |
| `post_measurements` | Push measured wind power (`WindPowerMeasurementForm`) |
| `get_measurements` | Read measured wind power |
| `post_curtailments` / `inspect_curtailments` | Push and read curtailments (`CurtailmentForm`) |
| `get_token_expiration` | Expiration status of your API key |

### `alitiqLoadAPI`: load forecast

| Method | Description |
|---|---|
| `create_location` | Add a load location (`LoadLocationForm`) |
| `list_locations` | List your load portfolio |
| `delete_location` | Delete a load location |
| `get_forecast` | Load forecast for one location |
| `get_forecast_portfolio` | Load forecast for all locations |
| `post_measurements` | Push measured load (`LoadMeasurementForm`) |
| `get_measurements` | Read measured load |
| `get_token_expiration` | Expiration status of your API key |

Full parameter documentation, response formats and the REST endpoints behind the SDK are at
[docs.alitiq.com](https://docs.alitiq.com). The REST API is described at
[api.alitiq.com/docs](https://api.alitiq.com/docs).

### Project structure

```plaintext
alitiq/
├── enumerations/            # ForecastModels, Services
├── models/                  # Pydantic input models per service
├── base.py                  # alitiqAPIBase: HTTP session, shared methods, TokenExpiration
├── load_forecast.py         # alitiqLoadAPI
├── solar_power_forecast.py  # alitiqSolarAPI
└── wind_power_forecast.py   # alitiqWindAPI
```

---

## Further reading

- [Getting started with the alitiq API portal for PV and wind](https://alitiq.com/en/blog/api-portal-onboarding-pv-wind)
- [Choosing a forecasting provider](https://alitiq.com/en/blog/choosing-a-forecasting-provider)
- [Forecast time horizons explained](https://alitiq.com/en/blog/forecast-time-horizons)
- [MAPE pitfalls when measuring forecast accuracy](https://alitiq.com/en/blog/mape-pitfalls-forecast-accuracy)
- [Reducing balancing costs with better forecasts](https://alitiq.com/en/balancing-costs)
- [Forecasting for the energy industry](https://alitiq.com/en/industries/energy)

---

## Contributing

Bug reports and pull requests are welcome. Please open an
[issue](https://github.com/alitiq/alitiq-py/issues) or:

1. Fork the repository.
2. Create a branch: `git checkout -b feature/new-feature`
3. Run `nox -s black isort lint`.
4. Commit your changes and open a pull request.

### Releasing

Build with `python3 -m build` and upload with twine: `twine upload -r pypi dist/*`

---

## License

MIT, see [LICENSE](LICENSE).

## Support & contact

- Technical questions: [support@alitiq.com](mailto:support@alitiq.com)
- API access and pricing: [sales@alitiq.com](mailto:sales@alitiq.com) or [alitiq.com/en/contact](https://alitiq.com/en/contact)
- Website: [alitiq.com](https://alitiq.com)
