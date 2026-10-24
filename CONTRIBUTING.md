# Contributing

Thank you for helping improve Dimplex Sierra BLE.

## Before opening an issue

1. Confirm the Tuya product ID and model without posting device IDs, UUIDs, local keys, Bluetooth addresses, or serial numbers.
2. Reproduce the problem on the latest tagged release.
3. Check existing issues.
4. Keep heat disabled while testing unknown datapoints.
5. Redact every log and screenshot.

## Development setup

Use Python 3.13 or newer.

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ruff==0.17.2
ruff check custom_components/dimplex_sierra_ble \
  --exclude custom_components/dimplex_sierra_ble/tuya_ble
python -m compileall custom_components/dimplex_sierra_ble
```

The vendored `tuya_ble` directory is pinned third-party code. Do not reformat or modify it casually. Any update must:

- identify the exact upstream commit;
- review the upstream license;
- update `THIRD_PARTY_NOTICES.md`;
- compare file hashes;
- repeat physical regression tests.

## Datapoint evidence

A new datapoint mapping requires reproducible evidence:

- baseline read;
- one isolated physical action;
- changed datapoint, type, and value;
- inverse action when safe;
- read-back confirmation;
- confirmation that heat remained in a known safe state.

Do not submit guessed mappings. Never probe unknown heating controls unattended.

## Pull requests

- Keep changes focused.
- Preserve config-entry and entity unique IDs.
- Add or update English and Spanish documentation.
- Update `CHANGELOG.md`.
- Explain safety impact and rollback.
- Do not include generated files, backups, databases, logs, or secrets.
- Ensure CI passes.

## Licensing

By contributing, you agree that your contribution is distributed under this repository's MIT License. Do not submit code with an incompatible license.
