"""Binary sensors for Whirlpool Appliances."""

from __future__ import annotations

from whirlpool.oven import Cavity

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
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
    """Set up the Whirlpool Appliances binary sensors from config entry."""

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
                    WhirpoolOvenCavityDoorBinarySensor(oven_device, cavity),
                ]
            )
        async_add_entities(oven_entities)


class WhirpoolOvenCavityDoorBinarySensor(WhirlpoolEntity, BinarySensorEntity):
    """State of an oven cavity door."""

    _attr_device_class = BinarySensorDeviceClass.DOOR

    def __init__(self, device: WhirlpoolOvenDevice, cavity: Cavity) -> None:
        """Initialize the cavity door binary sensor."""
        self.cavity = cavity
        super().__init__(device)

    @property
    def name(self) -> str:
        """Return name of the binary sensor."""
        return f"{self.device.get_cavity_name(self.cavity)} door"

    @property
    def is_on(self):
        """Return true if the cavity door is open."""
        return self.device.is_door_open(self.cavity)
