"""Validate credentials explicitly supplied to this integration by its user."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PRODUCT_ID,
    CONF_UUID,
    CREDENTIAL_FIELDS,
    MODEL,
    PRODUCT_CATEGORY,
    PRODUCT_ID,
    PRODUCT_NAME,
)
from .tuya_ble import TuyaBLEDeviceCredentials


class InvalidCredentials(ValueError):
    """A credential form error, without including submitted values."""

    def __init__(self, error_key: str = "invalid_credentials") -> None:
        self.error_key = error_key
        super().__init__(error_key)


def credentials_from_data(data: Mapping[str, Any]) -> TuyaBLEDeviceCredentials:
    """Build transport credentials from our own entry only, never another client.

    The V4 pairing payload contains UUID + six local-key bytes + device ID,
    padded to 44 bytes. Validation here is structural, not BLE authentication.
    """
    if any(
        not isinstance(value := data.get(field), str)
        or not value
        or not value.isascii()
        or not value.isprintable()
        or any(character.isspace() for character in value)
        for field in CREDENTIAL_FIELDS
    ):
        raise InvalidCredentials
    if data[CONF_PRODUCT_ID] != PRODUCT_ID:
        raise InvalidCredentials("not_supported")
    if (
        len(data[CONF_LOCAL_KEY]) != 16
        or len(data[CONF_UUID]) + 6 + len(data[CONF_DEVICE_ID]) > 44
    ):
        raise InvalidCredentials
    return TuyaBLEDeviceCredentials(
        uuid=data[CONF_UUID],
        local_key=data[CONF_LOCAL_KEY],
        device_id=data[CONF_DEVICE_ID],
        category=PRODUCT_CATEGORY,
        product_id=PRODUCT_ID,
        device_name=PRODUCT_NAME,
        product_model=MODEL,
        product_name=PRODUCT_NAME,
    )
