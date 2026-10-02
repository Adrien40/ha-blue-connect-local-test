# Hydrao Custom - Changelog

## 1.1.0

🐬🐬🐬🐬🐬🐬🐬🐬🐬🐬

This release is about accuracy and reliability: shower durations and the cold / comfort split are now correct, two new diagnostic sensors show how long the water stayed cold, and the integration is fully tested and strictly typed.

### 🚨 Breaking changes
- **Home Assistant 2026.5.0 or newer** (`hacs.json`, was 2025.1.0): the integration now relies on a Bluetooth helper first shipped in that release. Update Home Assistant before updating the integration.

### ✨ New features
- **Cold Water Shower Duration** sensor: time spent below the comfort temperature during the current shower. Diagnostic, disabled by default.
- **Time to Comfort Temperature** sensor: how long the water took to reach the comfort temperature. It stays *unknown* when the water was already warm at connection, because the cold phase cannot be measured then. Diagnostic, disabled by default.
- **Diagnostics download** (*Download diagnostics* on the device page), with the Bluetooth address, device name, title and device ID redacted so the file can be attached to a public issue.
- The **Flow Rate** sensor now has the *volume flow rate* device class, so Home Assistant can show it in other units.
- The **Bluetooth Signal** (RSSI) sensor is now disabled by default: it is a support tool. Enable it from the entity settings to check the Bluetooth range.

### 🐛 Bug fixes
- **Shower durations are now correct beyond about 21 minutes.** The device counts time in 1/50 s steps on 16 bits, so its counter wraps around every 21.8 minutes; the wrap-around is now handled, and the durations no longer restart from zero.
- **The cold / comfort split is more accurate.** When the temperature crosses the comfort threshold between two readings, the volume and the time are now split at the crossing point, instead of being counted entirely on the side of the latest reading.
- **Maximum Soaping Time out of range** (outside 10–600 s) is brought back into range with a warning in the log, instead of being sent to the device as is.
- Durations saved before the update (in minutes) are converted when restored, so a restart right after updating no longer shows values 60 times too small.
- The wasted volume, comfort shower volume and raw shower volume sensors now use the `total_increasing` state class instead of `measurement`, which Home Assistant rejects for the `water` device class (a warning was logged at every startup). See the upgrade notes.

### 🛡️ Hardening
- A drop of the device's duration counter that is not a wrap-around is treated as a device reset and counts for nothing, instead of producing a huge wrong duration.

### 🧰 Maintenance
- Every entity now shares a common base class (`HydraoEntity`): translated names, unique ID built from the Bluetooth address, device. **Entity IDs and unique IDs are unchanged.**
- Icons are defined in `icons.json` (same icons as before, the Bluetooth status keeps one icon per state).
- Durations are computed in seconds from integer counter differences, and displayed in minutes by Home Assistant.
- `PARALLEL_UPDATES` is set on every platform.
- Field descriptions (`data_description`) added to the setup and options forms, translated in all 19 languages.
- The whole integration passes `mypy --strict`, enforced by a dedicated *Typing* workflow.
- Test suite grown from 15 to over 400 tests, with 100 % coverage (lines and branches): simulated Bluetooth device, coordinator, config / options flows, entities, config entry lifecycle, translations.
- CI: pytest + coverage workflow (95 % minimum), *Typing* workflow, and a release workflow that publishes the notes from this changelog (`scripts/release_notes.py`). `.coveragerc` measures the integration only, with branches.
- The manifest declares the `platinum` quality scale (self-assessed in `quality_scale.yaml`, hassfest does not validate it for custom integrations), with tests keeping it consistent with the code.

### 📚 Documentation
- `README.md` / `README.fr.md`: minimum Home Assistant version, the new sensors, and new sections *How Data Is Updated*, *Use Cases*, *Automation Examples*, *Known Limitations* and *Removal*.

### 📋 Upgrade notes
- **Duration sensors keep their unit**: Home Assistant converts them automatically, so an existing *Shower Duration* still shows minutes.
- **Statistics of three sensors**: *Wasted Volume (Cold Water)*, *Comfort Shower Volume* and *Shower Volume* change state class. Home Assistant may offer to fix their long-term statistics in **Developer tools** > **Statistics**; accept it. For long-term statistics and the Water dashboard, use the cumulative sensors (*Total Cumulative Shower Volume*, *Total Cumulative Wasted Volume*, *Total Cumulative Comfort Shower Volume*) rather than the per-shower ones.
- The **Bluetooth Signal** sensor is only disabled on new installations: an existing one stays enabled.

🐬🐬🐬🐬🐬🐬🐬🐬🐬🐬

## 1.0.0

🐬🐬🐬🐬🐬🐬🐬🐬🐬🐬

### ✨ New features
- First stable release.

🐬🐬🐬🐬🐬🐬🐬🐬🐬🐬
