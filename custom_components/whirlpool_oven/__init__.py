"""The Whirlpool Appliances integration."""

import asyncio

from aiohttp import ClientError
from whirlpool.appliancesmanager import AppliancesManager
from whirlpool.auth import Auth
from whirlpool.backendselector import BackendSelector

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_BRAND, CONF_BRANDS_MAP, CONF_OVEN, CONF_REGION_MAP, DOMAIN
from .device import WhirlpoolOvenDevice, WhirpoolApplianceData

PLATFORMS = [Platform.BINARY_SENSOR, Platform.LIGHT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Whirlpool Appliances from a config entry."""

    session = async_get_clientsession(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {}

    region = CONF_REGION_MAP[config_entry.data.get(CONF_REGION, "EU")]
    brand = CONF_BRANDS_MAP[config_entry.data.get(CONF_BRAND, "Whirlpool")]
    backend_selector = BackendSelector(brand, region)
    auth = Auth(
        backend_selector,
        config_entry.data[CONF_USERNAME],
        config_entry.data[CONF_PASSWORD],
        session,
    )

    try:
        await auth.do_auth(store=False)
    except (ClientError, TimeoutError) as err:
        raise ConfigEntryNotReady("Unable to connect to Whirlpool") from err

    if not auth.is_access_token_valid():
        raise ConfigEntryAuthFailed("Incorrect password")

    appliances_manager = AppliancesManager(backend_selector, auth, session)
    if not await appliances_manager.fetch_appliances():
        raise ConfigEntryNotReady("Unable to fetch appliances from Whirlpool")

    hass.data[DOMAIN][config_entry.entry_id][CONF_OVEN] = {}
    for oven in appliances_manager.ovens:
        appliance_data = WhirpoolApplianceData(oven)
        device = WhirlpoolOvenDevice(
            hass, appliance_data, backend_selector, auth, session
        )
        await device.connect()
        hass.data[DOMAIN][config_entry.entry_id][CONF_OVEN][
            device.appliance_data.said
        ] = device

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )
    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
