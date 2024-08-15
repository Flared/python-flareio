import pytest
import requests_mock

from datetime import datetime
from flareio import FlareApiClient


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


def test_generate_token_tenant() -> None:
    client = _get_test_client(tenant_id=44)
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


def test_wrapped_methods() -> None:
    client = _get_test_client()
    assert client.token is None
    assert client.token_exp is None

    # POST: This one will generate since its the first one.
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "POST",
            "https://api.flare.io/tokens/generate",
            json={
                "token": "test-token-hello",
            },
            status_code=200,
        )
        mocker.register_uri(
            "POST",
            "https://api.flare.io/hello-post",
            json={"foo": "bar"},
            status_code=200,
        )

        client.post("https://api.flare.io/hello-post")
        assert mocker.last_request.url == "https://api.flare.io/hello-post"
        assert mocker.last_request.headers["Authorization"] == "Bearer test-token-hello"

    # GET
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "GET",
            "https://api.flare.io/hello-get",
            json={"foo": "bar"},
            status_code=200,
        )

        client.get("https://api.flare.io/hello-get")
        assert mocker.last_request.url == "https://api.flare.io/hello-get"
        assert mocker.last_request.headers["Authorization"] == "Bearer test-token-hello"

    # PUT
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "PUT",
            "https://api.flare.io/hello-put",
            json={"foo": "bar"},
            status_code=200,
        )

        client.put("https://api.flare.io/hello-put")
        assert mocker.last_request.url == "https://api.flare.io/hello-put"
        assert mocker.last_request.headers["Authorization"] == "Bearer test-token-hello"

    # DELETE
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "DELETE",
            "https://api.flare.io/hello-delete",
            json={"foo": "bar"},
            status_code=200,
        )

        client.delete("https://api.flare.io/hello-delete")
        assert mocker.last_request.url == "https://api.flare.io/hello-delete"
        assert mocker.last_request.headers["Authorization"] == "Bearer test-token-hello"
