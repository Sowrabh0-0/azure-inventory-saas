from __future__ import annotations

import uuid
import logging

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_secret
from app.models.identity import OAuthConnection
from app.repositories.azure import AzureInventoryRepository
from app.services.microsoft import ARM_SCOPES, AzureArmService, MicrosoftOAuthService

logger = logging.getLogger(__name__)


class InventorySyncService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.oauth = MicrosoftOAuthService()
        self.arm = AzureArmService()
        self.repo = AzureInventoryRepository(session)

    async def sync_tenant(self, tenant_id: uuid.UUID) -> None:
        if str(tenant_id) == "9188040d-6c67-4c5b-b112-36a304b66dad":
            logger.warning("Skipping ARM sync for Microsoft consumer tenant %s", tenant_id)
            return

        connection = await self.session.scalar(
            select(OAuthConnection).where(OAuthConnection.tenant_id == tenant_id).limit(1)
        )
        if connection is None:
            return
        refresh_token = decrypt_secret(connection.encrypted_refresh_token)
        try:
        tokens = await self.oauth.refresh_access_token(
            refresh_token,
            ARM_SCOPES,
            tenant_id=str(tenant_id),
        )
        except HTTPException as exc:
            logger.error("ARM token refresh failed for tenant %s: %s", tenant_id, exc.detail)
            return
        access_token = tokens["access_token"]
        if tokens.get("refresh_token"):
            connection.encrypted_refresh_token = tokens["refresh_token"]

        for subscription_item in await self.arm.subscriptions(access_token):
            subscription = await self.repo.upsert_subscription(tenant_id, subscription_item)
            for resource in await self.arm.resources(access_token, subscription.subscription_id):
                await self.repo.upsert_resource(tenant_id, subscription.id, resource)
        await self.session.commit()
