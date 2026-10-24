# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned

- Replace hard-coded entity names with Home Assistant entity translations.
- Add isolated tests for Sierra V4 framing and scalar codecs.
- Reduce dependency on private Tuya runtime internals where upstream APIs permit.

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
