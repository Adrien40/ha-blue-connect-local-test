"""Config flow and options flow (with Home Assistant); validation in test_config_flow.py."""

from __future__ import annotations

from time import monotonic
from unittest.mock import AsyncMock, patch

import pytest
import voluptuous as vol
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import (
    SOURCE_BLUETOOTH,
    SOURCE_REAUTH,
    SOURCE_RECONFIGURE,
    SOURCE_USER,
)
from homeassistant.data_entry_flow import FlowResultType

from custom_components.blue_connect_local.const import (
    CONF_ACCESS_CODE,
    CONF_CHLORINE_MODEL,
    CONF_CYA,
    CONF_IGNORE_ECHOES,
    CONF_MAC_ADDRESS,
    CONF_ORP_CALIB,
    CONF_ORP_MAX,
    CONF_ORP_MIN,
    CONF_ORP_REF,
    CONF_PASSIVE_MEASURES,
    CONF_PH_CALIB_4,
    CONF_PH_CALIB_7,
    CONF_PH_MAX,
    CONF_PH_MIN,
    CONF_PH_REF_4,
    CONF_PH_REF_7,
    CONF_REFERENCE_TIME,
    CONF_SCAN_INTERVAL,
    CONF_TEMP_MAX,
    CONF_TEMP_MIN,
    CONF_TEMP_OFFSET,
    DOMAIN,
)

from .conftest import make_entry
from .helpers import ACCESS_CODE, MAC, build_frame

DISCOVERED = (
    "custom_components.blue_connect_local.config_flow.async_discovered_service_info"
)
SETUP = "custom_components.blue_connect_local.async_setup_entry"


def _info(
    frame: bytes | None = None, name: str = "BC3-1234"
) -> BluetoothServiceInfoBleak:
    manufacturer = {0x1234: frame} if frame else {}
    return BluetoothServiceInfoBleak(
        name=name,
        address=MAC,
        rssi=-60,
        manufacturer_data=manufacturer,
        service_data={},
        service_uuids=[],
        source="local",
        device=BLEDevice(MAC, name, {}),
        advertisement=AdvertisementData(
            local_name=name,
            manufacturer_data=manufacturer,
            service_data={},
            service_uuids=[],
            rssi=-60,
            tx_power=None,
            platform_data=(),
        ),
        connectable=True,
        time=monotonic(),
        tx_power=None,
    )


def _sections(**over) -> dict:
    return {
        "general": {
            CONF_CHLORINE_MODEL: "chlorine",
            CONF_CYA: 40,
            **over.pop("general", {}),
        },
        "synchronization": {
            CONF_SCAN_INTERVAL: 60,
            CONF_REFERENCE_TIME: "08:00:00",
            CONF_PASSIVE_MEASURES: True,
            CONF_IGNORE_ECHOES: True,
            **over.pop("synchronization", {}),
        },
        "probes_calibration": {
            CONF_PH_CALIB_7: 7.0,
            CONF_PH_REF_7: 7.0,
            CONF_PH_CALIB_4: 4.0,
            CONF_PH_REF_4: 4.0,
            CONF_ORP_CALIB: 650,
            CONF_ORP_REF: 650,
            CONF_TEMP_OFFSET: 0.0,
            **over.pop("probes_calibration", {}),
        },
        **over,
    }


def _default_of(result, field: str):
    for key in result["data_schema"].schema:
        if key == field:
            return key.default()
    raise AssertionError(f"{field} not in schema")


async def _start_discovery(hass, frame=None):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=_info(frame)
    )


# ---------------------------------------------------------------------------
# Flux de configuration
# ---------------------------------------------------------------------------
async def test_discovery_creates_entry_with_access_code(hass):
    frame = build_frame(conductivity=1200)
    with (
        patch(DISCOVERED, return_value=[_info(frame)]),
        patch(SETUP, return_value=True),
    ):
        result = await _start_discovery(hass, frame)
        assert result["type"] is FlowResultType.FORM
        assert result["step_id"] == "user"
        selection = _default_of(result, CONF_MAC_ADDRESS)
        assert MAC in selection and "Gold" in selection

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_MAC_ADDRESS: selection, CONF_ACCESS_CODE: ACCESS_CODE, **_sections()},
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_MAC_ADDRESS: MAC,
        CONF_ACCESS_CODE: ACCESS_CODE,
        "has_conductivity": True,
    }
    assert result["result"].unique_id == MAC
    assert result["options"][CONF_CYA] == 40
    assert result["options"][CONF_CHLORINE_MODEL] == "chlorine"
    assert "general" not in result["options"]  # sections aplaties


async def test_discovery_of_a_silver_is_remembered(hass):
    frame = build_frame(conductivity=None)
    with (
        patch(DISCOVERED, return_value=[_info(frame)]),
        patch(SETUP, return_value=True),
    ):
        result = await _start_discovery(hass, frame)
        selection = _default_of(result, CONF_MAC_ADDRESS)
        assert "Silver" in selection
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_MAC_ADDRESS: selection, **_sections()}
        )
    assert result["data"]["has_conductivity"] is False
    assert result["data"][CONF_ACCESS_CODE] == ""  # mode passif uniquement
    assert "Silver" in result["title"]


