# Platform Enhancement: Progress Log

This log tracks how the existing app was turned into a multi-college platform for distributing and developing academic projects. It records what was inspected, what changed, how it was verified, and what is still open.

| Marker | Meaning |
|---|---|
| ✅ | done and verified |
| 🟡 | done, partly verified |
| ⬜ | not done |
| ⛔ | needs a person or external setup |

Every step is a git commit on top of `Baseline snapshot before platform enhancement`, so each change can be diffed or reverted.

---

## 1. Audit findings and their resolution

### Build and repository
| # | Finding | Status |
|---|---|---|
| B1 | Backend did not compile: `service/storage/FileStorageService` was missing. The `.gitignore` rule `storage/` also matched the Java package, so it was never committed. | ✅ Recreated. The ignore rule is now anchored to the repo root. |
| B2 | `api.js` defined ~19 methods twice; the later definition silently won, and the two `assignDeveloperToProject` versions took different arguments. "Live" mode also fell back to fake localStorage data whenever the backend errored. | ✅ Rewritten as a live-only client with one definition per method and typed errors. |
| B3 | Integration tests ran against the real local MySQL, using the root password. | ✅ Tests now use in-memory H2. |
| B4 | The production frontend fell back to a hard-coded, already-dead tunnel URL. | ✅ Production builds now require `VITE_API_URL`; the URL override is dev-only. |
| B5 | The README was the Vite template; setup docs covered Windows only. | ✅ Rewritten. |
| B6 | *(found during verification)* A bean cycle between `SecurityConfig`, the JWT filter, the repositories and Flyway would stop production startup. H2 tests couldn't catch it because Flyway is off there. | ✅ Flyway strategy moved to its own `FlywayConfig`. |
| B7 | *(found during verification)* Migrations V1–V12 did not match the entities. `ddl-auto=update` had been hiding missing columns, and `user_management.status` was VARCHAR while the entity stores INT. | ✅ V14 adds the columns and aligns the types, mapping existing status values. |

### Security
| # | Finding | Status |
|---|---|---|
| S1 | Payment bypass: `pay-remaining` unlocked any project for any amount. | ✅ Checks ownership and project state; the server prices it from the remaining balance. |
| S2 | `purchase-marketplace` worked on any project and overwrote the buyer. | ✅ Requires a published library project allocated to the buyer's college. Access is granted per user through entitlements. |
| S3 | Privilege escalation: ADMIN or DEVELOPER could create a SUPER_ADMIN; ADMIN could promote users. | ✅ Explicit role matrix. Nobody can mint a SUPER_ADMIN through the API. |
| S4 | Checkout trusted the item and amount sent by the client. | ✅ The generic checkout and the fake catalogue are removed. |
| S5 | DB root password and JWT secret were committed. | ✅ Moved to env or the git-ignored `application-local.properties`. The leaked JWT secret is rejected in `prod`. ⛔ **Rotate both.** |
| S6 | The JWT role claim was trusted; deactivation took up to 24 h to apply. | ✅ The filter reloads the account on every request. |
| S7 | IDOR in `/by-requirement`, `/assignments`, project status changes and project assignment. | ✅ Every endpoint checks access in the service layer. |
| S8 | Idempotency keys were global; replaying one returned another user's order. | ✅ Keys are scoped per user. |
| S9 | CORS allowed `*` with credentials. | ✅ Explicit allow-list. |
| S10 | OTP was never sent; registration is immediate. | ⛔ Needs SMTP or an SMS provider. Registration still requires choosing a valid college. |
| S11 | Flyway `repair()` ran on every boot. | ✅ Opt-in only. |
| S12 | Mock mode could be enabled in production. | ✅ Removed. |
| S13 | *(new)* Every boot reactivated all deactivated users. | ✅ Removed. |
| S14 | *(new)* The `/api/permissions` endpoints had no role check. | ✅ Super Admin only. |
| S15 | *(new)* Some checks treated anyone with the email `superadmin@academic.com` as Super Admin. | ✅ Removed; the role alone decides. |
| S16 | *(new)* No brute-force protection on login. | ✅ Locks for 15 min after 5 failures per email and IP (in-memory, per instance). |
| S17 | *(new)* "Delete all" endpoints for projects and requirements; project deletion used concatenated SQL. | ✅ Delete-all removed. Deletion is parameterized and refuses projects with orders or entitlements. |
| S18 | *(new)* The audit log wasn't scoped by college for college admins. | ✅ Scoped to their college's members. |

### Business gaps
| # | Gap | Status |
|---|---|---|
| G1 | No colleges | ✅ `colleges` table, college admins, student membership, activate/deactivate |
| G2 | One buyer per project | ✅ `project_entitlements`; existing buyers backfilled by V13 |
| G3 | No allocations | ✅ `college_project_allocations` with per-college price; allocate, revoke, edit price |
| G4 | Fake hard-coded catalogue | ✅ College-scoped marketplace backed by allocations |
| G5 | Library metadata missing | ✅ Abstract, domain, tags, price, install steps, publish/archive, file categories, preview flag, repository importer |
| G6 | Development workflow incomplete | ✅ College forwarding, quote, developer acceptance, progress, review loop, status history |
| G7 | Payments were inline fakes | ✅ `PaymentGateway` abstraction, `payment_transactions`, labelled simulation, 503 when no gateway |
| G8 | Dashboards not role-specific | ✅ Live dashboards per role |

