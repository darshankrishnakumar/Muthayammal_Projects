# 📋 Academic Integration Tool (AIT) — Master Website Testing Plan

> **Document Version:** 1.0.0  
> **Target System:** Academic Integration Tool (Split-Hosting Architecture)  
> **Audience:** Quality Assurance (QA) & Software Testing Team  
> **Author:** Antigravity Engineering Team  
> **Classification:** Confidential / Internal Testing Specification  

---

## 📑 Table of Contents

1. [Executive Summary & System Architecture Matrix](#1-executive-summary--system-architecture-matrix)
2. [Master Test Accounts & Credential Matrix](#2-master-test-accounts--credential-matrix)
3. [Phased Testing Execution Order](#3-phased-testing-execution-order)
4. [Detailed Testing Tasks (Task 1 to Task 21)](#4-detailed-testing-tasks)
   - [TASK 1: Application & Environment Testing](#task-1--application--environment-testing)
   - [TASK 2: Page & Route Navigation Testing](#task-2--page--route-navigation-testing)
   - [TASK 3: Registration & Onboarding Testing](#task-3--registration--onboarding-testing)
   - [TASK 4: Login & Authentication Testing](#task-4--login--authentication-testing)
   - [TASK 5: Role & Permission Matrix Testing](#task-5--role--permission-matrix-testing)
   - [TASK 6: Admin & Super Admin Management Testing](#task-6--admin--super-admin-management-testing)
   - [TASK 7: User & Researcher Feature Testing](#task-7--user--researcher-feature-testing)
   - [TASK 8: Form & Validation Engine Testing](#task-8--form--validation-engine-testing)
   - [TASK 9: Core Module & Workflow Testing](#task-9--core-module--workflow-testing)
   - [TASK 10: Full CRUD Matrix Testing](#task-10--full-crud-matrix-testing)
   - [TASK 11: REST API Specification Testing](#task-11--rest-api-specification-testing)
   - [TASK 12: Database Integrity & Schema Testing](#task-12--database-integrity--schema-testing)
   - [TASK 13: Security & Access Control Testing](#task-13--security--access-control-testing)
   - [TASK 14: UI / UX & Micro-Interactions Testing](#task-14--ui--ux--micro-interactions-testing)
   - [TASK 15: Responsive & Cross-Device Layout Testing](#task-15--responsive--cross-device-layout-testing)
   - [TASK 16: Cross-Browser & OS Compatibility Testing](#task-16--cross-browser--os-compatibility-testing)
   - [TASK 17: Error Handling & Boundary Condition Testing](#task-17--error-handling--boundary-condition-testing)
   - [TASK 18: Screenshot, Watermarking & Copy/Paste Security Testing](#task-18--screenshot-watermarking--copypaste-security-testing)
   - [TASK 19: End-to-End Real-World Scenario Testing](#task-19--end-to-end-real-world-scenario-testing)
   - [TASK 20: Regression Testing Protocol](#task-20--regression-testing-protocol)
   - [TASK 21: Final Acceptance & Production Readiness Testing](#task-21--final-acceptance--production-readiness-testing)
5. [Standard Bug Reporting Format & Severity Guidelines](#5-standard-bug-reporting-format--severity-guidelines)
6. [Master Test Execution Tracker](#6-master-test-execution-tracker)
7. [Final QA Sign-Off Checklist](#7-final-qa-sign-off-checklist)

---

## 1. Executive Summary & System Architecture Matrix

The **Academic Integration Tool (AIT)** is a secure, role-governed platform designed for academic project collaboration, requirement lifecycle tracking, file asset versioning, and marketplace transactions.

### Architecture Overview
- **Frontend SPA**: React 19 + Vite 8 + React Router v7 + Lucide React + Tailwind/Vanilla CSS Design System.
- **Backend Service**: Java 17 + Spring Boot 3.2.0 + Spring Security + JJWT + Hibernate ORM + HikariCP Connection Pool.
- **Database Layer**: MySQL 8.0 with Flyway Database Migration Engine (`V1` to `V12` schemas).
- **Public Tunnel Gateway**: Cloudflare HTTP/2 Tunnel Proxy bridging remote cloud frontend with local backend.

```
┌──────────────────────────────────────────────────────────┐
│                   Vercel Cloud Frontend                  │
│       https://academic-integration-tool.vercel.app       │
└────────────────────────────┬─────────────────────────────┘
                             │ HTTPS / REST (JSON + JWT)
                             ▼
┌──────────────────────────────────────────────────────────┐
│              Cloudflare Public Gateway Tunnel            │
│       https://creator-grants-leaders-delhi.trycloudflare.com
└────────────────────────────┬─────────────────────────────┘
                             │ Local Port Forward (8080)
                             ▼
┌──────────────────────────────────────────────────────────┐
│              Spring Boot 3.2.0 REST Backend              │
│                  http://localhost:8080                   │
└────────────────────────────┬─────────────────────────────┘
                             │ JDBC / HikariCP Pool (3306)
                             ▼
┌──────────────────────────────────────────────────────────┐
│                  MySQL 8.0 (academic_db)                 │
│              Local Service: MySQL80 on Port 3306         │
└──────────────────────────────────────────────────────────┘
```

---

## 2. Master Test Accounts & Credential Matrix

The testing team must utilize the following accounts configured within the local database and mock fallbacks:

| Role Identifier | Email Address | Password | Intended Test Usage | Access Scope |
| :--- | :--- | :--- | :--- | :--- |
| **SUPER_ADMIN** | `superadmin@academic.com` | `Superadmin123!` | Global Governance & Audit | Full platform rights, admin creation, access control matrices, system audit logs |
| **ADMIN (Assigned)** | `testadmin1@gmail.com` / `admin@academic.com` | `Admin123!` | Project & Requirement Admin | Project approval, team assignment, folder/file management, user status toggle |
| **PROJECT_DEVELOPER** | `developer@academic.com` | `Dev12345!` | Technical Execution | Developer workspace, sprint deliverables, asset uploads |
| **USER (Researcher)** | `testuser1@gmail.com` / `user@academic.com` | `User123!` | Academic Client / Researcher | Requirement submission, assigned project viewing, marketplace orders, watermarked file viewer |

> ⚠️ **Note for Testers:** When creating new users during registration testing, default OTP for mock mode is `123456`. In live mode, ensure the user record in table `user_management` has `email_verified = 1` and `status = 0` (`ACTIVE`).

---

## 3. Phased Testing Execution Order

To prevent false negatives caused by prerequisite dependencies, execute all testing tasks strictly in the following sequential order:

```
[Phase 1: Environment & Connectivity]
  └─► TASK 1: Application & Environment Testing
        │
[Phase 2: Authentication & Routing Security]
  ├─► TASK 2: Page & Route Navigation Testing
  ├─► TASK 3: Registration & Onboarding Testing
  ├─► TASK 4: Login & Authentication Testing
  └─► TASK 5: Role & Permission Matrix Testing
        │
[Phase 3: Role-Specific Capabilities & Forms]
  ├─► TASK 6: Admin & Super Admin Management Testing
  ├─► TASK 7: User & Researcher Feature Testing
  └─► TASK 8: Form & Validation Engine Testing
        │
[Phase 4: Core Engine & Data Operations]
  ├─► TASK 9: Core Module & Workflow Testing
  ├─► TASK 10: Full CRUD Matrix Testing
  ├─► TASK 11: REST API Specification Testing
  └─► TASK 12: Database Integrity & Schema Testing
        │
[Phase 5: Security & Platform Hardening]
  ├─► TASK 13: Security & Access Control Testing
  ├─► TASK 14: UI / UX & Micro-Interactions Testing
  ├─► TASK 15: Responsive & Cross-Device Layout Testing
  ├─► TASK 16: Cross-Browser & OS Compatibility Testing
  ├─► TASK 17: Error Handling & Boundary Condition Testing
  └─► TASK 18: Screenshot, Watermarking & Copy/Paste Security Testing
        │
[Phase 6: Verification & Acceptance]
  ├─► TASK 19: End-to-End Real-World Scenario Testing
  ├─► TASK 20: Regression Testing Protocol
  └─► TASK 21: Final Acceptance & Production Readiness Testing
```

---

## 4. Detailed Testing Tasks

---

### TASK 1 — Application & Environment Testing

- **Task ID:** `TASK-01`
- **Task Name:** Application & Environment Infrastructure Verification
- **Objective:** Verify that local database, Spring Boot backend, Cloudflare gateway, and Vite frontend build are active, healthy, and communicating without network failures.
- **Pages/Modules to Test:** Terminal environment, Localhost ports (`3306`, `8080`), Cloudflare Tunnel URL, Vercel frontend.
- **Test Account/Role:** System Engineer / QA Lead.
- **Preconditions:** MySQL service `MySQL80` started, Spring Boot jar started, tunnel daemon active.
- **Step-by-Step Instructions:**
  1. Verify MySQL service status: Run `Get-Service MySQL80` and ensure state is `Running`.
  2. Verify database connection: Check connectivity on port `3306`.
  3. Verify backend process: Send a GET request to `http://localhost:8080/api/auth/me` or `/api/requirements` and check response status.
  4. Verify Cloudflare tunnel: Send a GET request through `https://<tunnel-subdomain>.trycloudflare.com/api/requirements`.
  5. Check database schema migrations: Query table `academic_db.flyway_schema_history` to verify all 12 migration scripts (`V1` to `V12`) are applied with status `SUCCESS`.
- **Expected Result:** All services listen on designated ports; the public gateway forwards traffic to port `8080` with HTTP/2 and returns JSON responses.
- **What to Verify:** No connection timeouts, no Hikari connection pool exhaustion, no Flyway checksum errors.
- **Evidence Required:** Terminal port status screenshot, Flyway table query result, HTTP 200 response headers.
- **Pass Criteria:** MySQL, Backend, and Tunnel respond with HTTP 200 within < 1000ms.
- **Failure Criteria:** Port closed, connection refused, or Flyway migration failure.
- **Priority:** `BLOCKER`

---

### TASK 2 — Page & Route Navigation Testing

- **Task ID:** `TASK-02`
- **Task Name:** Complete Route Resolution and Deep Linking
- **Objective:** Test every client-side route defined in `App.jsx`, ensuring unauthorized guests are redirected to `/login`, authenticated users are routed to their designated workspaces, and invalid URLs redirect cleanly.
- **Pages/Modules to Test:** All 16 registered routes:
  - `/login`, `/register`, `/dashboard`, `/developer/workspace`, `/admin/project-review`, `/marketplace`, `/orders`, `/projects`, `/projects/:id`, `/projects/:id/folders/:folderId`, `/project-files`, `/requirements`, `/requirements/new`, `/requirements/:id`, `/requirements/:id/edit`, `/users`, `/admins`, `/audit-logs`, `/profile`.
- **Test Account/Role:** Unauthenticated Guest, `SUPER_ADMIN`, `ADMIN`, `USER`.
- **Preconditions:** Application accessible in browser.
- **Step-by-Step Instructions:**
  1. Access `http://localhost:5173/` or `https://academic-integration-tool.vercel.app/` without an active session. Verify redirect to `/login`.
  2. Attempt to navigate directly to `/dashboard`, `/projects`, `/admins`, `/orders`. Verify automatic bounce to `/login`.
  3. Log in as `user@academic.com`.
  4. Manually type `http://localhost:5173/admins` in address bar. Verify **"Access Denied"** card displays stating role `USER` does not possess clearance.
  5. Navigate to `/projects/1` and `/requirements/101`. Verify dynamic parameter components load correctly.
  6. Enter an undefined route such as `/unknown-route-999`. Verify fallback redirect to `/dashboard`.
- **Expected Result:** Protected routes block unauthorized access; allowed roles load respective page layouts without white-screen or infinite loading loops.
- **What to Verify:** ProtectedLayout shell (Navbar + Sidebar + Notification Drawer) renders properly on protected pages.
- **Evidence Required:** Browser screenshots of route transitions, Access Denied screen, and address bar URLs.
- **Pass Criteria:** 100% of routes resolve as declared in the security route table without console errors.
- **Failure Criteria:** Unauthenticated user views private data, or white-screen error occurs on refresh.
- **Priority:** `CRITICAL`

---

### TASK 3 — Registration & Onboarding Testing

- **Task ID:** `TASK-03`
- **Task Name:** User Registration & OTP Lifecycle Verification
- **Objective:** Validate end-to-end user self-registration, field input validations, duplicate account prevention, password strength constraints, and OTP verification flow.
- **Pages/Modules to Test:** `/register` (`Register.jsx`).
- **Test Account/Role:** New test candidate (`testuser_new@academic.com`).
- **Preconditions:** User is logged out.
- **Step-by-Step Instructions:**
  1. Navigate to `/register`.
  2. Attempt submission with empty form. Verify individual field error alerts for Full Name, Email, Mobile, Password.
  3. Enter mismatched passwords (e.g. `Pass1234!` vs `Pass5678!`). Verify confirmation error.
  4. Enter an already registered email (`user@academic.com`). Submit form. Verify duplicate account warning message.
  5. Enter valid details: Full Name `Test QA User`, Email `testuser_new@academic.com`, Mobile `+1234567890`, Organization `Academic QA Labs`, Password `UserTest123!`.
  6. Submit form. Verify transition to OTP verification modal/screen.
  7. Enter incorrect OTP `999999`. Verify invalid code error.
  8. Click **"Resend OTP"** button. Verify resend countdown timer triggers.
  9. Enter valid OTP `123456`. Verify success toast and automatic redirection to `/dashboard` with active session.
- **Expected Result:** Valid registration creates an active record in `user_management` with role `USER`, `status = ACTIVE`, and `email_verified = true`.
- **What to Verify:** Database record populated with encrypted password (BCrypt hash); JWT token saved in `localStorage`.
- **Evidence Required:** Registration UI screenshots, OTP screen, database select query output (`SELECT email, role, status, email_verified FROM user_management WHERE email='testuser_new@academic.com'`).
- **Pass Criteria:** Account successfully onboarded and logged in without manual DB intervention.
- **Failure Criteria:** Duplicate accounts permitted, plain-text password stored, or OTP bypass permitted.
- **Priority:** `HIGH`

---

### TASK 4 — Login & Authentication Testing

- **Task ID:** `TASK-04`
- **Task Name:** JWT Authentication, Session Clearance & Logout Lifecycle
- **Objective:** Verify user authentication against BCrypt hashes, token storage in `localStorage`, session restoration across page reloads, and token invalidation on logout.
- **Pages/Modules to Test:** `/login` (`Login.jsx`), `AuthContext.jsx`, `api.js`.
- **Test Account/Role:** `superadmin@academic.com`, `admin@academic.com`, `user@academic.com`, `testuser1@gmail.com`.
- **Preconditions:** Backend running on port 8080 with seeded accounts.
- **Step-by-Step Instructions:**
  1. Navigate to `/login`.
  2. Test Case `TC-AUTH-001`: Submit valid credentials for Super Admin (`superadmin@academic.com` / `Superadmin123!`). Verify login success and redirect to `/dashboard`.
  3. Test Case `TC-AUTH-002`: Submit incorrect password (`WrongPass!`). Verify error banner: *"Invalid email or password"*.
  4. Test Case `TC-AUTH-003`: Submit unregistered email (`ghost_user@academic.com`). Verify error message.
  5. Test Case `TC-AUTH-004`: Toggle the password visibility eye icon. Verify password switches between masked (`••••••`) and plain text.
  6. Test Case `TC-AUTH-005`: Check `localStorage.getItem('token')` in DevTools Console. Verify standard JWT structure (`header.payload.signature`).
  7. Test Case `TC-AUTH-006`: Refresh the page. Verify user remains logged in without re-entering credentials.
  8. Test Case `TC-AUTH-007`: Click **Logout** button from the user profile dropdown. Verify token is purged and user is redirected to `/login`.
  9. Test Case `TC-AUTH-008`: Click browser **Back** button after logout. Verify protected dashboard does not load from cache.
- **Expected Result:** Authentication succeeds only with valid credentials; JWT is verified on every API request; session terminates cleanly on logout.
- **What to Verify:** HTTP request headers include `Authorization: Bearer <jwt_token>` for all subsequent calls.
- **Evidence Required:** Login network payload screenshot, token in Application tab, response JSON with user profile object.
- **Pass Criteria:** Secure token management and error handling across all test credentials.
- **Failure Criteria:** Login allowed with wrong password, token leaks in URL, or back button exposes protected state.
- **Priority:** `BLOCKER`

---

### TASK 5 — Role & Permission Matrix Testing

- **Task ID:** `TASK-05`
- **Task Name:** Role-Based Access Control (RBAC) & Clearance Enforcement
- **Objective:** Validate strict boundary isolation across `SUPER_ADMIN`, `ADMIN`, `PROJECT_DEVELOPER`, and `USER` roles.
- **Pages/Modules to Test:** Sidebar navigation links, route guards, action buttons across all pages.
- **Test Account/Role:** Matrix across all 4 user roles.
- **Preconditions:** 4 distinct active accounts available.
- **Step-by-Step Instructions:**
  1. Log in as `USER` (`user@academic.com`):
     - Verify Sidebar only shows: Dashboard, Marketplace, Orders, Projects, Requirements, Project Files, Profile.
     - Verify Sidebar **DOES NOT** show: Admin Management, User Management, Audit Logs, Developer Workspace.
     - Navigate directly to `/admins`. Verify **Access Denied** page.
     - On `/projects/:id`, verify **"Create Folder"** and **"Assign Developer"** buttons are hidden.
  2. Log in as `ADMIN` (`admin@academic.com` / `testadmin1@gmail.com`):
     - Verify Sidebar displays: User Management, Audit Logs, Project Review, Projects, Requirements.
     - Verify Sidebar **DOES NOT** show: Admin Management (`/admins` is exclusive to Super Admin).
  3. Log in as `PROJECT_DEVELOPER` (`developer@academic.com`):
     - Verify access to `/developer/workspace` and `/projects`.
  4. Log in as `SUPER_ADMIN` (`superadmin@academic.com`):
     - Verify access to all 16 pages including `/admins`, `/users`, `/audit-logs`, and system access control presets.
- **Expected Result:** UI elements, routes, and backend endpoints enforce role restrictions strictly according to the clearance matrix.
- **What to Verify:** Backend returns HTTP 403 Forbidden if a `USER` calls admin endpoints (`POST /api/users` or `POST /api/projects`).
- **Evidence Required:** Side-by-side screenshots of Sidebar for each role; 403 Forbidden API network logs.
- **Pass Criteria:** Zero privilege escalation possible from UI or direct API invocation.
- **Failure Criteria:** User accessing admin views or executing unauthorized CRUD operations.
- **Priority:** `CRITICAL`

---

### TASK 6 — Admin & Super Admin Management Testing

- **Task ID:** `TASK-06`
- **Task Name:** Admin Coordinator Provisioning, Permission Matrix & Preset Engine
- **Objective:** Test Super Admin abilities to manage Admin accounts, configure granular permission matrices (`AdminPermission`), assign users to admins (`AdminUserAssignment`), and apply Access Control Presets.
- **Pages/Modules to Test:** `/admins` (`AdminManagement.jsx`), `AdminPermissionManagerModal.jsx`, `AdminAccessControlModal.jsx`.
- **Test Account/Role:** `superadmin@academic.com`.
- **Preconditions:** Super Admin session active.
- **Step-by-Step Instructions:**
  1. Navigate to `/admins`.
  2. Verify table lists all Admin coordinators with columns: Admin Name, Email, Status, Assigned Users count, Permissions summary, Actions.
  3. Click **"Create New Admin"**. Fill in details: Name `Coordinator Alpha`, Email `coord_alpha@academic.com`, Password `AdminPass123!`. Submit form.
  4. Verify new Admin appears in the registry.
  5. Click **"Manage Permissions"** icon for an Admin.
  6. Toggle specific granular permissions: `PROJECT_ASSIGNMENT_MANAGEMENT`, `REQUIREMENT_REVIEW`, `USER_MANAGEMENT`. Click **Save Permissions**.
  7. Open **"Access Control Preset Engine"** modal (`AdminAccessControlModal.jsx`):
     - Select target Admin.
     - Select Data Scope: `ASSIGNED_ONLY` or `ALL_STUDENTS_TEACHERS`.
     - Select Predefined Preset: *Standard Coordinator*, *Full Governance*, or *Auditor Mode*.
     - Verify preview updates dynamically.
     - Click **"Apply Preset Configuration"**.
  8. Click **"Assign Users"** icon. Select students/researchers to assign to this Admin. Save assignments.
- **Expected Result:** Granular permissions and presets are written to `admin_permissions` and `admin_user_assignments` tables in MySQL without foreign key or unique constraint violations.
- **What to Verify:** Admin logging in with restricted scope only sees assigned users on `/users` and `/projects`.
- **Evidence Required:** Admin Management table screenshot, Access Control Modal screenshot, SQL query output for `admin_permissions`.
- **Pass Criteria:** Presets and permissions apply cleanly and alter Admin visibility as expected.
- **Failure Criteria:** Preset application fails with 500 error or permissions fail to persist.
- **Priority:** `HIGH`

---

### TASK 7 — User & Researcher Feature Testing

- **Task ID:** `TASK-07`
- **Task Name:** Researcher Requirement Submission, Project File Access & Profile Management
- **Objective:** Verify academic researcher workflows including submitting requirements, tracking status changes, browsing project folders, and viewing documents via the secure viewer.
- **Pages/Modules to Test:** `/requirements/new`, `/requirements`, `/projects`, `/projects/:id`, `/profile`.
- **Test Account/Role:** `user@academic.com` / `testuser1@gmail.com`.
- **Preconditions:** Researcher session active.
- **Step-by-Step Instructions:**
  1. Navigate to `/requirements/new`.
  2. Fill requirement form: Title `AI Automated Thesis Checker`, Description `Machine learning pipeline to verify academic citations`, Budget `12000`, Tech Stack `Python, PyTorch, React`.
  3. Submit requirement. Verify requirement appears in `/requirements` with status `DRAFT` or `SUBMITTED`.
  4. Navigate to `/projects`. Verify only assigned projects are displayed.
  5. Click on an assigned project (e.g. `PRJ-8F3A21`).
  6. Browse folder tree: `01_Planning` ➡️ `SRS Documents`.
  7. Click on an asset (`System_Requirements_Specification.pdf`).
  8. Verify file opens in `SecureFileViewer` with dynamic user watermark overlay.
  9. Navigate to `/profile`. Update Full Name or Mobile Number. Save changes. Verify profile reflects updates immediately.
- **Expected Result:** Researcher can submit requirements, view assigned projects, inspect project files in watermarked mode, and update their profile.
- **What to Verify:** Researcher cannot view unassigned projects or unassigned folder assets.
- **Evidence Required:** Requirement creation confirmation screenshot, Secure Viewer rendering screenshot, Profile update confirmation.
- **Pass Criteria:** All researcher self-service actions operate smoothly without permission errors.
- **Failure Criteria:** User cannot submit requirements, or unauthorized files are visible.
- **Priority:** `HIGH`

---

### TASK 8 — Form & Validation Engine Testing

- **Task ID:** `TASK-08`
- **Task Name:** Input Validation, Boundary Values & Sanitization
- **Objective:** Test client-side and server-side validation rules across all input forms in the application.
- **Pages/Modules to Test:**
  - Requirement Form (`/requirements/new`)
  - User Registration Form (`/register`)
  - User Edit Modal (`/users`)
  - Admin Creation Form (`/admins`)
  - Folder Creation Modal (`/projects/:id`)
  - Marketplace Checkout Modal (`/marketplace`)
- **Test Account/Role:** `USER`, `ADMIN`, `SUPER_ADMIN`.
- **Preconditions:** Logged in with appropriate roles for each form.
- **Step-by-Step Instructions:**
  1. **Requirement Form Validation**:
     - Test Title with 1 character (Min length violation). Verify error message.
     - Test Budget with negative number `-500` or non-numeric string `abc`. Verify validation alert.
     - Test Title with 300+ characters (Max length boundary).
     - Test Description containing HTML/Script tags (`<script>alert(1)</script>`). Verify sanitization.
  2. **Registration Form Validation**:
     - Test invalid email formats (`user@`, `user@domain`, `@domain.com`). Verify email regex validation.
     - Test Mobile Number with alphabets (`+123ABC456`). Verify numeric constraint.
     - Test Password with less than 8 characters or missing uppercase/numbers.
  3. **Folder Creation Form**:
     - Test empty folder name.
     - Test folder name with illegal characters (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`). Verify rejection.
  4. **Marketplace Checkout Form**:
     - Test checkout without selecting payment method.
- **Expected Result:** Invalid inputs are rejected with clear, user-friendly error banners; forms cannot be submitted in an invalid state.
- **What to Verify:** Form submit buttons show loading spinners while processing and disable multiple clicks.
- **Evidence Required:** Screenshots of form validation tooltips and error alerts for each form.
- **Pass Criteria:** 100% of invalid test cases trigger appropriate validation messages without server crashes.
- **Failure Criteria:** Form submits with invalid data or crashes with uncaught JavaScript exception.
- **Priority:** `MEDIUM`

---

### TASK 9 — Core Module & Workflow Testing

- **Task ID:** `TASK-09`
- **Task Name:** Project Lifecycle Engine, Folder Hierarchy, Versioning & Orders
- **Objective:** Verify core business engines: Project Status Finite State Machine, Recursive Folder Tree, File Version History, and Marketplace Order Lifecycle.
- **Pages/Modules to Test:** `/projects/:id`, `FolderExplorer.jsx`, `VersionHistoryModal.jsx`, `/marketplace`, `/orders`.
- **Test Account/Role:** `ADMIN`, `SUPER_ADMIN`, `USER`.
- **Preconditions:** Seeded project with files available.
- **Step-by-Step Instructions:**
  1. **Project Lifecycle FSM**:
     - Open project in status `DRAFT`.
     - Test transitions: `DRAFT` ➡️ `APPROVED` ➡️ `IN_PROGRESS` ➡️ `COMPLETED`.
     - Attempt invalid transition: `DRAFT` ➡️ `COMPLETED`. Verify transition is blocked with warning.
  2. **Hierarchical Folder Explorer**:
     - Create root folder `01_Architecture`.
     - Create child subfolder `01_Architecture/Database_Design`.
     - Create grandchild subfolder `01_Architecture/Database_Design/Schemas`.
     - Verify breadcrumb path updates correctly: `Home > 01_Architecture > Database_Design > Schemas`.
     - Delete parent folder. Verify modal asks for recursive confirmation or prevents orphan assets.
  3. **Asset Versioning Engine**:
     - Upload file `SRS_Document.pdf` (Version 1).
     - Upload a modified file with the exact same name `SRS_Document.pdf` to the same folder.
     - Verify system automatically creates **Version 2** and sets `isCurrentVersion = true` on v2 while retaining v1 as historic.
     - Open **Version History Modal** (`VersionHistoryModal.jsx`). Verify both v1 and v2 are listed with upload timestamps and author email.
     - Click **"Rollback / Set Current"** on v1. Verify v1 becomes the active version.
  4. **Marketplace & Order Lifecycle**:
     - Navigate to `/marketplace`.
     - Click **"Purchase Solution"** on an academic module (e.g. *Machine Learning Assessment Engine*).
     - Select payment method (`Credit Card` / `Institutional Invoice`). Complete checkout.
     - Navigate to `/orders`. Verify new order appears with status `PROCESSING` or `COMPLETED`.
- **Expected Result:** All state machines transition cleanly, folder tree renders recursively without stack overflow, and asset versions are tracked accurately.
- **What to Verify:** Database tables `folder_master`, `asset_master`, `projects`, and `orders` reflect accurate relations and foreign keys.
- **Evidence Required:** Folder tree screenshot, Version History modal screenshot with multiple versions, Order detail invoice screenshot.
- **Pass Criteria:** Flawless execution of lifecycle rules, version tracking, and order placement.
- **Failure Criteria:** Duplicate key crash on version upload, broken breadcrumbs, or invalid project status transition.
- **Priority:** `CRITICAL`

---

### TASK 10 — Full CRUD Matrix Testing

- **Task ID:** `TASK-10`
- **Task Name:** Create, Read, Update, Delete (CRUD) Verification Matrix
- **Objective:** Systematically test CRUD operations across all 7 core entities in the application.
- **Pages/Modules to Test:** User Management, Admin Management, Projects, Requirements, Folders, Assets, Orders.
- **Test Account/Role:** `SUPER_ADMIN`, `ADMIN`.
- **Preconditions:** Admin session active.
- **Step-by-Step Instructions:**
  Execute the test matrix below for each entity:

| Entity | Create Test (C) | Read/List Test (R) | Update Test (U) | Delete/Soft-Delete Test (D) |
| :--- | :--- | :--- | :--- | :--- |
| **Users** | `POST /api/users` via UI modal | Verify in `/users` list with search & pagination | Edit name, email, status to `INACTIVE` | Soft-delete user (`deleted = true`). Verify hidden from standard list |
| **Admins** | Create admin in `/admins` | Verify in admin table with assigned user counts | Update admin permissions matrix | Deactivate/remove admin coordinator |
| **Requirements**| Submit new requirement | View list in `/requirements` & detail in `/requirements/:id` | Edit draft title, budget, description | Delete draft requirement |
| **Projects** | Create project linked to requirement | View project list and project summary cards | Update budget, tech stack, project status | Archive/Inactivate project |
| **Folders** | Create nested folder in `/projects/:id` | Expand folder hierarchy in tree view | Rename folder title | Delete empty folder |
| **Assets** | Upload document/image/audio | View asset in Secure Viewer and download | Edit asset description or upload new version | Delete asset (verify active flag becomes false) |
| **Orders** | Checkout item in `/marketplace` | View in `/orders` with itemized breakdown | Update order fulfillment status | Cancel pending order |

- **Expected Result:** All Create, Read, Update, Delete actions execute with immediate UI feedback and accurate DB persistence.
- **What to Verify:** Soft-deleted entities retain foreign key integrity and do not cause `NullPointerException` in parent joins.
- **Evidence Required:** Before and after screenshots for each entity update and deletion.
- **Pass Criteria:** 100% CRUD operations pass without data corruption.
- **Failure Criteria:** 500 error on update/delete or hard deletion causing cascade breaks.
- **Priority:** `HIGH`

---

### TASK 11 — REST API Specification Testing

- **Task ID:** `TASK-11`
- **Task Name:** REST API Contract, Response Codes & Payload Verification
- **Objective:** Verify backend API endpoints with automated HTTP assertions covering status codes, JSON response schemas, authorization headers, and error bodies.
- **Pages/Modules to Test:** Spring Boot Controller endpoints via Postman or Curl.
- **Test Account/Role:** Test script using JWT Bearer tokens for all roles.
- **Preconditions:** Spring Boot running on `http://localhost:8080` or via Cloudflare tunnel.
- **Step-by-Step Instructions:**
  Execute the following API test suite:

```http
### 1. Auth Login (Valid)
POST http://localhost:8080/api/auth/login
Content-Type: application/json

{ "email": "superadmin@academic.com", "password": "Superadmin123!" }
# Assert: Status == 200, Body contains "token", Body.user.role == "SUPER_ADMIN"

### 2. Auth Login (Invalid)
POST http://localhost:8080/api/auth/login
Content-Type: application/json

{ "email": "superadmin@academic.com", "password": "WrongPassword!" }
# Assert: Status == 401 or 400, Body contains error message

### 3. Get Requirements (Authenticated)
GET http://localhost:8080/api/requirements
Authorization: Bearer {{SUPERADMIN_TOKEN}}
# Assert: Status == 200, Body is Array

### 4. Create Project (Role Protected)
POST http://localhost:8080/api/projects
Authorization: Bearer {{USER_TOKEN}}
Content-Type: application/json

{ "projectName": "Unauthorized Project Creation", "budget": 5000 }
# Assert: Status == 403 Forbidden

### 5. Fetch Asset Content
GET http://localhost:8080/api/assets/1/content
Authorization: Bearer {{SUPERADMIN_TOKEN}}
# Assert: Status == 200, Content-Type matches mimeType

### 6. Admin Access Control Matrix
GET http://localhost:8080/api/admin-access-control/matrix
Authorization: Bearer {{SUPERADMIN_TOKEN}}
# Assert: Status == 200, Body contains permission definitions and admin states
```

- **Expected Result:** API conforms strictly to standard HTTP status codes: `200 OK`, `201 Created`, `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`.
- **What to Verify:** Responses include standard security headers (`X-Content-Type-Options: nosniff`, `Cache-Control`).
- **Evidence Required:** Postman Collection test run export or Newman CLI JSON test report.
- **Pass Criteria:** 100% API endpoints return expected status codes and matching JSON schemas.
- **Failure Criteria:** Unhandled 500 Internal Server Error, stack traces exposed in error response, or missing auth checks.
- **Priority:** `CRITICAL`

---

### TASK 12 — Database Integrity & Schema Testing

- **Task ID:** `TASK-12`
- **Task Name:** MySQL Schema Integrity, Foreign Keys, Flyway Migrations & Audit Trail
- **Objective:** Validate database schema structure, foreign key cascading, index performance, and automated audit log insertion.
- **Pages/Modules to Test:** MySQL Database `academic_db`, Table structures, Audit Log Controller.
- **Test Account/Role:** Database Administrator / QA Automation.
- **Preconditions:** Direct access to MySQL 8.0 on port 3306.
- **Step-by-Step Instructions:**
  1. Inspect `flyway_schema_history` table: Verify versions 1 through 12 are recorded.
  2. Verify essential tables exist:
     - `user_management`, `audit_log`, `requirements`, `projects`, `project_assignments`, `folder_master`, `asset_master`, `folder_permissions`, `file_permissions`, `admin_permissions`, `admin_user_assignments`, `orders`, `notifications`.
  3. Verify column constraints:
     - `requirements.image_url` is `LONGTEXT`.
     - `requirements.audio_url` is `LONGTEXT`.
     - `user_management.email` has `UNIQUE` constraint.
     - `projects.project_code` has `UNIQUE` constraint.
  4. Perform an action in the UI (e.g. Create a user or Approve a requirement).
  5. Query `audit_log` table:
     ```sql
     SELECT * FROM audit_log ORDER BY id DESC LIMIT 5;
     ```
     Verify that `actor_email`, `action`, `details`, and `timestamp` were automatically logged.
  6. Test transaction rollback: Attempt an invalid batch insert to verify partial writes are rolled back.
- **Expected Result:** Database maintains referential integrity; foreign key constraints prevent orphan records; all critical business mutations produce immutable audit log entries.
- **What to Verify:** No raw SQL exceptions in Spring Boot backend logs.
- **Evidence Required:** SQL schema query outputs, foreign key verification queries, and audit log table dump.
- **Pass Criteria:** All tables conform to Flyway DDL specifications and audit logging captures all state changes.
- **Failure Criteria:** Missing foreign key constraints, unlogged admin actions, or migration checksum mismatches.
- **Priority:** `HIGH`

---

### TASK 13 — Security & Access Control Testing

- **Task ID:** `TASK-13`
- **Task Name:** Security Hardening, Token Expiry, CORS, Password Hashing & Injection Defense
- **Objective:** Evaluate the application against common security vulnerabilities including JWT tampering, expired tokens, SQL injection, XSS, and broken object level authorization (BOLA).
- **Pages/Modules to Test:** Entire application surface and backend security filter chain.
- **Test Account/Role:** Security QA / Penetration Tester.
- **Preconditions:** Web security proxy (e.g. OWASP ZAP, Burp Suite, or DevTools).
- **Step-by-Step Instructions:**
  1. **JWT Tampering & Signature Check**:
     - Copy a valid JWT token. Modify the payload from `"role":"USER"` to `"role":"SUPER_ADMIN"` using jwt.io.
     - Send request with modified token. Verify backend returns HTTP 401/403 (Signature verification failed).
  2. **Expired Token Rejection**:
     - Send request with an expired JWT token. Verify request is rejected with `Session expired` message.
  3. **SQL Injection Defense**:
     - In user search input or requirement title, enter SQL injection payloads: `' OR 1=1 --`, `'; DROP TABLE test; --`.
     - Verify backend uses parameterized Spring Data JPA queries (`@Query` with binding parameters) and treats input as literal string.
  4. **Cross-Site Scripting (XSS) Defense**:
     - Enter XSS payload in Requirement Description: `<script>document.cookie</script><img src=x onerror=alert(1)>`.
     - Save and view requirement. Verify React escapes HTML entities and no JavaScript executes.
  5. **BOLA / IDOR Verification**:
     - Log in as User A (`user@academic.com`). Note an asset ID belonging to Project 1 (e.g. Asset ID 10).
     - If User A is not assigned to Project 2 (Asset ID 20), send direct GET request: `GET /api/assets/20/content`.
     - Verify backend checks `AccessControlService` or `FilePermissionRepository` and denies access with HTTP 403.
- **Expected Result:** Application resists all standard web injection vectors; JWT signatures are cryptographically verified; IDOR attempts are blocked.
- **What to Verify:** Passwords in database are hashed with BCrypt (starting with `$2a$` or `$2b$`).
- **Evidence Required:** Security test console outputs, tamper attempt rejection responses, sanitized XSS rendering screenshots.
- **Pass Criteria:** Zero critical security vulnerabilities or unauthorized data exposures.
- **Failure Criteria:** Successful privilege escalation, XSS script execution, or IDOR data leakage.
- **Priority:** `BLOCKER`

---

### TASK 14 — UI / UX & Micro-Interactions Testing

- **Task ID:** `TASK-14`
- **Task Name:** Design System, Glassmorphic Styling, Animations & Feedback States
- **Objective:** Test visual design fidelity, glassmorphism aesthetics, dark/light contrast ratios, hover states, loading skeletons, and interactive toast notifications.
- **Pages/Modules to Test:** All pages and modals across the application.
- **Test Account/Role:** UI/UX Tester.
- **Preconditions:** Display calibrated with standard sRGB color gamut.
- **Step-by-Step Instructions:**
  1. Verify typography: Font families (Inter / Outfit / Roboto) load without fallback to browser generic serif.
  2. Test card components: Glassmorphic cards have subtle borders (`border: 1px solid var(--border-color)`), background blurs (`backdrop-filter: blur(...)`), and box shadows.
  3. Test hover effects: Buttons, table rows, and navigation links have smooth CSS transitions on `:hover` and `:active`.
  4. Test loading states: When fetching data or performing search, verify spinning loaders or skeleton loaders render without layout shifts.
  5. Test notification toasts: Trigger actions (Save, Delete, Copy link). Verify toast slides in from top/bottom right and automatically dismisses after 3 seconds.
  6. Test modal dialogues: Clicking backdrop or press `Escape` key closes modal; modal locks scroll on parent body.
- **Expected Result:** Interface feels premium, responsive, alive, and visually polished without clipping, overflowing text, or broken icons.
- **What to Verify:** Lucide icons render crisply at proper sizes without missing glyphs.
- **Evidence Required:** UI component screenshots illustrating hover states, open modals, and toast alerts.
- **Pass Criteria:** Visual consistency across all 16 views with zero CSS overflow or broken layouts.
- **Failure Criteria:** Unstyled elements, visual glitches, or unresponsive click targets.
- **Priority:** `MEDIUM`

---

### TASK 15 — Responsive & Cross-Device Layout Testing

- **Task ID:** `TASK-15`
- **Task Name:** Viewport Adaptability & Mobile Breakpoint Testing
- **Objective:** Verify layout fluidity, sidebar collapsing, touch interaction compatibility, and data table wrapping across Desktop, Tablet, and Mobile screen resolutions.
- **Pages/Modules to Test:** All pages on responsive viewports.
- **Test Account/Role:** Mobile QA Tester.
- **Preconditions:** Chrome DevTools Device Mode or physical devices.
- **Step-by-Step Instructions:**
  1. Test Desktop Viewports (`1920x1080`, `1440x900`):
     - Verify full sidebar is visible; multi-column dashboard grid displays 3-4 columns.
  2. Test Tablet Viewports (`768x1024` iPad / Tablet):
     - Verify dashboard grids fold into 2 columns.
     - Verify sidebar collapses or transitions to hamburger drawer toggle.
  3. Test Mobile Viewports (`375x812` iPhone / `412x915` Android):
     - Verify mobile header displays hamburger menu button.
     - Open mobile navigation menu. Verify menu overlays screen and links are clickable with min 48px touch targets.
     - Verify tables on `/users`, `/requirements`, and `/audit-logs` provide horizontal scrolling (`overflow-x: auto`) without breaking the viewport width.
     - Test forms on mobile: Input fields do not trigger unwanted zooming (font size >= 16px).
- **Expected Result:** Website is 100% responsive and operable on all screen widths from 320px up to 4K displays.
- **What to Verify:** No horizontal scrollbar on the root `<body>` element on mobile.
- **Evidence Required:** Screenshots of Dashboard, User Management, and Requirement Form on Desktop, Tablet, and Mobile viewports.
- **Pass Criteria:** Flawless usability and legible text across all tested resolutions.
- **Failure Criteria:** Horizontal page blowout on mobile, clipped modal buttons, or unclickable mobile menu.
- **Priority:** `HIGH`

---

### TASK 16 — Cross-Browser & OS Compatibility Testing

- **Task ID:** `TASK-16`
- **Task Name:** Multi-Browser Engine & OS Rendering Verification
- **Objective:** Verify consistent behavior, JavaScript execution, and CSS rendering across major browser engines (Chromium, Gecko, WebKit).
- **Pages/Modules to Test:** Key workflows on multiple browsers.
- **Test Account/Role:** Cross-Browser QA Tester.
- **Preconditions:** Installed browsers: Google Chrome, Microsoft Edge, Mozilla Firefox, Apple Safari (or WebKit via Playwright).
- **Step-by-Step Instructions:**
  1. **Google Chrome (Chromium)**:
     - Perform login, file upload, video playback, and PDF rendering.
  2. **Microsoft Edge (Chromium)**:
     - Verify full parity with Chrome.
  3. **Mozilla Firefox (Gecko)**:
     - Verify CSS backdrop-filter glassmorphism renders.
     - Test scrollbar styling and audio playback for requirement audio assets.
  4. **Apple Safari (WebKit)**:
     - Verify flexbox and grid layouts, date picker inputs, and Secure Viewer canvas rendering.
     - Verify Service Worker caching (`sw.js`) functions without WebKit caching bugs.
- **Expected Result:** Seamless user experience with identical functional and visual outcomes across all tested browsers.
- **What to Verify:** Zero browser-specific JavaScript exceptions in browser console.
- **Evidence Required:** Console logs and page render screenshots from Chrome, Edge, Firefox, and Safari.
- **Pass Criteria:** All core features work without browser-specific degradation.
- **Failure Criteria:** Feature failure on any major browser.
- **Priority:** `MEDIUM`

---

### TASK 17 — Error Handling & Boundary Condition Testing

- **Task ID:** `TASK-17`
- **Task Name:** Resilience, Network Failure & Boundary Condition Testing
- **Objective:** Test application behavior under abnormal conditions such as backend disconnection, invalid JSON payloads, huge file uploads (>500MB), and slow network speeds.
- **Pages/Modules to Test:** `ErrorBoundary.jsx`, Network layer (`api.js`), File Upload Modal.
- **Test Account/Role:** QA Resilience Tester.
- **Preconditions:** Network throttling tools, file upload test assets.
- **Step-by-Step Instructions:**
  1. **Backend Unreachable / Offline Handling**:
     - Temporarily stop Spring Boot backend (`stop-server.bat`).
     - Attempt to perform an action on the frontend (e.g. submit login or fetch projects).
     - Verify frontend does not crash with an unhandled exception; verify a user-friendly error banner appears: *"Backend server is unreachable. Please check connection."*
  2. **React Error Boundary Test**:
     - Trigger a simulated render crash in a component.
     - Verify `ErrorBoundary.jsx` catches the failure and renders a graceful recovery card with a **"Reload Component"** button rather than a blank white screen.
  3. **File Upload Boundary Test**:
     - Attempt uploading an empty 0-byte file. Verify rejection.
     - Attempt uploading an oversized file (> 500MB). Verify upload modal prevents upload with size limit warning before exhausting memory.
  4. **Slow 3G Network Throttling**:
     - Enable "Slow 3G" in DevTools Network tab.
     - Navigate through pages. Verify route loading spinners (`RouteLoader`) display during bundle fetching.
- **Expected Result:** Application handles errors gracefully, informs the user clearly, and recovers without data corruption.
- **What to Verify:** Error Boundary logs errors to console while preventing app crashes.
- **Evidence Required:** Error boundary fallback UI screenshot, offline network alert screenshot.
- **Pass Criteria:** All fault injection tests result in handled states with clear user messaging.
- **Failure Criteria:** Unhandled white screen of death or silent data failure.
- **Priority:** `HIGH`

---

### TASK 18 — Screenshot, Watermarking & Copy/Paste Security Testing

- **Task ID:** `TASK-18`
- **Task Name:** Digital Rights Management (DRM), Dynamic Watermarking & Content Protection
- **Objective:** Validate specialized document security controls implemented in `SecureFileViewer.jsx`, including unselectable dynamic watermarks, window blur mitigation, and clipboard protection.
- **Pages/Modules to Test:** `/projects/:id` ➡️ `SecureFileViewer.jsx`, `/project-files`.
- **Test Account/Role:** `USER` (`user@academic.com`).
- **Preconditions:** Project asset (PDF, Image, or Code file) open in Secure Viewer.
- **Step-by-Step Instructions:**
  1. Open a confidential asset (e.g. `Architecture_Blueprint.png` or `Database_Schema_v1.sql`) in `SecureFileViewer`.
  2. **Dynamic Watermark Verification**:
     - Inspect the canvas overlay.
     - Verify the watermark displays:
       - Authenticated user's email: `user@academic.com`
       - Project Code / ID: e.g. `PRJ-8F3A21`
       - Live UTC timestamp
       - Semi-transparent, repetitive diagonal pattern across the entire viewport.
     - Attempt to highlight or select the watermark text. Verify `user-select: none` and `pointer-events: none` prevent selection.
  3. **Clipboard & Copy/Paste Protection**:
     - For text/code assets, attempt to highlight text and press `Ctrl + C` (or `Cmd + C`).
     - Verify copy event is intercepted and blocked or clipboard receives empty string.
     - Right-click on the document. Verify custom context menu or disabled browser context menu (`onContextMenu={(e) => e.preventDefault()}`).
  4. **Window Focus Loss & Risk Mitigation Layer**:
     - With the document visible in the viewer, switch active window focus (e.g. press `Alt + Tab` or click onto another application).
     - Verify document content immediately applies CSS blur filter (`backdrop-filter: blur(16px)` or `filter: blur(20px)`) and displays privacy shield message: *"Content hidden while window is out of focus."*
     - Return focus to browser window. Verify content unblurs instantly.
  5. **Screenshot Defense**:
     - Attempt standard OS screenshot shortcuts (`Win + Shift + S` or `PrintScreen`).
     - Verify watermark remains permanently fused over the visual render in all captured frames.
- **Expected Result:** Confidential assets are watermarked with user identity, cannot be selected or copied via clipboard, and blur automatically upon losing focus.
- **What to Verify:** Watermark overlay cannot be removed via simple DOM inspection without breaking the viewer render container.
- **Evidence Required:** Screenshot of Secure Viewer showing diagonal watermark overlay; screenshot of blurred state on window focus loss.
- **Pass Criteria:** Watermarking, copy-prevention, and blur-on-focus-loss perform reliably.
- **Failure Criteria:** Text can be freely selected/copied, or watermark is missing user metadata.
- **Priority:** `CRITICAL`

---

### TASK 19 — End-to-End Real-World Scenario Testing

- **Task ID:** `TASK-19`
- **Task Name:** Complete Business Lifecycle (Requirement to Delivery)
- **Objective:** Execute an end-to-end multi-role real-world scenario spanning requirement submission, admin review, project bootstrapping, asset upload, researcher assignment, and order completion.
- **Pages/Modules to Test:** Complete application flow across all user roles.
- **Test Account/Role:** Multi-user scenario (`USER`, `ADMIN`, `SUPER_ADMIN`).
- **Preconditions:** Clean database state or unique project code.
- **Step-by-Step Instructions:**
  Execute the full 8-step lifecycle:

```
[Step 1: Researcher (USER)]
  └─► Submits Requirement: "Automated Evaluation Engine" (Rs. 18,000)
        │
[Step 2: Project Admin (ADMIN)]
  └─► Reviews Requirement in /admin/project-review ──► Approves Requirement
        │
[Step 3: Super Admin (SUPER_ADMIN)]
  └─► Creates Project "PRJ-EVAL-2026" linked to Approved Requirement
        │
[Step 4: Project Admin (ADMIN)]
  └─► Creates Folder Structure: "01_Specs" -> "Final_Docs"
  └─► Uploads File: "Evaluation_Spec_v1.pdf"
        │
[Step 5: Project Admin (ADMIN)]
  └─► Assigns Researcher (testuser1@gmail.com) to PRJ-EVAL-2026
        │
[Step 6: Researcher (USER)]
  └─► Logs in ──► Opens PRJ-EVAL-2026 ──► Views "Evaluation_Spec_v1.pdf" with Watermark
        │
[Step 7: Researcher (USER)]
  └─► Purchases Add-on Module in /marketplace ──► Completes Checkout
        │
[Step 8: Super Admin (SUPER_ADMIN)]
  └─► Inspects /audit-logs ──► Verifies complete immutable audit trail of all 7 actions
```

- **Expected Result:** Seamless progression through all 8 steps without data gaps, permission blocks, or orphaned entities.
- **What to Verify:** Audit log records every transition with correct actor email and timestamp.
- **Evidence Required:** Sequential screenshots for all 8 lifecycle steps.
- **Pass Criteria:** Flawless end-to-end lifecycle execution.
- **Failure Criteria:** Breakage at any handoff point between user roles.
- **Priority:** `CRITICAL`

---

### TASK 20 — Regression Testing Protocol

- **Task ID:** `TASK-20`
- **Task Name:** Critical Path Regression & Historical Fix Verification
- **Objective:** Retest critical modules and verified bug fixes to ensure recent enhancements did not introduce regression bugs.
- **Pages/Modules to Test:**
  - `ProjectRepository.java` (`searchAssignedProjects` query)
  - `AdminAccessControlModal.jsx` (Duplicate key handling on preset application)
  - Service Worker v4 caching (`sw.js`)
  - Deep folder route resolution (`/projects/:id/folders/:folderId`)
- **Test Account/Role:** `SUPER_ADMIN`, `USER`.
- **Preconditions:** Latest build deployed.
- **Step-by-Step Instructions:**
  1. **Assigned Project Search Query**:
     - Log in as `USER`. Use project search box with mixed case letters and partial strings.
     - Verify query returns exact assigned projects without SQL syntax exception.
  2. **Access Control Preset Re-Application**:
     - Apply preset *Full Governance* to an Admin.
     - Immediately apply preset *Standard Coordinator* to the same Admin.
     - Verify no duplicate key SQL exception occurs (`admin_permissions` unique constraint properly managed via flush).
  3. **Service Worker Cache Invalidation**:
     - Hard refresh browser (`Ctrl + F5`).
     - Check DevTools Application ➡️ Service Workers. Verify `academic-tool-v4` is active and stale v1/v2/v3 caches are purged.
  4. **Deep Folder Routing**:
     - Directly reload a nested folder URL: `http://localhost:5173/projects/1/folders/2`.
     - Verify page re-hydrates folder contents correctly without redirecting to root.
- **Expected Result:** All known previous fixes remain stable and performant.
- **What to Verify:** Clean browser console and zero server exceptions.
- **Evidence Required:** Search results screenshot, Preset re-application confirmation, Service Worker cache inspector screenshot.
- **Pass Criteria:** All regression test cases pass 100%.
- **Failure Criteria:** Any recurrence of previously resolved bugs.
- **Priority:** `HIGH`

---

### TASK 21 — Final Acceptance & Production Readiness Testing

- **Task ID:** `TASK-21`
- **Task Name:** Final Quality Gate & Go/No-Go Acceptance Sign-Off
- **Objective:** Perform the final comprehensive audit across functional, security, performance, and operational criteria to certify the build for production handover.
- **Pages/Modules to Test:** Entire platform.
- **Test Account/Role:** Lead QA Engineer & Stakeholder.
- **Preconditions:** Tasks 1 through 20 completed with zero open Blocker or Critical defects.
- **Step-by-Step Instructions:**
  1. Review defect tracker: Confirm 0 Blocker, 0 Critical, and < 3 Low severity defects remain.
  2. Verify production build output: Run `npm.cmd run build` and ensure clean bundle generation without warnings.
  3. Verify security configurations: Confirm JWT secret is securely configured, debug SQL logs disabled (`spring.jpa.show-sql=false`), and mock mode disabled (`VITE_MOCK_MODE=false`).
  4. Verify production split-hosting connection: Vercel frontend communicating with live public gateway tunnel.
  5. Complete Final QA Checklist sign-off.
- **Expected Result:** System meets all production deployment criteria and is formally approved.
- **What to Verify:** Signed acceptance certificate with date and lead QA signature.
- **Evidence Required:** Build log summary, clean API test report, signed QA checklist.
- **Pass Criteria:** Formal sign-off granted by QA Lead.
- **Failure Criteria:** Unresolved Blocker/Critical defects or failed build.
- **Priority:** `BLOCKER`

---

## 5. Standard Bug Reporting Format & Severity Guidelines

When the testing team identifies a defect, log the issue using the following standard template:

### 🐞 Defect Report Template

```markdown
### [BUG-ID] Short, Descriptive Defect Title

- **Test Case ID:** (e.g. TC-AUTH-002 / TASK-09-03)
- **Module:** (e.g. Authentication / File Explorer / Project FSM)
- **Page URL / Route:** (e.g. /projects/1/folders/2)
- **User Role Tested:** (SUPER_ADMIN / ADMIN / PROJECT_DEVELOPER / USER)
- **Severity:** [ BLOCKER | CRITICAL | HIGH | MEDIUM | LOW ]
- **Priority:** [ P1 - Immediate | P2 - High | P3 - Normal | P4 - Low ]

#### Environment Details:
- OS: Windows 11 / macOS / Ubuntu
- Browser & Version: Chrome 124.0 / Edge 124.0 / Firefox 125.0
- Backend Mode: Live Cloudflare Tunnel / Localhost 8080

#### Steps to Reproduce:
1. Navigate to `/login` and log in as `user@academic.com`.
2. Open Project ID 1 from `/projects`.
3. Click 'Upload Asset' and select a file named `Spec_v1.pdf`.
4. Click 'Save' and observe response.

#### Expected Result:
File should upload successfully and create Version 1 in `asset_master`.

#### Actual Result:
Server returns HTTP 500 error: "Duplicate key constraint violation".

#### Evidence:
- **Screenshot / Video:** [Attach or link media file]
- **Console Log Error:** `Uncaught (in promise) Error: Request failed with status 500`
- **Network / API Response:** `{"status": 500, "message": "Cannot insert duplicate key in asset_master"}`
- **Database Impact:** Partial transaction left in `asset_master` without matching folder relation.

#### Defect Status:
- [ ] NEW
- [ ] ASSIGNED
- [ ] IN RESOLUTION
- [ ] FIXED - READY FOR RETEST
- [ ] VERIFIED & CLOSED
```

### 🏷️ Severity Classification Guidelines

| Severity Level | Definition & Criteria | SLA Resolution Window |
| :--- | :--- | :--- |
| 🔴 **BLOCKER** | System crash, database corruption, security breach, application won't build or start, login completely impossible. | Immediate (within 2 hours) |
| 🟠 **CRITICAL** | Core business workflow broken (e.g. Cannot create projects, cannot view watermarked files, role privilege escalation). No workaround available. | Within 8 hours |
| 🟡 **HIGH** | Major feature impaired (e.g. Search filters broken, CSV export failing, version rollback failing), but a temporary workaround exists. | Within 24 hours |
| 🔵 **MEDIUM** | Validation error messages misleading, UI layout misalignment on specific viewport, minor data sorting discrepancy. | Next Sprint Release |
| ⚪ **LOW** | Cosmetic typo, minor color contrast variation, icon alignment off by a few pixels. | Backlog |

---

## 6. Master Test Execution Tracker

The QA team should track test execution progress using the following master tracker matrix:

| Test Case ID | Module / Area | Test Scenario Description | Target Role | Execution Status | Assigned Tester | Evidence Reference |
| :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `TC-ENV-001` | Environment | MySQL 8.0 local service health on port 3306 | System QA | `NOT STARTED` | QA Engineer 1 | Port scan log |
| `TC-ENV-002` | Environment | Spring Boot backend initialization on 8080 | System QA | `NOT STARTED` | QA Engineer 1 | Backend log |
| `TC-ENV-003` | Environment | Cloudflare tunnel HTTP/2 gateway forwarding | System QA | `NOT STARTED` | QA Engineer 1 | Tunnel log |
| `TC-NAV-001` | Navigation | Public route resolution & guest login bounce | Guest | `NOT STARTED` | QA Engineer 2 | Route video |
| `TC-NAV-002` | Navigation | Protected route role clearance enforcement | USER | `NOT STARTED` | QA Engineer 2 | Access Denied shot |
| `TC-REG-001` | Registration | Complete user onboarding with OTP `123456` | New User | `NOT STARTED` | QA Engineer 2 | Onboarding video |
| `TC-REG-002` | Registration | Duplicate email rejection validation | Existing User| `NOT STARTED` | QA Engineer 2 | Error alert shot |
| `TC-AUTH-001`| Auth | Valid Super Admin login & JWT storage | SUPER_ADMIN | `NOT STARTED` | QA Engineer 3 | Network token shot |
| `TC-AUTH-002`| Auth | Invalid password error handling | Any Role | `NOT STARTED` | QA Engineer 3 | Error toast shot |
| `TC-AUTH-003`| Auth | Token cleanup and session reset on logout | USER | `NOT STARTED` | QA Engineer 3 | Storage dump |
| `TC-RBAC-001`| Permissions | User sidebar isolation vs Super Admin sidebar | Multi-Role | `NOT STARTED` | QA Engineer 3 | Sidebar matrix |
| `TC-ADM-001` | Admin | Admin coordinator provisioning & user link | SUPER_ADMIN | `NOT STARTED` | QA Engineer 1 | Admin table shot |
| `TC-ADM-002` | Admin | Access control preset application to admin | SUPER_ADMIN | `NOT STARTED` | QA Engineer 1 | Preset modal shot |
| `TC-USR-001` | User | Requirement creation with media attachment | USER | `NOT STARTED` | QA Engineer 2 | Req form shot |
| `TC-USR-002` | User | Profile updating & session sync | USER | `NOT STARTED` | QA Engineer 2 | Profile page shot |
| `TC-CORE-001`| Core Engine | Project lifecycle FSM transition validity | ADMIN | `NOT STARTED` | QA Engineer 1 | Status change shot |
| `TC-CORE-002`| Core Engine | Recursive folder tree creation & breadcrumbs | ADMIN | `NOT STARTED` | QA Engineer 1 | Tree hierarchy shot |
| `TC-CORE-003`| Core Engine | Duplicate asset upload version incrementation| ADMIN | `NOT STARTED` | QA Engineer 1 | Version modal shot |
| `TC-CORE-004`| Core Engine | Marketplace checkout & order generation | USER | `NOT STARTED` | QA Engineer 2 | Order invoice shot |
| `TC-CRUD-001`| CRUD | User entity soft-deletion and list filter | SUPER_ADMIN | `NOT STARTED` | QA Engineer 3 | DB select log |
| `TC-API-001` | API | Automated Postman contract suite run | System QA | `NOT STARTED` | QA Automation | Postman runner log |
| `TC-DB-001`  | Database | Flyway V1-V12 migration validation & audit log| DBA / QA | `NOT STARTED` | QA Engineer 1 | SQL query table |
| `TC-SEC-001` | Security | JWT signature tampering defense | Security QA | `NOT STARTED` | Security Lead | 401 response log |
| `TC-SEC-002` | Security | IDOR defense on unassigned asset retrieval | USER | `NOT STARTED` | Security Lead | 403 response log |
| `TC-UI-001`  | UI / UX | Glassmorphic design & toast notification | UI Tester | `NOT STARTED` | QA Engineer 2 | UI gallery shots |
| `TC-RESP-001`| Responsive | Mobile 375px viewport menu & table scroll | Mobile QA | `NOT STARTED` | QA Engineer 3 | Mobile captures |
| `TC-DRM-001` | DRM / Viewer| Dynamic diagonal watermark on document view | USER | `NOT STARTED` | QA Engineer 2 | Watermark capture |
| `TC-DRM-002` | DRM / Viewer| Window focus loss blur effect verification | USER | `NOT STARTED` | QA Engineer 2 | Blur state capture |
| `TC-E2E-001` | E2E | 8-Step full lifecycle requirement to delivery| Multi-Role | `NOT STARTED` | QA Lead | Full session video |
| `TC-REG-001` | Regression | Duplicate key on preset re-application check| SUPER_ADMIN | `NOT STARTED` | QA Engineer 1 | Preset re-test shot|
| `TC-ACC-001` | Acceptance | Final quality gate review & build sign-off | QA Lead | `NOT STARTED` | QA Lead & Mgmt | Signed checklist |

---

## 7. Final QA Sign-Off Checklist

Before certifying the website for production release, the testing team lead must check and sign off on every item below:

### 🔐 1. Authentication & Security
- [ ] Password hashes stored in MySQL using BCrypt algorithm.
- [ ] JWT tokens expire after configured TTL (`academic.jwt.expiration-ms=86400000`).
- [ ] Protected routes block unauthorized URL tampering with **Access Denied** fallback.
- [ ] Secure File Viewer enforces diagonal watermarking containing email, project code, and UTC timestamp.
- [ ] Window focus-loss applies immediate blur protection over confidential assets.
- [ ] Clipboard copy/paste and right-click context menus are disabled inside the viewer container.
- [ ] SQL Injection and XSS inputs are sanitized without script execution.

### 👥 2. Role Governance & Access Control
- [ ] `SUPER_ADMIN` has exclusive clearance to `/admins` and Access Control Presets.
- [ ] `ADMIN` coordinators are restricted to assigned students/researchers when scoped.
- [ ] `USER` researchers cannot access admin menus or modify projects.
- [ ] `PROJECT_DEVELOPER` has isolated access to `/developer/workspace`.

### 📂 3. Core Engine & Data Integrity
- [ ] Project status transitions adhere strictly to the declared Finite State Machine.
- [ ] Recursive folder tree creates, moves, and deletes folders without orphan assets.
- [ ] Duplicate filename uploads automatically increment `version_no` in `asset_master`.
- [ ] Marketplace checkouts create valid records in `orders` table.
- [ ] All database changes trigger automatic logging to `audit_log`.

### 💻 4. Cross-Platform & Resilience
- [ ] Layout is fully responsive across Desktop (1920px), Tablet (768px), and Mobile (375px).
- [ ] Verified across Chrome, Edge, Firefox, and Safari without rendering defects.
- [ ] Offline or backend disconnect triggers clear, user-friendly error banners.
- [ ] React Error Boundary prevents blank white screens on runtime exceptions.
- [ ] Service Worker v4 invalidates outdated caches cleanly.

---

### ✍️ Final Acceptance Authorization

| Role | Name | Signature | Date | Decision |
| :--- | :--- | :--- | :--- | :---: |
| **Lead QA Engineer** | _______________________ | _______________________ | ____________ | `[ ] APPROVED  [ ] REJECTED` |
| **Lead Developer** | _______________________ | _______________________ | ____________ | `[ ] APPROVED  [ ] REJECTED` |
| **Project Stakeholder**| _______________________ | _______________________ | ____________ | `[ ] APPROVED  [ ] REJECTED` |
