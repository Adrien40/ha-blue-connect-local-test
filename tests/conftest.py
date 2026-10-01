# Copyright (c) 2026 Adrien40
# SPDX-License-Identifier: GPL-3.0-only

"""Shared pytest fixtures for the Hydrao Custom integration test suite."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Make `custom_components.hydrao_custom` importable without installing it.
sys.path.insert(0, str(Path(__file__).parent.parent))

# ---------------------------------------------------------------------------

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading custom_components/ for every test automatically."""
    yield


@pytest.fixture
def mock_entry():
    """A minimal MockConfigEntry standing in for the Hydrao config entry."""
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    entry = MockConfigEntry(
        domain="hydrao_custom",
        data={
            "address": "AA:BB:CC:DD:EE:FF",
            "name": "Hydrao EEFF",
            "has_connected_once": True,
        },
        options={"min_temp_threshold": 33.0},
    )
    return entry


@pytest.fixture
async def coordinator(hass, mock_entry):
    """A HydraoDataUpdateCoordinator wired to a mock config entry, without
    starting the real BLE loop or bluetooth listener."""
    from custom_components.hydrao_custom.coordinator import (
        HydraoDataUpdateCoordinator,
    )

    mock_entry.add_to_hass(hass)
    coord = HydraoDataUpdateCoordinator(hass, mock_entry)
    mock_entry.runtime_data = coord
    return coord


@pytest.fixture
def bluetooth_loaded(hass):
    """Declare the `bluetooth` dependency as already set up.

    The real component needs system Bluetooth (and USB) support that a test
    environment doesn't have; config and options flows only need Home
    Assistant to consider the dependency loaded."""
    hass.config.components.add("bluetooth")


@pytest.fixture
def mock_setup_entry():
    """Replace the integration's setup, so finishing a config flow doesn't
    start the Bluetooth listener and the BLE loop."""
    with patch(
        "custom_components.hydrao_custom.async_setup_entry", return_value=True
    ) as mock:
        yield mock
