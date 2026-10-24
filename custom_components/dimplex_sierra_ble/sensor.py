"""Diagnostic sensors for the Dimplex Sierra."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, DP_CURRENT_TEMPERATURE, DP_TEMPERATURE_UNIT
from .coordinator import DimplexSierraCoordinator
from .entity import DimplexSierraEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DimplexSierraCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [DimplexRawDP103Sensor(coordinator), DimplexTemperatureUnitSensor(coordinator)]
    )


class DimplexRawDP103Sensor(DimplexSierraEntity, SensorEntity):
    _attr_name = "Dato interno DP103"
    _attr_icon = "mdi:code-braces"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: DimplexSierraCoordinator) -> None:
        super().__init__(coordinator, "raw_dp103")

    @property
    def native_value(self) -> int | None:
        value = self._dp_value(DP_CURRENT_TEMPERATURE)
        return int(value) if value is not None else None


class DimplexTemperatureUnitSensor(DimplexSierraEntity, SensorEntity):
    _attr_name = "Unidad de temperatura"
    _attr_icon = "mdi:temperature-celsius"

    def __init__(self, coordinator: DimplexSierraCoordinator) -> None:
        super().__init__(coordinator, "temperature_unit_sensor")

    @property
    def native_value(self) -> str | None:
        value = self._dp_value(DP_TEMPERATURE_UNIT)
        if value == 0:
            return "Celsius"
        if value == 1:
            return "Fahrenheit"
        return None
