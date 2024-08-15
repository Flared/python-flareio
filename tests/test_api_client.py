import pytest
import requests_mock

from datetime import datetime
from flareio import FlareApiClient
from flareio.exceptions import TokenError


def _get_test_client(tenant_id: int | None = None) -> FlareApiClient:
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


def test_generate_token() -> None:
    client = _get_test_client()
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
        assert mocker.last_request.headers["Authorization"] == "test-api-key"


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


def test_bad_domain() -> None:
    client = _get_test_client()
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

    with pytest.raises(
        Exception,
        match="Please only use the client to access the api.flare.io domain.",
    ):
        client.post("https://bad.com/hello-post")
