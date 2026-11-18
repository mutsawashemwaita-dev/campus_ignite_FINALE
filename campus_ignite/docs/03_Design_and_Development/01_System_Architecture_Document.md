# System Architecture Document
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | System Architecture Document |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Architectural Overview

Campus Ignite follows a clean Multi-Tier Model-View-Template (MVT) architecture powered by Django 5+, decoupled frontend templates, and managed cloud infrastructure.

The presentation tier delivers responsive HTML5/Bootstrap 5.3 views, WhiteNoise handles high-efficiency static assets with caching headers, and Neon PostgreSQL provides resilient persistent storage.

- Presentation Tier: Decoupled templates with dynamic live JS, modal spotlights, and CSS micro-interactions.
- Application Tier: Modular Django apps (accounts, cells, departments, services, evangelism, notifications, schedule).
- Data Tier: Neon Cloud PostgreSQL with connection retry resilience middleware.

## 2. Architecture Diagram & Component Flow

Client Web Browser -> HTTPS TLS 1.3 -> Render Reverse Proxy -> Gunicorn/WSGI -> Django Security & Retry Middleware -> URL Router -> Controller Views -> Model Managers -> PostgreSQL Neon DB.
