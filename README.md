# python-flareio

flareio is a light [Flare API](https://api.docs.flare.io/) SDK that wraps requests and adds Flare API authentication.

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

## Dev Commands

- `make test` will run tests
- `make format` format will format the code
- `make lint` will run typechecking + linting
