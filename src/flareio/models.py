import dataclasses


@dataclasses.dataclass(frozen=True)
class ScrollEventsResult:
    metadata: dict
    event: dict
    next: str | None
