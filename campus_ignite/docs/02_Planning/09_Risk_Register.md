# Risk Register
**Campus Ignite Management System — 02 Planning Phase**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Risk Register |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Risk Assessment & Matrix

Identified risks are monitored and mitigated according to probability and impact rankings.

| Risk ID | Risk Description | Likelihood | Impact | Mitigation Strategy | Status |
| --- | --- | --- | --- | --- | --- |
| RSK-01 | Render cold start delay on free tier web service | Medium | Medium | Keep-alive ping and lightweight memory footprint | Mitigated |
| RSK-02 | Database connection dropping on serverless Neon | High | High | Implemented RetryDBConnectionMiddleware with 3-attempt reconnect | Resolved |
| RSK-03 | Mobile viewport layout breakage during cell reporting | Low | Medium | Mobile-first CSS responsive breakpoints tested across devices | Mitigated |
| RSK-04 | Unauthorized access to confidential pastoral records | Low | High | Rigorous role-based access decorators and test verification | Secured |

## 2. Contingency Reserves

Automated daily database backups via Neon cloud snapshots ensure zero data loss in disaster recovery scenarios.
