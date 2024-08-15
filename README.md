# python-flareio

`flareio` is a light [Flare API](https://api.docs.flare.io/) SDK that wraps requests and automatically manages authentication.

Usage examples and use cases are documented on the [Flare API documentation](https://api.docs.flare.io/concepts/sdk).

## Installing

The library can be installed via `pip install flareio`.


## Basic Usage

```python
from flareio import FlareApiClient

client = FlareApiClient(
    api_key="fw-...",
)

sources = client.get(
    "https://api.flare.io/leaksdb/v2/sources",
).json()
```

## Contributing

- `make test` will run tests
- `make format` format will format the code
- `make lint` will run typechecking + linting
