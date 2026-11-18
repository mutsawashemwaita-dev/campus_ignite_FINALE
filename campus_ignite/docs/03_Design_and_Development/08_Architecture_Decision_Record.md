# Architecture Decision Record
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Architecture Decision Record |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. ADR-001: Neon Serverless PostgreSQL Adoption

Context: Initial local development used MySQL; production required a reliable cloud DB.

Decision: Adopt Neon Serverless PostgreSQL configured via `DATABASE_URL` with connection pooling.

Consequences: Highly reliable production uptime, automated backups, zero hosting fee.

## 2. ADR-002: Modularization of ReportLab PDF Engine

Context: PDF generation was previously duplicated across multiple views.

Decision: Centralize shared ReportLab canvas, headers, footers, and styles into `apps/core/pdf.py`.

Consequences: Eliminated code duplication, enabled consistent church branding across all PDF exports.

## 3. ADR-003: Member Decoupling Architecture

Context: Church members who do not need platform login credentials were previously forced to have mock passwords.

Decision: Add `is_member_only` boolean flag and manager querysets to separate system users from congregation members.

Consequences: Simplified user management and seamless promotion of members to login users.
