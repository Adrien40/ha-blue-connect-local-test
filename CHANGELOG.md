# Changelog

## 1.2.1

### Fixed
- `compute_ph_calibrated` silently returned the raw pH (or `ref_7`) on a
  degenerate calibration (measured points too close together) instead of
  signaling it. It now raises, and the coordinator falls back to the raw pH
  with a logged warning, matching the "Degenerate pH calibration" handling
  already used by Flipr Local.
- A notification dropped because the queue was full (`maxsize=4`) was
  silently ignored. It is now logged at debug level.
- BLE signal lost/found events were not logged (Flipr Local already logged
  them). Added matching debug logs, including the distinction between a
  fresh signal loss and recovery from a stale `out_of_range` status.
- The "New analysis" button only caught `HomeAssistantError` and
  `RuntimeError` around the background refresh, unlike Flipr Local which
  catches any exception. Widened to `Exception` so an unexpected error type
  still gets a clean logged message instead of an unhandled background-task
  traceback.
- When the Bluetooth signal was unavailable, the coordinator skipped the
  connection attempt silently. Now logs a debug message, matching Flipr Local.
- The device lookup only tried `connectable=True` before giving up. It now
  falls back to `connectable=False` first, matching Flipr Local: a device
  seen only by a scanner that cannot connect to it directly is no longer
  treated as missing.

## 1.2.0

### Requirements (breaking)
- **Home Assistant 2026.3.0 or newer** (`hacs.json`), i.e. the first release shipped with
  Python 3.14. The test suite passes on 2026.3.0 and 2026.9.3.

### Added
- **Raw ORP** diagnostic sensor (mV), next to the existing raw pH: the probe value *before* any
  offset, to calibrate on a reference solution.

### Note on chlorine
- The integration deliberately has **no chlorine estimate**: ORP is an oxidising strength, not a
  concentration (it changes with pH, temperature, stabilizer, other oxidisers and probe ageing), and
  a wrong but precise-looking chlorine value is worse than none. The **CyA** entity and the
  **treatment type** (chlorine/bromine) are kept, but no calculated value depends on them at the moment.

### Fixed
- Invalid BLE frames retried forever: `retry_count` was reset before the frame was decoded, so the
  retry budget never ran out and the "unreachable after retries" state was never reached.
- `async_shutdown` did not call the parent implementation (scheduled refresh and debouncer were
  left running after unload) and was not idempotent: with `config_entry` passed to the coordinator
  Home Assistant now calls it on unload too, which would have cancelled the Bluetooth callbacks twice.
- The first analysis timer (2 s after startup) was never cancelled when the entry was unloaded.
- `device_registry.async_get_device` is deprecated on recent Home Assistant (2026.9) while its
  replacement does not exist yet on 2026.3.0: a compatibility helper now works on both.
- `validate_calibration` raised on a non-numeric ORP / offset / CyA / scan interval value.

### Hardened
- A computed pH outside 0-14 becomes *unknown* instead of being displayed.
- Langelier index and equilibrium pH reject NaN/inf inputs.

### Internal
- Coordinator receives its `config_entry` explicitly; BLE pauses are named constants.
- Test suite grown from 40 to ~300 tests: simulated Bluetooth (authentication, notifications,
  passive advertisements, echoes, Silver/Gold), coordinator, config/options flow, migration chain
  1.1 → 1.4, entities, translations consistency, property-based tests.
- CI: pytest + coverage workflow (Python 3.14, same GitHub Actions versions as the other workflows);
  explicit ruff / pytest configuration in `pyproject.toml`; `requirements_test.txt`.
- Code style (ruff): `asyncio.TimeoutError` → `TimeoutError` and Python 3.14 syntax `except A, B:` in
  `button.py`, `time.py` and `coordinator.py`.
- Version bumped to 1.2.0.

### Documentation
- `README.md` / `README.fr.md`: minimum Home Assistant version, raw ORP, why there is no chlorine
  sensor, development section.
