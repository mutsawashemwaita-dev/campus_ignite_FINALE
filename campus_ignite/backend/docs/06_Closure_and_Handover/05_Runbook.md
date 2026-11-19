# Runbook
**Campus Ignite Management System — 06 Closure & Handover**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Runbook |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Standard Operating Procedures (SOPs)

SOP-01: Manual Service Restart on Render — Navigate to Render Dashboard -> Select 'campus-ignite' -> Click 'Manual Deploy' -> 'Deploy latest commit'.

SOP-02: Executing Database Migrations — Connect via Render Shell or run `python manage.py migrate`.

SOP-03: Creating Superuser Account — Run `python manage.py createsuperuser` via terminal shell.

SOP-04: Emergency Database Failover — Update `DATABASE_URL` environment variable with backup connection string.
