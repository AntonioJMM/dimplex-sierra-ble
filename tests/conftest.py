"""Fixtures use synthetic credentials and never contact a physical fireplace."""

from __future__ import annotations

import pytest
from bleak.backends.device import BLEDevice
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from pytest_homeassistant_custom_component.common import mock_component

from custom_components.dimplex_sierra_ble.const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PRODUCT_ID,
    CONF_UUID,
    FD50_SERVICE_UUID,
    PRODUCT_ID,
    TUYA_MANUFACTURER_ID,
)

ADDRESS = ":".join(["00"] * 6)


@pytest.fixture(autouse=True)
def custom_integrations(hass, enable_custom_integrations, mock_bluetooth):
    """Isolate OS Bluetooth setup; individual API calls are patched in tests."""
    mock_component(hass, "bluetooth")


@pytest.fixture
def credentials():
    """Synthetic values, not device credentials."""
    return {
        CONF_UUID: "u" * 16,
        CONF_LOCAL_KEY: "k" * 16,
        CONF_DEVICE_ID: "d" * 20,
        CONF_PRODUCT_ID: PRODUCT_ID,
    }


@pytest.fixture
def advertisement():
    return BluetoothServiceInfoBleak(
        name="TY",
        address=ADDRESS,
        rssi=-50,
        manufacturer_data={TUYA_MANUFACTURER_ID: b"synthetic"},
        service_data={},
        service_uuids=[FD50_SERVICE_UUID],
        source="test",
        device=BLEDevice(ADDRESS, "TY", None),
        advertisement=None,
        connectable=True,
        time=0.0,
        tx_power=None,
    )
