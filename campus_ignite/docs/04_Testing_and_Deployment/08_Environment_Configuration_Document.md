# Environment Configuration Document
**Campus Ignite Management System — 04 Testing & Deployment**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Environment Configuration Document |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Environment Configuration Dictionary

Configuration variables are managed via decouple (`.env` locally, Render Dashboard environment variables in production).

| Variable Name | Required | Example / Description | Purpose |
| --- | --- | --- | --- |
| SECRET_KEY | Yes | django-insecure-... | Cryptographic signing key |
| DEBUG | Yes | False (in production) | Disables sensitive debug traces |
| DATABASE_URL | Yes | postgresql://user:pass@host/db | Neon PostgreSQL connection string |
| ALLOWED_HOSTS | Yes | campus-ignite-finale.onrender.com, * | Allowed host headers |
| CSRF_TRUSTED_ORIGINS | Yes | https://campus-ignite-finale.onrender.com | Trusted origin for CSRF tokens |
