# Changelog

## 1.1.0

- New sensors: cold water shower duration and time to comfort temperature.
- Durations are now computed in seconds from the device's 1/50 s counter, with
  correct handling of the 16-bit counter wrap-around.
- Every entity now shares a common base class (`HydraoEntity`).
- Config and options flows: a description for each field.
- Integration Quality Scale: Bronze declared (`quality_scale.yaml`).
- Translations completed in all languages.
- Requires Home Assistant 2026.5.0 or newer.
