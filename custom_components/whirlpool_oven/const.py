"""Constants for the Whirlpool Appliances integration."""

import logging
from typing import Final

from whirlpool.backendselector import Brand, Region
from whirlpool.oven import CavityState, CookMode

DOMAIN: Final = "whirlpool_oven"

LOGGER = logging.getLogger(__package__)

CONF_BRAND: Final = "brand"
CONF_OVEN: Final = "oven"
CONF_LAUNDRY: Final = "laundry"
CONF_AIRCON: Final = "aircon"


CONF_BRANDS_MAP: Final = {
    "Whirlpool": Brand.Whirlpool,
    "Maytag": Brand.Maytag,
    "KitchenAid": Brand.KitchenAid,
}
CONF_REGION_MAP: Final = {
    "EU": Region.EU,
    "US": Region.US,
}

BRAND_WHIRLPOOL: Final = "Whirlpool"
BRAND_MAYTAG: Final = "Maytag"
BRAND_KITCHENAID: Final = "KitchenAid"
BRAND_AMANA: Final = "Amana"

OVEN_CAVITY_NAME_SINGLE: Final = "Oven"
OVEN_CAVITY_NAME_LOWER: Final = "Lower oven"
OVEN_CAVITY_NAME_LOWER_H: Final = "Left oven"
OVEN_CAVITY_NAME_UPPER: Final = "Upper oven"
OVEN_CAVITY_NAME_UPPER_H: Final = "Right oven"

OVEN_CAVITY_STATES: Final = {
    CavityState.Standby: "standby",
    CavityState.Preheating: "preheating",
    CavityState.Cooking: "cooking",
    CavityState.NotPresent: "not_present",
}

OVEN_COOK_MODES: Final = {
    CookMode.Standby: "standby",
    CookMode.Bake: "bake",
    CookMode.ConvectBake: "convection_bake",
    CookMode.Broil: "broil",
    CookMode.ConvectBroil: "convection_broil",
    CookMode.ConvectRoast: "convection_roast",
    CookMode.KeepWarm: "keep_warm",
    CookMode.AirFry: "air_fry",
}

OVEN_MODELS_HORIZONTAL: Final = ["KFDC558JSS", "KFGC558JSS"]
