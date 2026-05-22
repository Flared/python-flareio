import dataclasses

import typing as t


@dataclasses.dataclass(frozen=True)
class ScrollEventsResult:
    metadata: dict
    event: dict
    next: t.Optional[str]
