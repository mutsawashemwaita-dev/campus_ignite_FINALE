# Issue Log
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Issue Log |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Technical Issue Tracking Register

Historical register of encountered technical defects and their resolutions.

| Issue ID | Category | Description | Severity | Resolution | Status |
| --- | --- | --- | --- | --- | --- |
| ISS-01 | Database | Neon connection closed abruptly on idle container | High | Implemented RetryDBConnectionMiddleware | Closed |
| ISS-02 | PDF Export | ReportLab canvas overlapping table footer on multi-page | Medium | Adjusted Flowable margins and dynamic page numbering | Closed |
| ISS-03 | Forms | Dropdown querysets evaluated at module import time | Medium | Moved queryset evaluation lazily inside form __init__ | Closed |
| ISS-04 | Mobile UX | Sidebar overlapping dashboard content on small screens | Low | Added off-canvas toggle with responsive backdrop | Closed |
