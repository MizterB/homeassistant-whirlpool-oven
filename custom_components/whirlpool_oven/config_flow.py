"""Config flow for Whirlpool Appliances integration."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from typing import Any

from aiohttp import ClientError
import voluptuous as vol
from whirlpool.appliancesmanager import AppliancesManager
from whirlpool.auth import Auth
from whirlpool.backendselector import BackendSelector

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_PASSWORD, CONF_REGION, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_BRAND, CONF_BRANDS_MAP, CONF_REGION_MAP, DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_REGION): vol.In(list(CONF_REGION_MAP)),
        vol.Required(CONF_BRAND): vol.In(list(CONF_BRANDS_MAP)),
    }
)

REAUTH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_BRAND): vol.In(list(CONF_BRANDS_MAP)),
    }
)


async def validate_input(
    hass: core.HomeAssistant, data: dict[str, str]
) -> dict[str, str]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)
    region = CONF_REGION_MAP[data[CONF_REGION]]
    brand = CONF_BRANDS_MAP[data[CONF_BRAND]]
    backend_selector = BackendSelector(brand, region)
    auth = Auth(backend_selector, data[CONF_USERNAME], data[CONF_PASSWORD], session)
    try:
        await auth.do_auth()
    except (TimeoutError, ClientError) as exc:
        raise CannotConnect from exc

    if not auth.is_access_token_valid():
        raise InvalidAuth

    appliances_manager = AppliancesManager(backend_selector, auth, session)
    await appliances_manager.fetch_appliances()
    if (
        appliances_manager.aircons is None
        and appliances_manager.washer_dryers is None
        and appliances_manager.ovens is None
    ):
        raise NoAppliances

    return {"title": data[CONF_USERNAME]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Whirlpool Sixth Sense."""

    VERSION = 1
    entry: config_entries.ConfigEntry | None

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> FlowResult:
        """Handle re-authentication with Whirlpool Sixth Sense."""

        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm re-authentication with Whirlpool Sixth Sense."""
        errors: dict[str, str] = {}

        if user_input:
            assert self.entry is not None
            password = user_input[CONF_PASSWORD]
            brand = user_input[CONF_BRAND]
            data = {
                **self.entry.data,
                CONF_PASSWORD: password,
                CONF_BRAND: brand,
            }

            try:
                await validate_input(self.hass, data)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except (CannotConnect, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                self.hass.config_entries.async_update_entry(self.entry, data=data)
                await self.hass.config_entries.async_reload(self.entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=REAUTH_SCHEMA,
            errors=errors,
        )

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except NoAppliances:
            errors["base"] = "no_appliances"
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(
                user_input[CONF_USERNAME].lower(), raise_on_progress=False
            )
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class NoAppliances(exceptions.HomeAssistantError):
    """Error to indicate no supported appliances in the user account."""
