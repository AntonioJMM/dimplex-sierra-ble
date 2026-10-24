"""Climate entity for the Dimplex Sierra."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    DOMAIN,
    DP_HEAT,
    DP_HEATER_DISABLED,
    DP_POWER,
    DP_TARGET_TEMPERATURE,
    DP_TEMPERATURE_UNIT,
)
from .coordinator import DimplexSierraCoordinator
from .entity import DimplexSierraEntity
from .tuya_ble import TuyaBLEDataPointType


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: DimplexSierraCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DimplexClimate(coordinator)])


class DimplexClimate(DimplexSierraEntity, ClimateEntity):
    _attr_name = "Climatización"
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )

    def __init__(self, coordinator: DimplexSierraCoordinator) -> None:
        super().__init__(coordinator, "climate")

    @property
    def temperature_unit(self) -> str:
        return (
            UnitOfTemperature.FAHRENHEIT
            if self._dp_value(DP_TEMPERATURE_UNIT) == 1
            else UnitOfTemperature.CELSIUS
        )

    @property
    def min_temp(self) -> float:
        return 64 if self.temperature_unit == UnitOfTemperature.FAHRENHEIT else 18

    @property
    def max_temp(self) -> float:
        return 82 if self.temperature_unit == UnitOfTemperature.FAHRENHEIT else 27

    @property
    def target_temperature_step(self) -> float:
        return 2 if self.temperature_unit == UnitOfTemperature.FAHRENHEIT else 1

    @property
    def current_temperature(self) -> float | None:
        # DP103 changes independently and has produced physically impossible
        # values. Do not present it as a temperature until its encoding is
        # confirmed from additional protocol captures.
        return None

    @property
    def target_temperature(self) -> float | None:
        value = self._dp_value(DP_TARGET_TEMPERATURE)
        if value is None or value > self.max_temp:
            return None
        return float(value)

    @property
    def hvac_mode(self) -> HVACMode:
        return HVACMode.HEAT if self._dp_value(DP_HEAT) is True else HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.HEAT:
            if self._dp_value(DP_HEATER_DISABLED) is True:
                raise HomeAssistantError(
                    "The heater safety lock is enabled; hold Heat on the front "
                    "panel for 10 seconds"
                )
            if self._dp_value(DP_POWER) is not True:
                await self.coordinator.async_write_dp(
                    DP_POWER, TuyaBLEDataPointType.DT_BOOL.value, True
                )
            await self.coordinator.async_write_dp(
                DP_HEAT, TuyaBLEDataPointType.DT_BOOL.value, True
            )
            return
        await self.coordinator.async_write_dp(
            DP_HEAT, TuyaBLEDataPointType.DT_BOOL.value, False
        )

    async def async_set_temperature(self, **kwargs: Any) -> None:
        requested = float(kwargs[ATTR_TEMPERATURE])
        value = round(requested)
        value = max(round(self.min_temp), min(round(self.max_temp), value))
        await self.coordinator.async_write_dp(
            DP_TARGET_TEMPERATURE,
            TuyaBLEDataPointType.DT_ENUM.value,
            value,
        )

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)
