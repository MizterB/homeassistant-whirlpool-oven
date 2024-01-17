"""Constants for the Whirlpool Appliances integration."""

import logging
from typing import Final

from whirlpool.backendselector import Region
from whirlpool.oven import CavityState, CookMode

DOMAIN: Final = "whirlpool_oven"

LOGGER = logging.getLogger(__package__)

CONF_OVEN: Final = "oven"
CONF_LAUNDRY: Final = "laundry"
CONF_AIRCON: Final = "aircon"
CONF_REGION_MAP = {
    "EU": Region.EU,
    "US": Region.US,
}

BRAND_WHIRLPOOL: Final = "Whirlpool"
BRAND_MAYTAG: Final = "Maytag"
BRAND_KITCHENAID: Final = "KitchenAid"
BRAND_AMANA: Final = "Amana"

OVEN_CAVITY_NAME = "oven"
OVEN_CAVITY_UPPER = "upper"
OVEN_CAVITY_UPPER_ALT = "right"
OVEN_CAVITY_LOWER = "lower"
OVEN_CAVITY_LOWER_ALT = "left"

OVEN_CAVITY_STATES = {
    CavityState.Standby: "standby",
    CavityState.Preheating: "preheating",
    CavityState.Cooking: "cooking",
    CavityState.NotPresent: "not_present",
}

OVEN_COOK_MODES = {
    CookMode.Standby: "standby",
    CookMode.Bake: "bake",
    CookMode.ConvectBake: "convection_bake",
    CookMode.Broil: "broil",
    CookMode.ConvectBroil: "convection_broil",
    CookMode.ConvectRoast: "convection_roast",
    CookMode.KeepWarm: "keep_warm",
    CookMode.AirFry: "air_fry",
}
