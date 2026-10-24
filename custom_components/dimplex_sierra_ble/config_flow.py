"""Config flow for Dimplex Sierra BLE."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import (
    DOMAIN,
    FD50_SERVICE_UUID,
    PRODUCT_NAME,
    TUYA_MANUFACTURER_ID,
)


class DimplexSierraConfigFlow(ConfigFlow, domain=DOMAIN):
    """Discover and configure the fireplace without storing Tuya secrets."""

    VERSION = 1

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        services = {value.lower() for value in discovery_info.service_uuids} | {
            value.lower() for value in discovery_info.service_data
        }
        if (
            FD50_SERVICE_UUID not in services
            or TUYA_MANUFACTURER_ID not in discovery_info.manufacturer_data
            or discovery_info.name != "TY"
        ):
            return self.async_abort(reason="not_sierra")
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self.context["title_placeholders"] = {"name": PRODUCT_NAME}
        return self.async_create_entry(
            title=PRODUCT_NAME,
            data={CONF_ADDRESS: discovery_info.address},
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        candidates: dict[str, str] = {}
        for discovery in bluetooth.async_discovered_service_info(self.hass):
            services = {value.lower() for value in discovery.service_uuids} | {
                value.lower() for value in discovery.service_data
            }
            if (
                FD50_SERVICE_UUID in services
                and TUYA_MANUFACTURER_ID in discovery.manufacturer_data
                and discovery.name == "TY"
            ):
                candidates[discovery.address] = PRODUCT_NAME

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=PRODUCT_NAME,
                data={CONF_ADDRESS: address},
            )

        if not candidates:
            return self.async_abort(reason="not_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(candidates)}),
        )
