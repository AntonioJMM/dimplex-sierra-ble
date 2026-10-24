# Dimplex Sierra BLE for Home Assistant

[![Validate](https://github.com/AntonioJMM/dimplex-sierra-ble/actions/workflows/validate.yml/badge.svg)](https://github.com/AntonioJMM/dimplex-sierra-ble/actions/workflows/validate.yml)
[![GitHub release](https://img.shields.io/github/v/release/AntonioJMM/dimplex-sierra-ble?include_prereleases)](https://github.com/AntonioJMM/dimplex-sierra-ble/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Local Bluetooth control for selected Dimplex Sierra electric fireplaces using Tuya BLE V4.2 over the `0xFD50` service.

> [!IMPORTANT]
> This is an independent community project. It is not affiliated with, endorsed by, or supported by Dimplex, Tuya, or Home Assistant.
>
> The integration is currently **beta**. It has been physically validated on one Sierra 48 unit with product ID `0fsaqmtu`. Other products may use different datapoints and must not be assumed compatible.

[Documentación en español](README.es.md)

## Features

- Local BLE polling and control; no command proxy or MQTT broker required.
- Main power and heater control.
- Target temperature and continuous-heat mode.
- Flame effect and brightness.
- Ember-bed effect and brightness.
- Crackling sound on/off.
- Timer from 0 to 8 hours.
- Heater safety-lock diagnostic.
- Celsius/Fahrenheit display-state diagnostic.
- Every write is followed by a read-back verification.
- BLE is disconnected after each operation.
- Tuya credentials are reused in memory and are never copied into this integration's config entry.

## Confirmed hardware

| Product | Model | Tuya product ID | Status |
|---|---|---|---|
| Dimplex Sierra 48 | `SIL48` / `X-SIL48` | `0fsaqmtu` | Physically tested |

The integration deliberately rejects unsupported product IDs during credential lookup. A Bluetooth advertisement named `TY` is not sufficient proof of compatibility because many Tuya BLE products use that name.

## Requirements

- Home Assistant with a working Bluetooth integration and a connectable Bluetooth adapter or proxy.
- The fireplace must be in Bluetooth range and advertising.
- The official Home Assistant **Tuya** integration must already contain the fireplace and expose its BLE credentials in memory.
- Home Assistant `2026.10.0` or newer for the currently tested release line.

### Important Tuya dependency

Commands are local after setup, but the integration currently obtains the BLE UUID and local key from the official Tuya integration's runtime data. This is an internal Home Assistant/Tuya interface and can change in a future Home Assistant release. No key is written to this integration's files or config entry.

## Installation

### HACS custom repository

1. Open HACS.
2. Select **Integrations**.
3. Open the menu and choose **Custom repositories**.
4. Add `https://github.com/AntonioJMM/dimplex-sierra-ble` with category **Integration**.
5. Install **Dimplex Sierra BLE**.
6. Restart Home Assistant.

This project is not yet included in the default HACS repository list.

### Manual installation

1. Download a tagged release.
2. Copy `custom_components/dimplex_sierra_ble` into your Home Assistant `/config/custom_components/` directory.
3. Restart Home Assistant.
4. Go to **Settings → Devices & services → Add integration**.
5. Search for **Dimplex Sierra BLE**.

Do not install from an unreviewed branch on a production Home Assistant instance.

## Setup

1. Configure Home Assistant Bluetooth.
2. Configure the official Tuya integration and confirm that the fireplace exists there.
3. Power the fireplace so it advertises over BLE.
4. Add **Dimplex Sierra BLE** from **Settings → Devices & services**.
5. Select the discovered fireplace.

No Tuya password, UUID, local key, Bluetooth address, or device ID should be posted in an issue.

## Entities

The integration creates 13 entities:

- Climate control.
- Power, heat, and sound switches.
- Thermostat, flame-effect, and ember-effect selects.
- Flame brightness, ember brightness, and timer numbers.
- Heater-lock binary sensor.
- Temperature-unit and raw-DP103 diagnostic sensors.

DP103 is intentionally exposed only as a diagnostic raw value. It has produced values that are not physically plausible as room temperature and is therefore not used as `current_temperature`.

## Safety notes

- The physical heater lock is not remotely overridden.
- Heat is never inferred from main power; power and heat are separate datapoints.
- Keep the heater switch off during initial testing.
- Do not build unattended heating automations until you have verified behavior on your exact hardware.
- Sound DP108 applies with a short delay, so it receives one additional verification read.
- If a command cannot be confirmed, Home Assistant reports an error instead of assuming success.

## Privacy and logging

The integration does not intentionally log or persist the Tuya local key, Tuya UUID, Bluetooth address, or device ID. The bundled transport logger is suppressed because upstream debug messages may contain device identifiers.

Before opening an issue:

- remove Bluetooth addresses, UUIDs, local keys, Tuya IDs, serial numbers, and account details;
- do not enable debug logging unless a maintainer provides a narrowly scoped procedure;
- review diagnostics and screenshots manually.

See [SECURITY.md](SECURITY.md).

## Known limitations

- Only product ID `0fsaqmtu` is supported.
- Only one physical unit has been validated so far.
- Credential retrieval depends on private runtime details of the official Tuya integration.
- DP103 is not understood.
- Fahrenheit behavior has not received the same physical validation as Celsius.
- Bluetooth discovery uses common Tuya advertisement characteristics; final compatibility is enforced during setup, not by the local name alone.

## Development

```bash
python3.14 -m compileall custom_components/dimplex_sierra_ble
ruff check custom_components/dimplex_sierra_ble \
  --exclude custom_components/dimplex_sierra_ble/tuya_ble
```

Pull requests should include tests or reproducible protocol evidence for every new datapoint. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Third-party code

The bundled Tuya BLE transport is MIT-licensed code from `ShonP40/Tuya-BLE`, pinned to commit `e9d09366ccddaf793f052817f6c7dcaab3d821a2`, and derives from `PlusPlus-ua/ha_tuya_ble`.

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and the license stored beside the bundled transport.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
