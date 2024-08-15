import pytest
import requests_mock

from flareio import FlareApiClient
from flareio.exceptions import TokenError

import typing as t


def _get_test_client(tenant_id: t.Optional[int] = None) -> FlareApiClient:
    return FlareApiClient(
        api_key="test-api-key",
        tenant_id=tenant_id,
    )


def test_create_client() -> None:
    FlareApiClient(api_key="test")


def test_create_client_empty_api_key() -> None:
    with pytest.raises(Exception, match="API Key cannot be empty."):
        FlareApiClient(
            api_key="",
        )


def test_generate_token_error() -> None:
    client = _get_test_client()
    assert client.token is None
    assert client.token_exp is None

    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "POST",
            "https://api.flare.io/tokens/generate",
            json={
                "error": {},
            },
            status_code=400,
        )

    with pytest.raises(TokenError):
        client.generate_token()
