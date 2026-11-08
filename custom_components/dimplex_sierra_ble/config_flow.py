"""Explicitly confirm the fireplace and collect this integration's credentials."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers import selector

from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PRODUCT_ID,
    CONF_UUID,
    CREDENTIAL_FIELDS,
    DOMAIN,
    FD50_SERVICE_UUID,
    PRODUCT_NAME,
    TUYA_MANUFACTURER_ID,
)
from .credentials import InvalidCredentials, credentials_from_data


def _is_candidate(discovery: BluetoothServiceInfoBleak) -> bool:
    """Recognize generic Tuya advertisements, not a verified Sierra identity."""
    services = {value.lower() for value in discovery.service_uuids} | {
        value.lower() for value in discovery.service_data
    }
    return (
        FD50_SERVICE_UUID in services
        and TUYA_MANUFACTURER_ID in discovery.manufacturer_data
        and discovery.name == "TY"
    )


def _credentials_schema() -> vol.Schema:
    """Never prefill or echo secrets in a form."""
    private_text = selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
    )
    return vol.Schema(
        {
            vol.Required(CONF_PRODUCT_ID): selector.TextSelector(),
            vol.Required(CONF_UUID): private_text,
            vol.Required(CONF_DEVICE_ID): private_text,
            vol.Required(CONF_LOCAL_KEY): private_text,
        }
    )


class DimplexSierraConfigFlow(ConfigFlow, domain=DOMAIN):
    """Obtain consent and credentials without accessing the Tuya integration."""

    VERSION = 2

    def __init__(self) -> None:
        self._address: str | None = None

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Discovery must never create an entry without the user's consent."""
        if not _is_candidate(discovery_info):
            return self.async_abort(reason="not_sierra")
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._address = discovery_info.address
        self.context["title_placeholders"] = {"name": PRODUCT_NAME}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Explain that TY/FD50 also matches unrelated products."""
        if user_input is not None:
            return await self.async_step_credentials()
        self._set_confirm_only()
        return self.async_show_form(step_id="bluetooth_confirm")

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select an advertising candidate, then request its own credentials."""
        candidates = {
            discovery.address: PRODUCT_NAME
            for discovery in bluetooth.async_discovered_service_info(self.hass)
            if _is_candidate(discovery)
        }
        if not candidates:
            return self.async_abort(reason="not_found")
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            if address not in candidates:
                return self.async_abort(reason="not_found")
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            self._address = address
            return await self.async_step_credentials()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(candidates)}),
        )

    async def async_step_credentials(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Persist only credentials provided directly by this user."""
        self.context.pop("confirm_only", None)
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                credentials_from_data(user_input)
            except InvalidCredentials as exc:
                errors["base"] = exc.error_key
            else:
                assert self._address is not None
                return self.async_create_entry(
                    title=PRODUCT_NAME,
                    data={
                        CONF_ADDRESS: self._address,
                        **{field: user_input[field] for field in CREDENTIAL_FIELDS},
                    },
                )
        return self.async_show_form(
            step_id="credentials", data_schema=_credentials_schema(), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Allow correcting credentials without deleting the fireplace entry."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                credentials_from_data(user_input)
            except InvalidCredentials as exc:
                errors["base"] = exc.error_key
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        field: user_input[field] for field in CREDENTIAL_FIELDS
                    },
                )
        return self.async_show_form(
            step_id="reconfigure", data_schema=_credentials_schema(), errors=errors
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> ConfigFlowResult:
        """Ask legacy entries for credentials; never import them silently."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Keep the entry and its unique ID when the user supplies credentials."""
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                credentials_from_data(user_input)
            except InvalidCredentials as exc:
                errors["base"] = exc.error_key
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        field: user_input[field] for field in CREDENTIAL_FIELDS
                    },
                )
        return self.async_show_form(
            step_id="reauth_confirm", data_schema=_credentials_schema(), errors=errors
        )
