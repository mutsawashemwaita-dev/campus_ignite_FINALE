# Security and Data Protection Plan
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Security and Data Protection Plan |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Authentication & Role-Based Access Control (RBAC)

Strict role hierarchy enforced at both URL routing and view decorators:

1. Administrator: Full system oversight, user management, system configs.

2. Pastor: Access to consolidated reports, pastoral directories, service logging.

3. Cell Leader: Access to assigned cell fellowship and report submissions.

4. Member: Self-service profile, calendar viewing, public directory.

## 2. Data Protection & Defensive Architecture

Password Security: PBKDF2 with SHA-256 and salt.

SQL Injection Defense: Exclusively uses Django ORM parameterized queries; raw SQL strictly prohibited.

XSS Protection: Automatic template context escaping enabled on all user inputs.

CSRF Defense: Cross-Site Request Forgery tokens validated on every state-changing request.
