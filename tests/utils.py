import requests_mock

from flareio import FlareApiClient

import typing as t


def get_test_client(
    *,
    tenant_id: t.Optional[int] = None,
    authenticated: bool = True,
) -> FlareApiClient:
    client = FlareApiClient(
        api_key="test-api-key",
        tenant_id=tenant_id,
    )

    if authenticated:
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                "POST",
                "https://api.flare.io/tokens/generate",
                json={
                    "token": "test-token-hello",
                },
                status_code=200,
            )
            client.generate_token()

    return client
