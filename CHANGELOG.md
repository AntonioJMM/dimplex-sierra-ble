# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned

- Replace hard-coded entity names with Home Assistant entity translations.
- Add isolated tests for Sierra V4 framing and scalar codecs.

## [0.4.0] - 2026-11-08

### Changed

- **Breaking setup change:** users supply their own Tuya BLE UUID, device ID, local key and product ID through this integration's config flow. The values are now stored in its Home Assistant config entry; protect configuration files and backups.
- Existing entries migrate to version 2 and request credentials through reauthentication without changing entry or entity identities. Back up before upgrading; rollback requires restoring the pre-upgrade backup.
- Bluetooth discovery requires explicit `bluetooth_confirm` consent before credential entry. Generic TY/FD50 advertisements never create an entry automatically.
- Transient advertisement, initial-read and Bluetooth connection failures raise `ConfigEntryNotReady` so Home Assistant retries startup, with connection cleanup on failure.

### Added

- Own credential reconfiguration flow to correct values without removing the entry.
- English and Spanish credential, reauthentication, reconfiguration, confirmation and validation messages.
- Automated regression tests using synthetic credentials and mocked Bluetooth, including Home Assistant's setup-retry state.

### Removed

- Dependency on the official Tuya integration and access to its runtime credentials, clients or device managers.

### Validation scope

- BLE protocol, datapoints and control behavior are unchanged from the physically tested 0.3.0 release. The new credential and migration paths are automated-test validated, not yet physically revalidated.

## [0.3.0] - 2026-10-24

### Added

- Verified sound switch using DP108.
- Delayed second read-back for the sound datapoint.
- English and Spanish public documentation.
- HACS metadata, original brand icon, CI, security policy, contribution guide, and third-party notices.

### Changed

- Replaced the unidentified DP108 diagnostic binary sensor with a sound switch.

### Removed

- Obsolete DP108 diagnostic entity.

## [0.2.1] - 2026-10-18

### Changed

- Removed the false interpretation of DP103 as room temperature.
- Exposed DP103 only as a raw diagnostic value.

## [0.2.0] - 2026-10-18

### Added

- Local Tuya BLE V4.2 polling and verified writes.
- Power, heat, climate, flame, ember-bed, brightness, timer, lock, and temperature-unit entities.

## [0.1.0] - 2026-10-18

### Added

- Initial experimental Dimplex Sierra BLE integration.
