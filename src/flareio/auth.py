from requests import PreparedRequest
from requests.auth import AuthBase


class _StaticHeadersAuth(AuthBase):
    def __init__(
        self,
        *,
        headers: dict[str, str],
    ) -> None:
        self._headers: dict[str, str] = headers

    def __call__(
        self,
        r: PreparedRequest,
    ) -> PreparedRequest:
        r.headers.update(self._headers)
        return r


class _EmptyAuth(AuthBase):
    def __call__(
        self,
        r: PreparedRequest,
    ) -> PreparedRequest:
        return r
