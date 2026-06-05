from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import AuthContext, get_current_context
from app.db.session import get_session
from app.repositories.azure import AzureInventoryRepository
from app.schemas.azure import AzureResourceOut, SubscriptionOut, TenantOverview

router = APIRouter(prefix="/api/v1", tags=["inventory"])


@router.get("/overview", response_model=TenantOverview)
async def overview(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_session),
) -> TenantOverview:
    return TenantOverview(**await AzureInventoryRepository(session).overview(context.tenant_id))


@router.get("/subscriptions", response_model=list[SubscriptionOut])
async def subscriptions(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_session),
) -> list[SubscriptionOut]:
    return list(await AzureInventoryRepository(session).list_subscriptions(context.tenant_id))


@router.get("/resources", response_model=list[AzureResourceOut])
async def resources(
    resource_type: str | None = Query(default=None),
    resource_group: str | None = Query(default=None),
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_session),
) -> list[AzureResourceOut]:
    return list(
        await AzureInventoryRepository(session).list_resources(
            context.tenant_id, resource_type=resource_type, resource_group=resource_group
        )
    )


@router.get("/resource-groups", response_model=list[AzureResourceOut])
async def resource_groups(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_session),
) -> list[AzureResourceOut]:
    return list(await AzureInventoryRepository(session).list_resources(context.tenant_id))


@router.get("/aks", response_model=list[AzureResourceOut])
async def aks(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_session),
) -> list[AzureResourceOut]:
    return list(
        await AzureInventoryRepository(session).list_resources(
            context.tenant_id, "Microsoft.ContainerService/managedClusters"
        )
    )


@router.get("/storage", response_model=list[AzureResourceOut])
async def storage(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_session),
) -> list[AzureResourceOut]:
    return list(
        await AzureInventoryRepository(session).list_resources(
            context.tenant_id, "Microsoft.Storage/storageAccounts"
        )
    )


@router.get("/keyvaults", response_model=list[AzureResourceOut])
async def keyvaults(
    context: AuthContext = Depends(get_current_context),
    session: AsyncSession = Depends(get_session),
) -> list[AzureResourceOut]:
    return list(
        await AzureInventoryRepository(session).list_resources(context.tenant_id, "Microsoft.KeyVault/vaults")
    )

