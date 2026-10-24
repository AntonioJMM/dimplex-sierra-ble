"""Selectors for the Dimplex Sierra."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    CONTINUOUS_HEAT_VALUE,
    DOMAIN,
    DP_EMBER_COLOR,
    DP_FLAME_COLOR,
    DP_TARGET_TEMPERATURE,
    TARGET_TEMPERATURES_C,
)
from .coordinator import DimplexSierraCoordinator
from .entity import DimplexSierraEntity
from .tuya_ble import TuyaBLEDataPointType


@dataclass(frozen=True, kw_only=True)
class DimplexSelectDescription(SelectEntityDescription):
    dp_id: int
    value_to_option: dict[int, str]


THERMOSTAT_OPTIONS = {
    **{value: f"{value} °C" for value in TARGET_TEMPERATURES_C},
    CONTINUOUS_HEAT_VALUE: "Calor continuo",
}
FLAME_OPTIONS = {
    0: "Apagada",
    1: "Rotación (L1)",
    **{value: f"L{value}" for value in range(2, 9)},
}
EMBER_OPTIONS = {
    1: "Rotación (d1)",
    **{value: f"d{value}" for value in range(2, 9)},
    9: "Brasas oscilantes (d9)",
}

SELECTS = (
    DimplexSelectDescription(
        key="thermostat_setting",
        name="Ajuste del termostato",
        icon="mdi:thermostat",
        dp_id=DP_TARGET_TEMPERATURE,
        value_to_option=THERMOSTAT_OPTIONS,
    ),
    DimplexSelectDescription(
        key="flame_color",
        name="Efecto de llama",
        icon="mdi:fire",
        dp_id=DP_FLAME_COLOR,
        value_to_option=FLAME_OPTIONS,
    ),
    DimplexSelectDescription(
        key="ember_color",
        name="Efecto del lecho de brasas",
        icon="mdi:campfire",
        dp_id=DP_EMBER_COLOR,
        value_to_option=EMBER_OPTIONS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DimplexSierraCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DimplexSelect(coordinator, description) for description in SELECTS
    )


class DimplexSelect(DimplexSierraEntity, SelectEntity):
    entity_description: DimplexSelectDescription

    def __init__(self, coordinator, description: DimplexSelectDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_options = list(description.value_to_option.values())
        self._option_to_value = {
            option: value for value, option in description.value_to_option.items()
        }

    @property
    def current_option(self) -> str | None:
        return self.entity_description.value_to_option.get(
            self._dp_value(self.entity_description.dp_id)
        )

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_write_dp(
            self.entity_description.dp_id,
            TuyaBLEDataPointType.DT_ENUM.value,
            self._option_to_value[option],
        )
