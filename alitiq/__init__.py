"""easy access"""

from alitiq.load_forecast import alitiqLoadAPI  # noqa
from alitiq.models.load_forecast import LoadMeasurementForm  # noqa
from alitiq.models.solar_power_forecast import PvMeasurementForm  # noqa
from alitiq.models.solar_power_forecast import SolarPowerPlantModel  # noqa
from alitiq.models.wind_power_forecast import WindParkModel  # noqa
from alitiq.models.wind_power_forecast import WindPowerMeasurementForm  # noqa
from alitiq.models.wind_power_forecast import (  # noqa, sames solar_power_forecast CurtailmentForm
    CurtailmentForm,
)
from alitiq.solar_power_forecast import alitiqSolarAPI  # noqa
from alitiq.wind_power_forecast import alitiqWindAPI  # noqa
