"""BLE coordinator for the Dimplex Sierra fireplace."""

from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from struct import pack
from types import MethodType
from typing import Any

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import PRODUCT_ID, PRODUCT_NAME
from .tuya_ble import (
    AbstaractTuyaBLEDeviceManager,
    TuyaBLEDataPointType,
    TuyaBLEDevice,
    TuyaBLEDeviceCredentials,
)
from .tuya_ble.const import TuyaBLECode

_LOGGER = logging.getLogger(__name__)
# The vendored prototype logs Bluetooth addresses at debug/error level. Keep it
# silent and expose only redacted coordinator errors.
logging.getLogger(f"{__package__}.tuya_ble").setLevel(logging.CRITICAL)

DPState = dict[int, tuple[int, Any]]


class _CredentialsManager(AbstaractTuyaBLEDeviceManager):
    def __init__(self, credentials: TuyaBLEDeviceCredentials) -> None:
        self._credentials = credentials

    async def get_device_credentials(
        self,
        address: str,
        force_update: bool = False,
        save_data: bool = False,
    ) -> TuyaBLEDeviceCredentials:
        return self._credentials


def _get_tuya_credentials(hass: HomeAssistant) -> TuyaBLEDeviceCredentials:
    """Reuse credentials already held by the official Tuya integration."""
    for entry in hass.config_entries.async_entries("tuya"):
        listener = getattr(entry, "runtime_data", None)
        manager = getattr(listener, "manager", None)
        if manager is None:
            continue
        for device in manager.device_map.values():
            if getattr(device, "product_id", "") != PRODUCT_ID:
                continue
            if not all(
                getattr(device, attribute, None)
                for attribute in ("uuid", "local_key", "id", "category")
            ):
                continue
            return TuyaBLEDeviceCredentials(
                device.uuid,
                device.local_key,
                device.id,
                device.category,
                device.product_id,
                getattr(device, "name", PRODUCT_NAME),
                None,
                getattr(device, "product_name", PRODUCT_NAME),
                None,
            )
    raise UpdateFailed("Tuya credentials for the Dimplex Sierra are unavailable")


def _decode_scalar(raw: bytes, dp_type: int) -> Any:
    if dp_type == TuyaBLEDataPointType.DT_BOOL.value:
        return bool(int.from_bytes(raw, "big"))
    if dp_type == TuyaBLEDataPointType.DT_VALUE.value:
        return int.from_bytes(raw, "big", signed=True)
    if dp_type == TuyaBLEDataPointType.DT_ENUM.value:
        return int.from_bytes(raw, "big", signed=False)
    if dp_type == TuyaBLEDataPointType.DT_STRING.value:
        return raw.decode(errors="replace")
    return bytes(raw)


def _encode_scalar(dp_type: int, value: Any) -> bytes:
    if dp_type == TuyaBLEDataPointType.DT_BOOL.value:
        return bytes([1 if value else 0])
    if dp_type == TuyaBLEDataPointType.DT_VALUE.value:
        return pack(">i", int(value))
    if dp_type == TuyaBLEDataPointType.DT_ENUM.value:
        number = int(value)
        if not 0 <= number <= 0xFFFFFFFF:
            raise HomeAssistantError("Enum value is outside the Tuya range")
        if number <= 0xFF:
            return bytes([number])
        if number <= 0xFFFF:
            return number.to_bytes(2, "big")
        return number.to_bytes(4, "big")
    if dp_type == TuyaBLEDataPointType.DT_STRING.value:
        return str(value).encode()
    if isinstance(value, bytes):
        return value
    raise HomeAssistantError("Unsupported Tuya datapoint type")


