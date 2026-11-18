# Operations and Maintenance Manual
**Campus Ignite Management System — 06 Closure & Handover**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Operations and Maintenance Manual |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Daily & Routine Maintenance Procedures

Routine operational tasks required to maintain peak system health:

1. Daily Health Checks: Review Render application logs and Neon database connection metrics.

2. Database Backup Verification: Verify automated daily snapshots on Neon cloud dashboard.

3. Static File Integrity: Ensure collectstatic runs cleanly upon any asset modification.

## 2. Troubleshooting Common Issues

Issue: Web service container enters sleep state on idle.

Remedy: Normal behavior on free tier; waking up takes ~30 seconds on initial request.

Issue: User cannot log in after creation.

Remedy: Check if `is_member_only` is true. Promote member to login user via Edit Person form.
