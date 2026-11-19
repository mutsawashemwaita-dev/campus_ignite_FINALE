# Rollback Plan
**Campus Ignite Management System — 04 Testing & Deployment**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Rollback Plan |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Rollback Trigger Criteria

A rollback is immediately triggered if any of the following occur post-deployment:

1. Critical failure preventing user authentication.

2. Fatal database migration failure or corruption.

3. Persistent HTTP 500 error on core dashboard views.

## 2. Rollback Execution Steps

Step 1: Revert master branch commit via `git revert <commit_hash>` and push.

Step 2: If database migrations need reverting: `python manage.py migrate <app_name> <previous_migration_number>`.

Step 3: Trigger manual deploy of the stable release tag on Render.

Step 4: Conduct verification smoke tests and notify stakeholders.
