# Coding Standards and Repository Guidelines
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Coding Standards and Repository Guidelines |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Code Standards & Style Conventions

Python code adheres to PEP 8 standards with 120 character line limits.

Django views must implement clear separation of concerns (thin views, rich models/managers).

Frontend HTML templates must avoid inline JavaScript; scripts are organized under `frontend/static/js/`.

## 2. Git Branching & Commit Conventions

Branch Strategy: `master` branch is production-ready and deploys automatically to Render.

Feature Branches: `feature/<name>` for new capabilities, `fix/<name>` for bug fixes.

Commit Messages: Conventional Commits standard (e.g., 'feat: add live dashboard counters', 'fix: resolve db retry timeout').
