import requests_mock

import typing as t

from flareio import FlareApiClient


def get_test_client(
    *,
    tenant_id: t.Optional[int] = None,
    authenticated: bool = True,
    api_domain: t.Optional[str] = None,
    _enable_beta_features: bool = False,
) -> FlareApiClient:
    client = FlareApiClient(
        api_key="test-api-key",
        tenant_id=tenant_id,
        api_domain=api_domain,
        _enable_beta_features=_enable_beta_features,
    )

    if authenticated:
        with requests_mock.Mocker() as mocker:
            mocker.register_uri(
                "POST",
                f"https://{client._api_domain}/tokens/generate",
                json={
                    "token": "test-token-hello",
                },
                status_code=200,
            )
            client.generate_token()

    return client
