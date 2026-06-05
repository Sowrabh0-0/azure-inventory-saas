from __future__ import annotations

import base64
import json
import time
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from cryptography.fernet import Fernet
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from jwt import PyJWKClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_session
from app.repositories.identity import UserRepository

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    user_id: str
    tenant_id: str
    azure_tenant_id: str
    azure_oid: str
    email: str


def encrypt_secret(value: str) -> str:
    return Fernet(settings.token_encryption_key.encode()).encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    return Fernet(settings.token_encryption_key.encode()).decrypt(value.encode()).decode()


def sign_session(payload: dict[str, Any]) -> str:
    claims = {**payload, "iat": int(time.time()), "exp": int(time.time()) + 3600 * 8}
    return jwt.encode(claims, settings.jwt_signing_key, algorithm="HS256")


def decode_session(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_signing_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc


async def validate_microsoft_jwt(access_token: str) -> dict[str, Any]:
    try:
        header = jwt.get_unverified_header(access_token)
        unverified = jwt.decode(access_token, options={"verify_signature": False})
        issuer = unverified.get("iss")
        tenant_id = unverified.get("tid") or "consumers"
        if not issuer or not issuer.startswith("https://login.microsoftonline.com/"):
            raise HTTPException(status_code=401, detail="Token issuer is not supported")
        jwks_url = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
        jwk_client = PyJWKClient(jwks_url)
        signing_key = jwk_client.get_signing_key(header["kid"]).key
        claims = jwt.decode(
            access_token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.microsoft_audience,
            issuer=issuer,
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid Microsoft token") from exc

    claims["tid"] = claims.get("tid") or tenant_id
    claims["oid"] = claims.get("oid") or claims.get("sub")
    if not claims.get("oid"):
        raise HTTPException(status_code=401, detail="Required subject claim is missing")
    return claims


async def get_current_context(
    request: Request, session: AsyncSession = Depends(get_session)
) -> AuthContext:
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    claims = decode_session(token)
    repo = UserRepository(session)
    user = await repo.get_by_id_for_tenant(claims["user_id"], claims["tenant_id"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session user not found")
    return AuthContext(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        azure_tenant_id=user.tenant.azure_tenant_id,
        azure_oid=user.azure_oid,
        email=user.email,
    )


async def fetch_json_with_bearer(url: str, token: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(url, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
        return response.json()
