"""Diagnostic binary sensors for the Dimplex Sierra."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, DP_HEATER_DISABLED
from .coordinator import DimplexSierraCoordinator
from .entity import DimplexSierraEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DimplexSierraCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DimplexHeaterLockSensor(coordinator)])


class DimplexHeaterLockSensor(DimplexSierraEntity, BinarySensorEntity):
    _attr_name = "Calefactor deshabilitado"
    _attr_icon = "mdi:lock-alert"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DimplexSierraCoordinator) -> None:
        super().__init__(coordinator, "heater_disabled")

    @property
    def is_on(self) -> bool | None:
        value = self._dp_value(DP_HEATER_DISABLED)
        return bool(value) if value is not None else None
