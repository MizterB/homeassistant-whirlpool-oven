"""Device data for the Whirpool Appliances integration."""
from __future__ import annotations

from aiohttp import ClientSession
from whirlpool.auth import Auth
from whirlpool.backendselector import BackendSelector
from whirlpool.oven import Cavity, Oven

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    BRAND_AMANA,
    BRAND_KITCHENAID,
    BRAND_MAYTAG,
    BRAND_WHIRLPOOL,
    DOMAIN,
    LOGGER,
    OVEN_CAVITY_STATES,
    OVEN_COOK_MODES,
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

        self.oven.register_attr_callback(self.on_update)

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

    @property
    def cavity_name(self, cavity: Cavity) -> bool:
        """Return the name of the oven cavity."""
        upper_exists = self.oven.get_oven_cavity_exists(Cavity.Upper)
        lower_exists = self.oven.get_oven_cavity_exists(Cavity.Lower)
        return self.oven.get_online() | False

    @property
    def is_online(self) -> bool:
        """Return the online status of the oven."""
        return self.oven.get_online() | False

    @property
    def upper_state(self) -> str:
        """Return the state of the upper/right oven."""
        state = self.oven.get_cavity_state(Cavity.Upper)
        return OVEN_CAVITY_STATES.get(state)

    @property
    def upper_mode(self) -> str:
        """Return the mode of the upper/right oven."""
        mode = self.oven.get_cook_mode(Cavity.Upper)
        return OVEN_COOK_MODES.get(mode)

    @property
    def upper_current_temperature(self) -> float:
        """Return the current temperature of the upper/right oven."""
        temp = self.oven.get_temp(Cavity.Upper)
        return temp if temp != 0 else None

    @property
    def upper_target_temperature(self) -> float:
        """Return the target temperature of the upper/right oven."""
        temp = self.oven.get_target_temp(Cavity.Upper)
        return temp if temp != 0 else None

    @property
    def upper_door(self) -> str:
        """Return the door state of the upper/right oven."""
        return str(self.oven.get_door_opened(Cavity.Upper))

    @property
    def upper_light(self) -> str:
        """Return the light state of the upper/right oven."""
        return str(self.oven.get_light(Cavity.Upper))

    @property
    def lower_state(self) -> str:
        """Return the state of the lower/left oven."""
        state = self.oven.get_cavity_state(Cavity.Lower)
        return OVEN_CAVITY_STATES.get(state)

    @property
    def lower_mode(self) -> str:
        """Return the mode of the lower/left oven."""
        mode = self.oven.get_cook_mode(Cavity.Lower)
        return OVEN_COOK_MODES.get(mode)

    @property
    def lower_current_temperature(self) -> float:
        """Return the current temperature of the lower/left oven."""
        temp = self.oven.get_temp(Cavity.Lower)
        return temp if temp != 0 else None

    @property
    def lower_target_temperature(self) -> float:
        """Return the target temperature of the lower/left oven."""
        temp = self.oven.get_target_temp(Cavity.Lower)
        return temp if temp != 0 else None

    @property
    def lower_door(self) -> str:
        """Return the door state of the lower/left oven."""
        return str(self.oven.get_door_opened(Cavity.Lower))

    @property
    def lower_light(self) -> str:
        """Return the light state of the lower/left oven."""
        return str(self.oven.get_light(Cavity.Lower))
