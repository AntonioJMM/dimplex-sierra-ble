"""Switches for the Dimplex Sierra."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, DP_HEAT, DP_POWER, DP_SOUND
from .coordinator import DimplexSierraCoordinator
from .entity import DimplexSierraEntity
from .tuya_ble import TuyaBLEDataPointType


@dataclass(frozen=True, kw_only=True)
class DimplexSwitchDescription(SwitchEntityDescription):
    dp_id: int
    verification_retries: int = 0
    verification_delay: float = 0.0


SWITCHES = (
    DimplexSwitchDescription(
        key="power", name="Encendido", icon="mdi:fireplace", dp_id=DP_POWER
    ),
    DimplexSwitchDescription(
        key="heat", name="Calefacción", icon="mdi:radiator", dp_id=DP_HEAT
    ),
    DimplexSwitchDescription(
        key="sound",
        name="Sonido",
        icon="mdi:volume-high",
        dp_id=DP_SOUND,
        verification_retries=1,
        verification_delay=3.0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DimplexSierraCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DimplexSwitch(coordinator, description) for description in SWITCHES
    )


class DimplexSwitch(DimplexSierraEntity, SwitchEntity):
    entity_description: DimplexSwitchDescription

    def __init__(self, coordinator, description: DimplexSwitchDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        value = self._dp_value(self.entity_description.dp_id)
        return bool(value) if value is not None else None

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_write_dp(
            self.entity_description.dp_id,
            TuyaBLEDataPointType.DT_BOOL.value,
            True,
            verification_retries=self.entity_description.verification_retries,
            verification_delay=self.entity_description.verification_delay,
        )

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_write_dp(
            self.entity_description.dp_id,
            TuyaBLEDataPointType.DT_BOOL.value,
            False,
            verification_retries=self.entity_description.verification_retries,
            verification_delay=self.entity_description.verification_delay,
        )