async def test_already_configured_device_aborts(hass):
    make_entry().add_to_hass(hass)
    result = await _start_discovery(hass, build_frame())
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize("code", ["short", "TOOLONG1234", "ABCDEFGH!", "ÉÉÉÉÉÉÉÉÉ"])
async def test_invalid_access_code_is_rejected(hass, code):
    with patch(DISCOVERED, return_value=[_info()]), patch(SETUP, return_value=True):
        result = await _start_discovery(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MAC_ADDRESS: _default_of(result, CONF_MAC_ADDRESS),
                CONF_ACCESS_CODE: code,
                **_sections(),
            },
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_ACCESS_CODE: "invalid_access_code"}


async def test_invalid_calibration_shows_error(hass):
    with patch(DISCOVERED, return_value=[_info()]), patch(SETUP, return_value=True):
        result = await _start_discovery(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MAC_ADDRESS: _default_of(result, CONF_MAC_ADDRESS),
                **_sections(
                    probes_calibration={CONF_PH_CALIB_4: 7.5, CONF_PH_CALIB_7: 4.5}
                ),
            },
        )
    assert result["errors"] == {CONF_PH_CALIB_7: "ph_slope_mismatch"}


async def test_manual_mac_entry(hass):
    with patch(DISCOVERED, return_value=[]), patch(SETUP, return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        bad = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"manual_mac_address": "not-a-mac", **_sections()}
        )
        assert bad["errors"] == {"manual_mac_address": "invalid_mac"}

        good = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"manual_mac_address": MAC.lower(), **_sections()}
        )
    assert good["type"] is FlowResultType.CREATE_ENTRY
    assert good["data"][CONF_MAC_ADDRESS] == MAC


async def test_no_mac_provided(hass):
    with patch(DISCOVERED, return_value=[]), patch(SETUP, return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], _sections()
        )
    assert result["errors"] == {"base": "no_mac_provided"}


async def test_conflicting_dropdown_and_manual_mac(hass):
    with patch(DISCOVERED, return_value=[_info()]), patch(SETUP, return_value=True):
        result = await _start_discovery(hass)
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_MAC_ADDRESS: _default_of(result, CONF_MAC_ADDRESS),
                "manual_mac_address": "11:22:33:44:55:66",
                **_sections(),
            },
        )
    assert result["errors"] == {"base": "mac_conflict"}


async def test_manual_mac_already_configured_aborts(hass):
    make_entry().add_to_hass(hass)
    with patch(DISCOVERED, return_value=[]), patch(SETUP, return_value=True):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {"manual_mac_address": MAC, **_sections()}
        )
    assert result["type"] is FlowResultType.ABORT


# ---------------------------------------------------------------------------
# Flux d'options
# ---------------------------------------------------------------------------
def _options_input(access_code=ACCESS_CODE, **over) -> dict:
    thresholds = {
        CONF_PH_MIN: 6.9,
        CONF_PH_MAX: 7.4,
        CONF_ORP_MIN: 650,
        CONF_ORP_MAX: 750,
        CONF_TEMP_MIN: 6.0,
        CONF_TEMP_MAX: 32.0,
    }
    thresholds.update(over.pop("alert_thresholds", {}))
    sections = _sections(**over)
    # In the options form, the access code lives in the "general" section.
    sections["general"] = {CONF_ACCESS_CODE: access_code, **sections["general"]}
    return {**sections, "alert_thresholds": thresholds}


async def test_options_form_prefills_current_values(hass, entry, coordinator):
    coordinator.update_local_state({CONF_CYA: 55, CONF_CHLORINE_MODEL: "bromine"})
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    general = result["data_schema"].schema["general"].schema.schema
    defaults = {str(k): k.default() for k in general if str(k) != CONF_ACCESS_CODE}
    assert defaults[CONF_CYA] == 55
    assert defaults[CONF_CHLORINE_MODEL] == "bromine"


async def test_options_saved_and_pushed_to_coordinator(hass, entry, coordinator):
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        _options_input(
            general={CONF_CYA: 70, CONF_CHLORINE_MODEL: "bromine"},
            probes_calibration={CONF_TEMP_OFFSET: 1.5},
            alert_thresholds={CONF_PH_MAX: 7.8},
        ),
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[CONF_CYA] == 70
    assert entry.options[CONF_CHLORINE_MODEL] == "bromine"
    assert coordinator.data[CONF_CYA] == 70
    assert coordinator.data[CONF_PH_MAX] == 7.8
    assert coordinator.data[CONF_TEMP_OFFSET] == 1.5


async def test_changing_access_code_triggers_analysis(hass, entry, coordinator):
    coordinator._force_one_shot = False
    coordinator.async_request_refresh = AsyncMock()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], _options_input(access_code="ZZ99YY88X")
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done(wait_background_tasks=True)
    assert coordinator._force_one_shot is True
    coordinator.async_request_refresh.assert_awaited()


