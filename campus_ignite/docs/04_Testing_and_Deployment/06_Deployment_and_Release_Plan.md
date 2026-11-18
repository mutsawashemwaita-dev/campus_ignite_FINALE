# Deployment and Release Plan
**Campus Ignite Management System — 04 Testing & Deployment**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Deployment and Release Plan |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Production Release Pipeline

Campus Ignite is deployed to Render cloud hosting via automated git-triggered continuous deployment.

Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`

Start Command: `gunicorn backend.campus_ignite_project.wsgi:application`

## 2. Post-Deployment Smoke Tests

Verify HTTP 200 on landing page and dashboard.

Verify WhiteNoise serves CSS and JS assets with valid caching headers.

Verify database connection pool to Neon PostgreSQL.
