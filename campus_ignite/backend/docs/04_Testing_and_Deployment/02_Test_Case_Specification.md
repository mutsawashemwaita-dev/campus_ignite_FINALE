# Test Case Specification
**Campus Ignite Management System — 04 Testing & Deployment**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Test Case Specification |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Automated Test Cases Matrix

The automated test suite exercises 19 distinct test scenarios across all core Django applications.

| Test Case ID | Module | Scenario Description | Expected Result |
| --- | --- | --- | --- |
| TC-ACC-01 | apps.accounts | Congregation member created with is_member_only=True | User cannot authenticate via login form |
| TC-ACC-02 | apps.accounts | Member promoted to login user with password | User successfully authenticates and gains dashboard access |
| TC-CEL-01 | apps.cells | Cell leader creates meeting report via dropdown selector | Report is saved with correct cell FK and attendance count |
| TC-DEP-01 | apps.departments | Department head creates new member via department detail | Member added to department member roster and verified |
| TC-SER-01 | apps.services | Administrator records Sunday service with headcount | Record saved and reflects in dashboard 'Last Service' card |
| TC-EVG-01 | apps.evangelism | Soul winner logs new recruit with follow-up status | Recruit displayed on public evangelism scoreboard |
| TC-PDF-01 | apps.core.pdf | Generate consolidated weekly PDF report | Returns HTTP 200 with application/pdf content type |
