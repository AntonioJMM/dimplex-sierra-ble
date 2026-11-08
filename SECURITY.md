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

Dimplex Sierra BLE accepts the BLE UUID, local key, device ID and product ID directly from the user through its own config flow. It does not read another integration's config entries, runtime clients, device managers or credentials. The official Tuya integration is not a dependency.

The credentials and Bluetooth address are stored in this integration's Home Assistant config entry. Password selectors conceal form input, not the stored values. Home Assistant's configuration directory and backups therefore contain sensitive material and must be protected. Legacy entries request user-provided credentials; migration does not copy credentials from Tuya.

Validation errors use fixed messages without credential values. Credentials are not intentionally included in integration logs or diagnostics. Bluetooth discovery requires explicit confirmation before credential entry because its Tuya advertisement signature is not model-specific.

The bundled transport logger is forced to `CRITICAL` because upstream debug and error messages can contain device identifiers. Contributors must preserve this protection unless every affected message has been audited and redacted.

## Scope

Security reports should concern this repository. Vulnerabilities in Home Assistant, Tuya, Dimplex firmware, Bluetooth stacks, or third-party dependencies should also be reported to their respective maintainers.
