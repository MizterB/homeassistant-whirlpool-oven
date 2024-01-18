"""Sensors for Whirlpool Appliances."""
from __future__ import annotations

from whirlpool.oven import Cavity

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import CONF_OVEN, DOMAIN, OVEN_CAVITY_STATES, OVEN_COOK_MODES
from .device import WhirlpoolOvenDevice
from .entity import WhirlpoolEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Whirlpool Appliances sensors."""

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
                    WhirpoolOvenCavityStateSensor(oven_device, cavity),
                    WhirpoolOvenCookModeSensor(oven_device, cavity),
                    WhirpoolOvenTemperatureSensor(oven_device, cavity, "current"),
                    WhirpoolOvenTemperatureSensor(oven_device, cavity, "target"),
                ]
            )
        async_add_entities(oven_entities)


class WhirpoolOvenCavityStateSensor(WhirlpoolEntity, SensorEntity):
    """State of an oven cavity."""

    _attr_icon = "mdi:stove"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(OVEN_CAVITY_STATES.values())

    def __init__(self, device, cavity: Cavity):
        """Initialize the cavity state sensor."""
        self.cavity = cavity
        super().__init__(device)

    @property
    def name(self) -> str:
        """Return name of the sensor."""
        return f"{self.device.get_cavity_name(self.cavity)} state"

    @property
    def native_value(self) -> StateType | str:
        """Return native value of sensor."""
        return self.device.cavity_state(self.cavity)


class WhirpoolOvenCookModeSensor(WhirlpoolEntity, SensorEntity):
    """Cook mode of an oven cavity."""

    _attr_icon = "mdi:stove"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = list(OVEN_COOK_MODES.values())

    def __init__(self, device, cavity: Cavity):
        """Initialize the cook mode sensor."""
        self.cavity = cavity
        super().__init__(device)

    @property
    def name(self) -> str:
        """Return name of the sensor."""
        return f"{self.device.get_cavity_name(self.cavity)} cook mode"

    @property
    def native_value(self) -> StateType | str:
        """Return native value of sensor."""
        return self.device.cook_mode(self.cavity)


class WhirpoolOvenTemperatureSensor(WhirlpoolEntity, SensorEntity):
    """Temperature of an oven cavity."""

    _attr_icon = "mdi:thermometer"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, device, cavity: Cavity, temperature_type: str):
        """Initialize the cook mode sensor."""
        self.cavity = cavity
        self.temperature_type = temperature_type
        super().__init__(device)

    @property
    def name(self) -> str:
        """Return name of the sensor."""
        return f"{self.device.get_cavity_name(self.cavity)} {self.temperature_type} temperature"

    @property
    def native_value(self) -> StateType | str:
        """Return native value of sensor."""
        if self.temperature_type == "current":
            return self.device.current_temperature(self.cavity)
        if self.temperature_type == "target":
            return self.device.target_temperature(self.cavity)
