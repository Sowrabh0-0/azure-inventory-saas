from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.identity import Tenant
from app.services.sync import InventorySyncService


@celery_app.task(name="app.tasks.sync.sync_tenant")
def sync_tenant(tenant_id: str) -> None:
    async def runner() -> None:
        async with SessionLocal() as session:
            await InventorySyncService(session).sync_tenant(tenant_id)

    asyncio.run(runner())


@celery_app.task(name="app.tasks.sync.sync_all_tenants")
def sync_all_tenants() -> None:
    async def runner() -> None:
        async with SessionLocal() as session:
            tenants = list(await session.scalars(select(Tenant.id)))
        for tenant_id in tenants:
            sync_tenant.delay(str(tenant_id))

    asyncio.run(runner())

