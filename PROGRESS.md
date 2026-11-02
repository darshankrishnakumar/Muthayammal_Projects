# Platform Enhancement — Progress Log

This file tracks the transformation of the existing app into a multi-college academic
project distribution and development platform. It records what was inspected, what changed,
what was verified, and what is still open. Status markers: ✅ done and verified · 🟡 done, not
fully verified · ⬜ not started · ⛔ blocked on a human.

A baseline git commit (`Baseline snapshot before platform enhancement`) was made before any
change, so every step below can be diffed or reverted.

---

## 1. Audit findings (Phase 1)

### Build / repository
| # | Finding | Severity |
|---|---|---|
| B1 | Backend did not compile: `com.academic.service.storage.FileStorageService` was missing. Root cause: `.gitignore` rule `storage/` also matched `src/main/java/.../service/storage/`, so the package was never committed upstream. | Blocker |
| B2 | `src/utils/api.js` defines the same keys twice inside one object literal (`getRequirements`, `getRequirementById`, `getRequirementStats`, `createRequirement`, `updateRequirement`, `submitRequirement`, `approveRequirement`, `rejectRequirement`, `getApprovedRequirements`, `getProjectByRequirementId`, `getDevelopers`, `getDeveloperProjects`, `assignDeveloperToProject`, `getAdminPermissions`, `updateAdminPermissions`, `applyAdminPreset`, `getAssignedUsers`, `assignUsersToAdmin`, `getAccessControlOverview`). The later definition silently wins; `assignDeveloperToProject` has two incompatible signatures. | High |
| B3 | Integration tests run against the real local MySQL `academic_db` with the root password. | High |
| B4 | Production frontend falls back to a hard-coded, already-dead Cloudflare tunnel URL. | Medium |
| B5 | README is the Vite template; setup docs are Windows-only. | Low |

### Security
| # | Finding | Severity |
|---|---|---|
| S1 | **Payment bypass**: `POST /api/projects/{id}/pay-remaining` has no ownership or state check and accepts a client-chosen amount. Any user can unlock any project for ₹0.01 and is recorded as its owner. | Critical |
| S2 | **Purchase hijack**: `POST /api/projects/{id}/purchase-marketplace` works on any project (not only marketplace items), overwrites `purchasedByUserId`, and sets status `ACCESS_GRANTED`. | Critical |
| S3 | **Privilege escalation**: `POST /api/users` only blocks role `USER`; an `ADMIN` or `PROJECT_DEVELOPER` can create a `SUPER_ADMIN`. `PUT /api/users/{id}` lets an ADMIN promote a user to `SUPER_ADMIN`. | Critical |
| S4 | `/api/orders/checkout` trusts client-supplied item name and amount and marks it `COMPLETED`. | High |
| S5 | Hard-coded DB root password and JWT signing secret in `application.properties` (and test config); seeded accounts with known passwords. | High |
| S6 | JWT filter trusts the role claim in the token; role changes, deactivation and deletion do not take effect until the token expires (24 h). | High |
| S7 | IDOR: `GET /api/projects/by-requirement/{id}`, `GET /api/projects/{id}/assignments` have no access check. `PROJECT_DEVELOPER` can change any project's status and assign users to any project. | High |
| S8 | Idempotency keys are global; replaying another user's key returns their order. | Medium |
| S9 | CORS allows `*` origins with credentials; `@CrossOrigin("*")` on controllers. | Medium |
| S10 | Registration skips OTP (`emailVerified=true` immediately). OTP exists but is never sent. | Medium (needs mail infra) |
| S11 | Flyway `repair()` runs on every boot, which hides migration checksum drift. | Low |
| S12 | Frontend mock mode (localStorage fake DB, fake logins) can be switched on in production builds. | Medium |

### Business model gaps
| # | Gap |
|---|---|
| G1 | No **College** concept at all. ADMINs are global, not college-scoped. |
| G2 | A project can have only one buyer (`projects.purchased_by_user_id`), so one library project cannot be distributed to many students or colleges. |
| G3 | No college → project **allocation**. |
| G4 | Marketplace catalog is a hard-coded list of 6 fake items in `OrderService.getCatalog()`. |
| G5 | Library metadata missing: abstract, domain, tags, price, publish/archive state, install instructions, file categories, preview assets. |
| G6 | Custom development flow has no "college admin forwards" step, no developer acceptance, no progress tracking, no status history/timeline. |
| G7 | Payments are simulated inline with no provider abstraction and no transaction records. |
| G8 | Dashboards are not role-specific and do not reflect colleges. |

