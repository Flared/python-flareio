import requests_mock

from .utils import get_test_client

from flareio.auth import _EmptyAuth
from flareio.auth import _StaticHeadersAuth


def test_custom_auth_empty() -> None:
    client = get_test_client(
        authenticated=False,
        _auth=_EmptyAuth(),
    )
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "POST",
            "https://api.flare.io/hello-post",
            status_code=200,
        )
        client.post(
            "https://api.flare.io/hello-post",
            json={"foo": "bar"},
        )
        assert not mocker.last_request.headers.get("Authorization")


def test_custom_auth_static() -> None:
    client = get_test_client(
        authenticated=False,
        _auth=_StaticHeadersAuth(
            headers={
                "first-header": "first-value",
                "Authorization": "auth-value",
            }
        ),
    )
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "POST",
            "https://api.flare.io/hello-post",
            status_code=200,
        )
        client.post(
            "https://api.flare.io/hello-post",
            json={"foo": "bar"},
            headers={"second-header": "second-value"},
        )
        assert mocker.last_request.headers["Authorization"] == "auth-value"
        assert mocker.last_request.headers["first-header"] == "first-value"
        assert mocker.last_request.headers["second-header"] == "second-value"
