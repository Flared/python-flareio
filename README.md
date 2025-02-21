# python-flareio

`flareio` is a light [Flare API](https://api.docs.flare.io/) SDK that wraps [requests](https://requests.readthedocs.io/) and automatically manages authentication.

Usage examples and use cases are documented in the [Flare API documentation](https://api.docs.flare.io/sdk/python).

## Installing

`flareio` is [available on PyPI](https://pypi.org/project/flareio/).

The library can be installed via `pip install flareio`.

## Basic Usage

```python
import os

from flareio import FlareApiClient


client = FlareApiClient.from_env()

resp = client.get("/tokens/test")

print(resp.json())
```

## Contributing

- `make test` will run tests
- `make format` format will format the code
- `make lint` will run typechecking + linting
