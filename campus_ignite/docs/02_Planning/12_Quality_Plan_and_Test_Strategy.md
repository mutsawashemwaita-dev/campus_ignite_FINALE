# Quality Plan and Test Strategy
**Campus Ignite Management System — 02 Planning Phase**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Quality Plan and Test Strategy |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Quality Objectives

100% pass rate on all automated tests prior to master branch merges.

Zero high or critical severity security defects in production.

Full compatibility across modern web browsers (Chrome, Firefox, Safari, Edge, Mobile Safari).

## 2. Multi-Tier Test Strategy

The quality framework incorporates multiple levels of verification.

| Test Level | Scope & Focus | Tooling & Execution |
| --- | --- | --- |
| Unit Testing | Model validations, managers, querysets, PDF helpers | Django TestCase, unittest |
| Integration Testing | Auth views, form submissions, RBAC permissions, redirects | Django Client test harness |
| Static Verification | Static file collection, manifest checks, syntax linting | manage.py collectstatic, flake8 |
| UAT | Pastoral review of reports and member workflows | Live Render staging verification |
