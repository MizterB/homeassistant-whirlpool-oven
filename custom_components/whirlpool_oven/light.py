"""Support for Whirlpool Appliances lights."""

from __future__ import annotations

from typing import Any

from whirlpool.oven import Cavity

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_OVEN, DOMAIN
from .device import WhirlpoolOvenDevice
from .entity import WhirlpoolEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Whirlpool Appliances lights from config entry."""

    for oven_device in hass.data[DOMAIN][config_entry.entry_id][CONF_OVEN].values():
        oven_device: WhirlpoolOvenDevice
        oven_entities = []
        cavities = []
        if oven_device.oven.get_oven_cavity_exists(Cavity.Upper):
            cavities.append(Cavity.Upper)
        if oven_device.oven.get_oven_cavity_exists(Cavity.Lower):
            cavities.append(Cavity.Lower)

        for cavity in cavities:
            oven_entities.extend(
                [
                    WhirpoolOvenCavityLight(oven_device, cavity),
                ]
            )
        async_add_entities(oven_entities)


class WhirpoolOvenCavityLight(WhirlpoolEntity, LightEntity):
    """Representation of an oven cavity light."""

    _attr_color_mode = ColorMode.ONOFF

    def __init__(self, device: WhirlpoolOvenDevice, cavity: Cavity) -> None:
        """Initialize the cavity door binary sensor."""
        self.cavity = cavity
        super().__init__(device)

    @property
    def name(self) -> str:
        """Return name of the light."""
        return f"{self.device.get_cavity_name(self.cavity)} light"

    @property
    def is_on(self):
        """Return true if the cavity light in on."""
        return self.device.is_light_on(self.cavity)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        await self.device.turn_on_light(self.cavity)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        await self.device.turn_off_light(self.cavity)
