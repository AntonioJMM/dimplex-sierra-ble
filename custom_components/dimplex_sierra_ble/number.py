"""Numeric controls for the Dimplex Sierra."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, DP_EMBER_BRIGHTNESS, DP_FLAME_BRIGHTNESS, DP_TIMER
from .coordinator import DimplexSierraCoordinator
from .entity import DimplexSierraEntity
from .tuya_ble import TuyaBLEDataPointType


@dataclass(frozen=True, kw_only=True)
class DimplexNumberDescription(NumberEntityDescription):
    dp_id: int


NUMBERS = (
    DimplexNumberDescription(
        key="flame_brightness",
        name="Brillo de llama",
        icon="mdi:brightness-6",
        dp_id=DP_FLAME_BRIGHTNESS,
        native_min_value=1,
        native_max_value=3,
        native_step=1,
        mode=NumberMode.SLIDER,
    ),
    DimplexNumberDescription(
        key="ember_brightness",
        name="Brillo del lecho de brasas",
        icon="mdi:brightness-5",
        dp_id=DP_EMBER_BRIGHTNESS,
        native_min_value=1,
        native_max_value=3,
        native_step=1,
        mode=NumberMode.SLIDER,
    ),
    DimplexNumberDescription(
        key="timer",
        name="Temporizador",
        icon="mdi:timer-outline",
        dp_id=DP_TIMER,
        native_min_value=0,
        native_max_value=8,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.HOURS,
        mode=NumberMode.SLIDER,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DimplexSierraCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DimplexNumber(coordinator, description) for description in NUMBERS
    )


class DimplexNumber(DimplexSierraEntity, NumberEntity):
    entity_description: DimplexNumberDescription

    def __init__(self, coordinator, description: DimplexNumberDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        value = self._dp_value(self.entity_description.dp_id)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_write_dp(
            self.entity_description.dp_id,
            TuyaBLEDataPointType.DT_VALUE.value,
            int(value),
        )
