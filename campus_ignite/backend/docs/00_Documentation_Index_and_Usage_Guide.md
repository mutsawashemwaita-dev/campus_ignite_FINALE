# Documentation Index and Usage Guide
**Campus Ignite Management System — Master Governance Index**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Documentation Index and Usage Guide |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Purpose & Scope

This master documentation index provides the complete reference and navigation structure for all engineering, project management, and governance documentation for the Campus Ignite Management System.

Campus Ignite is an enterprise-grade institutional web platform built for campus ministries, churches, and fellowship networks to coordinate cell fellowships, departments, Sunday services, pastoral oversight, and evangelism outreach.

- Standardized lifecycle documentation following PMI/PMBOK and software engineering standards.
- Complete traceability from Project Initiation through Planning, Design, Testing, Monitoring, and Handover.
- Single source of truth for maintainers, ministry executives, and prospective technical contributors.

## 2. Document Phase Structure & Mapping

The repository is organized into six core sequential phases plus root documentation.

| Phase | Folder Name | Key Deliverables | Status |
| --- | --- | --- | --- |
| Phase 1 | 01_Initiation | Project Charter, Business Case, Stakeholder Register, Feasibility Study | Approved |
| Phase 2 | 02_Planning | Project Plan, Scope & WBS, BRD, SRS, RTM, Schedule, Budget, RACI, Risk, QA | Approved |
| Phase 3 | 03_Design_and_Development | Architecture, Tech Design, DB Schema, API Specs, UI/UX, Security, ADRs | Implemented |
| Phase 4 | 04_Testing_and_Deployment | Test Plan, Test Cases, UAT Plan & Sign-off, Deployment & Rollback, Runbook | Verified |
| Phase 5 | 05_Monitoring_and_Control | Project Status, Minutes, Action Log, Budget Variance, Phase Gate Reviews | Maintained |
| Phase 6 | 06_Closure_and_Handover | Closure Report, Final Acceptance, Lessons Learned, O&M Manual, SLA, Handover | Operational |

## 3. Governance & Change Control

Any modifications to architecture, data models, or production deployment configurations require a formal Change Request (CR) documented in `03_Design_and_Development/11_Change_Request_Form.docx` and tracked in the Change Request Log.

- All code changes must pass the automated Django test suite before merging into master.
- Production releases are automated via Render and Neon PostgreSQL connection pools.
- Documentation must be updated concurrently with major system enhancements.
