# Software Requirements Specification
**Campus Ignite Management System — 02 Planning Phase**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Software Requirements Specification |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. System Architecture & Environment

Campus Ignite is a Python 3.12+ web application powered by the Django Framework, running in a production container on Render with a serverless PostgreSQL database on Neon.

## 2. Detailed Functional Requirements

Each functional requirement is specified with inputs, processing logic, and expected output.

| SRS ID | Feature Area | Specification & Acceptance Criteria |
| --- | --- | --- |
| SRS-01 | Authentication | Secure PBKDF2 password hashing, session tokens, CSRF protection. |
| SRS-02 | Role Authorization | Role decorators (@role_required) enforce access across admin/pastor/leader/member. |
| SRS-03 | Cell Reports | Auto-populate cell metadata; store headcount, topic, and offerings. |
| SRS-04 | PDF Generation | Modular ReportLab views render printable PDF packets on demand. |
| SRS-05 | Command Palette | Universal Ctrl+K spotlight modal for instant keyboard navigation. |
| SRS-06 | Stat Roll-ups | Vanilla JS count-up animation for numeric dashboard indicators. |

## 3. Non-Functional Requirements

Performance: Page rendering < 500ms; Database query optimization using select_related/prefetch_related.

Security: HTTPS enforcement, Secure cookies, X-Content-Type-Options, X-Frame-Options, CSRF tokens on all POST requests.

Usability: Fully responsive layout supporting viewports from 320px (mobile) to 4K desktop displays.
