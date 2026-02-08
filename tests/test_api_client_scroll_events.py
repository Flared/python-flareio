import pytest
import requests_mock

from .utils import get_test_client

from flareio._ratelimit import _Limiter


def test_scroll_events() -> None:
    api_client = get_test_client()

    no_limit: _Limiter = _Limiter._unlimited()

    # This should make no http call.
    with requests_mock.Mocker() as mocker:
        events_iterator = api_client.scroll_events(
            method="GET",
            pages_url="https://api.flare.io/pages",
            events_url="https://api.flare.io/events",
            params={
                "from": None,
            },
            _pages_limiter=no_limit,
            _events_limiter=no_limit,
        )
        assert len(mocker.request_history) == 0

    # First page
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "GET",
            "https://api.flare.io/pages",
            json={
                "items": [
                    {"metadata": {"uid": "first_event_uid"}},
                ],
                "next": "second_page",
            },
            status_code=200,
        )
        mocker.register_uri(
            "GET",
            "https://api.flare.io/events",
            json={"event": "hello"},
            status_code=200,
        )

        event, cursor = next(events_iterator)
        assert len(mocker.request_history) == 2
        assert event == {"event": "hello"}
        assert cursor == "second_page"

    # Last page
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "GET",
            "https://api.flare.io/pages",
            json={
                "items": [],
                "next": None,
            },
        )
        with pytest.raises(StopIteration):
            next(events_iterator)
        assert len(mocker.request_history) == 1


def test_scroll_events_items() -> None:
    """
    scroll_events_metadata is used by the flareio-cli
    """
    api_client = get_test_client()
    no_limit: _Limiter = _Limiter._unlimited()

    events_iterator = api_client._scroll_events_items(
        method="GET",
        pages_url="https://api.flare.io/pages",
        events_url="https://api.flare.io/events",
        params={
            "from": None,
        },
        _pages_limiter=no_limit,
        _events_limiter=no_limit,
    )

    # First page
    with requests_mock.Mocker() as mocker:
        mocker.register_uri(
            "GET",
            "https://api.flare.io/pages",
            json={
                "items": [
                    {"metadata": {"uid": "first_event_uid"}},
                ],
                "next": "second_page",
            },
            status_code=200,
        )
        mocker.register_uri(
            "GET",
            "https://api.flare.io/events",
            json={"event": "hello"},
            status_code=200,
        )

        result = next(events_iterator)
        assert len(mocker.request_history) == 2
        assert result.item == {"metadata": {"uid": "first_event_uid"}}
        assert result.data == {"event": "hello"}
        assert result.next == "second_page"
