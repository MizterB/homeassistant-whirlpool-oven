"""Device data for the Whirpool Appliances integration."""
from __future__ import annotations

from datetime import datetime, timedelta

from aiohttp import ClientSession
from whirlpool.auth import Auth
from whirlpool.backendselector import BackendSelector
from whirlpool.oven import Cavity, Oven

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    BRAND_AMANA,
    BRAND_KITCHENAID,
    BRAND_MAYTAG,
    BRAND_WHIRLPOOL,
    DOMAIN,
    LOGGER,
    OVEN_CAVITY_NAME_LOWER,
    OVEN_CAVITY_NAME_LOWER_H,
    OVEN_CAVITY_NAME_SINGLE,
    OVEN_CAVITY_NAME_UPPER,
    OVEN_CAVITY_NAME_UPPER_H,
    OVEN_CAVITY_STATES,
    OVEN_COOK_MODES,
    OVEN_MODELS_HORIZONTAL,
)


def get_brand_from_model(model_number: str) -> str:
    """Get the brand name from the model number."""
    if model_number[0] == "W":
        return BRAND_WHIRLPOOL
    elif model_number[0] == "M":
        return BRAND_MAYTAG
    elif model_number[0] == "K":
        return BRAND_KITCHENAID
    elif model_number[0] == "A":
        return BRAND_AMANA
    else:
        return BRAND_WHIRLPOOL


class WhirpoolApplianceData:
    """Class for Whirlpool API appliance data."""

    def __init__(self, appliance_data: dict[str, str]) -> None:
        """Convert dict to properties."""
        self.said = appliance_data.get("SAID")
        self.name = appliance_data.get("NAME")
        self.data_model = appliance_data.get("DATA_MODEL")
        self.category = appliance_data.get("CATEGORY")
        self.model_number = appliance_data.get("MODEL_NUMBER")
        self.serial_number = appliance_data.get("SERIAL_NUMBER")


class WhirlpoolOvenDevice(DataUpdateCoordinator):
    """Oven device data."""

    def __init__(
        self,
        hass: HomeAssistant,
        appliance_data: WhirpoolApplianceData,
        backend_selector: BackendSelector,
        auth: Auth,
        session: ClientSession,
    ) -> None:
        """Initialize the device."""
        self.hass: HomeAssistant = hass
        self.appliance_data: WhirpoolApplianceData = appliance_data
        self.backend_selector: BackendSelector = backend_selector
        self.auth: Auth = auth
        self.session: ClientSession = session
        self.oven: Oven = Oven(
            backend_selector,
            auth,
            appliance_data.said,
            session,
        )

        # Register for the updates provided by the Whirlpool API
        self.oven.register_attr_callback(self.on_update)

        # Create a periodic keep-alive call to prevent the API connection from going stale
        async_track_time_interval(self.hass, self.keep_alive, timedelta(minutes=5))

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}-{self.appliance_data.said}",
        )

    async def connect(self) -> None:
        """Listen for oven events."""
        await self.oven.connect()

    def on_update(self) -> None:
        """Handle oven data update callbacks."""
        LOGGER.debug(f"Oven data for {self.appliance_data.name} has been updated")

    async def keep_alive(self, trigger: datetime) -> None:
        """Listen for oven events."""
        LOGGER.debug(f"Keeping the API connection alive")
        await self.oven.fetch_data()

    def register_callback(self, fn: callable):
        """Register a callback for oven updates."""
        self.oven.register_attr_callback(fn)

    def unregister_callback(self, fn: callable):
        """Unregister a callback for oven updates."""
        self.oven.unregister_attr_callback(fn)

    @property
    def has_multiple_cavities(self) -> bool:
        """True if the oven has multiple cavities."""
        if self.oven.get_oven_cavity_exists(
            Cavity.Upper
        ) and self.oven.get_oven_cavity_exists(Cavity.Lower):
            return True
        return False

    @property
    def cavities_are_horizontal(self) -> bool:
        """True if the oven has multiple cavities in a horizontal layout."""
        for horizontal_model in OVEN_MODELS_HORIZONTAL:
            if horizontal_model in self.appliance_data.model_number:
                return True
        return False

    def get_cavity_name(self, cavity: Cavity) -> str:
        """Return the name of a cavity, based on number of cavities and orientation."""
        name = OVEN_CAVITY_NAME_SINGLE
        if self.has_multiple_cavities:
            if cavity == Cavity.Lower:
                if self.cavities_are_horizontal:
                    name = OVEN_CAVITY_NAME_LOWER_H
                else:
                    name = OVEN_CAVITY_NAME_LOWER
            elif cavity == Cavity.Upper:
                if self.cavities_are_horizontal:
                    name = OVEN_CAVITY_NAME_UPPER_H
                else:
                    name = OVEN_CAVITY_NAME_UPPER
        return name

    @property
    def is_online(self) -> bool:
        """Return the online status of the oven."""
        return self.oven.get_online() | False

    def cavity_state(self, cavity: Cavity) -> str:
        """Return the state of an oven cavity."""
        state = self.oven.get_cavity_state(cavity)
        return OVEN_CAVITY_STATES.get(state)

    def cook_mode(self, cavity: Cavity) -> str:
        """Return the mode of an oven cavity."""
        mode = self.oven.get_cook_mode(cavity)
        return OVEN_COOK_MODES.get(mode)

    def current_temperature(self, cavity: Cavity) -> float:
        """Return the current temperature of an oven cavity."""
        temp = self.oven.get_temp(cavity)
        return temp if temp != 0 else None

    def target_temperature(self, cavity: Cavity) -> float:
        """Return the target temperature of an oven cavity."""
        temp = self.oven.get_target_temp(cavity)
        return temp if temp != 0 else None

    def is_door_open(self, cavity: Cavity) -> bool:
        """Return True if an oven cavity door is open."""
        return self.oven.get_door_opened(cavity)

    def is_light_on(self, cavity: Cavity) -> bool:
        """Return True if an oven cavity light is on."""
        return self.oven.get_light(cavity)

    async def turn_on_light(self, cavity: Cavity) -> None:
        """Turn on an oven cavity light."""
        await self.oven.set_light(True, cavity)

    async def turn_off_light(self, cavity: Cavity) -> None:
        """Turn off an oven cavity light."""
        await self.oven.set_light(False, cavity)
