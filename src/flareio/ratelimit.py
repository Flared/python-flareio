import time

from datetime import datetime
from datetime import timedelta

import typing as t


class Limiter:
    def __init__(
        self,
        *,
        tick_interval: timedelta,
        _sleeper: t.Callable[[float], None] = time.sleep,
    ) -> None:
        self._tick_interval: timedelta = tick_interval
        self._next_tick: datetime = datetime.now()
        self._sleeper: t.Callable[[float], None] = _sleeper
        self._slept_for: float = 0.0

    def _push_next_tick(self) -> None:
        self._next_tick = datetime.now() + self._tick_interval

    @staticmethod
    def _seconds_until(t: datetime) -> float:
        td: timedelta = t - datetime.now()
        return max(td.total_seconds(), 0.0)

    def _sleep(self, seconds: float) -> None:
        self._sleeper(seconds)
        self._slept_for += seconds

    def tick(self) -> None:
        """
        You should call this method before making a request.
        The first time will be instantaneous.
        """
        self._sleep(self._seconds_until(self._next_tick))
        self._push_next_tick()

    @classmethod
    def _unlimited(cls) -> "Limiter":
        return cls(tick_interval=timedelta(seconds=0))

    @classmethod
    def from_seconds(cls, tick_interval_seconds: int) -> "Limiter":
        return cls(
            tick_interval=timedelta(
                seconds=tick_interval_seconds,
            )
        )
