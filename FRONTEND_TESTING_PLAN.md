# 🖥️ Academic Integration Tool (AIT) — Master Frontend Testing Plan

> **Target System:** Academic Integration Tool (Client-Side Single Page Application)  
> **Framework:** React 19 + Vite 8 + React Router v7 + Lucide Icons + Modern CSS  
> **Audience:** Frontend Quality Assurance (QA) & UI/UX Testing Team  
> **Version:** 1.0.0 (Production Release Candidate)  
> **Scope:** **FRONTEND ONLY** (UI, Layout, Routing, Forms, State, Validation, UX, DRM Viewer, Responsive & Cross-Browser Behavior)  

---

## 📌 Testing Scope & Non-Scope Mandate

### ✅ IN SCOPE (Frontend Testing Only):
- Visual design fidelity, glassmorphism card rendering, and CSS token consistency.
- Client-side routing, route guards (`ProtectedRoute`, `PublicRoute`), and navigation redirects.
- Form controls, input formatting, client-side validation rules, and error banner presentations.
- UI loading skeletons, spinning indicators, empty data states, and feedback toast messages.
- Role-based UI masking, sidebar navigation items visibility, and action button authorization.
- Interactive components (`FolderExplorer`, `SecureFileViewer`, `FileUploadModal`, `VersionHistoryModal`, `NotificationDrawer`, `AdminAccessControlModal`).
- Responsive layout transitions across Desktop, Tablet, and Mobile viewports.
- Cross-browser DOM rendering and touch/click interactions.

### 🚫 STRICTLY OUT OF SCOPE:
- Backend Java/Spring Boot internal logic or service layer unit tests.
- MySQL database tables, Flyway migrations, indexing, or JDBC configurations.
- API implementation code (e.g. controller annotations or Spring Security filter internals).
- *Rule for API failures:* If an API/backend failure impairs the UI, log the issue as:  
  👉 **"Frontend issue caused by API/backend dependency"** (without modifying backend code).

---

## 📑 Table of Contents

