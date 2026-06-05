from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.azure import AzureResource, Subscription


class AzureInventoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_subscriptions(self, tenant_id: str) -> list[Subscription]:
        result = await self.session.scalars(
            select(Subscription)
            .where(Subscription.tenant_id == uuid.UUID(tenant_id))
            .order_by(Subscription.display_name)
        )
        return list(result)

    async def list_resources(
        self, tenant_id: str, resource_type: str | None = None, resource_group: str | None = None
    ) -> list[AzureResource]:
        stmt = select(AzureResource).where(AzureResource.tenant_id == uuid.UUID(tenant_id))
        if resource_type:
            stmt = stmt.where(AzureResource.resource_type.ilike(resource_type))
        if resource_group:
            stmt = stmt.where(AzureResource.resource_group == resource_group)
        result = await self.session.scalars(stmt.order_by(AzureResource.resource_type, AzureResource.name))
        return list(result)

    async def overview(self, tenant_id: str) -> dict[str, int]:
        tenant_uuid = uuid.UUID(tenant_id)
        subscriptions = await self.session.scalar(
            select(func.count()).select_from(Subscription).where(Subscription.tenant_id == tenant_uuid)
        )
        resources = await self.session.scalar(
            select(func.count()).select_from(AzureResource).where(AzureResource.tenant_id == tenant_uuid)
        )

        async def count_type(resource_type: str) -> int:
            value = await self.session.scalar(
                select(func.count())
                .select_from(AzureResource)
                .where(
                    AzureResource.tenant_id == tenant_uuid,
                    AzureResource.resource_type == resource_type,
                )
            )
            return int(value or 0)

        return {
            "subscriptions": int(subscriptions or 0),
            "resources": int(resources or 0),
            "virtual_machines": await count_type("Microsoft.Compute/virtualMachines"),
            "storage_accounts": await count_type("Microsoft.Storage/storageAccounts"),
            "aks_clusters": await count_type("Microsoft.ContainerService/managedClusters"),
            "key_vaults": await count_type("Microsoft.KeyVault/vaults"),
        }

    async def upsert_subscription(self, tenant_id: uuid.UUID, item: dict) -> Subscription:
        stmt = (
            insert(Subscription)
            .values(
                tenant_id=tenant_id,
                subscription_id=item["subscriptionId"],
                display_name=item["displayName"],
                state=item.get("state", "Unknown"),
                authorization_source=item.get("authorizationSource"),
            )
            .on_conflict_do_update(
                constraint="uq_subscriptions_tenant_subscription",
                set_={
                    "display_name": item["displayName"],
                    "state": item.get("state", "Unknown"),
                    "authorization_source": item.get("authorizationSource"),
                },
            )
            .returning(Subscription)
        )
        return (await self.session.scalars(stmt)).one()

    async def upsert_resource(self, tenant_id: uuid.UUID, subscription_id: uuid.UUID, item: dict) -> None:
        stmt = (
            insert(AzureResource)
            .values(
                tenant_id=tenant_id,
                subscription_id=subscription_id,
                azure_resource_id=item["id"],
                name=item["name"],
                resource_type=item["type"],
                resource_group=_resource_group_from_id(item["id"]),
                location=item.get("location"),
                tags=item.get("tags") or {},
                properties=item.get("properties") or {},
            )
            .on_conflict_do_update(
                constraint="uq_resources_tenant_resource",
                set_={
                    "name": item["name"],
                    "resource_type": item["type"],
                    "resource_group": _resource_group_from_id(item["id"]),
                    "location": item.get("location"),
                    "tags": item.get("tags") or {},
                    "properties": item.get("properties") or {},
                },
            )
        )
        await self.session.execute(stmt)


def _resource_group_from_id(resource_id: str) -> str | None:
    parts = resource_id.split("/")
    lowered = [part.lower() for part in parts]
    if "resourcegroups" not in lowered:
        return None
    return parts[lowered.index("resourcegroups") + 1]

