# Security Notes

- Refresh tokens are encrypted with Fernet before storage.
- ARM calls are backend-only.
- Session cookie is HTTP-only.
- PKCE state and verifier are held in HTTP-only cookies during login.
- Every API route derives tenant context from backend session validation.
- NSG SSH access should be restricted to your public IP.
- For public HTTPS testing, terminate TLS in Nginx and set `COOKIE_SECURE=true`.

Dev shortcuts intentionally present:

- PostgreSQL and Redis are containerized on the VM.
- Secrets are stored in `.env` on the VM.
- HTTP is enabled for quick testing.

Move those to managed services and secure secret storage before production.

