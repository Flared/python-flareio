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
        tenant_id: int | None = None,
    ) -> None:
        if not api_key:
            raise Exception("API Key cannot be empty.")
        self.api_key: str = api_key
        self.tenant_id: int | None = tenant_id

        self.token: str | None = None
        self.token_exp: datetime | None = None

    def generate_token(self) -> str:
        payload: dict | None = None

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
        token: str | None = self.token
        if not token or (self.token_exp and self.token_exp < datetime.now()):
            token = self.generate_token()

        return {"Authorization": f"Bearer {token}"}

    def _request(
        self,
        method: str,
        url: str,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> requests.Response:
        if not url.startswith("https://api.flare.io"):
            raise Exception(
                "Please only use the client to access the api.flare.io domain."
            )
        headers = kwargs.pop("headers", None) or {}
        headers = {
            **headers,
            **self._auth_headers(),
        }
        return requests.request(
            method,
            url,
            *args,
            **kwargs,
            headers=headers,
        )

    def post(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> requests.Response:
        return self._request("POST", *args, **kwargs)

    def get(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> requests.Response:
        return self._request("GET", *args, **kwargs)

    def put(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> requests.Response:
        return self._request("PUT", *args, **kwargs)

    def delete(
        self,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> requests.Response:
        return self._request("DELETE", *args, **kwargs)
