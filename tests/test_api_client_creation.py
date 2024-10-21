import pytest
import requests_mock

from .utils import get_test_client
from datetime import datetime
from packaging.version import Version
from urllib3 import __version__ as urllib_version

from flareio import FlareApiClient
from flareio.exceptions import TokenError


def test_create_client() -> None:
    FlareApiClient(api_key="test")


def test_create_client_empty_api_key() -> None:
    with pytest.raises(Exception, match="API Key cannot be empty."):
        FlareApiClient(
            api_key="",
        )


def test_generate_token() -> None:
    client = get_test_client(authenticated=False)
    assert client._api_token is None
    assert client._api_token_exp is None
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

        assert client._api_token == "test-token-hello"
        assert client._api_token_exp
        assert client._api_token_exp >= datetime.now()

        assert mocker.last_request.url == "https://api.flare.io/tokens/generate"
        assert mocker.last_request.text is None
        assert mocker.last_request.headers["Authorization"] == "test-api-key"


def test_generate_token_error() -> None:
    client = get_test_client(authenticated=False)
    assert client._api_token is None
    assert client._api_token_exp is None

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


def test_backoff_max() -> None:
    if Version(urllib_version) >= Version("2.0.0"):
        retry = FlareApiClient._create_retry()
        assert hasattr(retry, "backoff_max")
        assert retry.backoff_max == 15
