# Asset and Credentials Handover Document
**Campus Ignite Management System — 06 Closure & Handover**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Asset and Credentials Handover Document |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Digital Assets & Repository Inventory

Primary Source Code Repository: GitHub (`mutsawashemwaita-dev/campus_ignite_FINALE`).

Production Web Service: Render Cloud Platform (`campus-ignite-finale.onrender.com`).

Production Database: Neon Serverless Cloud PostgreSQL.

| Asset Category | Platform / Provider | Access Level Transferred | Primary Contact |
| --- | --- | --- | --- |
| Source Code Repo | GitHub | Admin / Owner | Mutsawashe Mwaita |
| Hosting Environment | Render | Owner / Administrator | Mutsawashe Mwaita |
| Cloud Database | Neon | Owner / Administrator | Mutsawashe Mwaita |
| Domain & DNS | Render Cloud DNS | Managed SSL / DNS | Mutsawashe Mwaita |

## 2. Security & Credentials Handover Protocol

All production credentials (SECRET_KEY, DATABASE_URL) are securely injected as environment variables in Render; never hardcoded in source control.
