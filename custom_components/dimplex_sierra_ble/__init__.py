"""Dimplex Sierra BLE integration."""

from __future__ import annotations

from contextlib import suppress

from bleak.exc import BleakError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN, PLATFORMS
from .coordinator import DimplexSierraCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator = DimplexSierraCoordinator(hass, entry)
    try:
        await coordinator.async_initialize()
    except (ConfigEntryAuthFailed, ConfigEntryNotReady):
        with suppress(Exception):
            await coordinator.async_close()
        raise
    except (UpdateFailed, BleakError, OSError, TimeoutError):
        with suppress(Exception):
            await coordinator.async_close()
        raise ConfigEntryNotReady(
            "The Dimplex Sierra Bluetooth connection is not ready"
        ) from None
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Retain legacy entry/entity identity; setup will request user credentials."""
    if entry.version > 2:
        return False
    if entry.version < 2:
        hass.config_entries.async_update_entry(entry, version=2, minor_version=1)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: DimplexSierraCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_close()
    return unload_ok
