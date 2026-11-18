# Test Plan
**Campus Ignite Management System — 04 Testing & Deployment**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Test Plan |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Testing Objectives & Scope

Validates the operational stability, data integrity, and security compliance of Campus Ignite before production releases.

Testing covers unit test cases, form validation, RBAC security decorators, PDF generation, database migrations, and UI responsiveness.

## 2. Test Levels & Strategy

Unit Testing: Testing models, custom querysets, managers, and utility functions in isolation.

Integration Testing: Verifying view response codes, redirects, context variables, and session management.

Security Testing: Validating CSRF protection, RBAC role gating, and credential authorization.
