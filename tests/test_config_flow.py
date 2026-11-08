"""Regression tests for consent, independent credentials and migration reauth."""

from unittest.mock import patch

import pytest
from homeassistant.config_entries import (
    SOURCE_BLUETOOTH,
    SOURCE_REAUTH,
    SOURCE_RECONFIGURE,
    SOURCE_USER,
)
from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.dimplex_sierra_ble.const import (
    CONF_LOCAL_KEY,
    CONF_PRODUCT_ID,
    DOMAIN,
)

from .conftest import ADDRESS


@pytest.fixture(autouse=True)
def mock_setup_entry():
    """Entry creation must not connect to hardware in config flow tests."""
    with patch(
        "custom_components.dimplex_sierra_ble.async_setup_entry", return_value=True
    ):
        yield


async def test_bluetooth_requires_confirmation_and_credentials(
    hass, advertisement, credentials
):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=advertisement
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "bluetooth_confirm"
    flow = hass.config_entries.flow.async_get(result["flow_id"])
    assert flow["context"]["confirm_only"] is True
    assert not hass.config_entries.async_entries(DOMAIN)

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "credentials"
    flow = hass.config_entries.flow.async_get(result["flow_id"])
    assert not flow["context"].get("confirm_only")
    assert not hass.config_entries.async_entries(DOMAIN)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], credentials
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {CONF_ADDRESS: ADDRESS, **credentials}
    assert result["result"].unique_id == ADDRESS
    assert result["result"].version == 2


async def test_unrelated_tuya_cannot_be_auto_added(hass, advertisement, credentials):
    """An otherwise identical Tuya advert needs consent and a supported product."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=advertisement
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**credentials, CONF_PRODUCT_ID: "another_product"}
    )
    assert result["step_id"] == "credentials"
    assert result["errors"] == {"base": "not_supported"}
    assert not hass.config_entries.async_entries(DOMAIN)


@pytest.mark.parametrize("field", ["name", "service_uuids", "manufacturer_data"])
async def test_nonmatching_advertisement(hass, advertisement, field):
    replacements = {"name": "Other", "service_uuids": [], "manufacturer_data": {}}
    setattr(advertisement, field, replacements[field])
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=advertisement
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "not_sierra"


async def test_duplicate_advertisement(hass, advertisement, credentials):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id=ADDRESS,
        version=2,
        data={CONF_ADDRESS: ADDRESS, **credentials},
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=advertisement
    )
    assert result["reason"] == "already_configured"


async def test_manual_selection_then_own_credentials(hass, advertisement, credentials):
    with patch(
        "custom_components.dimplex_sierra_ble.config_flow.bluetooth.async_discovered_service_info",
        return_value=[advertisement],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        assert result["step_id"] == "user"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_ADDRESS: ADDRESS}
        )
        assert result["step_id"] == "credentials"
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], credentials
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_invalid_credentials_not_echoed(hass, advertisement, credentials):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=advertisement
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**credentials, CONF_LOCAL_KEY: "too_short"}
    )
    assert result["errors"] == {"base": "invalid_credentials"}
    assert credentials[CONF_LOCAL_KEY] not in str(result)
    assert "too_short" not in str(result)


async def test_no_candidates(hass):
    with patch(
        "custom_components.dimplex_sierra_ble.config_flow.bluetooth.async_discovered_service_info",
        return_value=[],
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
    assert result["reason"] == "not_found"


@pytest.mark.parametrize(
    ("source", "step_id", "reason"),
    [
        (SOURCE_REAUTH, "reauth_confirm", "reauth_successful"),
        (SOURCE_RECONFIGURE, "reconfigure", "reconfigure_successful"),
    ],
)
async def test_credential_update_preserves_entry(
    hass, credentials, source, step_id, reason
):
    entry = MockConfigEntry(
        domain=DOMAIN, unique_id=ADDRESS, version=2, data={CONF_ADDRESS: ADDRESS}
    )
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": source, "entry_id": entry.entry_id},
        data=entry.data if source == SOURCE_REAUTH else None,
    )
    assert result["step_id"] == step_id
    with patch.object(hass.config_entries, "async_reload", return_value=True):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], credentials
        )
        await hass.async_block_till_done()
    assert result["reason"] == reason
    assert hass.config_entries.async_entries(DOMAIN) == [entry]
    assert entry.unique_id == ADDRESS
    assert entry.data == {CONF_ADDRESS: ADDRESS, **credentials}
