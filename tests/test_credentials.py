"""Pure validation tests use only synthetic credential material."""

import pytest

from custom_components.dimplex_sierra_ble.const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_PRODUCT_ID,
    CONF_UUID,
)
from custom_components.dimplex_sierra_ble.credentials import (
    InvalidCredentials,
    credentials_from_data,
)


@pytest.mark.parametrize(
    "field", [CONF_DEVICE_ID, CONF_LOCAL_KEY, CONF_UUID, CONF_PRODUCT_ID]
)
def test_missing_field(credentials, field):
    credentials.pop(field)
    with pytest.raises(InvalidCredentials):
        credentials_from_data(credentials)


@pytest.mark.parametrize("value", ["", "short", "k" * 17, "\u00e9" * 16, None])
def test_invalid_key(credentials, value):
    credentials[CONF_LOCAL_KEY] = value
    with pytest.raises(InvalidCredentials) as exc:
        credentials_from_data(credentials)
    assert exc.value.error_key == "invalid_credentials"
    assert str(exc.value) == "invalid_credentials"


def test_unsupported_product(credentials):
    credentials[CONF_PRODUCT_ID] = "not_a_sierra"
    with pytest.raises(InvalidCredentials) as exc:
        credentials_from_data(credentials)
    assert exc.value.error_key == "not_supported"


def test_pairing_payload_limit(credentials):
    credentials[CONF_DEVICE_ID] = "d" * 22
    result = credentials_from_data(credentials)
    assert result.device_id == "d" * 22
    credentials[CONF_DEVICE_ID] = "d" * 23
    with pytest.raises(InvalidCredentials):
        credentials_from_data(credentials)


def test_valid_data(credentials):
    result = credentials_from_data(credentials)
    assert result.local_key == credentials[CONF_LOCAL_KEY]
    assert result.category == "qn"
