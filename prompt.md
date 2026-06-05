You are a senior cloud platform engineer and full-stack architect.

Build a production-grade multi-tenant Azure resource inventory SaaS platform using:

Frontend:
- Next.js 15 (App Router)
- TypeScript
- TailwindCSS
- shadcn/ui
- Zustand or React Context
- MSAL Browser SDK

Backend:
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Celery
- Pydantic v2
- JWT validation
- Microsoft Graph API integration
- Azure Resource Manager API integration

Infrastructure:
- Terraform
- Docker
- Docker Compose
- Azure Container Apps OR AKS-ready manifests
- Azure Key Vault integration
- Azure PostgreSQL Flexible Server
- Azure Redis Cache
- Azure Application Registration automation
- Managed Identity support

Goal:
Build a secure multi-tenant SaaS platform where users authenticate using Microsoft OAuth / Entra ID and can view ONLY their own Azure tenant resources for analysis.

==================================================
CORE REQUIREMENTS
==================================================

The platform must:

1. Allow users to sign in using Microsoft OAuth 2.0
2. Support multi-tenant Entra ID authentication
3. Use Authorization Code Flow with PKCE
4. Store:
   - user_id
   - tenant_id
   - email
   - encrypted refresh token
5. Retrieve Azure resources using:
   - Microsoft Graph API
   - Azure Resource Manager API
6. Ensure strict tenant isolation
7. Prevent resource leakage between tenants
8. Support multiple users from different tenants
9. Display Azure resources on frontend dashboard
10. Include secure RBAC validation

==================================================
AUTHENTICATION REQUIREMENTS
==================================================

Use:
- Microsoft Entra ID
- MSAL
- OAuth2 Authorization Code Flow
- OpenID Connect

Required scopes:
- openid
- profile
- email
- offline_access
- User.Read

Azure ARM scope:
- https://management.azure.com/user_impersonation

Graph endpoint:
- https://graph.microsoft.com/

ARM endpoint:
- https://management.azure.com/

The backend must:
- validate JWT tokens
- validate issuer
- validate audience
- validate tenant ID
- extract:
  - tid
  - oid
  - preferred_username
- never trust frontend claims

==================================================
TENANT ISOLATION REQUIREMENTS
==================================================

Every database query MUST be scoped by:
- tenant_id

Every API route MUST:
- validate tenant ownership
- prevent cross-tenant access

Examples:

GOOD:
SELECT * FROM resources WHERE tenant_id = ?

BAD:
SELECT * FROM resources

Users from Tenant A must NEVER see Tenant B resources.

==================================================
FEATURES
==================================================

Build:

1. Authentication
   - Login with Microsoft
   - Logout
   - Session handling
   - Refresh token flow

2. Dashboard
   - Tenant overview
   - Subscription list
   - Resource groups
   - Virtual machines
   - Storage accounts
   - AKS clusters
   - Key Vaults

3. Tenant onboarding
   - Consent flow
   - RBAC validation
   - Subscription discovery

4. Background sync jobs
   - Celery tasks
   - periodic resource sync
   - token refresh handling

5. API Security
   - JWT middleware
   - rate limiting
   - CORS protection
   - secure cookies
   - CSRF considerations

==================================================
DATABASE MODELS
==================================================

Create models for:

tenants
users
subscriptions
azure_resources
oauth_connections
sync_jobs

Include:
- UUID primary keys
- timestamps
- indexes
- foreign keys
- tenant isolation constraints

==================================================
FASTAPI REQUIREMENTS
==================================================

Implement:

/auth/login
/auth/callback
/auth/logout
/auth/me

/api/v1/subscriptions
/api/v1/resources
/api/v1/resource-groups
/api/v1/aks
/api/v1/storage
/api/v1/keyvaults

Use:
- dependency injection
- service layer architecture
- repository pattern
- async SQLAlchemy

==================================================
NEXTJS REQUIREMENTS
==================================================

Implement:
- App Router
- protected routes
- middleware auth guard
- server/client component separation
- dashboard layout
- responsive UI
- loading states
- error boundaries

Pages:
- login
- dashboard
- subscriptions
- resources
- settings

==================================================
MICROSOFT GRAPH INTEGRATION
==================================================

Retrieve:
- organization info
- users
- groups
- tenant metadata

==================================================
AZURE ARM INTEGRATION
==================================================

Retrieve:
- subscriptions
- resource groups
- resources
- AKS clusters
- storage accounts
- key vaults
- VNets

==================================================
SECURITY REQUIREMENTS
==================================================

MANDATORY:

- encrypt refresh tokens
- never expose ARM tokens to frontend
- backend-only ARM calls
- use HTTP-only cookies
- use PKCE
- secure secret management
- no plaintext secrets in code
- RBAC least privilege model

==================================================
TERRAFORM REQUIREMENTS
==================================================

Generate Terraform for:

1. Resource Group
2. Virtual Network
3. Subnets
4. PostgreSQL Flexible Server
5. Redis Cache
6. Key Vault
7. Storage Account
8. Container Apps OR AKS
9. Managed Identity
10. App Registration
11. Application Insights
12. Log Analytics Workspace

Terraform requirements:
- modular structure
- reusable variables
- tfvars support
- outputs
- remote backend support
- environments:
  - dev
  - staging
  - prod

==================================================
DOCKER REQUIREMENTS
==================================================

Generate:
- Dockerfiles
- docker-compose.yml
- multi-stage builds
- production optimizations

==================================================
PROJECT STRUCTURE
==================================================

Generate proper monorepo structure:

/frontend
/backend
/infra
/docs

==================================================
DELIVERABLES
==================================================

Generate:

1. Full project structure
2. Backend implementation
3. Frontend implementation
4. Terraform code
5. Docker setup
6. Database migrations
7. Environment variable examples
8. README.md
9. Architecture diagram (Mermaid)
10. API documentation
11. Authentication flow diagram
12. Tenant isolation explanation

==================================================
CODE QUALITY
==================================================

Requirements:
- production-grade
- typed code
- clean architecture
- reusable modules
- comments where needed
- avoid mock placeholders unless necessary
- secure defaults
- scalable design

==================================================
BONUS FEATURES
==================================================

If possible include:
- Azure Policy analysis
- RBAC visualization
- Cost analysis foundation
- Resource tagging analysis
- CSPM-style inventory engine
- background sync scheduler
- webhook/event support

==================================================
IMPORTANT
==================================================

Do NOT create a toy project.

Generate:
- enterprise-style architecture
- realistic SaaS structure
- scalable backend
- proper security boundaries
- production-ready Terraform patterns

Use latest stable versions for all frameworks and providers.