# Scope Statement and WBS
**Campus Ignite Management System — 02 Planning Phase**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Scope Statement and WBS |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Project Scope Description

The Campus Ignite platform encompasses an end-to-end church and campus ministry operations portal. Deliverables include user management, multi-role authorization, cell fellowship reporting, department coordination, service records, calendar scheduling, notification alerts, PDF report generation, and an interactive live dashboard.

- Product Deliverable 1: Core Authentication & RBAC (Admin, Pastor, Leader, Member).
- Product Deliverable 2: Cells Fellowship Hub & Weekly Meeting Reports.
- Product Deliverable 3: Sunday Services Attendance & Headcount Tracking.
- Product Deliverable 4: Ministry Calendar & Event Scheduling.
- Product Deliverable 5: Consolidated Weekly PDF Reporting Engine.
- Product Deliverable 6: Dynamic Live Dashboard with Tactile Micro-Interactions.

## 2. Work Breakdown Structure (WBS)

The WBS decomposes the total project scope into manageable work packages.

| WBS Code | Work Package Name | Key Deliverable |
| --- | --- | --- |
| 1.0 | Project Initiation & Governance | Charter, Business Case, Architecture Selection |
| 2.0 | Core Infrastructure & Models | Django Project Setup, Neon PostgreSQL, WhiteNoise |
| 3.0 | Authentication & Member Accounts | CustomUser Model, Login/Signup, RBAC Middleware |
| 4.0 | Cells & Fellowship Management | Cell Roster, Meeting Reports, Autocomplete Dropdowns |
| 5.0 | Departments & Ministries | Department Memberships, Posts, Calendar Integration |
| 6.0 | Services & Evangelism Hub | Headcount Records, Convert Follow-ups, Scoreboard |
| 7.0 | PDF & Reporting Engine | ReportLab Modularization, Consolidated Reports |
| 8.0 | Interactive Dashboard & Polish | Live Greetings, Counters, Ripple Wave, Quick Jump |
| 9.0 | Testing, Deployment & Handover | Automated Tests, Render CI/CD, Documentation Pack |

## 3. Project Exclusions (Out of Scope)

Direct financial donation payment gateways, custom native iOS/Android mobile apps (web is fully responsive), and physical biometric hardware integration.
