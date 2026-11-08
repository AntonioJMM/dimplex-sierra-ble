"""Initial BLE read failures must reach Home Assistant's retry mechanism."""

from unittest.mock import AsyncMock, MagicMock, patch

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_ADDRESS
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.dimplex_sierra_ble.const import DOMAIN

from .conftest import ADDRESS


async def test_initial_read_failure_is_retryable_and_disconnects(hass, credentials):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=ADDRESS,
        version=2,
        data={CONF_ADDRESS: ADDRESS, **credentials},
    )
    entry.add_to_hass(hass)
    device = MagicMock()
    device.initialize = AsyncMock()
    device._execute_disconnect = AsyncMock()
    with (
        patch(
            "custom_components.dimplex_sierra_ble.coordinator.bluetooth.async_ble_device_from_address",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.dimplex_sierra_ble.coordinator.TuyaBLEDevice",
            return_value=device,
        ),
        patch(
            "custom_components.dimplex_sierra_ble.coordinator.DimplexSierraCoordinator._read_locked",
            side_effect=UpdateFailed("synthetic initial read failure"),
        ),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY
    device.initialize.assert_awaited_once()
    assert device._execute_disconnect.await_count >= 1
    device._send_packet.assert_not_called()
    assert entry.entry_id not in hass.data.get(DOMAIN, {})
