from datetime import datetime
from datetime import timedelta

from flareio._ratelimit import _Limiter


def test_limiter() -> None:
    # Setup limiter
    limiter: _Limiter = _Limiter(
        tick_interval=timedelta(seconds=35),
        _sleeper=lambda _: None,
    )

    # The first tick is instantaneous. This is so that the limiter
    # never sleeps if the requests are taking longer than the interval.
    t_1: datetime = limiter._next_tick
    limiter.tick()
    t_2: datetime = limiter._next_tick
    assert limiter._slept_for == 0
    assert t_2 > t_1

    # Second tick is delayed.
    limiter.tick()
    t_3: datetime = limiter._next_tick
    assert t_3 > t_2
    assert limiter._slept_for > 30  # Intentionally not exact to avoid test races.


def test_seconds_until() -> None:
    future: datetime = datetime.now() + timedelta(seconds=10)
    assert _Limiter._seconds_until(future) > 5


def test_seconds_until_negative() -> None:
    now: datetime = datetime.now()
    past = now - timedelta(seconds=10)
    assert _Limiter._seconds_until(past) == 0.0


def test_limiter_unlimited() -> None:
    limiter: _Limiter = _Limiter._unlimited()
    assert limiter._slept_for == 0
    limiter.tick()
    limiter.tick()
    limiter.tick()
    assert limiter._slept_for == 0
