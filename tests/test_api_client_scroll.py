import pytest
import requests
import requests_mock

from .utils import get_test_client

import typing as t


def test_scroll() -> None:
    api_client = get_test_client()

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
