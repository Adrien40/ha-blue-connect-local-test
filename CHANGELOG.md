# Changelog

## Unreleased

- Integration Quality Scale: Platinum declared (`quality_scale.yaml`,
  `manifest.json`). The last open rule, `test-coverage`, is met: every module
  is covered at 100% (lines and branches) and the Tests workflow now fails
  below 95%.
- 178 new tests: BLE connection cycle (scripted fake client), config writes,
  "new shower" reboot, background loop, sensors, button, number, switch and
  the config entry lifecycle.
- `quality_scale.yaml` is now also checked against the CI coverage threshold
  and the `mypy --strict` step.

## 1.1.0

- New sensors: cold water shower duration and time to comfort temperature.
- Durations are now computed in seconds from the device's 1/50 s counter, with
  correct handling of the 16-bit counter wrap-around.
- Every entity now shares a common base class (`HydraoEntity`).
- Config and options flows: a description for each field.
- Integration Quality Scale: Bronze declared (`quality_scale.yaml`).
- Translations completed in all languages.
- Requires Home Assistant 2026.5.0 or newer.
