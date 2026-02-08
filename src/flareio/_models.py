import dataclasses


@dataclasses.dataclass(frozen=True)
class _ScrollEventsResult:
    item: dict
    data: dict
    next: str | None
