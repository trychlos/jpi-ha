# pyJPI - An asynchronous Python module to interact with Android devices running JPI

<!-->
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=plastic)](https://github.com/trychlos/pyjpi)
-->

[![Latest release](https://img.shields.io/github/v/release/trychlos/pyjpi?style=plastic&logo=github&logoColor=white&label=Latest%20release&color=green)](https://github.com/trychlos/pyjpi/release)
[![Latest commit](https://img.shields.io/github/last-commit/trychlos/pyjpi?style=plastic&logo=github&logoColor=white&label=Latest%20commit&color=green)](https://github.com/trychlos/pyjpi)
[![PyPI version](https://img.shields.io/pypi/v/pyJPI?style=plastic&logo=pypi&logoColor=white&color=green)](https://pypi.org/project/pyJPI/)

[![CodeFactor](https://img.shields.io/codefactor/grade/github/trychlos/pyjpi?style=plastic&logo=codefactor&logoColor=white)](https://www.codefactor.io/repository/github/trychlos/pyjpi)
[![Code coverage](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Ftrychlos%2Fpyjpi%2Fmaster%2F.github%2Fassets%2Fcoverage.json&style=plastic&logo=codecov&logoColor=white)](https://app.codecov.io/gh/trychlos/pyjpi)
[![Max cyclomatic complexity](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Ftrychlos%2Fpyjpi%2Fmaster%2F.github%2Fassets%2Fradon.json&style=plastic)](https://github.com/trychlos/pyjpi)

<!--
[![CodeRabbit.ai is Awesome](https://img.shields.io/badge/AI-orange?label=CodeRabbit&color=orange&link=https%3A%2F%2Fcoderabbit.ai)](https://coderabbit.ai)
[![renovate maintained](https://img.shields.io/badge/maintained%20with-renovate-blue?logo=renovatebot)](https://github.com/compatech/python-airos/issues/8)

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=CoMPaTech_python-airos&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=CoMPaTech_python-airos)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=CoMPaTech_python-airos&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=CoMPaTech_python-airos)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=CoMPaTech_python-airos&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=CoMPaTech_python-airos)
-->

## Overview

`pyJPI` is an asynchronous Python library designed to programmatically interact with Android devices running JPI.

This library is a key component for a core integration with [Home Assistant](https://www.home-assistant.io).

More details on the integration can be found on the [JPI](https://www.home-assistant.io/integrations/jpi/) page.

## Features

- Asynchronous operations are built with ``aiohttp` for non-blocking I/O, which is perfect for integrations and background tasks.
- API: `battInfo`
- API: `get`
- API: `getDeviceName`

## Installation

You can install `pyJPI` from PyPI using pip:

```Bash
pip install pyjpi
```

## Usage

Here is a more detailed example of how to use the library to connect, fetch status, and perform an action on an Android device running JPI.

```Python
import aiohttp
from pyjpi import jpiInit

async def main():
    """Main function to demonstrate library usage."""
    # Create an aiohttp session with SSL verification disabled.
    # Be cautious with this setting; it's useful for self-signed certificates
    # but not recommended for production environments without proper validation.
    session = aiohttp.ClientSession( connector=aiohttp.TCPConnector( verify_ssl=False ))

    # Get a handle on the pyJPI library.
    handle = await jpiInit( session )

    # Have an URL somewhere.
    url = "http://myhost.example.com:8080"

    # Then just has to call the library functions.
    try:
        res = await handle.get( url )
        # returns a dict { resp: ClientResponse, text: str } or False
        res = await handle.getDeviceName( url )
        # returns the device name as set by the manufacturer (a single string) or False
        res = await handle.battInfo( url )
        # returns a dict { level: integer, charging: bool, power: bool }


if __name__ == "__main__":
    main()
```

## Available functions

- `async jpiInit( session: aiohttp.ClientSession ) -> JPILibrary`:

Initializes the library.

Returns a handle on it.

## Available classes

- `JPILibrary`:

The class which manages the devices accesses.

## Available `JPILibrary` methods

- `async get( url: str) -> dict`:

Runs a HTTP GET method on the specified URL.

Returns a dict with:

```Python
    resp: the `aiohttp.ClientResponse`
    text: the resp.text() content
```

- `async getDeviceName( url: str) -> str`:

Runs a HTTP GET method on f"{url}?action=getDeviceName" url.

Returns a string which contains the device name as set by the manufacturer.

- `async battInfo( url: str) -> dict`:

Runs a HTTP GET method on on f"{url}?action=battInfo" url.

Returns a dict with:

```Python
    level: an integer with the current battery level in %
    charging: a boolean which says if the battery is currently charging
    power: a boolean which says if the power is on on the device.
```

## Contributing

We welcome contributions as well as additional codeowners to `pyjpi`.

## Issues & help

In case of support or error, please report your issue request to our [Issues tracker](https://github.com/trychlos/pyjpi/issues).
