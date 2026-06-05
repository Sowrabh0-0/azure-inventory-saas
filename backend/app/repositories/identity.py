from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.identity import OAuthConnection, Tenant, User


class TenantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, azure_tenant_id: str, display_name: str | None = None) -> Tenant:
        tenant = await self.session.scalar(select(Tenant).where(Tenant.azure_tenant_id == azure_tenant_id))
        if tenant:
            return tenant
        tenant = Tenant(azure_tenant_id=azure_tenant_id, display_name=display_name)
        self.session.add(tenant)
        await self.session.flush()
        return tenant


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id_for_tenant(self, user_id: str, tenant_id: str) -> User | None:
        return await self.session.scalar(
            select(User).where(User.id == uuid.UUID(user_id), User.tenant_id == uuid.UUID(tenant_id))
        )

    async def get_or_create(
        self, tenant_id: uuid.UUID, azure_oid: str, email: str, display_name: str | None = None
    ) -> User:
        user = await self.session.scalar(
            select(User).where(User.tenant_id == tenant_id, User.azure_oid == azure_oid)
        )
        if user:
            user.email = email
            user.display_name = display_name
            return user
        user = User(tenant_id=tenant_id, azure_oid=azure_oid, email=email, display_name=display_name)
        self.session.add(user)
        await self.session.flush()
        return user


class OAuthRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_refresh_token(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        encrypted_refresh_token: str,
        scopes: list[str],
    ) -> OAuthConnection:
        connection = await self.session.scalar(
            select(OAuthConnection).where(
                OAuthConnection.tenant_id == tenant_id,
                OAuthConnection.user_id == user_id,
                OAuthConnection.provider == "microsoft",
            )
        )
        if connection is None:
            connection = OAuthConnection(
                tenant_id=tenant_id,
                user_id=user_id,
                provider="microsoft",
                scopes=scopes,
                encrypted_refresh_token=encrypted_refresh_token,
            )
            self.session.add(connection)
        else:
            connection.scopes = scopes
            connection.encrypted_refresh_token = encrypted_refresh_token
        await self.session.flush()
        return connection

