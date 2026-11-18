# Go Live Checklist
**Campus Ignite Management System — 04 Testing & Deployment**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Go Live Checklist |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Production Cutover Verification Checklist

The following verification steps were executed prior to declaring production go-live:

| Checklist Item | Responsible Owner | Verification Result |
| --- | --- | --- |
| Production Neon DB connected and migrated | DevOps Lead | Verified (All migrations applied) |
| WhiteNoise static compression verified | Frontend Lead | Verified (131 static assets collected) |
| Automated test suite green (19/19) | QA Lead | Verified (100% pass) |
| HTTPS TLS certificate active on Render | Security Lead | Verified (Valid SSL certificate) |
| Default administrator superuser provisioned | Project Lead | Verified (Admin account active) |
| Live interactive dashboard operational | UI Lead | Verified (Counters & search live) |
