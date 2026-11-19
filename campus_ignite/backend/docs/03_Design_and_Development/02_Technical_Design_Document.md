# Technical Design Document
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Technical Design Document |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Modular Django Application Architecture

The backend codebase is compartmentalized into discrete Django applications residing under `backend/apps/`:

| App Name | Directory Path | Core Responsibilities |
| --- | --- | --- |
| apps.accounts | backend/apps/accounts | CustomUser, Auth, RBAC, Alumni, Dashboard Views |
| apps.cells | backend/apps/cells | Cell Fellowship Models, Meeting Reports, Autocompletes |
| apps.departments | backend/apps/departments | Department Management, Rosters, Event Scheduling |
| apps.services | backend/apps/services | Sunday Service Records, Sermons, Attendance Stats |
| apps.evangelism | backend/apps/evangelism | Soul Winning Outreach Records, Converts Scoreboard |
| apps.notifications | backend/apps/notifications | Alert Delivery Engine, Birthday Reminder Automation |
| apps.schedule | backend/apps/schedule | FullCalendar Integration, Institutional Calendar |
| apps.core.pdf | backend/apps/core/pdf.py | Modularized ReportLab PDF Canvas & Flowable Helpers |

## 2. Connection Resilience Middleware

`RetryDBConnectionMiddleware` intercepts operational database dropouts common in serverless environments, safely retrying queries up to 3 times with exponential backoff before reporting an error.
