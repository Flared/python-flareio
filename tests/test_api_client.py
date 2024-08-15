import pytest
import requests_mock

from datetime import datetime
from flareio import FlareApiClient


def test_create_client() -> None:
    FlareApiClient(
        api_key="test",
    )


def test_create_client_empty_api_key() -> None:
    with pytest.raises(Exception, match="API Key cannot be empty."):
        FlareApiClient(
            api_key="",
        )


def test_generate_token() -> None:
    client = FlareApiClient(
        api_key="hey",
    )
    assert client.token is None
    assert client.token_exp is None

    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "POST",
            "https://api.flare.io/tokens/generate",
            json={
                "token": "test-token-hello",
            },
            status_code=200,
        )

        token = client.generate_token()
        assert token == "test-token-hello"

        assert client.token == "test-token-hello"
        assert client.token_exp
        assert client.token_exp >= datetime.now()

        assert mocker.last_request.url == "https://api.flare.io/tokens/generate"
        assert mocker.last_request.text is None


def test_generate_token_tenant() -> None:
    client = FlareApiClient(
        api_key="hey",
        tenant_id=44,
    )
    assert client.token is None
    assert client.token_exp is None

    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "POST",
            "https://api.flare.io/tokens/generate",
            json={
                "token": "test-token-hello",
            },
            status_code=200,
        )

        client.generate_token()
        assert mocker.last_request.url == "https://api.flare.io/tokens/generate"
        assert mocker.last_request.json() == {
            "tenant_id": 44,
        }
