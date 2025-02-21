import os
import requests

from datetime import datetime
from datetime import timedelta
from http.cookiejar import DefaultCookiePolicy
from requests.adapters import HTTPAdapter
from urllib.parse import urljoin
from urllib.parse import urlparse
from urllib3.util import Retry

import typing as t

from flareio.exceptions import TokenError
from flareio.version import __version__ as _flareio_version


class FlareApiClient:
    def __init__(
        self,
        *,
        api_key: str,
        tenant_id: t.Optional[int] = None,
        session: t.Optional[requests.Session] = None,
    ) -> None:
        if not api_key:
            raise Exception("API Key cannot be empty.")
        self._api_key: str = api_key
        self._tenant_id: t.Optional[int] = tenant_id

        self._api_token: t.Optional[str] = None
        self._api_token_exp: t.Optional[datetime] = None
        self._session = session or self._create_session()

    @classmethod
    def from_env(cls) -> "FlareApiClient":
        api_key: t.Optional[str] = os.environ.get("FLARE_API_KEY")
        if not api_key:
            raise Exception(
                "Please set the FLARE_API_KEY environment variable. Otherwise, initiate the client using FlareApiClient(api_key=...)."
            )
        tenant_id: t.Optional[str] = os.environ.get("FLARE_TENANT_ID")
        return cls(
            api_key=api_key,
            tenant_id=int(tenant_id) if tenant_id else None,
        )

    @staticmethod
    def _create_session() -> requests.Session:
        session = requests.Session()

        # Set User-Agent
        session.headers["User-Agent"] = (
            f"python-flareio/{_flareio_version} requests/{requests.__version__}"
        )

        # Don't accept cookies.
        session.cookies.set_policy(
            policy=DefaultCookiePolicy(
                allowed_domains=[],
            ),
        )

        # Enable retries
        session.mount(
            "https://",
            HTTPAdapter(max_retries=FlareApiClient._create_retry()),
        )

        return session

    @staticmethod
    def _create_retry() -> Retry:
        retry = Retry(
            total=5,
            backoff_factor=2,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods={"GET", "POST"},
        )

        # Support for urllib3 < 2.X
        if hasattr(retry, "backoff_max"):
            retry.backoff_max = 15

        return retry

    def generate_token(self) -> str:
        payload: t.Optional[dict] = None

        if self._tenant_id is not None:
            payload = {
                "tenant_id": self._tenant_id,
            }

        resp = self._session.post(
            "https://api.flare.io/tokens/generate",
            json=payload,
            headers={
                "Authorization": self._api_key,
            },
        )
        try:
            resp.raise_for_status()
        except Exception as ex:
            raise TokenError("Failed to fetch API Token") from ex
        token: str = resp.json()["token"]

        self._api_token = token
        self._api_token_exp = datetime.now() + timedelta(minutes=45)

        return token

    def _auth_headers(self) -> dict:
        api_token: t.Optional[str] = self._api_token
        if not api_token or (
            self._api_token_exp and self._api_token_exp < datetime.now()
        ):
            api_token = self.generate_token()

        return {"Authorization": f"Bearer {api_token}"}

    def _request(
        self,
        *,
        method: str,
        url: str,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Optional[t.Dict[str, t.Any]] = None,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> requests.Response:
        url = urljoin("https://api.flare.io", url)

        netloc: str = urlparse(url).netloc
        if not netloc == "api.flare.io":
            raise Exception(
                f"Client was used to access {netloc=} at {url=}. Only the domain api.flare.io is supported."
            )

        headers = {
            **(headers or {}),
            **self._auth_headers(),
        }

        return self._session.request(
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

    def scroll(
        self,
        *,
        method: t.Literal[
            "GET",
            "POST",
        ],
        url: str,
        params: t.Optional[t.Dict[str, t.Any]] = None,
        json: t.Optional[t.Dict[str, t.Any]] = None,
        headers: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> t.Iterator[requests.Response]:
        if method not in {"GET", "POST"}:
            raise Exception("Scrolling is only supported for GET or POST")

        from_in_params: bool = "from" in (params or {})
        from_in_json: bool = "from" in (json or {})

        if not (from_in_params or from_in_json):
            raise Exception("You must specify from either in params or in json")
        if from_in_params and from_in_json:
            raise Exception("You can't specify from both in params and in json")

        while True:
            resp = self._request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers,
            )
            resp.raise_for_status()

            yield resp

            resp_body = resp.json()

            if "next" not in resp_body:
                raise Exception(
                    "'next' was not found in the response body. Are you sure it supports scrolling?"
                )

            next_page: t.Optional[str] = resp_body["next"]
            if not next_page:
                break

            if params and from_in_params:
                params["from"] = next_page
            if json and from_in_json:
                json["from"] = next_page
