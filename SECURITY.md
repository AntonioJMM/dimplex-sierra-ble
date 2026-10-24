# Security policy

## Supported versions

Security fixes are provided for the latest tagged release only.

## Reporting a vulnerability

Use [GitHub private vulnerability reporting](https://github.com/AntonioJMM/dimplex-sierra-ble/security/advisories/new). Do not open a public issue for a suspected credential leak, authentication weakness, or exposure of device identifiers.

Never include:

- Tuya username or password;
- Tuya local key, UUID, device ID, or access token;
- Bluetooth or MAC address;
- Home Assistant tokens;
- public IP addresses or private DNS names;
- unredacted debug logs or diagnostics.

If private reporting is unavailable, contact the repository owner through a private channel and provide only a minimal description until a secure exchange method is agreed.

## Credential handling design

Dimplex Sierra BLE reads the required BLE credentials from the official Tuya integration's in-memory runtime data. It does not intentionally copy them into its own config entry, diagnostics, or log messages.

The bundled transport logger is forced to `CRITICAL` because upstream debug and error messages can contain device identifiers. Contributors must preserve this protection unless every affected message has been audited and redacted.

## Scope

Security reports should concern this repository. Vulnerabilities in Home Assistant, Tuya, Dimplex firmware, Bluetooth stacks, or third-party dependencies should also be reported to their respective maintainers.
