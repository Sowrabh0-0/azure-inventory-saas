from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Subscription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "subscription_id", name="uq_subscriptions_tenant_subscription"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    subscription_id: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False)
    authorization_source: Mapped[str | None] = mapped_column(String(128))

    resources: Mapped[list["AzureResource"]] = relationship(back_populates="subscription")


class AzureResource(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "azure_resources"
    __table_args__ = (UniqueConstraint("tenant_id", "azure_resource_id", name="uq_resources_tenant_resource"),)

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("subscriptions.id"), index=True
    )
    azure_resource_id: Mapped[str] = mapped_column(Text, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    resource_group: Mapped[str | None] = mapped_column(String(255), index=True)
    location: Mapped[str | None] = mapped_column(String(128))
    tags: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    subscription: Mapped[Subscription] = relationship(back_populates="resources")

