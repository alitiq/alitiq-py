"""enumeration class for alitiq forecasting models"""

from enum import Enum


class ForecastModels(Enum):
    """alitiq's forecasting - Models"""

    OPTIMIZED = "optimized"
    ICON_EU = "icon_eu"
    ICON_D2 = "icon_d2"
    ICON = "icon"
    HARMONIE_DINI = "harmonie_dini"
    ARPEGE = "arpege"
    GFS = "gfs"


FORECASTING_MODELS_TO_ALITIQ_MODEL_NAMING = {
    ForecastModels.OPTIMIZED: "optimized",
    ForecastModels.ICON_EU: "icon_eu_update",
    ForecastModels.ICON_D2: "icon_d2",
    ForecastModels.ARPEGE: "arpege",
    ForecastModels.ICON: "icon_global",
    ForecastModels.HARMONIE_DINI: "harmonie_dini",
}
