# Database Design and Data Dictionary
**Campus Ignite Management System — 03 Design & Development**

| Field | Value |
|---|---|
| **Project** | Campus Ignite (Campus Christian Institution) |
| **Document** | Database Design and Data Dictionary |
| **Author / Owner** | Mutsawashe Mwaita (Project Lead & Administrator) |
| **Version & Status** | 1.0 — Production Approved & Operational |

## 1. Relational Schema Architecture

The data model enforces relational integrity with indexed foreign keys, constraints, and optimized query managers.

| Model Name | Table Name | Key Fields & Types | Key Relationships |
| --- | --- | --- | --- |
| CustomUser | accounts_customuser | username (Char), email (Email), role (Char), is_member_only (Bool) | Auth base model |
| Cell | cells_cell | name (Char), meeting_day (Char), time (Time), facilitator (FK) | FK to CustomUser |
| CellMeetingReport | cells_cellmeetingreport | cell (FK), date (Date), head_count (Int), offerings (Dec) | FK to Cell |
| Department | departments_department | name (Char), dept_type (Char), leader (FK) | FK to CustomUser |
| DepartmentMember | departments_departmentmember | department (FK), user (FK), role (Char) | M2M Bridge Table |
| ServiceRecord | services_servicerecord | date (Date), message_title (Char), head_count (Int) | Unique by service |
| Notification | notifications_notification | recipient (FK), title (Char), is_read (Bool) | FK to CustomUser |

## 2. Indexing Strategy

B-tree indexes are applied on `is_member_only`, `recipient`, `is_read`, `date`, and foreign keys to guarantee sub-millisecond query execution.
