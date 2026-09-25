"""diagnostics.py: presence of expected data, MAC address and access code redacted."""

from __future__ import annotations

from custom_components.blue_connect_local.diagnostics import (
    async_get_config_entry_diagnostics,
)

from .helpers import ACCESS_CODE, MAC


async def test_diagnostics_redacts_sensitive_data(hass, coordinator, entry):
    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["entry"]["data"]["mac_address"] == "**REDACTED**"
    assert MAC not in str(result)
    assert ACCESS_CODE not in str(result)


async def test_diagnostics_includes_coordinator_state(hass, coordinator, entry):
    await coordinator.async_refresh()
    result = await async_get_config_entry_diagnostics(hass, entry)

    assert result["coordinator"]["last_update_success"] is True
    assert "ph" in result["coordinator"]["data"]
    assert result["entry"]["version"] == entry.version
