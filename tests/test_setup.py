"""Regression tests for setup retries and independent credentials."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bleak.exc import BleakError
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_ADDRESS
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.dimplex_sierra_ble import (
    async_migrate_entry,
    async_setup_entry,
)
from custom_components.dimplex_sierra_ble.const import DOMAIN
from custom_components.dimplex_sierra_ble.coordinator import (
    DimplexSierraCoordinator,
    _get_entry_credentials,
)

from .conftest import ADDRESS


@pytest.fixture
def entry(hass, credentials):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=ADDRESS,
        version=2,
        data={CONF_ADDRESS: ADDRESS, **credentials},
    )
    entry.add_to_hass(hass)
    return entry


def test_credentials_from_own_entry_without_tuya(entry, credentials):
    result = _get_entry_credentials(entry)
    assert result.local_key == credentials["local_key"]
    assert result.uuid == credentials["uuid"]
    assert result.device_id == credentials["device_id"]


async def test_legacy_migration_keeps_identity_and_requests_credentials(
    hass, entity_registry
):
    entry = MockConfigEntry(
        domain=DOMAIN, unique_id=ADDRESS, version=1, data={CONF_ADDRESS: ADDRESS}
    )
    entry.add_to_hass(hass)
    entry_id = entry.entry_id
    entity = entity_registry.async_get_or_create(
        "switch", DOMAIN, "synthetic_power", config_entry=entry
    )
    assert await async_migrate_entry(hass, entry)
    assert entry.version == 2
    assert entry.entry_id == entry_id
    assert entry.unique_id == ADDRESS
    assert entry.data == {CONF_ADDRESS: ADDRESS}
    assert entity_registry.async_get(entity.entity_id) is entity
    assert entity.config_entry_id == entry_id
    with pytest.raises(ConfigEntryAuthFailed):
        _get_entry_credentials(entry)


async def test_missing_advertisement_is_retryable(hass, entry):
    coordinator = DimplexSierraCoordinator(hass, entry)
    with (
        patch(
            "custom_components.dimplex_sierra_ble.coordinator.bluetooth.async_ble_device_from_address",
            return_value=None,
        ),
        pytest.raises(ConfigEntryNotReady),
    ):
        await coordinator.async_initialize()
    assert coordinator.device is None


@pytest.mark.parametrize(
    "failure",
    [UpdateFailed("test"), BleakError("test"), OSError("test"), TimeoutError()],
)
async def test_transient_setup_errors_retry_and_close(hass, entry, failure):
    coordinator = MagicMock()
    coordinator.async_initialize = AsyncMock(side_effect=failure)
    coordinator.async_close = AsyncMock()
    with (
        patch(
            "custom_components.dimplex_sierra_ble.DimplexSierraCoordinator",
            return_value=coordinator,
        ),
        pytest.raises(ConfigEntryNotReady),
    ):
        await async_setup_entry(hass, entry)
    coordinator.async_close.assert_awaited_once()
    assert entry.entry_id not in hass.data.get(DOMAIN, {})


async def test_cleanup_error_does_not_mask_retry(hass, entry):
    coordinator = MagicMock()
    coordinator.async_initialize = AsyncMock(side_effect=UpdateFailed("test"))
    coordinator.async_close = AsyncMock(side_effect=BleakError("cleanup"))
    with (
        patch(
            "custom_components.dimplex_sierra_ble.DimplexSierraCoordinator",
            return_value=coordinator,
        ),
        pytest.raises(ConfigEntryNotReady),
    ):
        await async_setup_entry(hass, entry)


async def test_framework_marks_transient_setup_for_retry(hass, entry):
    coordinator = MagicMock()
    coordinator.async_initialize = AsyncMock(side_effect=UpdateFailed("test"))
    coordinator.async_close = AsyncMock()
    with patch(
        "custom_components.dimplex_sierra_ble.DimplexSierraCoordinator",
        return_value=coordinator,
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY


async def test_auth_error_is_not_silently_retried(hass, entry):
    coordinator = MagicMock()
    coordinator.async_initialize = AsyncMock(side_effect=ConfigEntryAuthFailed("test"))
    coordinator.async_close = AsyncMock()
    with (
        patch(
            "custom_components.dimplex_sierra_ble.DimplexSierraCoordinator",
            return_value=coordinator,
        ),
        pytest.raises(ConfigEntryAuthFailed),
    ):
        await async_setup_entry(hass, entry)
    coordinator.async_close.assert_awaited_once()


async def test_successful_setup_forwards_platforms(hass, entry):
    coordinator = MagicMock()
    coordinator.async_initialize = AsyncMock()
    with (
        patch(
            "custom_components.dimplex_sierra_ble.DimplexSierraCoordinator",
            return_value=coordinator,
        ),
        patch.object(hass.config_entries, "async_forward_entry_setups") as forward,
    ):
        assert await async_setup_entry(hass, entry)
    assert hass.data[DOMAIN][entry.entry_id] is coordinator
    forward.assert_awaited_once()