class DimplexSierraCoordinator(DataUpdateCoordinator[DPState]):
    """Poll and control a Dimplex Sierra over Tuya BLE V4.2."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=PRODUCT_NAME,
            update_interval=timedelta(seconds=60),
        )
        self.entry = entry
        self.address: str = entry.data[CONF_ADDRESS]
        self.device: TuyaBLEDevice | None = None
        self._state: DPState = {}
        self._operation_lock = asyncio.Lock()

    async def async_initialize(self) -> None:
        credentials = _get_tuya_credentials(self.hass)
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device is None:
            raise UpdateFailed(
                "The Dimplex Sierra Bluetooth advertisement is unavailable"
            )
        self.device = TuyaBLEDevice(_CredentialsManager(credentials), ble_device, None)
        self.device._parse_datapoints_v4 = MethodType(  # noqa: SLF001
            self._parse_sierra_v4, self.device
        )
        await self.device.initialize()
        await self.async_config_entry_first_refresh()

    def _parse_sierra_v4(self, device: TuyaBLEDevice, data: bytes) -> None:
        """Parse Sierra FD50 reports: header + DP + type + length + value."""
        if len(data) < 11 or data[5] != 0x80:
            return
        dp_id = data[7]
        dp_type = data[8]
        data_len = int.from_bytes(data[9:11], "big")
        if data_len < 1 or 11 + data_len > len(data):
            return
        try:
            type_enum = TuyaBLEDataPointType(dp_type)
        except ValueError:
            return
        raw = data[11 : 11 + data_len]
        value = _decode_scalar(raw, dp_type)
        self._state[dp_id] = (dp_type, value)
        device._datapoints._update_from_device(  # noqa: SLF001
            dp_id, asyncio.get_running_loop().time(), 0, type_enum, value
        )
        device._fire_callbacks([device._datapoints[dp_id]])  # noqa: SLF001

    async def _prepare_device(self) -> TuyaBLEDevice:
        if self.device is None:
            raise UpdateFailed("The BLE device is not initialized")
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if ble_device is None:
            raise UpdateFailed("The Dimplex Sierra is not advertising")
        self.device._ble_device = ble_device  # noqa: SLF001
        self.device._expected_disconnect = False  # noqa: SLF001
        return self.device

    async def _disconnect(self) -> None:
        if self.device is None:
            return
        try:
            await self.device._execute_disconnect()  # noqa: SLF001
        finally:
            self.device._expected_disconnect = False  # noqa: SLF001

    async def _read_locked(self) -> DPState:
        device = await self._prepare_device()
        self._state = {}
        try:
            async with asyncio.timeout(50):
                await device.update()
                await asyncio.sleep(1)
        except TimeoutError as exc:
            raise UpdateFailed("Timed out reading the Dimplex Sierra") from exc
        except Exception as exc:
            raise UpdateFailed("Unable to read the Dimplex Sierra over BLE") from exc
        if not self._state:
            raise UpdateFailed("The Dimplex Sierra returned no datapoints")
        return dict(self._state)

    async def _async_update_data(self) -> DPState:
        async with self._operation_lock:
            try:
                return await self._read_locked()
            finally:
                await self._disconnect()

    async def async_write_dp(
        self,
        dp_id: int,
        dp_type: int,
        value: Any,
        *,
        verification_retries: int = 0,
        verification_delay: float = 0.0,
    ) -> None:
        """Write one scalar V4 datapoint and verify it by reading it back."""
        async with self._operation_lock:
            device = await self._prepare_device()
            raw = _encode_scalar(dp_type, value)
            payload = (
                b"\x00\x00\x00\x00\x01"
                + bytes([dp_id, dp_type])
                + len(raw).to_bytes(2, "big")
                + raw
            )
            try:
                async with asyncio.timeout(50):
                    await device._send_packet(  # noqa: SLF001
                        TuyaBLECode.FUN_SENDER_DPS_V4, payload, True
                    )
                    await asyncio.sleep(0.5)
                state = await self._read_locked()
                for _ in range(verification_retries):
                    if state.get(dp_id) == (dp_type, value):
                        break
                    if verification_delay > 0:
                        await asyncio.sleep(verification_delay)
                    state = await self._read_locked()
            except (TimeoutError, UpdateFailed) as exc:
                raise HomeAssistantError("BLE command could not be verified") from exc
            except Exception as exc:
                raise HomeAssistantError("BLE command failed") from exc
            finally:
                await self._disconnect()
            if state.get(dp_id) != (dp_type, value):
                raise HomeAssistantError(
                    "The fireplace rejected the requested setting; its previous "
                    "state was preserved"
                )
            self.async_set_updated_data(state)

    async def async_close(self) -> None:
        async with self._operation_lock:
            await self._disconnect()
