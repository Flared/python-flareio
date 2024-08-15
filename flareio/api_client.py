import requests

from datetime import datetime
from datetime import timedelta
from flareio.exceptions import TokenError

import typing as t


class FlareApiClient:
    def __init__(
        self,
        *,
        api_key: str,
        tenant_id: t.Optional[int] = None,
    ) -> None:
        if not api_key:
            raise Exception("API Key cannot be empty.")
        self.api_key: str = api_key
        self.tenant_id: t.Optional[int] = tenant_id

        self.token: t.Optional[str] = None
        self.token_exp: t.Optional[datetime] = None

    def generate_token(self) -> str:
        payload: t.Optional[dict] = None

        if self.tenant_id is not None:
            payload = {
                "tenant_id": self.tenant_id,
            }

        resp = requests.post(
            "https://api.flare.io/tokens/generate",
            json=payload,
            headers={
                "Authorization": self.api_key,
            },
        )
        try:
            resp.raise_for_status()
        except Exception as ex:
            raise TokenError("Failed to fetch API Token") from ex
        token: str = resp.json()["token"]

        self.token = token
        self.token_exp = datetime.now() + timedelta(minutes=45)

        return token

    def _auth_headers(self) -> dict:
        token: t.Optional[str] = self.token
        if not token or (self.token_exp and self.token_exp < datetime.now()):
            token = self.generate_token()

        return {"Authorization": f"Bearer {token}"}

    def _request(
        self,
        *,
        method: str,
        url: str,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Optional[t.Dict[str, t.Any]] = None,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> requests.Response:
        if not url.startswith("https://api.flare.io"):
            raise Exception(
                "Please only use the client to access the api.flare.io domain."
            )
        headers = {
            **(headers or {}),
            **self._auth_headers(),
        }
        return requests.request(
            method=method,
            url=url,
            params=params,
            json=json,
            headers=headers,
        )

    def post(
        self,
        url: str,
        *,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Optional[t.Dict[str, t.Any]] = None,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> requests.Response:
        return self._request(
            method="POST",
            url=url,
            params=params,
            json=json,
            headers=headers,
        )

    def get(
        self,
        url: str,
        *,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Optional[t.Dict[str, t.Any]] = None,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> requests.Response:
        return self._request(
            method="GET",
            url=url,
            params=params,
            json=json,
            headers=headers,
        )

    def put(
        self,
        url: str,
        *,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Optional[t.Dict[str, t.Any]] = None,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> requests.Response:
        return self._request(
            method="PUT",
            url=url,
            params=params,
            json=json,
            headers=headers,
        )

    def delete(
        self,
        url: str,
        *,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Optional[t.Dict[str, t.Any]] = None,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> requests.Response:
        return self._request(
            method="DELETE",
            url=url,
            params=params,
            json=json,
            headers=headers,
        )
