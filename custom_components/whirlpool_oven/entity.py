"""Base entity class for Whirlpool Appliances entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .device import WhirlpoolOvenDevice, get_brand_from_model


class WhirlpoolEntity(Entity):
    """A base class for Whirlpool Appliances entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False
    _attr_force_update = False

    def __init__(self, device: list[WhirlpoolOvenDevice], **kwargs) -> None:
        """Initialize the Whirlpool entity."""

        self.device: list[WhirlpoolOvenDevice] = device

        self._attr_unique_id = f"{self.device.appliance_data.said}-{self.name}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return a device description for device registry."""

        return DeviceInfo(
            identifiers={(DOMAIN, self.device.appliance_data.said)},
            name=self.device.appliance_data.name.title(),
            manufacturer=get_brand_from_model(
                self.device.appliance_data.model_number,
            ),
            model=self.device.appliance_data.model_number,
            serial_number=self.device.appliance_data.serial_number,
        )

    async def async_added_to_hass(self) -> None:
        """Register for device state updates."""
        self.device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Unegister from device state updates."""
        self.device.unregister_callback(self.async_write_ha_state)

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        return self.device.is_online
