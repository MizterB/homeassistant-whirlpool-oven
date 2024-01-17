"""Sensors for Whirlpool Appliances."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import CONF_OVEN, DOMAIN, OVEN_CAVITY_STATES, OVEN_COOK_MODES
from .device import WhirlpoolOvenDevice, get_brand_from_model


@dataclass(frozen=True)
class WhirlpoolSensorEntityDescriptionMixin:
    """Describes a Whirlpool Appliances sensor entity."""

    value_fn: Callable[[WhirlpoolOvenDevice], StateType]


@dataclass(frozen=True)
class WhirlpoolSensorEntityDescription(
    SensorEntityDescription, WhirlpoolSensorEntityDescriptionMixin
):
    """Describes a Whirlpool Appliances sensor entity."""


OVEN_SENSORS: tuple[WhirlpoolSensorEntityDescription, ...] = (
    WhirlpoolSensorEntityDescription(
        key="cavity_state_upper",
        name="Upper cavity state",
        icon="mdi:stove",
        device_class=SensorDeviceClass.ENUM,
        options=list(OVEN_CAVITY_STATES.values()),
        value_fn=lambda device: device.upper_state,
    ),
    WhirlpoolSensorEntityDescription(
        key="cook_mode_upper",
        name="Upper cavity cook mode",
        icon="mdi:stove",
        device_class=SensorDeviceClass.ENUM,
        options=list(OVEN_COOK_MODES.values()),
        value_fn=lambda device: device.upper_mode,
    ),
    WhirlpoolSensorEntityDescription(
        key="temp_upper",
        name="Upper cavity temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: device.upper_current_temperature,
    ),
    WhirlpoolSensorEntityDescription(
        key="target_temp_upper",
        name="Upper cavity target temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: device.upper_target_temperature,
    ),
    WhirlpoolSensorEntityDescription(
        key="light_upper",
        name="Upper cavity light on",
        icon="mdi:lightbulb",
        device_class=SensorDeviceClass.ENUM,
        options=["True", "False"],
        value_fn=lambda device: device.upper_light,
    ),
    WhirlpoolSensorEntityDescription(
        key="door_opened_upper",
        name="Upper cavity door open",
        icon="mdi:door",
        device_class=SensorDeviceClass.ENUM,
        options=["True", "False"],
        value_fn=lambda device: device.upper_door,
    ),
    WhirlpoolSensorEntityDescription(
        key="cavity_state_lower",
        name="Lower cavity state",
        icon="mdi:stove",
        device_class=SensorDeviceClass.ENUM,
        options=list(OVEN_CAVITY_STATES.values()),
        value_fn=lambda device: device.lower_state,
    ),
    WhirlpoolSensorEntityDescription(
        key="cook_mode_lower",
        name="Lower cavity cook mode",
        icon="mdi:stove",
        device_class=SensorDeviceClass.ENUM,
        options=list(OVEN_COOK_MODES.values()),
        value_fn=lambda device: device.lower_mode,
    ),
    WhirlpoolSensorEntityDescription(
        key="temp_lower",
        name="Lower cavity temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: device.lower_current_temperature,
    ),
    WhirlpoolSensorEntityDescription(
        key="target_temp_lower",
        name="Lower cavity target temperature",
        icon="mdi:thermometer",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda device: device.lower_target_temperature,
    ),
    WhirlpoolSensorEntityDescription(
        key="light_lower",
        name="Lower cavity light on",
        icon="mdi:lightbulb",
        device_class=SensorDeviceClass.ENUM,
        options=["True", "False"],
        value_fn=lambda device: device.lower_light,
    ),
    WhirlpoolSensorEntityDescription(
        key="door_opened_lower",
        name="Lower cavity door open",
        icon="mdi:door",
        device_class=SensorDeviceClass.ENUM,
        options=["True", "False"],
        value_fn=lambda device: device.lower_door,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Whirlpool Appliances sensors."""

    for device in hass.data[DOMAIN][config_entry.entry_id][CONF_OVEN].values():
        device: WhirlpoolOvenDevice
        async_add_entities(
            WhirpoolOvenSensor(device, sensor) for sensor in OVEN_SENSORS
        )


class WhirpoolOvenSensor(SensorEntity):
    """Representation of a Whirlpool oven sensor."""

    entity_description: WhirlpoolSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        device: WhirlpoolOvenDevice,
        entity_description: WhirlpoolSensorEntityDescription,
    ) -> None:
        """Initialize the sensor entity."""

        self.device = device
        self.entity_description = entity_description

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.device.appliance_data.said)},
            name=self.device.appliance_data.name.title(),
            manufacturer=get_brand_from_model(
                self.device.appliance_data.model_number,
            ),
            model=self.device.appliance_data.model_number,
            serial_number=self.device.appliance_data.serial_number,
        )
        self._attr_unique_id = (
            f"{self.device.appliance_data.said}-{self.entity_description.key}"
        )

    async def async_added_to_hass(self) -> None:
        """Connect to the cloud."""
        self.device.oven.register_attr_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Disconnect from the cloud before removing."""
        self.device.oven.unregister_attr_callback(self.async_write_ha_state)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.device.is_online

    @property
    def native_value(self) -> StateType | str:
        """Return native value of sensor."""
        return self.entity_description.value_fn(self.device)
