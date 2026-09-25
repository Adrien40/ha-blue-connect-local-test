"""Fixtures communes : Bluetooth simulé, entrée de configuration, coordinateur."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from dataclasses import dataclass, field
from time import monotonic
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from bleak.backends.device import BLEDevice
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.blue_connect_local.const import (
    CONF_ACCESS_CODE,
    CONF_MAC_ADDRESS,
    DOMAIN,
)
from custom_components.blue_connect_local.coordinator import BlueConnectCoordinator

from .helpers import ACCESS_CODE, MAC, FakeBlueClient, build_frame

pytest_plugins = "pytest_homeassistant_custom_component"

PKG = "custom_components.blue_connect_local"


@pytest.fixture(autouse=True)
def _enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Autorise HA à charger custom_components/ pendant les tests."""


@dataclass
class BleEnv:
    """État pilotable du Bluetooth simulé."""

    client: FakeBlueClient = field(default_factory=FakeBlueClient)
    scanner_count: int = 1
    last_seen_age: float | None = 0.0  # None = jamais vu
    device_present: bool = True
    rssi: int = -60
    establish: AsyncMock = field(default_factory=AsyncMock)

    def device(self) -> BLEDevice | None:
        return BLEDevice(MAC, "BC3 test", {}) if self.device_present else None

    def service_info(self) -> SimpleNamespace | None:
        if self.last_seen_age is None:
            return None
        return SimpleNamespace(time=monotonic() - self.last_seen_age, rssi=self.rssi)


@pytest.fixture
def ble(monkeypatch: pytest.MonkeyPatch) -> Generator[BleEnv]:
    """Bluetooth simulé : un client qui renvoie une trame valide par déclenchement."""
    env = BleEnv(client=FakeBlueClient(frames=[build_frame()]))

    async def _establish(*_args, **_kwargs):
        return env.client

    env.establish.side_effect = _establish

    with (
        patch(
            f"{PKG}.coordinator.async_ble_device_from_address",
            lambda *a, **k: env.device(),
        ),
        patch(
            f"{PKG}.coordinator.async_last_service_info",
            lambda *a, **k: env.service_info(),
        ),
        patch(
            f"{PKG}.coordinator.async_scanner_count", lambda *a, **k: env.scanner_count
        ),
        patch(
            f"{PKG}.sensor.async_last_service_info", lambda *a, **k: env.service_info()
        ),
        patch(f"{PKG}.coordinator.establish_connection", env.establish),
    ):
        # Cycles courts : les tests n'attendent jamais 60 s pour de vrai.
        for name, value in (
            ("TIMEOUT_NOTIFICATION_WAIT", 0.2),
            ("TIMEOUT_GATT_OP", 0.5),
            ("AUTH_SETTLE_DELAY", 0.0),
            ("AUTH_STATUS_RETRY_DELAY", 0.0),
            ("GATT_WRITE_RETRY_DELAY", 0.0),
        ):
            monkeypatch.setattr(f"{PKG}.coordinator.{name}", value)
        yield env


def make_entry(
    *,
    access_code: str | None = ACCESS_CODE,
    version: int = 1,
    minor_version: int = 4,
    **options,
) -> MockConfigEntry:
    """Entrée Blue Connect (version 1.4). Sans `access_code` : mode passif seul."""
    data = {CONF_MAC_ADDRESS: MAC}
    if access_code:
        data[CONF_ACCESS_CODE] = access_code
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=MAC,
        title="Blue Connect",
        version=version,
        minor_version=minor_version,
        data=data,
        options=options,
    )


@pytest.fixture
def entry() -> MockConfigEntry:
    return make_entry()


@pytest.fixture
async def setup_integration(
    hass: HomeAssistant, enable_bluetooth: None, ble: BleEnv
) -> AsyncGenerator[Callable[..., Awaitable[BlueConnectCoordinator]]]:
    """Installe l'entrée et décharge à la fin (annule aussi les minuteries)."""
    entries: list[MockConfigEntry] = []

    async def _setup(config_entry: MockConfigEntry) -> BlueConnectCoordinator:
        config_entry.add_to_hass(hass)
        entries.append(config_entry)
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done(wait_background_tasks=True)
        return hass.data[DOMAIN][config_entry.entry_id]

    yield _setup

    for config_entry in entries:
        if config_entry.state is ConfigEntryState.LOADED:
            await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()


@pytest.fixture
async def coordinator(entry, setup_integration) -> BlueConnectCoordinator:
    """Coordinateur installé avec un code d'accès, sans 1re analyse automatique."""
    return await setup_integration(entry)


def entity_id(hass: HomeAssistant, domain: str, key: str) -> str:
    """entity_id d'une entité, retrouvée par son unique_id."""
    found = er.async_get(hass).async_get_entity_id(domain, DOMAIN, f"{MAC}_{key}")
    assert found is not None, f"no {domain} entity with unique_id {MAC}_{key}"
    return found
