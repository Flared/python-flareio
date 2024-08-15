import requests

from datetime import datetime
from datetime import timedelta


class FlareApiClient:
    def __init__(
        self,
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

        token: str = requests.post(
            "https://api.flare.io/tokens/generate",
            json=payload,
        ).json()["token"]

        self.token = token
        self.token_exp = datetime.now() + timedelta(minutes=45)

        return token
