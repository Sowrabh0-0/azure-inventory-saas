from __future__ import annotations

from pydantic import BaseModel


class LoginUrlOut(BaseModel):
    authorization_url: str


class MeOut(BaseModel):
    user_id: str
    tenant_id: str
    azure_tenant_id: str
    email: str