async def test_unchanged_access_code_does_not_trigger_analysis(
    hass, entry, coordinator
):
    coordinator._force_one_shot = False
    coordinator.async_request_refresh = AsyncMock()
    result = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(
        result["flow_id"], _options_input()
    )
    await hass.async_block_till_done(wait_background_tasks=True)
    assert coordinator._force_one_shot is False
    coordinator.async_request_refresh.assert_not_awaited()


async def test_options_reject_invalid_access_code(hass, entry, coordinator):
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], _options_input(access_code="bad")
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_ACCESS_CODE: "invalid_access_code"}


@pytest.mark.parametrize(
    ("over", "field", "code"),
    [
        (
            {"alert_thresholds": {CONF_PH_MIN: 7.6, CONF_PH_MAX: 7.0}},
            CONF_PH_MIN,
            "ph_threshold_error",
        ),
        (
            {"alert_thresholds": {CONF_TEMP_MIN: 40, CONF_TEMP_MAX: 10}},
            CONF_TEMP_MIN,
            "temp_threshold_error",
        ),
        (
            {"alert_thresholds": {CONF_ORP_MIN: 900, CONF_ORP_MAX: 700}},
            CONF_ORP_MIN,
            "orp_threshold_error",
        ),
        (
            {"probes_calibration": {CONF_PH_CALIB_4: 7.5, CONF_PH_CALIB_7: 4.5}},
            CONF_PH_CALIB_7,
            "ph_slope_mismatch",
        ),
    ],
)
async def test_options_validation_errors(hass, entry, coordinator, over, field, code):
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], _options_input(**over)
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {field: code}


# ---------------------------------------------------------------------------
# Reauthentication
# ---------------------------------------------------------------------------
async def test_invalid_access_code_starts_reauth(hass, entry, coordinator):
    entry.async_start_reauth(hass)
    await hass.async_block_till_done()

    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    reauth_flows = [f for f in flows if f["context"]["source"] == SOURCE_REAUTH]
    assert len(reauth_flows) == 1
    assert reauth_flows[0]["context"]["entry_id"] == entry.entry_id


async def test_reauth_confirm_updates_access_code(hass, entry, coordinator):
    entry.async_start_reauth(hass)
    await hass.async_block_till_done()

    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    reauth_flow_id = flows[0]["flow_id"]

    result = await hass.config_entries.flow.async_configure(
        reauth_flow_id, {CONF_ACCESS_CODE: "NEWCODE99"}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert entry.data[CONF_ACCESS_CODE] == "NEWCODE99"


# ---------------------------------------------------------------------------
# Flux de reconfiguration (changement d'appareil physique / code d'accès)
# ---------------------------------------------------------------------------
NEW_MAC = "11:22:33:44:55:66"


async def _start_reconfigure(hass, entry):
    return await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )


async def test_reconfigure_form_prefills_current_values(hass, entry, coordinator):
    result = await _start_reconfigure(hass, entry)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    schema_defaults = {
        field.schema: field.default()
        for field in result["data_schema"].schema
        if field.default is not vol.UNDEFINED
    }
    assert schema_defaults[CONF_MAC_ADDRESS] == MAC
    assert schema_defaults[CONF_ACCESS_CODE] == ACCESS_CODE


async def test_reconfigure_updates_mac_and_access_code(hass, entry, coordinator):
    result = await _start_reconfigure(hass, entry)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_MAC_ADDRESS: NEW_MAC, CONF_ACCESS_CODE: "NEWCODE99"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_MAC_ADDRESS] == NEW_MAC
    assert entry.data[CONF_ACCESS_CODE] == "NEWCODE99"
    assert entry.unique_id == NEW_MAC


async def test_reconfigure_rejects_invalid_mac(hass, entry, coordinator):
    result = await _start_reconfigure(hass, entry)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_MAC_ADDRESS: "not-a-mac", CONF_ACCESS_CODE: ACCESS_CODE},
    )
    assert result["errors"] == {CONF_MAC_ADDRESS: "invalid_mac"}
    # The original entry must be untouched.
    assert entry.data[CONF_MAC_ADDRESS] == MAC


async def test_reconfigure_rejects_invalid_access_code(hass, entry, coordinator):
    result = await _start_reconfigure(hass, entry)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_MAC_ADDRESS: MAC, CONF_ACCESS_CODE: "short"},
    )
    assert result["errors"] == {CONF_ACCESS_CODE: "invalid_access_code"}


async def test_reconfigure_can_keep_the_same_mac(hass, entry, coordinator):
    """Just correcting the access code, without changing the device."""
    result = await _start_reconfigure(hass, entry)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_MAC_ADDRESS: MAC, CONF_ACCESS_CODE: "NEWCODE99"},
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_ACCESS_CODE] == "NEWCODE99"


async def test_reconfigure_aborts_if_mac_used_by_another_entry(
    hass, entry, coordinator
):
    other_mac = "AA:AA:AA:AA:AA:AA"
    other_entry = make_entry()
    other_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(other_entry, unique_id=other_mac)

    result = await _start_reconfigure(hass, entry)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_MAC_ADDRESS: other_mac, CONF_ACCESS_CODE: ACCESS_CODE},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    # The original entry must be untouched.
    assert entry.data[CONF_MAC_ADDRESS] == MAC
