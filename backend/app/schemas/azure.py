from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SubscriptionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subscription_id: str
    display_name: str
    state: str
    authorization_source: str | None = None


class AzureResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    azure_resource_id: str
    name: str
    resource_type: str
    resource_group: str | None
    location: str | None
    tags: dict
    properties: dict
    updated_at: datetime


class TenantOverview(BaseModel):
    subscriptions: int
    resources: int
    virtual_machines: int
    storage_accounts: int
    aks_clusters: int
    key_vaults: int