---

## 2. Verification

**Backend tests** (`mvn test`, H2): 54 pass. `PlatformIntegrationTest` covers:
- college isolation for users, allocations, requirements and the audit log
- privilege escalation
- revoked access for deactivated tokens
- marketplace scoping
- server-side pricing and idempotency
- 503 when no gateway is enabled
- preview vs. full file access and audited downloads
- permission endpoints locked down
- the full custom-development lifecycle through final payment
- dashboards for each role

**Migrations on real MySQL 8.0** (throwaway Docker container, never the developer's database):
- Fresh install: V1–V14 apply and Hibernate `validate` passes.
- V12-shaped legacy database upgrade: status values mapped, marketplace projects turned into library projects, buyers carried over as entitlements, `validate` passes.

**Browser end-to-end** (Vite dev server + backend on the MySQL container, light/dark and 375px mobile):
1. Super Admin registers a college and creates its admin.
2. Imports 3 projects from a fixture built from the real repository READMEs.
3. Allocates 2 of them at a college price.
4. A student registers into the college and sees only the 2 allocated projects.
5. The student buys one (simulated payment, clearly labelled), gets full access, and downloads a valid ZIP. The unallocated project returns 403.
6. Custom flow: student submits → admin forwards → Super Admin quotes → student pays the advance → Super Admin assigns developer and reviewer → developer accepts and uploads → reviewer approves.
7. Deliverable returns 403 before the final payment and 200 after it. The requirement completes, and the timeline and orders are correct.

**Frontend:** `npm run build` passes. `oxlint`: 0 errors, 2 fast-refresh style warnings.

**Full library import (55 projects):** imported from a clone of `darshankrishnakumar/Muthayammal_Projects` into the docker-compose MySQL (`academic_db`, port 3308).
- **Result:** 55/55 imported, 0 failures; 1,521 files, 724 MB of private storage.
- **Contents:** every project has a source archive, a database file, slides, documentation, screenshots and one demo video. 425 screenshots and 55 videos are marked as previews.
- **Metadata:** all 55 have a title from the master catalogue and an abstract with markdown removed. Domains are spread across 8 categories.
- **Re-runs:** adding 0 files on a re-run confirms idempotency. The "refresh metadata" mode keeps codes, prices and status.
- **Spot check:** a real 3-minute demo video streamed through the protected endpoint and played as a pre-purchase preview for a student.
- **Pricing guard:** publishing without a price was refused.
- **Final state:** all 55 are unpriced drafts, so none is visible to students until priced and published.

**Importer fixes found during the real import:**
- Titles now come from the master README's catalogue table; emoji and `PROJECT-NN:` prefixes are removed, and acronyms are cased correctly.
- Abstracts fall back through Abstract → Overview → tagline → first paragraph → `docs/README.md` / `architecture.md`, and skip candidates that are empty once cleaned.
- Walkthrough scripts are filed as documentation, not video.
- Added an Agriculture domain; face recognition counts as Computer Vision; gait analysis counts as Healthcare.
- **Pricing guard:** unpriced projects can't be published, and purchase refuses a missing price. Previously a missing price meant a ₹0, i.e. free, purchase.

---

## 3. Still open

| Item | Why it's open |
|---|---|
| ⛔ Set prices and publish the 55 library projects | They were imported as unpriced drafts. Publishing now requires a price (₹0 is allowed for free projects). |
| ⛔ Restore project 17's phishing dataset | `Phishing_Email.csv` (52 MB) is missing from the upstream repository's Git LFS storage (GitHub returns 404), so project 17's source archive contains only the LFS pointer file. |
| ⛔ Real payment gateway | Needs merchant credentials. The integration point is ready (`PaymentGateway`); see the README. |
| ⛔ Email/OTP verification | Needs mail infrastructure. |
| ⛔ Rotate the leaked JWT secret and MySQL password | Must be done by the owner on their servers. |
| ⬜ Refund workflow | Statuses exist (`REFUNDED`); there is no refund action or UI yet. |
| ⬜ "Recent downloads" on the student dashboard | Downloads are audited (`FILE_DOWNLOADED`) but not yet shown on the dashboard. |
| ⬜ Platform settings screen | Settings are environment-based today. |
| ⬜ Login lockout across instances | In-memory, so it doesn't share state between instances. Use Redis or the database for multi-node deployments. |
| 🟡 Retained admin screens (users, admins, developers, audit log, profile, file explorer and modals) | Adapted and smoke-tested in the browser (they render with live data); not every edit form was clicked through. |
