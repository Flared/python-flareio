import pytest
import requests
import requests_mock

from datetime import datetime
from flareio import FlareApiClient
from flareio.exceptions import TokenError

import typing as t


def _get_test_client(
    *,
    tenant_id: t.Optional[int] = None,
    authenticated: bool = True,
) -> FlareApiClient:
    client = FlareApiClient(
        api_key="test-api-key",
        tenant_id=tenant_id,
    )

    if authenticated:
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

    return client


def test_create_client() -> None:
    FlareApiClient(api_key="test")


def test_create_client_empty_api_key() -> None:
    with pytest.raises(Exception, match="API Key cannot be empty."):
        FlareApiClient(
            api_key="",
        )


def test_generate_token() -> None:
    client = _get_test_client(authenticated=False)
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
    client = _get_test_client(authenticated=False)
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


def test_bad_domain() -> None:
    client = _get_test_client()

    with pytest.raises(
        Exception,
        match="Please only use the client to access the api.flare.io domain.",
    ):
        client.post("https://bad.com/hello-post")


def test_wrapped_methods() -> None:
    client = _get_test_client(authenticated=False)
    assert client._api_token is None
    assert client._api_token_exp is None

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
            status_code=200,
        )

        client.post("https://api.flare.io/hello-post", json={"foo": "bar"})
        assert mocker.last_request.url == "https://api.flare.io/hello-post"
        assert mocker.last_request.headers["Authorization"] == "Bearer test-token-hello"
        assert mocker.last_request.json() == {"foo": "bar"}

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


def test_scroll() -> None:
    api_client = _get_test_client()

    # This should make no http call.
    with requests_mock.Mocker() as mocker:
        response_iterator: t.Iterator[requests.Response] = api_client.scroll(
            method="GET",
            url="https://api.flare.io/leaksdb/v2/sources",
            params={
                "from": None,
            },
        )
        assert len(mocker.request_history) == 0

    # First page
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "GET",
            "https://api.flare.io/leaksdb/v2/sources",
            json={
                "items": [1, 2, 3],
                "next": "second_page",
            },
            status_code=200,
        )
        resp: requests.Response = next(response_iterator)
        assert resp.json() == {"items": [1, 2, 3], "next": "second_page"}

        assert len(mocker.request_history) == 1
        assert mocker.last_request.query == ""

    # Second Page
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "GET",
            "https://api.flare.io/leaksdb/v2/sources?from=second_page",
            json={
                "items": [4, 5, 6],
                "next": "third_page",
            },
            status_code=200,
        )
        resp = next(response_iterator)
        assert resp.json() == {"items": [4, 5, 6], "next": "third_page"}
        assert len(mocker.request_history) == 1
        assert mocker.last_request.query == "from=second_page"

    # Third Page
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "GET",
            "https://api.flare.io/leaksdb/v2/sources?from=third_page",
            json={
                "items": [7, 8, 9],
                "next": None,
            },
            status_code=200,
        )
        resp = next(response_iterator)
        assert resp.json() == {
            "items": [7, 8, 9],
            "next": None,
        }
        assert len(mocker.request_history) == 1
        assert mocker.last_request.query == "from=third_page"

    # We stop here.
    with requests_mock.Mocker() as mocker:
        with pytest.raises(StopIteration):
            resp = next(response_iterator)
        assert len(mocker.request_history) == 0
