# JPI for Home Assistant

JPI is a custom Home Assistant integration for Android devices running the
[JPI application](https://jpi-domotique.com/). It communicates directly with
the device over the local network through the `pyjpi` asynchronous library.

## Features

- Configuration and reconfiguration through the Home Assistant UI
- Local polling with a configurable interval
- Battery-level sensor
- Charging, external-power, and last-seen attributes
- Automatic entity unavailability when communication fails
- Multiple JPI devices, distinguished by their complete network endpoints
- Migration of existing installations without changing their entity or device
  identifiers

## Requirements

- A supported Android device running JPI
- JPI accessible from Home Assistant over HTTP or HTTPS
- The complete device URL, including its port when required, for example:
  `http://phone.example.com:8080`

## Installation

JPI is a manually installed custom integration. It is not bundled with Home
Assistant and is not currently distributed through HACS.

Clone the repository directly into the Home Assistant custom-components
directory:

```shell
cd /config/custom_components
git clone https://github.com/trychlos/jpi-ha.git jpi
```

The resulting path must contain:

```text
/config/custom_components/jpi/manifest.json
```

Restart Home Assistant after installation or upgrade.

To update an installation created this way:

```shell
git -C /config/custom_components/jpi pull --ff-only
```

This approach keeps one working copy and does not require duplicating the
integration files.

## Configuration

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **JPI**.
4. Enter the complete URL of the JPI device.
5. Choose the polling interval in seconds.

The setup flow contacts the device and retrieves its manufacturer and model
before creating the entry. The device must therefore be online and reachable
during configuration.

Each complete hostname-and-port endpoint can be configured once. Devices with
the same short hostname remain distinct when their complete endpoints differ.

## Reconfiguration

Open the JPI integration entry and select **Reconfigure** to change its polling
interval. The device URL is intentionally preserved.

## Entities

Each configured device provides a battery sensor:

- State: battery level as a percentage
- `charging`: whether the battery is charging
- `power`: whether external power is connected
- `last_seen`: time of the most recent successful update

The sensor becomes unavailable after an update failure and becomes available
again after communication recovers.

## Existing installations

Entries created by earlier versions retain their existing Home Assistant
device identifiers, entity unique IDs, entry title, and familiar UI names.
This prevents existing dashboards, scripts, and automations from breaking.

New entries use the complete normalized endpoint for duplicate detection and a
Home Assistant-managed internal identifier for their entities and devices.

## Removal

1. Remove the JPI entry from **Settings → Devices & services**.
2. Stop Home Assistant.
3. Remove `/config/custom_components/jpi`.
4. Start Home Assistant again.

Removing the files without first removing the config entry can leave an
unavailable entry in Home Assistant.

## Development

The repository intentionally stores the integration and its tests together.
For a sibling Home Assistant Core checkout, use symbolic links instead of
copying files:

```shell
ln -s ../../../jpi-ha core/homeassistant/components/jpi
ln -s ../../../jpi-ha/tests core/tests/components/jpi
ln -s ../../../jpi-ha core/config/custom_components/jpi
```

Install the sibling `pyjpi` checkout in Core's virtual environment:

```shell
core/.venv/bin/python -m pip install --editable pyjpi
```

Run the integration tests through Core's test path:

```shell
core/.venv/bin/pytest core/tests/components/jpi
```

Running pytest directly against `jpi-ha/tests` is not supported because Home
Assistant's tests rely on the Core `tests` package namespace.

## Known limitations

- JPI devices are configured manually; discovery is not implemented.
- Only battery information is currently exposed.
- The integration requires network access to the Android device.
- HTTPS certificate or authentication configuration is not currently exposed.

## Support

Report problems through the
[JPI Home Assistant issue tracker](https://github.com/trychlos/jpi-ha/issues).
Include the Home Assistant version, integration version, JPI URL with sensitive
host information redacted, and relevant log messages.

## Contributing

Contributions and additional maintainers are welcome. Please run the JPI test
suite before submitting changes.
