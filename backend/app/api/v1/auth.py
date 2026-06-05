from __future__ import annotations

import base64
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    AuthContext,
    encrypt_secret,
    get_current_context,
    sign_session,
    validate_microsoft_jwt,
)
from app.db.session import get_session
from app.repositories.identity import OAuthRepository, TenantRepository, UserRepository
from app.schemas.auth import LoginUrlOut, MeOut
from app.services.microsoft import GraphService, LOGIN_SCOPES, MicrosoftOAuthService

router = APIRouter(prefix="/auth", tags=["auth"])
oauth = MicrosoftOAuthService()


@router.get("/login", response_model=LoginUrlOut)
async def login(response: Response, tenant: str | None = Query(default=None)) -> LoginUrlOut:
    state = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    response.set_cookie("oauth_state", state, httponly=True, secure=settings.cookie_secure, samesite="lax")
    response.set_cookie("pkce_verifier", verifier, httponly=True, secure=settings.cookie_secure, samesite="lax")
    if tenant:
        response.set_cookie("oauth_tenant", tenant, httponly=True, secure=settings.cookie_secure, samesite="lax")
    else:
        response.delete_cookie("oauth_tenant")
    return LoginUrlOut(authorization_url=oauth.authorization_url(state, challenge, tenant))


@router.get("/callback")
async def callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    expected_state = request.cookies.get("oauth_state")
    verifier = request.cookies.get("pkce_verifier")
    requested_tenant = request.cookies.get("oauth_tenant")
    if not expected_state or expected_state != state or not verifier:
        raise HTTPException(status_code=401, detail="Invalid OAuth state")

    tokens = await oauth.exchange_code(code, verifier, requested_tenant)
    if "id_token" not in tokens or "access_token" not in tokens or "refresh_token" not in tokens:
        raise HTTPException(status_code=401, detail="Microsoft did not return required tokens")
    claims = await validate_microsoft_jwt(tokens["id_token"])
    tid = claims["tid"]
    oid = claims["oid"]
    email = claims.get("preferred_username") or claims.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Email claim is missing")

    org = await GraphService().organization(tokens["access_token"])
    tenant = await TenantRepository(session).get_or_create(tid, org.get("displayName"))
    user = await UserRepository(session).get_or_create(
        tenant.id, oid, email, claims.get("name") or claims.get("preferred_username")
    )
    await OAuthRepository(session).upsert_refresh_token(
        tenant.id, user.id, encrypt_secret(tokens["refresh_token"]), LOGIN_SCOPES
    )
    await session.commit()

    session_token = sign_session(
        {
            "user_id": str(user.id),
            "tenant_id": str(tenant.id),
            "azure_tenant_id": tenant.azure_tenant_id,
            "azure_oid": user.azure_oid,
            "email": user.email,
        }
    )
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        settings.session_cookie_name,
        session_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
    )
    response.delete_cookie("oauth_state")
    response.delete_cookie("pkce_verifier")
    response.delete_cookie("oauth_tenant")
    return response


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(settings.session_cookie_name, domain=settings.cookie_domain)
    return {"status": "ok"}


@router.get("/me", response_model=MeOut)
async def me(context: AuthContext = Depends(get_current_context)) -> MeOut:
    return MeOut(**context.__dict__)
