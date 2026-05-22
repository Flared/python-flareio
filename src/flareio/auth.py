from requests import PreparedRequest
from requests.auth import AuthBase

import typing as t


class _StaticHeadersAuth(AuthBase):
    def __init__(
        self,
        *,
        headers: t.Dict[str, str],
    ) -> None:
        self._headers: t.Dict[str, str] = headers

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