---

## 2. Target architecture (decisions)

* **One central library.** Library projects live once in `projects` (`project_type = LIBRARY`).
  Files are stored once (existing folder/asset storage). Colleges get access through
  `college_project_allocations`, never through copies.
* **Colleges.** New `colleges` table; `user_management.college_id` (required for ADMIN and USER,
  null for SUPER_ADMIN and PROJECT_DEVELOPER).
* **USER = student account** belonging to exactly one college.
* **Entitlements.** New `project_entitlements` (user, project, source, order) replaces the single
  `purchased_by_user_id` as the access grant. The old column is kept and back-filled for
  compatibility.
* **College isolation is enforced in services** through one `CollegeScopeService`; every
  ADMIN/USER query is filtered by the actor's college; deny by default.
* **Payments.** `PaymentGateway` interface; `SimulatedPaymentGateway` is active only when
  `academic.payments.simulation-enabled=true` and every transaction it records is labelled
  `SIMULATED`. The server always computes the amount. Access is granted only from a
  verified payment transaction.
* **Custom development flow.** Requirement: `DRAFT → SUBMITTED → (college admin forwards)
  SUPER_ADMIN_REVIEW → (super admin quotes) ADVANCE_PAYMENT_PENDING → (paid)
  ADVANCE_PAYMENT_COMPLETED → (project created, developer assigned) IN_PROGRESS → COMPLETED`.
  Project: `DEVELOPER_ASSIGNED → (developer accepts) IN_PROGRESS → READY_FOR_REVIEW →
  CHANGES_REQUESTED | REVIEW_APPROVED → READY_FOR_FINAL_PAYMENT → ACCESS_GRANTED`.
  Every transition is written to `status_history` for the timeline.
* **Config.** Secrets come from environment variables; a git-ignored
  `application-local.properties` holds local values; tests use an in-memory H2 database.
* **Frontend.** Keep React/Vite/plain CSS. Add a token-based design system, a reusable component
  set, and a small set of ReactBits-style effects (reveal, count-up, spotlight card) written
  in-house with `prefers-reduced-motion` respected, without pulling in an animation framework.

---

## 3. Implementation checklist

### Phase 0 — Stabilise
- ✅ Baseline git commit
- ✅ Restore `FileStorageService` (B1); anchor `.gitignore` storage rules
- ⬜ Isolated H2 test profile (B3)
- ⬜ Secrets to env / local profile (S5), CORS allow-list (S9), Flyway repair opt-in (S11)

### Phase 1 — Backend domain
- ⬜ Migration V13: colleges, allocations, entitlements, payment transactions, status history, library metadata columns
- ⬜ College CRUD + college admin assignment
- ⬜ Library management (metadata, publish/archive, file categories, preview flag)
- ⬜ Allocation APIs (bulk allocate, revoke, price override)
- ⬜ Marketplace API backed by allocations
- ⬜ Payment gateway abstraction + verified purchase/advance/final flows
- ⬜ Custom development workflow + status history
- ⬜ Role dashboards API

### Phase 2 — Security hardening
- ⬜ JWT filter reloads user (S6)
- ⬜ Role-creation matrix (S3)
- ⬜ Payment endpoints (S1, S2, S4, S8)
- ⬜ IDOR fixes (S7) and college isolation in user/requirement/order/project queries
- ⬜ Entitlement-based file access

### Phase 3 — Frontend
- ⬜ Design tokens + component library
- ⬜ App shell: collapsible sidebar, top bar, breadcrumbs, role navigation, mobile nav
- ⬜ API layer cleanup (B2, B4, S12)
- ⬜ Pages: dashboards, library, colleges, allocations, marketplace, project detail, orders, development workflow

### Phase 4 — Verification
- ⬜ Backend unit + integration tests (college isolation, payments, transitions, file access)
- ⬜ Frontend build + lint
- ⬜ End-to-end walk-through of all four roles against a local backend

### Phase 5 — Deployment readiness
- ⬜ `.env.example`, `application-local.properties.example`, README rewrite

---

## 4. Session log

*(newest last)*

1. Audit completed; findings above.