1. [Frontend Architecture & Component Inventory](#1-frontend-architecture--component-inventory)
2. [Test Accounts & Role Matrix](#2-test-accounts--role-matrix)
3. [Phased Frontend Execution Order](#3-phased-frontend-execution-order)
4. [Detailed Frontend Testing Tasks (Task 1 to Task 21)](#4-detailed-frontend-testing-tasks)
   - [TASK 1: Application Launch & Initial UI](#task-1--application-launch--initial-ui)
   - [TASK 2: Route & Navigation Testing](#task-2--route--navigation-testing)
   - [TASK 3: Login UI & Session State Testing](#task-3--login-ui--session-state-testing)
   - [TASK 4: Registration & OTP Onboarding UI Testing](#task-4--registration--otp-onboarding-ui-testing)
   - [TASK 5: Role-Based Frontend Access Testing](#task-5--role-based-frontend-access-testing)
   - [TASK 6: Dashboard UI Testing (All Roles)](#task-6--dashboard-ui-testing-all-roles)
   - [TASK 7: Admin & Super Admin Management UI Testing](#task-7--admin--super-admin-management-ui-testing)
   - [TASK 8: Developer Workspace UI Testing](#task-8--developer-workspace-ui-testing)
   - [TASK 9: User & Researcher Interface Testing](#task-9--user--researcher-interface-testing)
   - [TASK 10: Form Controls & Frontend Validation Testing](#task-10--form-controls--frontend-validation-testing)
   - [TASK 11: Project Catalog & Details UI Testing](#task-11--project-catalog--details-ui-testing)
   - [TASK 12: Hierarchical Folder Explorer UI Testing](#task-12--hierarchical-folder-explorer-ui-testing)
   - [TASK 13: File Upload & Version History Modal Testing](#task-13--file-upload--version-history-modal-testing)
   - [TASK 14: Secure File Viewer & Content Protection UI Testing](#task-14--secure-file-viewer--content-protection-ui-testing)
   - [TASK 15: Requirements Management UI Testing](#task-15--requirements-management-ui-testing)
   - [TASK 16: Marketplace & Orders UI Testing](#task-16--marketplace--orders-ui-testing)
   - [TASK 17: Notification Drawer UI Testing](#task-17--notification-drawer-ui-testing)
   - [TASK 18: User Profile & Password Change UI Testing](#task-18--user-profile--password-change-ui-testing)
   - [TASK 19: Search, Filter, Sort & Pagination UI Testing](#task-19--search-filter-sort--pagination-ui-testing)
   - [TASK 20: Responsive Viewports & Cross-Browser UI Testing](#task-20--responsive-viewports--cross-browser-ui-testing)
   - [TASK 21: End-to-End Frontend User Workflows](#task-21--end-to-end-frontend-user-workflows)
5. [Frontend Defect Report Template & Severity Rubric](#5-frontend-defect-report-template--severity-rubric)
6. [Master Frontend Test Execution Tracker](#6-master-frontend-test-execution-tracker)
7. [Final Frontend Acceptance Sign-Off Checklist](#7-final-frontend-acceptance-sign-off-checklist)

---

## 1. Frontend Architecture & Component Inventory

### Registered Client Routes (`src/App.jsx`)
```
├── Public Routes
│   ├── /login                     (Login.jsx)
│   └── /register                  (Register.jsx)
│
└── Protected Routes (ProtectedLayout.jsx)
    ├── /dashboard                 (Dashboard.jsx)               [SUPER_ADMIN, ADMIN, PROJECT_DEVELOPER, USER]
    ├── /developer/workspace       (DeveloperWorkspace.jsx)      [SUPER_ADMIN, PROJECT_DEVELOPER]
    ├── /admin/project-review      (ProjectReviewWorkspace.jsx)  [SUPER_ADMIN, ADMIN]
    ├── /marketplace               (Marketplace.jsx)             [SUPER_ADMIN, ADMIN, USER]
    ├── /orders                    (Orders.jsx)                  [SUPER_ADMIN, ADMIN, USER]
    ├── /projects                  (Projects.jsx)                [SUPER_ADMIN, ADMIN, PROJECT_DEVELOPER, USER]
    ├── /projects/:id              (ProjectDetail.jsx)           [SUPER_ADMIN, ADMIN, PROJECT_DEVELOPER, USER]
    ├── /projects/:id/folders/:folderId (ProjectDetail.jsx)      [SUPER_ADMIN, ADMIN, USER]
    ├── /project-files             (ProjectFiles.jsx)            [SUPER_ADMIN, ADMIN, USER]
    ├── /requirements              (Requirements.jsx)            [SUPER_ADMIN, ADMIN, USER]
    ├── /requirements/new          (RequirementForm.jsx)         [USER]
    ├── /requirements/:id          (RequirementDetail.jsx)       [SUPER_ADMIN, ADMIN, USER]
    ├── /requirements/:id/edit     (RequirementForm.jsx)         [USER]
    ├── /users                     (UserManagement.jsx)          [SUPER_ADMIN, ADMIN]
    ├── /admins                    (AdminManagement.jsx)         [SUPER_ADMIN]
    ├── /audit-logs                (AuditLogs.jsx)               [SUPER_ADMIN, ADMIN]
    └── /profile                   (Profile.jsx)                 [SUPER_ADMIN, ADMIN, PROJECT_DEVELOPER, USER]
```

### Core Frontend Components (`src/components/`)
- `ProtectedLayout.jsx`: Responsive layout container with persistent sidebar, top navigation bar, clearance badge, profile pill, and notification drawer toggle.
- `FolderExplorer.jsx`: Hierarchical tree browser with collapsible nodes, drag/drop indicators, breadcrumb trail, asset status tags, and action toolbars.
- `SecureFileViewer.jsx`: Sandboxed content rendering frame with dynamic 45° diagonal watermark overlay, focus-loss blur layer, and right-click/copy interception.
- `FileUploadModal.jsx`: Drag-and-drop file target with MIME type detection, size validation, and multi-file progress indicators.
- `VersionHistoryModal.jsx`: Modal displaying historical revisions, rollback triggers, and active version badges.
- `NotificationDrawer.jsx`: Slide-out panel with unread badge counter, individual read actions, and clear-all triggers.
- `AdminAccessControlModal.jsx` & `AdminPermissionManagerModal.jsx`: Granular permission toggles, preset configuration dropdowns, and live permission matrix previews.
- `ErrorBoundary.jsx`: Fallback UI catcher rendering user-friendly crash recovery cards with reload action.

---

## 2. Test Accounts & Role Matrix

Use these predefined accounts to test role-specific UI visibility and behavior:

| Role Tested | Test Email | Default Test Password | Expected UI Clearance |
| :--- | :--- | :--- | :--- |
| **SUPER_ADMIN** | `superadmin@academic.com` | `Superadmin123!` | All 16 pages visible; exclusive access to `/admins` and Access Control Presets. |
| **ADMIN** | `testadmin1@gmail.com` / `admin@academic.com` | `Admin123!` | `/admin/project-review`, `/users`, `/audit-logs`, `/projects`, `/requirements`. |
| **PROJECT_DEVELOPER** | `developer@academic.com` | `Dev12345!` | `/developer/workspace`, `/projects`, `/profile`, `/dashboard`. |
| **USER (Researcher)** | `testuser1@gmail.com` / `user@academic.com` | `User123!` | `/requirements/new`, `/marketplace`, `/orders`, `/projects`, `/project-files`. |

---

## 3. Phased Frontend Execution Order

```
[Phase 1: Shell & Visual Base]  ──► TASK 1: Application Launch & Initial UI
                                 │
[Phase 2: Authentication & RBAC]─► TASK 2: Route & Navigation Testing
                                 ├─► TASK 3: Login UI & Session State Testing
                                 ├─► TASK 4: Registration & OTP UI Testing
                                 └─► TASK 5: Role-Based Frontend Access Testing
                                 │
[Phase 3: Workspaces & Portals] ──► TASK 6: Dashboard UI Testing (All Roles)
                                 ├─► TASK 7: Admin & Super Admin Management UI
                                 ├─► TASK 8: Developer Workspace UI Testing
                                 └─► TASK 9: User & Researcher Interface Testing
                                 │
[Phase 4: Component & Controls] ──► TASK 10: Form Controls & Validation Testing
                                 ├─► TASK 11: Project Catalog & Details UI
                                 ├─► TASK 12: Hierarchical Folder Explorer UI
                                 ├─► TASK 13: File Upload & Version History UI
                                 ├─► TASK 14: Secure File Viewer & DRM Testing
                                 ├─► TASK 15: Requirements Management UI
                                 ├─► TASK 16: Marketplace & Orders UI
                                 ├─► TASK 17: Notification Drawer UI
                                 ├─► TASK 18: User Profile & Password Change UI
                                 └─► TASK 19: Search, Filter, Sort & Pagination UI
                                 │
[Phase 5: Quality & Experience] ──► TASK 20: Responsive & Cross-Browser Testing
                                 ├─► TASK 21: End-to-End Frontend User Workflows
                                 └─► FINAL ACCEPTANCE SIGN-OFF
```

---

## 4. Detailed Frontend Testing Tasks

---

### TASK 1 — Application Launch & Initial UI

- **Task ID:** `TASK-FE-01`
- **Task Name:** Application Initialization & Static Asset Integrity
- **Objective:** Verify that the frontend bundle loads instantly without blank screens, unstyled flashes, missing fonts, or broken icons.
- **Components/Pages:** `index.html`, `index.css`, `App.jsx`, `RouteLoader`.
- **Preconditions:** Frontend web server running (`http://localhost:5173` or Vercel URL).
- **Step-by-Step Instructions:**
  1. Open browser in Incognito mode.
  2. Navigate to root URL (`/`).
  3. Observe initial loading spinner (`RouteLoader`) during first-paint.
  4. Verify redirect smoothly lands on `/login`.
  5. Check browser DevTools Console for any 404 resource errors (fonts, SVGs, favicon).
  6. Inspect rendered typography: Confirm font family is `Inter` / `Outfit` / `Roboto` (not generic Times/Arial).
  7. Verify CSS design system tokens: Primary blue buttons (`var(--primary)`), dark theme background (`var(--bg-main)`), and glassmorphism borders are applied.
- **Expected Result:** Clean initial page render in < 1.5s with zero runtime console exceptions.
- **What Tester Should Verify:** No missing Lucide icons, no text overlapping, no horizontal page jump.
- **Pass Criteria:** 100% visual asset loading with 0 console errors.
- **Failure Criteria:** White screen of death (WSOD), broken SVG icons, or unstyled raw HTML.
- **Priority:** `BLOCKER`

---

### TASK 2 — Route & Navigation Testing

- **Task ID:** `TASK-FE-02`
- **Task Name:** Client-Side Routing, Route Guards & Deep-Linking
- **Objective:** Verify navigation between all 16 client routes, active link highlights, browser back/forward buttons, and unauthorized route bounces.
- **Components/Pages:** `App.jsx`, `ProtectedRoute`, `PublicRoute`, `ProtectedLayout.jsx`.
- **Preconditions:** Browser open with no active session.
- **Step-by-Step Instructions:**
  1. Attempt direct URL access to `/dashboard`, `/projects`, `/admins`, `/orders`.
     - *Verify:* Immediate redirection to `/login`.
  2. Log in as `USER` (`user@academic.com`).
  3. In address bar, type `http://localhost:5173/login`.
     - *Verify:* `PublicRoute` immediately redirects back to `/dashboard` (logged-in user cannot view login page).
  4. Manually enter a restricted route in address bar: `/admins`.
     - *Verify:* Renders **"Access Denied"** card stating *"Your account role (USER) does not possess clearance for this management section"*.
     - *Verify:* Clicking **"Go Back"** returns user to previous view.
  5. Enter a non-existent URL: `/invalid-route-xyz`.
     - *Verify:* `RootRedirect` cleanly routes user back to `/dashboard`.
  6. Click through each sidebar link sequentially: Dashboard ➡️ Projects ➡️ Requirements ➡️ Marketplace ➡️ Orders ➡️ Profile.
     - *Verify:* Active navigation link receives blue background highlight (`.nav-link.active`) and matching page title renders in header.
  7. Press browser **Back** and **Forward** buttons repeatedly.
     - *Verify:* History stack navigates without page reloads or broken state.
- **Expected Result:** All routes resolve deterministically with proper role clearance enforcement.
- **Pass Criteria:** Zero route mismatch errors; forbidden pages render custom Access Denied component.
- **Failure Criteria:** Unauthorized view exposes protected data, or refresh causes 404 page.
- **Priority:** `CRITICAL`

---

### TASK 3 — Login UI & Session State Testing

- **Task ID:** `TASK-FE-03`
- **Task Name:** Login Interface, Password Masking & Session Persistence
- **Objective:** Test login form interactions, input masks, loading indicators, error toast alerts, and localStorage session hydration.
- **Components/Pages:** `/login` (`Login.jsx`), `AuthContext.jsx`.
- **Preconditions:** User is logged out.
- **Step-by-Step Instructions:**
  1. Navigate to `/login`.
  2. **Empty Validation:** Click **"Sign In"** button with blank inputs.
     - *Verify:* Input fields highlight with red border; tooltip/alert displays: *"Please fill in all fields"*.
  3. **Password Masking Toggle:**
     - Type `SecretPassword123!` in password input.
     - Verify default state is masked dots (`••••••••`).
     - Click the **Eye icon** (`EyeOff` / `Eye`).
     - Verify text becomes visible; icon toggles to open eye.
  4. **Invalid Credentials Handling:**
     - Enter `user@academic.com` and incorrect password `WrongPass!`.
     - Click **"Sign In"**.
     - Verify button switches to spinning loading state: *"Authenticating..."*.
     - Verify red alert banner renders with clear error message.
  5. **Successful Login & Session Storage:**
     - Enter `superadmin@academic.com` and `Superadmin123!`.
     - Click **"Sign In"**.
     - Verify smooth transition redirect to `/dashboard`.
     - Open DevTools ➡️ Application ➡️ Local Storage.
     - Verify `token` (JWT string) and `currentUser` (JSON object) are stored.
  6. **Page Refresh Session Test:**
     - Refresh page (`F5`).
     - Verify user remains logged in on `/dashboard` without flashing back to login screen.
  7. **Sign Out UI:**
     - Click **"Sign Out"** button in sidebar footer.
     - Verify `localStorage` is cleared and user lands on `/login`.
- **Expected Result:** Login UI provides immediate visual feedback, masks sensitive input, and manages session state smoothly.
- **Pass Criteria:** All interactive states (default, loading, error, success, signout) render accurately.
- **Failure Criteria:** UI freezes during authentication, password visible by default, or session drops on refresh.
- **Priority:** `BLOCKER`

---

### TASK 4 — Registration & OTP Onboarding UI Testing

- **Task ID:** `TASK-FE-04`
- **Task Name:** Multi-Step Registration Form & OTP Verification UI
- **Objective:** Test user self-registration form, input validation tooltips, OTP entry screen, resend countdown timer, and onboarding completion.
- **Components/Pages:** `/register` (`Register.jsx`).
- **Preconditions:** User is logged out.
- **Step-by-Step Instructions:**
  1. Navigate to `/register`.
  2. **Validation Rule Checks:**
     - Enter invalid email format `not-an-email`. Observe real-time validation warning.
     - Enter password `abc` (less than 8 chars). Observe password requirement hint.
     - Enter mismatched passwords in Password and Confirm Password. Observe mismatch error.
  3. **Form Submission:**
     - Fill valid details: Full Name: `Jane Researcher`, Email: `jane_qa@academic.com`, Mobile: `+1-555-0192`, Organization: `MIT Labs`, Password: `TestPassword123!`.
     - Click **"Create Account"**.
     - Verify button shows loading spinner.
  4. **OTP Screen Transition:**
     - Verify UI transitions to 6-digit OTP verification card with recipient email displayed.
  5. **Invalid OTP Entry:**
     - Enter `000000`. Click **"Verify & Activate"**.
     - Verify red error banner appears: *"Invalid verification OTP"*.
  6. **Resend OTP Timer:**
     - Observe the **"Resend Code"** button.
     - Verify countdown timer ticks down (e.g. 30s) before allowing another click.
  7. **Successful Activation:**
     - Enter valid OTP `123456`.
     - Verify green success banner renders and UI automatically routes to `/dashboard`.
- **Expected Result:** Seamless two-step registration wizard with clear validation messages at every step.
- **Pass Criteria:** All form fields validate properly; OTP screen handles invalid, resend, and success states.
- **Failure Criteria:** Page crash on OTP submission or inability to resend code.
- **Priority:** `HIGH`

---

### TASK 5 — Role-Based Frontend Access Testing

- **Task ID:** `TASK-FE-05`
- **Task Name:** Role-Based Navigation & Action Control Matrix
- **Objective:** Verify that every user role (`SUPER_ADMIN`, `ADMIN`, `PROJECT_DEVELOPER`, `USER`) sees only the specific navigation links, action buttons, and views permitted for their role.
- **Components/Pages:** `ProtectedLayout.jsx`, all page headers & action bars.
- **Preconditions:** Test accounts for all 4 roles available.
- **Step-by-Step Instructions:**
  Log in sequentially with each role and verify the UI matches the matrix below:

| UI Element / Route | `SUPER_ADMIN` | `ADMIN` | `PROJECT_DEVELOPER` | `USER` |
| :--- | :---: | :---: | :---: | :---: |
| **Clearance Badge in Header** | `SUPER_ADMIN` (Blue) | `ADMIN` (Cyan) | `PROJECT_DEVELOPER` (Amber)| `USER` (Gray) |
| **Sidebar: Dashboard** (`/dashboard`) | ✅ Visible | ✅ Visible | ✅ Visible | ✅ Visible |
| **Sidebar: Developer Workspace** (`/developer/workspace`)| ✅ Visible | ❌ Hidden | ✅ Visible | ❌ Hidden |
| **Sidebar: Project Review Queue** (`/admin/project-review`)| ✅ Visible | ✅ Visible | ❌ Hidden | ❌ Hidden |
| **Sidebar: Marketplace** (`/marketplace`) | ✅ Visible | ✅ Visible | ❌ Hidden | ✅ Visible |
| **Sidebar: My Orders** (`/orders`) | ✅ Visible | ✅ Visible | ❌ Hidden | ✅ Visible |
| **Sidebar: Projects** (`/projects`) | ✅ Visible | ✅ Visible | ✅ Visible | ✅ Visible |
| **Sidebar: Requirements** (`/requirements`) | ✅ "Requirements" | ✅ "Requirements" | ❌ Hidden | ✅ "My Requirements" |
| **Sidebar: User Management** (`/users`) | ✅ Visible | ✅ Visible | ❌ Hidden | ❌ Hidden |
| **Sidebar: Admin Management** (`/admins`) | ✅ Visible | ❌ Hidden | ❌ Hidden | ❌ Hidden |
| **Sidebar: Audit Logs** (`/audit-logs`) | ✅ Visible | ✅ Visible | ❌ Hidden | ❌ Hidden |
| **Button: "Submit Requirement"** | ❌ Hidden | ❌ Hidden | ❌ Hidden | ✅ Visible |
| **Button: "Create Project"** | ✅ Visible | ✅ Visible | ❌ Hidden | ❌ Hidden |
| **Button: "Manage Permissions"** | ✅ Visible | ❌ Hidden | ❌ Hidden | ❌ Hidden |

- **Expected Result:** UI renders tailored interfaces per role without showing disabled dead-end links or buttons.
- **Pass Criteria:** 100% compliance with the Role-Based Navigation Matrix.
- **Failure Criteria:** Any restricted menu item or administrative button visible to regular `USER`.
- **Priority:** `CRITICAL`

---

### TASK 6 — Dashboard UI Testing (All Roles)

- **Task ID:** `TASK-FE-06`
- **Task Name:** Dynamic Dashboard Metrics, Quick Actions & Recent Activity
- **Objective:** Verify that each role's dashboard renders appropriate metric cards, quick-action shortcuts, and data tables.
- **Components/Pages:** `/dashboard` (`Dashboard.jsx`).
- **Preconditions:** Logged in as respective roles.
- **Step-by-Step Instructions:**
  1. **Super Admin Dashboard:**
     - Verify summary cards: *Total Projects*, *Active Users*, *Admin Coordinators*, *System Audit Events*.
     - Verify Quick Actions: *"Provision Admin"*, *"Access Control Presets"*, *"View System Audit"*.
     - Verify recent user activity table renders with avatar initial badges and role tags.
  2. **Admin Dashboard:**
     - Verify metric cards: *Active Projects*, *Assigned Researchers*, *Pending Requirements*, *Expired Deadlines Warning Card*.
     - Verify shortcut to *"Project Review Queue"*.
  3. **Developer Dashboard:**
     - Verify metric cards: *Assigned Sprints*, *Deliverables in Progress*, *Awaiting Admin Review*.
     - Verify Quick Action button: *"Open Developer Workspace"*.
  4. **User / Researcher Dashboard:**
     - Verify metric cards: *My Submitted Requirements*, *Active Assigned Projects*, *Recent Marketplace Orders*.
     - Verify Quick Action button: *"Submit New Requirement"*.
  5. **Empty States & Loading:**
     - Test dashboard render when user has 0 projects. Verify clean empty-state placeholder: *"No active projects found. Start by submitting a requirement."*
- **Expected Result:** Dashboard cards calculate and render data cleanly with responsive card grids.
- **Pass Criteria:** All metric cards display numbers, icons, and action links matching current user role.
- **Failure Criteria:** Undefined/NaN values in metric cards, broken quick-action links, or misaligned grid items.
- **Priority:** `HIGH`

---

### TASK 7 — Admin & Super Admin Management UI Testing

- **Task ID:** `TASK-FE-07`
- **Task Name:** Admin Coordinator Registry, Permission Matrix Modal & Preset Engine UI
- **Objective:** Test Super Admin and Admin interfaces for user status toggles, admin creation, granular permission assignment, and preset engine modals.
- **Components/Pages:** `/admins` (`AdminManagement.jsx`), `/users` (`UserManagement.jsx`), `AdminAccessControlModal.jsx`, `AdminPermissionManagerModal.jsx`.
- **Preconditions:** Super Admin session active.
- **Step-by-Step Instructions:**
  1. **Admin Management Page (`/admins`):**
     - Verify data table columns: *Admin Name*, *Email*, *Status Badge*, *Assigned Researchers Count*, *Active Permissions List*, *Actions Toolbar*.
     - Click **"Create New Admin"**. Verify modal pops up with Name, Email, Password fields.
     - Submit form with valid data. Verify new Admin row appears in the table with success toast notification.
  2. **Granular Permission Manager Modal:**
     - Click **"Permissions" icon** on an Admin card.
     - Verify checkbox switches for: `PROJECT_ASSIGNMENT_MANAGEMENT`, `ADMIN_MANAGEMENT`, `USER_MANAGEMENT`, `REQUIREMENT_REVIEW`, `FILE_MANAGEMENT`.
     - Toggle 2 permissions on/off. Click **"Save Changes"**.
     - Verify modal closes and permission badges update dynamically on the parent row.
  3. **Access Control Preset Engine Modal (`AdminAccessControlModal.jsx`):**
     - Click **"Access Presets"** button.
     - Test Scope Dropdown: Select `ASSIGNED_ONLY` vs `ALL_STUDENTS_TEACHERS`.
     - Test Preset Cards: Click *Standard Coordinator* ➡️ *Full Governance* ➡️ *Auditor Mode*.
     - Observe the **Live Configuration Preview** panel updating checkboxes in real-time.
     - Click **"Apply Configuration"**. Verify success banner and spinner.
  4. **User Management Page (`/users`):**
     - Click **Status Toggle** switch on a user row (Active 🔄 Inactive).
     - Verify status badge immediately flips from green `ACTIVE` to gray `INACTIVE`.
     - Click **Edit User** modal. Update Full Name. Verify instant table row update.
- **Expected Result:** All administrative modals open smoothly, provide real-time visual feedback, and reflect changes immediately in data tables.
- **Pass Criteria:** Modals trap focus, close on Escape key, and display clear success/error feedback.
- **Failure Criteria:** Modal backdrop prevents closing, checkbox toggles fail to re-render, or unhandled 500 error toast.
- **Priority:** `HIGH`

---

### TASK 8 — Developer Workspace UI Testing

- **Task ID:** `TASK-FE-08`
- **Task Name:** Developer Workspace, Sprints, Deliverables & Submission Modal UI
- **Objective:** Verify developer-exclusive workspace layout, assigned sprint project cards, status progression buttons, and deliverable submission modal.
- **Components/Pages:** `/developer/workspace` (`DeveloperWorkspace.jsx`).
- **Preconditions:** Logged in as `PROJECT_DEVELOPER` (`developer@academic.com`) or `SUPER_ADMIN`.
- **Step-by-Step Instructions:**
  1. Navigate to `/developer/workspace`.
  2. Verify workspace header: Title with `Code2` icon and **"Refresh"** button.
  3. Verify Project Cards:
     - Project Code (e.g. `PRJ-8F3A21`), Project Title, Status Badge (e.g. `In Development`, `Testing`, `Awaiting Review`).
     - Tech Stack pills (e.g. `Java`, `React`, `MySQL`).
     - Action Buttons: *"Start Development"*, *"Submit Deliverable for Review"*, *"Open Project Files"*.
  4. **Status Progression Action:**
     - Click **"Start Development"** on an assigned project.
     - Verify status badge dynamically flips to `IN_PROGRESS` with blue background.
  5. **Submit for Review Modal:**
     - Click **"Submit for Review"** button.
     - Verify modal opens with textarea: *"Deliverables Notes / Release Description"*.
     - Test Empty Submission: Click Submit with empty notes. Observe validation message.
     - Enter notes: *"Completed API Integration and uploaded SRS architecture diagram v2"*.
     - Click **"Confirm & Submit"**.
     - Verify submit button shows spinner: *"Submitting..."*.
     - Verify success alert: *"Project successfully submitted for Admin Review!"*.
     - Verify card status badge updates to `Awaiting Review`.
- **Expected Result:** Developer workspace provides clear task management and smooth deliverable submission modals.
- **Pass Criteria:** Buttons update state reactively and deliverable modal validates notes input.
- **Failure Criteria:** Submit button fails to trigger action or status badge fails to refresh.
- **Priority:** `HIGH`

---

### TASK 9 — User & Researcher Interface Testing

- **Task ID:** `TASK-FE-09`
- **Task Name:** Researcher Workflow, Requirement Wizard & Assigned Projects
- **Objective:** Verify student and researcher self-service user experience across requirement creation, assigned project explorer, and order tracking.
- **Components/Pages:** `/requirements/new`, `/requirements`, `/projects`, `/orders`, `/profile`.
- **Preconditions:** Logged in as `USER` (`user@academic.com` / `testuser1@gmail.com`).
- **Step-by-Step Instructions:**
  1. Navigate to `/requirements/new`.
  2. Verify form layout: Title, Category, Budget (Rs.), Target Technology Stack, Detailed Description, Media Upload Box.
  3. Fill out the requirement form and click **"Submit Requirement"**.
  4. Verify redirect to `/requirements` and confirm new item is highlighted in the list with `DRAFT` or `SUBMITTED` badge.
  5. Navigate to `/projects`.
  6. Verify that only projects assigned to this researcher are listed.
  7. Click on an assigned project card. Verify project details page opens with Project Code, Budget, and embedded `FolderExplorer`.
  8. Navigate to `/orders`. Verify list of purchased marketplace assets with download buttons.
- **Expected Result:** Clean, intuitive researcher interface with no administrative clutter or confusing jargon.
- **Pass Criteria:** End-to-end user navigation flows smoothly without permission errors or visual breaks.
- **Failure Criteria:** User sees unassigned projects or cannot submit new requirements.
- **Priority:** `HIGH`

---

### TASK 10 — Form Controls & Frontend Validation Testing

- **Task ID:** `TASK-FE-10`
- **Task Name:** Comprehensive Form Validation, Boundary Value & Input Sanitization
- **Objective:** Test every form field across the website for required validations, boundary inputs, character length limits, and UI error states.
- **Components/Pages:** Requirement Form, Registration Form, User Edit Modal, Admin Modal, Checkout Modal.
- **Preconditions:** Appropriate role logged in for each form.
- **Step-by-Step Instructions:**
  Execute tests on the specific form controls below:

| Form & Field Tested | Test Input Data | Expected Frontend UI Behavior |
| :--- | :--- | :--- |
| **Requirement Title** | Empty | Red outline; message: *"Title is required"* |
| **Requirement Title** | 1 Character (`A`) | Validation warning: *"Title must be at least 3 characters"* |
| **Requirement Title** | 250+ Characters | Text truncated or character counter warns limit exceeded |
| **Requirement Budget**| Negative number (`-200`) | Input rejected or message: *"Budget must be greater than 0"* |
| **Requirement Budget**| Non-numeric string (`abc`) | Keystroke blocked or HTML5 number validation error |
| **Requirement Description**| `<script>alert(1)</script>` | Renders as escaped plain text without script execution |
| **User Email Input** | `invalid_email.com` | Email regex error: *"Please enter a valid email address"* |
| **User Mobile Input** | `+123ABC456` | Numeric filter warning or formatted phone number display |
| **Password Input** | `weak` (4 chars) | Password meter shows red *"Weak: Min 8 chars, 1 number, 1 symbol"* |
| **Folder Name Input**| `Folder/With/Slashes` | Special character error: *"Folder name cannot contain slashes or symbols"* |
| **Marketplace Quantity**| `0` or `-1` | Prevented by min="1" attribute or disabled checkout button |

- **Expected Result:** Forms provide instant visual validation, highlight invalid inputs with red borders, and disable submit buttons during processing.
- **Pass Criteria:** 100% of invalid test cases produce helpful user-facing validation errors.
- **Failure Criteria:** Form submits with invalid data or throws unhandled JavaScript error.
- **Priority:** `HIGH`

---

### TASK 11 — Project Catalog & Details UI Testing

- **Task ID:** `TASK-FE-11`
- **Task Name:** Project Explorer, Status Filter Tabs & Details Header
- **Objective:** Verify project list cards, status filter tabs, search filter reactivity, and project detail overview bar.
- **Components/Pages:** `/projects` (`Projects.jsx`), `/projects/:id` (`ProjectDetail.jsx`).
- **Preconditions:** Seeded projects available.
- **Step-by-Step Instructions:**
  1. Navigate to `/projects`.
  2. **Status Filter Tabs:**
     - Click filter tabs: `All`, `In Progress`, `Approved`, `Completed`, `Draft`.
     - Verify project card grid re-renders dynamically showing only matching items.
  3. **Live Search Input:**
     - Type project code `PRJ-8F3A21` in search box.
     - Verify instant filtering without full page reload.
     - Type non-existent query `XXXXXX`. Verify empty state: *"No matching projects found."*
  4. **Project Details Page (`/projects/:id`):**
     - Click **"View Project"** on a card.
     - Verify Top Banner: Project Title, Project Code Badge, Status Badge with icon, Budget Badge (`Rs. 15,000.00`).
     - Verify Metadata Strip: Created Date, Created By email, Linked Requirement link.
     - Verify Assigned Team Pill: Shows assigned researcher name, avatar, and assignment notes.
     - Verify Bottom Section embeds the interactive `FolderExplorer`.
- **Expected Result:** Fast, responsive project catalog with clear status indicators and seamless transition into project details.
- **Pass Criteria:** Filter tabs, search box, and details header render all metadata accurately.
- **Failure Criteria:** Missing project code, broken folder explorer embed, or search lag > 300ms.
- **Priority:** `HIGH`

---

### TASK 12 — Hierarchical Folder Explorer UI Testing

- **Task ID:** `TASK-FE-12`
- **Task Name:** Folder Hierarchy Tree, Deep Breadcrumbs & Item Actions
- **Objective:** Test interactive folder tree component (`FolderExplorer.jsx`), node expand/collapse, deep breadcrumbs, folder creation modal, and asset listing.
- **Components/Pages:** `FolderExplorer.jsx`, `/projects/:id/folders/:folderId`.
- **Preconditions:** Project opened with nested folder structure.
- **Step-by-Step Instructions:**
  1. **Tree Expand / Collapse:**
     - Click the chevron/folder icon next to `01_Planning`.
     - Verify subfolders expand smoothly (`SRS Documents`, `Architecture`).
     - Click chevron again. Verify subfolder branch collapses.
  2. **Breadcrumb Trail Navigation:**
     - Click down into `01_Planning` ➡️ `SRS Documents`.
     - Verify Breadcrumb trail renders: `Home > 01_Planning > SRS Documents`.
     - Click `01_Planning` in the breadcrumb. Verify view immediately navigates up one level.
  3. **Create Nested Folder Modal:**
     - Click **"New Folder"** button.
     - Modal prompts for Folder Name. Enter `Database_Schemas`.
     - Click **"Create"**.
     - Verify `Database_Schemas` appears inside the current active folder node.
  4. **Folder Rename & Delete:**
     - Click three-dot action menu on a folder.
     - Click **"Rename"**. Change title to `Database_Schemas_v2`. Verify instant rename.
     - Click **"Delete Folder"**. Verify confirmation dialog appears warning about contained assets.
  5. **Empty Folder State:**
     - Open an empty folder.
     - Verify friendly empty state: *"This folder is empty. Upload documents or create a subfolder."*
- **Expected Result:** Folder tree acts like a native desktop file explorer with instant breadcrumb updates.
- **Pass Criteria:** Tree expansion, breadcrumb clicks, and folder mutations execute without UI glitches.
- **Failure Criteria:** Orphaned breadcrumbs, broken folder tree collapse, or unhandled modal errors.
- **Priority:** `CRITICAL`

---

### TASK 13 — File Upload & Version History Modal Testing

- **Task ID:** `TASK-FE-13`
- **Task Name:** Drag-and-Drop File Upload & Version History Rollback UI
- **Objective:** Test drag-and-drop file upload target, file size validation, duplicate filename versioning detection, and version rollback modal.
- **Components/Pages:** `FileUploadModal.jsx`, `VersionHistoryModal.jsx`.
- **Preconditions:** Folder opened in Project Details.
- **Step-by-Step Instructions:**
  1. **File Upload Modal (`FileUploadModal.jsx`):**
     - Click **"Upload File"** button in Folder Explorer toolbar.
     - Verify upload dropzone appears with dotted border: *"Drag & drop files here or browse"*.
     - Drag a file from OS desktop into the dropzone. Verify dropzone highlights with blue glow.
     - Test File Size Guard: Attempt selecting a dummy file > 500MB.
       - *Verify:* Instant rejection banner: *"File size exceeds 500MB maximum limit."*
  2. **Upload Progress & Asset Card:**
     - Select a valid file `SRS_Specification.pdf` (1.2MB).
     - Enter optional Description: *"Official SRS document v1"*.
     - Click **"Start Upload"**.
     - Verify progress bar animates from 0% to 100% with spinner.
     - Verify modal closes and new asset row appears in the folder table with PDF icon.
  3. **Duplicate Filename Auto-Versioning:**
     - Re-open Upload Modal and select a file with the identical name `SRS_Specification.pdf`.
     - Observe UI prompt: *"A file with this name already exists. Uploading will create Version 2."*
     - Click **"Upload New Version"**.
     - Verify asset row now displays badge: `v2 (Current)`.
  4. **Version History Modal (`VersionHistoryModal.jsx`):**
     - Click the version badge (`v2`) or three-dot menu ➡️ **"Version History"**.
     - Verify modal opens listing:
       - `v2` (Current) — Uploaded today by `admin@academic.com` — Active
       - `v1` (Archived) — Uploaded earlier — Inactive
     - Click **"Set as Current Version"** on `v1`.
     - Verify confirmation alert, modal closes, and asset list updates to show `v1` active.
- **Expected Result:** Clear, user-friendly file upload progress and intuitive multi-version rollback management.
- **Pass Criteria:** Drag-and-drop targets work smoothly; version history modal clearly differentiates current vs historic versions.
- **Failure Criteria:** Browser freezes on drop, version badge fails to increment, or missing rollback trigger.
- **Priority:** `HIGH`

---

### TASK 14 — Secure File Viewer & Content Protection UI Testing

- **Task ID:** `TASK-FE-14`
- **Task Name:** Sandboxed Document Viewer, Dynamic Watermarking & Focus-Loss Blur Layer
- **Objective:** Test specialized security controls in `SecureFileViewer.jsx`, verifying dynamic canvas watermark rendering, text/PDF/media rendering, copy/paste prevention, and blur-on-focus-loss.
- **Components/Pages:** `SecureFileViewer.jsx`.
- **Preconditions:** Asset (PDF, PNG, MP4, SQL, or MD) opened in Project Files or Folder Explorer.
- **Step-by-Step Instructions:**
  1. **Multi-Format Rendering:**
     - Open `System_Requirements.pdf` ➡️ Verify built-in canvas/PDF viewer renders pages.
     - Open `Architecture_Blueprint.png` ➡️ Verify image scales cleanly with zoom controls.
     - Open `Academic_Demo.mp4` ➡️ Verify custom HTML5 video player with play/pause/time scrubber.
     - Open `Database_Schema_v1.sql` ➡️ Verify syntax-highlighted code container with line numbers.
  2. **Dynamic 45° Watermark Overlay:**
     - Inspect the watermark across the viewer canvas.
     - Verify repeated semi-transparent diagonal text:
       - Logged-in user email (e.g. `user@academic.com`)
       - Project Code (e.g. `PRJ-8F3A21`)
       - Live UTC Date & Time
     - Attempt to click or drag watermark. Verify `pointer-events: none` ensures document underlying controls remain clickable.
  3. **Clipboard & Context Menu Disabling:**
     - In text/code view, try selecting text with cursor. Verify `user-select: none` blocks text highlight.
     - Press `Ctrl + C` / `Cmd + C`. Verify copy event is intercepted and no text is copied to clipboard.
     - Right-click anywhere in the viewer. Verify default browser context menu is blocked (`preventDefault()`).
  4. **Window Blur & Focus Loss Shield:**
     - While viewing a document, click outside the browser window or press `Alt + Tab`.
     - Verify document content immediately applies heavy blur (`filter: blur(20px)`).
     - Verify privacy overlay message displays: *"Content protected. Viewer is paused while window is out of focus."*
     - Return focus to browser window. Verify document unblurs instantly.
- **Expected Result:** Document renders crisply with permanent user identity watermark, copy protection, and instant blur when window focus is lost.
- **Pass Criteria:** Watermark accurately reflects current user; copy/context menu disabled; focus-loss blur activates without delay.
- **Failure Criteria:** Plain text selectable, watermark missing user email, or blur fails on Alt+Tab.
- **Priority:** `CRITICAL`

---

### TASK 15 — Requirements Management UI Testing

- **Task ID:** `TASK-FE-15`
- **Task Name:** Requirement Submission Form, Status Badges & Admin Review Lifecycle
- **Objective:** Verify requirement registry table, search/filter controls, requirement detail views with media player preview, and review status transitions.
- **Components/Pages:** `/requirements` (`Requirements.jsx`), `/requirements/new`, `/requirements/:id` (`RequirementDetail.jsx`).
- **Preconditions:** User and Admin test accounts.
- **Step-by-Step Instructions:**
  1. **Requirement Registry View (`/requirements`):**
     - Verify table columns: *ID / Title*, *Category*, *Budget*, *Status Badge*, *Submitted By*, *Created Date*, *Actions*.
     - Test Status Filter: Click `All`, `Draft`, `Submitted`, `Approved`, `Rejected`. Verify table rows filter instantly.
     - Test Search Box: Search by requirement title. Verify instant filter.
     - Click **"Export CSV"** button. Verify browser triggers download of CSV file.
  2. **Requirement Detail View (`/requirements/:id`):**
     - Click **"View Details"** on a requirement.
     - Verify Status Pill: Displays status with color coding (`DRAFT` = Gray, `APPROVED` = Green, `REJECTED` = Red).
     - Verify Media Preview Section:
       - If image attached, renders thumbnail with lightbox preview.
       - If audio briefing attached, renders embedded audio player with play/pause and duration bar.
  3. **Admin Review & Decision Bar (When logged in as Admin):**
     - Verify Admin Decision Bar renders at top: **"Approve Requirement"** (Green) and **"Reject Requirement"** (Red).
     - Click **"Approve"**. Verify status badge updates to `APPROVED` with checkmark icon.
     - Verify regular `USER` does not see the Approve/Reject decision buttons.
- **Expected Result:** Clear requirement tracking with media previews and role-gated approval toolbars.
- **Pass Criteria:** Filter tabs work reactively; media preview players render audio/image attachments.
- **Failure Criteria:** User sees admin approval buttons, or media player fails to load attached audio.
- **Priority:** `HIGH`

---

### TASK 16 — Marketplace & Orders UI Testing

- **Task ID:** `TASK-FE-16`
- **Task Name:** Academic Marketplace Catalog, Checkout Modal & Order Tracking
- **Objective:** Test marketplace solution cards, search/category filtering, purchase checkout modal, and my-orders invoice history.
- **Components/Pages:** `/marketplace` (`Marketplace.jsx`), `/orders` (`Orders.jsx`).
- **Preconditions:** Logged in as `USER` or `ADMIN`.
- **Step-by-Step Instructions:**
  1. **Marketplace Catalog View (`/marketplace`):**
     - Verify solution cards: Product Thumbnail image, Title, Description snippet, Author/Institution badge, Price tag (`Rs. 499.00`), Star rating, **"Purchase Solution"** button.
     - Test Category Filter Pills: `All`, `Machine Learning`, `Data Analytics`, `Evaluation Tools`, `Security Frameworks`.
     - Verify clicking a category filters visible solution cards with smooth CSS transition.
  2. **Interactive Checkout Modal:**
     - Click **"Purchase Solution"** on a card.
     - Verify checkout modal displays:
       - Item Summary & Price Breakdown.
       - Payment Method Selector: Radio buttons for *Credit/Debit Card* and *Institutional PO / Invoice*.
       - Terms & Conditions checkbox.
     - Test validation: Attempt submit without checking Terms. Observe warning alert.
     - Check Terms, select payment method, and click **"Complete Purchase"**.
     - Verify button shows spinner: *"Processing Order..."*.
     - Verify success confirmation modal appears with Order Reference Number (e.g. `ORD-98214`).
  3. **Orders History View (`/orders`):**
     - Navigate to `/orders`.
     - Verify table lists all past orders: *Order ID*, *Item Purchased*, *Purchase Date*, *Amount Paid*, *Status Badge (`COMPLETED` / `PROCESSING`)*, *Invoice Download Button*.
     - Click **"Download Invoice"**. Verify printable invoice card renders.
- **Expected Result:** Polished e-commerce marketplace experience with clean checkout modal and order invoice tracking.
- **Pass Criteria:** Category filters update cards reactively; checkout flow creates visible record in Orders view.
- **Failure Criteria:** Checkout modal hangs, price calculation NaN, or orders table fails to update.
- **Priority:** `MEDIUM`

---

### TASK 17 — Notification Drawer UI Testing

- **Task ID:** `TASK-FE-17`
- **Task Name:** Slide-Out Notification Drawer & Unread Counter Badge
- **Objective:** Test top-bar notification bell icon, unread counter badge, slide-out drawer animation, mark-as-read toggles, and clear-all actions.
- **Components/Pages:** `NotificationDrawer.jsx`, `ProtectedLayout.jsx`.
- **Preconditions:** Logged in with unread system notifications.
- **Step-by-Step Instructions:**
  1. **Notification Bell & Counter:**
     - Observe notification bell icon in top header bar.
     - Verify red badge pill displays unread count (e.g. `3`).
  2. **Drawer Open / Close Animation:**
     - Click the notification bell.
     - Verify notification drawer smoothly slides in from right edge of screen (`transform: translateX(0)`).
     - Verify background receives semi-transparent overlay backdrop.
     - Click backdrop or **Close (X)** button. Verify drawer slides back out.
  3. **Notification Items & Mark as Read:**
     - Re-open drawer.
     - Verify notification items display: Icon (Warning/Info/Check), Title, Message body, Relative timestamp (e.g. *"10 minutes ago"*).
     - Click on an unread notification item.
     - Verify unread blue dot disappears and header unread badge count decreases by 1.
  4. **Clear All Notifications:**
     - Click **"Clear All"** link in drawer header.
     - Verify all notifications are removed.
     - Verify empty drawer state renders: Bell icon illustration + *"You have no notifications"*.
- **Expected Result:** Responsive, non-intrusive notification drawer with real-time counter updates.
- **Pass Criteria:** Drawer opens/closes with smooth animation; unread counter badge syncs with read actions.
- **Failure Criteria:** Drawer clips off-screen, counter fails to decrement, or backdrop click fails to dismiss.
- **Priority:** `MEDIUM`

---

### TASK 18 — User Profile & Password Change UI Testing

- **Task ID:** `TASK-FE-18`
- **Task Name:** Profile Details Editor, Role Clearance Card & Password Change UI
- **Objective:** Test `/profile` interface, personal information updates, session clearance badge display, and password modification form validation.
- **Components/Pages:** `/profile` (`Profile.jsx`).
- **Preconditions:** Logged in as any valid user.
- **Step-by-Step Instructions:**
  1. Navigate to `/profile`.
  2. **Profile Overview Card:**
     - Verify user avatar initial, Full Name, Email, Organization, Account Created Date.
     - Verify **Role Clearance Pill**: Displays role name with security shield icon and clearance level explanation.
  3. **Edit Personal Information:**
     - Update Full Name: `Dr. Alex Morgan`.
     - Update Mobile: `+1-555-9012`.
     - Click **"Save Changes"**.
     - Verify success toast: *"Profile updated successfully!"*.
     - Verify top header user pill immediately updates to display `Dr. Alex Morgan`.
  4. **Change Password Form Validation:**
     - In Password section, enter Current Password, New Password, and Confirm New Password.
     - Test Mismatch: Enter `NewPass123!` and `DifferentPass123!`.
       - *Verify:* Red warning: *"New passwords do not match"*.
     - Test Short Password: Enter `short`.
       - *Verify:* Warning: *"Password must be at least 8 characters"*.
     - Fill valid passwords and click **"Update Password"**.
     - Verify success alert and password fields clear automatically.
- **Expected Result:** Profile page updates user metadata and reflects changes in real-time across the application shell.
- **Pass Criteria:** Header user badge syncs with profile name update; password validation prevents weak/mismatched entries.
- **Failure Criteria:** Profile update fails to persist in UI cache or header fails to re-render.
- **Priority:** `MEDIUM`

---

### TASK 19 — Search, Filter, Sort & Pagination UI Testing

- **Task ID:** `TASK-FE-19`
- **Task Name:** Table Search Reactivity, Column Sorting & Multi-Page Pagination
- **Objective:** Verify search debounce, multi-column sorting arrows, status dropdown filtering, and pagination button controls across all tabular pages (`/projects`, `/requirements`, `/users`, `/audit-logs`, `/orders`).
- **Components/Pages:** Data tables across all views.
- **Preconditions:** Seeded data loaded with > 10 rows.
- **Step-by-Step Instructions:**
  1. **Instant Search Debounce:**
     - On `/users`, type `super` in the search box.
     - Verify table immediately filters to `superadmin@academic.com` without page lag.
     - Clear the search box. Verify full list restores instantly.
  2. **Case-Insensitive Search:**
     - Type uppercase `ADMIN` and lowercase `admin`. Verify identical matching results.
  3. **Column Header Sorting:**
     - On `/projects` or `/audit-logs`, click column header: **"Created Date"** or **"Project Name"**.
     - Verify ascending sort arrow (`▲`) appears and rows re-order A-to-Z / Oldest-to-Newest.
     - Click column header again. Verify descending sort arrow (`▼`) appears and rows flip Z-to-A.
  4. **Multi-Criteria Filter Combination:**
     - On `/requirements`, select Status: `APPROVED` AND type search query: `System`.
     - Verify table shows only rows that satisfy **both** conditions simultaneously.
  5. **Pagination Controls:**
     - Verify bottom pagination bar: *Showing 1-10 of 45 items*, **Previous**, **Next**, page numbers (`1`, `2`, `3`, `4`, `5`).
     - Click **"Next"** (`>`). Verify page 2 loads, table rows refresh, and active page pill highlights `2`.
     - Click **"Previous"** (`<`). Verify returns to page 1; **Previous** button becomes disabled on page 1.
- **Expected Result:** Instant, accurate tabular searching, sorting, and multi-page pagination.
- **Pass Criteria:** Sorting arrows accurately indicate direction; search filters combined with pagination without index errors.
- **Failure Criteria:** Pagination breaks on filtered search results, or sorting throws JavaScript sort error.
- **Priority:** `HIGH`

---

### TASK 20 — Responsive Viewports & Cross-Browser UI Testing

- **Task ID:** `TASK-FE-20`
- **Task Name:** Multi-Viewport Adaptability & Cross-Browser Visual Parity
- **Objective:** Verify layout responsiveness, sidebar collapsing, touch target sizing, and visual parity across Desktop, Tablet, and Mobile screen widths in all major browsers.
- **Components/Pages:** Entire frontend application.
- **Preconditions:** Chrome DevTools Device Emulation or physical mobile devices; Chrome, Edge, Firefox, Safari.
- **Step-by-Step Instructions:**
  1. **Desktop Viewports (`1920x1080` / `1440x900`):**
     - Full sidebar width (260px) visible with icon and label text.
     - Dashboard cards layout in 3-4 column CSS grid.
  2. **Tablet Viewport (`768x1024` iPad):**
     - Sidebar collapses to compact icon-only column (80px) with tooltips.
     - Header adjusts padding; dashboard grid wraps into 2 columns.
  3. **Mobile Viewport (`375x812` iPhone / `412x915` Android):**
     - Sidebar collapses off-canvas; top header displays **Hamburger Menu** icon (`Menu`).
     - Click hamburger icon. Verify full-height mobile navigation drawer slides in.
     - Data tables on `/users`, `/requirements`, and `/audit-logs` provide smooth horizontal scroll container (`overflow-x: auto`) without expanding the outer page body.
     - Modals (e.g. Upload Modal, Review Modal) resize to 95vw with accessible touch close buttons (min 44x44px).
  4. **Cross-Browser Parity Test:**
     - **Google Chrome**: Verify baseline styling and animations.
     - **Microsoft Edge**: Verify identical Chromium performance.
     - **Mozilla Firefox**: Verify glassmorphic card backdrop blur (`backdrop-filter: blur(12px)`) renders properly without gray artifacts.
     - **Apple Safari (iOS/macOS)**: Verify flexbox alignments, date picker inputs, and SVG rendering.
- **Expected Result:** Flawless visual aesthetics and total touch/click usability across all device form factors.
- **Pass Criteria:** Zero horizontal page blowout on mobile; mobile menu accessible; consistent font and colors on all browsers.
- **Failure Criteria:** Overlapping text on mobile, inaccessible buttons on touch devices, or broken styling in Firefox/Safari.
- **Priority:** `CRITICAL`

---

### TASK 21 — End-to-End Frontend User Workflows

- **Task ID:** `TASK-FE-21`
- **Task Name:** Complete Real-World Multi-Role Frontend Workflows
- **Objective:** Execute full end-to-end user journeys from login to completion for all 4 roles to verify that all frontend pages, modals, notifications, and navigations integrate seamlessly.
- **Components/Pages:** All pages across the website.
- **Preconditions:** Frontend connected to active backend or mock engine.
- **Step-by-Step Instructions:**

#### 👤 Workflow A: Academic Researcher (`USER`)
1. Open `/login` ➡️ Sign in as `user@academic.com`.
2. Lands on `/dashboard` ➡️ Click **"Submit New Requirement"**.
3. Fill `/requirements/new` form with title *"Automated Evaluation Portal"*, budget `Rs. 15,000` ➡️ Click Submit.
4. Navigate to `/requirements` ➡️ Confirm requirement appears in list.
5. Navigate to `/projects` ➡️ Open assigned project `PRJ-8F3A21`.
6. Browse `FolderExplorer` ➡️ Open subfolder `SRS Documents` ➡️ Click `SRS_Specification.pdf`.
7. `SecureFileViewer` opens ➡️ Verify dynamic diagonal watermark with `user@academic.com`.
8. Alt+Tab out of window ➡️ Verify document blurs ➡️ Alt+Tab back in ➡️ Verify unblurs.
9. Close viewer ➡️ Navigate to `/marketplace` ➡️ Click **"Purchase Solution"** on an academic tool.
10. Complete checkout in modal ➡️ Navigate to `/orders` ➡️ Verify invoice is listed.
11. Navigate to `/profile` ➡️ Update phone number ➡️ Click **"Sign Out"** in sidebar.

#### 👔 Workflow B: Project Coordinator (`ADMIN`)
1. Open `/login` ➡️ Sign in as `admin@academic.com`.
2. Lands on `/dashboard` ➡️ Open `/requirements` ➡️ Click on submitted requirement.
3. In Decision Bar, click **"Approve Requirement"** ➡️ Confirm status becomes `APPROVED`.
4. Navigate to `/admin/project-review` ➡️ Review developer deliverables ➡️ Click **"Approve Deliverables"**.
5. Navigate to `/projects` ➡️ Open project ➡️ Create folder `02_Deliverables`.
6. Open Upload Modal ➡️ Upload `Architecture_Blueprint.png` ➡️ Confirm upload in folder tree.
7. Click **"Sign Out"**.

#### 🛡️ Workflow C: Global Administrator (`SUPER_ADMIN`)
1. Open `/login` ➡️ Sign in as `superadmin@academic.com`.
2. Lands on `/dashboard` ➡️ Navigate to `/admins`.
3. Click **"Create New Admin"** ➡️ Provision test coordinator ➡️ Confirm appearance in table.
4. Click **"Access Presets"** ➡️ Select *Full Governance* preset ➡️ Click **"Apply Configuration"**.
5. Navigate to `/users` ➡️ Toggle user status ➡️ Edit user role.
6. Navigate to `/audit-logs` ➡️ Verify all recent actions appear in the immutable timeline.
7. Click **"Sign Out"**.

#### 💻 Workflow D: Project Developer (`PROJECT_DEVELOPER`)
1. Open `/login` ➡️ Sign in as `developer@academic.com`.
2. Lands on `/dashboard` ➡️ Click **"Developer Workspace"** in sidebar.
3. In `/developer/workspace`, find assigned project card.
4. Click **"Start Development"** ➡️ Confirm badge flips to `In Development`.
5. Click **"Submit for Review"** ➡️ Enter release notes in modal ➡️ Confirm submission.
6. Open project folder ➡️ Inspect version history of asset ➡️ Click **"Sign Out"**.

- **Expected Result:** All 4 workflows complete smoothly from start to finish with zero UI dead-ends or unhandled errors.
- **Pass Criteria:** 100% of the 4 complete workflows pass without friction.
- **Failure Criteria:** User gets stuck at any intermediate step or modal fails to dismiss.
- **Priority:** `BLOCKER`

---

## 5. Frontend Defect Report Template & Severity Rubric

When logging a frontend issue, use the following standardized format:

```markdown
### [FE-BUG-001] Brief, Descriptive Title of UI Issue

- **Test Case ID:** (e.g. TC-FE-DRM-002 / TASK-FE-14)
- **Module / Component:** (e.g. SecureFileViewer / FolderExplorer / Login)
- **Page Route:** (e.g. /projects/1 or /register)
- **User Role Tested:** (SUPER_ADMIN / ADMIN / PROJECT_DEVELOPER / USER)
- **Browser & OS:** Chrome 124 on Windows 11 / Safari on macOS
- **Screen Resolution:** 1920x1080 (Desktop) / 375x812 (Mobile)
- **Severity:** [ BLOCKER | CRITICAL | HIGH | MEDIUM | LOW ]

#### Steps to Reproduce:
1. Log in as `user@academic.com`.
2. Navigate to `/projects/1` and open `FolderExplorer`.
3. Click on `Architecture_Blueprint.png` to launch `SecureFileViewer`.
4. Press `Alt + Tab` to switch focus away from the browser window.

#### Expected Result:
The document should immediately apply a 20px blur filter and display the focus-loss privacy shield message.

#### Actual Result:
The document remains completely unblurred and visible while the window is out of focus.

#### Evidence:
- **Screenshot / Recording:** [Attach screenshot or GIF recording]
- **Console Error (if any):** `Uncaught TypeError: window.addEventListener is not a function at SecureFileViewer.jsx:45`
- **UI Dependency Note:** (e.g. "Frontend issue caused by API/backend dependency" OR "Pure frontend UI bug")

#### Defect Status:
- [ ] NEW
- [ ] IN TRIAGE
- [ ] FIX IN PROGRESS
- [ ] READY FOR RETEST
- [ ] VERIFIED & CLOSED
```

### 🏷️ Frontend Severity Rubric

| Severity | Frontend Impact Definition | Example |
| :--- | :--- | :--- |
| 🔴 **BLOCKER** | Entire application is unusable; login impossible; white screen of death. | Root bundle crash, cannot type in login form. |
| 🟠 **CRITICAL** | Core user journey blocked with no workaround; security DRM failure. | Watermark missing on secure viewer; cannot submit requirement. |
| 🟡 **HIGH** | Major component broken, but an alternate path or manual workaround exists. | File drag & drop fails (browse still works); filter search laggy. |
| 🔵 **MEDIUM** | Cosmetic misalignment, incorrect badge color, or animation glitch. | Modal close icon misaligned by 4px; toast dismisses too fast. |
| ⚪ **LOW** | Minor typo or minor aesthetic suggestion. | Text typo in placeholder description. |

---

## 6. Master Frontend Test Execution Tracker

The QA team should execute and record all test cases in the master tracker below:

| Test ID | Module | Test Case Description | Role | Browser | Viewport | Assigned QA | Status | Defect ID | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `TC-FE-APP-001` | Launch | Bundle first-paint & RouteLoader spinner | Guest | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | Load video |
| `TC-FE-APP-002` | Launch | Design system CSS tokens & font loading | Guest | Firefox | 1440x900 | QA 1 | `NOT STARTED` | — | DevTools shot |
| `TC-FE-NAV-001` | Routing | Public route bounce to `/login` | Guest | Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Nav video |
| `TC-FE-NAV-002` | Routing | Role-restricted route Access Denied fallback | USER | Edge | 1920x1080 | QA 1 | `NOT STARTED` | — | Card shot |
| `TC-FE-AUTH-001`| Auth | Valid Super Admin login & session redirect | SUPER_ADMIN| Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Login capture |
| `TC-FE-AUTH-002`| Auth | Password eye icon mask/unmask toggle | Any | Safari | 1440x900 | QA 2 | `NOT STARTED` | — | Toggle shot |
| `TC-FE-AUTH-003`| Auth | Invalid credentials error banner presentation | Any | Firefox | 1920x1080 | QA 2 | `NOT STARTED` | — | Alert shot |
| `TC-FE-AUTH-004`| Auth | Sign Out button localStorage session purge | USER | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Storage shot |
| `TC-FE-REG-001` | Onboarding| Registration form field validation rules | New User | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | Form shot |
| `TC-FE-REG-002` | Onboarding| 6-digit OTP verification card transition | New User | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | OTP shot |
| `TC-FE-REG-003` | Onboarding| Resend OTP countdown timer verification | New User | Edge | 1920x1080 | QA 3 | `NOT STARTED` | — | Timer video |
| `TC-FE-RBAC-001`| RBAC | User vs Admin vs Super Admin sidebar items | Multi-Role | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | Sidebar matrix|
| `TC-FE-DASH-001`| Dashboard | Super Admin metric cards & quick actions | SUPER_ADMIN| Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Dash shot |
| `TC-FE-DASH-002`| Dashboard | Researcher active projects & empty state | USER | Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Empty shot |
| `TC-FE-ADM-001` | Admin | Admin coordinator table & creation modal | SUPER_ADMIN| Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Admin shot |
| `TC-FE-ADM-002` | Admin | Access control preset selector & preview | SUPER_ADMIN| Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Preset shot |
| `TC-FE-DEV-001` | Developer | Developer workspace sprint project cards | DEV | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | Dev card shot |
| `TC-FE-DEV-002` | Developer | Deliverables submission modal & notes form | DEV | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | Modal shot |
| `TC-FE-USR-001` | User | Requirement creation wizard submission | USER | Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Req form shot |
| `TC-FE-FORM-001`| Validation | Budget input negative & string rejection | USER | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Tooltip shot |
| `TC-FE-FORM-002`| Validation | Script tag XSS input text sanitization | USER | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Render shot |
| `TC-FE-PRJ-001` | Projects | Status filter tabs & live search debounce | USER | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | Search video |
| `TC-FE-PRJ-002` | Projects | Project details header & team pill badges | USER | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | Header shot |
| `TC-FE-FLD-001` | Explorer | Recursive tree expand/collapse & breadcrumb| ADMIN | Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Tree video |
| `TC-FE-FLD-002` | Explorer | New subfolder creation & rename modal | ADMIN | Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Modal shot |
| `TC-FE-UPL-001` | Upload | Drag & drop target hover glow & size guard | ADMIN | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Upload shot |
| `TC-FE-UPL-002` | Versioning| Duplicate filename auto-versioning badge | ADMIN | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Badge shot |
| `TC-FE-UPL-003` | Versioning| Version history modal rollback to v1 | ADMIN | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | History shot |
| `TC-FE-DRM-001` | DRM Viewer| 45° dynamic diagonal watermark rendering | USER | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | Watermark shot|
| `TC-FE-DRM-002` | DRM Viewer| Window focus loss blur overlay activation | USER | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | Blur shot |
| `TC-FE-DRM-003` | DRM Viewer| Right-click & Ctrl+C clipboard interception| USER | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | Intercept shot|
| `TC-FE-REQ-001` | Requirements| Requirement detail media audio player | USER | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | Player shot |
| `TC-FE-REQ-002` | Requirements| Admin approve/reject decision toolbar | ADMIN | Chrome | 1920x1080 | QA 3 | `NOT STARTED` | — | Bar shot |
| `TC-FE-MKT-001` | Marketplace| Category filter pills & solution cards | USER | Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Catalog shot |
| `TC-FE-MKT-002` | Marketplace| Checkout modal terms check & purchase | USER | Chrome | 1920x1080 | QA 1 | `NOT STARTED` | — | Checkout shot|
| `TC-FE-NOTIF-001`| Notifications| Slide-out drawer animation & unread badge | USER | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Drawer video |
| `TC-FE-PROF-001`| Profile | User metadata update & header sync | USER | Chrome | 1920x1080 | QA 2 | `NOT STARTED` | — | Profile shot |
| `TC-FE-RESP-001`| Responsive | Mobile 375px hamburger drawer navigation | USER | Chrome (Emul)| 375x812 | QA 3 | `NOT STARTED` | — | Mobile video |
| `TC-FE-RESP-002`| Responsive | Tablet 768px icon-only collapsed sidebar | USER | Edge | 768x1024 | QA 3 | `NOT STARTED` | — | Tablet shot |
| `TC-FE-BRW-001` | Cross-Browser| Firefox backdrop-filter blur rendering | USER | Firefox | 1920x1080 | QA 1 | `NOT STARTED` | — | Firefox shot |
| `TC-FE-BRW-002` | Cross-Browser| Safari flexbox & SVG rendering parity | USER | Safari | 1440x900 | QA 1 | `NOT STARTED` | — | Safari shot |
| `TC-FE-E2E-001` | Workflow | Full Researcher Journey (Req to Viewer) | USER | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | E2E video |
| `TC-FE-E2E-002` | Workflow | Full Admin Journey (Review to File Upload) | ADMIN | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | E2E video |
| `TC-FE-E2E-003` | Workflow | Full Super Admin Journey (Presets & Audit) | SUPER_ADMIN| Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | E2E video |
| `TC-FE-E2E-004` | Workflow | Full Developer Journey (Sprint to Submit) | DEV | Chrome | 1920x1080 | QA Lead | `NOT STARTED` | — | E2E video |

---

## 7. Final Frontend Acceptance Sign-Off Checklist

Before granting production approval, the QA Lead must certify all items below:

### 🖥️ Visual & Layout Readiness
- [ ] Application loads without White Screen of Death (WSOD) or flashes of unstyled content.
- [ ] Glassmorphism styling, primary color palette, and typography render cleanly.
- [ ] Responsive layouts operate smoothly on Desktop (1920px), Tablet (768px), and Mobile (375px).
- [ ] Mobile hamburger menu opens and closes without horizontal viewport blowout.
- [ ] Verified visual consistency across Chrome, Edge, Firefox, and Safari.

### 🛡️ Authentication & Access Control
- [ ] Unauthorized URL direct access cleanly redirects to `/login`.
- [ ] Role clearance badge accurately displays active role (`SUPER_ADMIN`, `ADMIN`, `PROJECT_DEVELOPER`, `USER`).
- [ ] Role-restricted views render custom **Access Denied** fallback card.
- [ ] Logout completely purges `localStorage` session tokens and resets navigation.

### ⚙️ Interactive Components & Forms
- [ ] All forms validate required fields, email formats, and number bounds with user-friendly alerts.
- [ ] `FolderExplorer` expands, collapses, creates subfolders, and updates breadcrumbs correctly.
- [ ] `FileUploadModal` supports drag-and-drop, validates file size limits (500MB), and shows progress.
- [ ] `VersionHistoryModal` handles duplicate filenames with version increments and rollback triggers.
- [ ] `SecureFileViewer` renders dynamic 45° diagonal watermark with user email and UTC time.
- [ ] `SecureFileViewer` blurs immediately on window focus loss and prevents right-click/copying.
- [ ] `NotificationDrawer` updates unread badge counter and supports mark-as-read actions.
- [ ] `ErrorBoundary` catches unexpected render crashes with recovery buttons.

---

### 🏁 Final Quality Decision

```
[ ] PASS  — FRONTEND IS PRODUCTION READY
[ ] FAIL  — FRONTEND IS NOT READY (Open Blocker/Critical defects exist)
```

| Sign-Off Role | Name | Signature | Date |
| :--- | :--- | :--- | :--- |
| **Lead Frontend QA Engineer** | _________________________ | _________________________ | ____________ |
| **Lead UI/UX Designer** | _________________________ | _________________________ | ____________ |
| **Frontend Engineering Lead** | _________________________ | _________________________ | ____________ |
