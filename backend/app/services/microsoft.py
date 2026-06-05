from __future__ import annotations

from urllib.parse import urlencode

import httpx
from fastapi import HTTPException

from app.core.config import settings

LOGIN_SCOPES = [
    "openid",
    "profile",
    "email",
    "offline_access",
    "User.Read",
]

ARM_SCOPES = ["https://management.azure.com//user_impersonation"]


class MicrosoftOAuthService:
    def authorization_url(self, state: str, code_challenge: str) -> str:
        query = urlencode(
            {
                "client_id": settings.microsoft_client_id,
                "response_type": "code",
                "redirect_uri": settings.microsoft_redirect_uri,
                "response_mode": "query",
                "scope": " ".join(LOGIN_SCOPES),
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": "S256",
                "prompt": "select_account",
            }
        )
        return f"{settings.microsoft_authority}/oauth2/v2.0/authorize?{query}"

    async def exchange_code(self, code: str, code_verifier: str) -> dict:
        token_url = f"{settings.microsoft_authority}/oauth2/v2.0/token"
        data = {
            "client_id": settings.microsoft_client_id,
            "client_secret": settings.microsoft_client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.microsoft_redirect_uri,
            "code_verifier": code_verifier,
            "scope": " ".join(LOGIN_SCOPES),
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()

    async def refresh_access_token(self, refresh_token: str, scopes: list[str] | None = None) -> dict:
        token_url = f"{settings.microsoft_authority}/oauth2/v2.0/token"
        data = {
            "client_id": settings.microsoft_client_id,
            "client_secret": settings.microsoft_client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": " ".join(scopes or LOGIN_SCOPES),
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(token_url, data=data)
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=response.json())
            response.raise_for_status()
            return response.json()


class GraphService:
    async def organization(self, access_token: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{settings.graph_base_url}/organization",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code in {400, 401, 403}:
                return {}
            response.raise_for_status()
            data = response.json()
            return data["value"][0] if data.get("value") else {}


class AzureArmService:
    api_version = "2022-12-01"

    async def subscriptions(self, access_token: str) -> list[dict]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.get(
                f"{settings.arm_base_url}/subscriptions?api-version=2022-12-01",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json().get("value", [])

    async def resources(self, access_token: str, subscription_id: str) -> list[dict]:
        url = (
            f"{settings.arm_base_url}/subscriptions/{subscription_id}/resources"
            "?api-version=2021-04-01"
        )
        resources: list[dict] = []
        async with httpx.AsyncClient(timeout=90) as client:
            while url:
                response = await client.get(url, headers={"Authorization": f"Bearer {access_token}"})
                response.raise_for_status()
                payload = response.json()
                resources.extend(payload.get("value", []))
                url = payload.get("nextLink")
        return resources
