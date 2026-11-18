# API Specification
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | API Specification |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Internal AJAX & JSON Endpoints

Lightweight AJAX endpoints provide fast tactile feedback without full-page reloads.

| Endpoint URL | HTTP Method | Payload / Parameters | Response Format | Purpose |
| --- | --- | --- | --- | --- |
| /notifications/<id>/read/ | POST | X-CSRFToken header | JSON: {status: 'ok'} | Mark single alert as read |
| /notifications/mark-all-read/ | POST | X-CSRFToken header | JSON: {status: 'ok'} | Mark all user alerts read |
| /calendar/api/events/ | GET | start, end timestamps | JSON: Array of calendar events | Feed events to FullCalendar |
| /cells/api/search/ | GET | q=query_string | JSON: Array of cell results | Quick datalist autocomplete |

## 2. Security & CSRF Enforcement

All POST requests enforce standard Django CSRF token validation via `getCsrf()` extracted from document cookies.
