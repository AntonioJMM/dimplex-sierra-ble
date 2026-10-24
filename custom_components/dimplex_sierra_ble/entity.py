"""Base entities for Dimplex Sierra BLE."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, PRODUCT_NAME
from .coordinator import DimplexSierraCoordinator


class DimplexSierraEntity(CoordinatorEntity[DimplexSierraCoordinator]):
    """Base class shared by all Sierra entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DimplexSierraCoordinator, key: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.entry_id)},
            name=PRODUCT_NAME,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    def _dp_value(self, dp_id: int):
        item = self.coordinator.data.get(dp_id) if self.coordinator.data else None
        return item[1] if item else None
