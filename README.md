# Academic Integration Tool

A multi-college platform for distributing completed academic projects and managing custom project development.

- **Central library.** The platform owner keeps one library of completed projects: abstract, docs, source code, database files, demo video, screenshots and install steps. Each project is stored **once**.
- **Allocations.** Projects reach colleges through **allocations**. One project can be offered to any number of colleges, each with its own price.
- **Students.** Students browse only what their college offers, preview it, and buy it. They can also request a custom project.
- **Custom development.** A custom request goes through college review, a quote, an advance payment, developer assignment, review and a final payment. Each step is recorded on a timeline.
- **Access.** Deliverables unlock only after the backend verifies the payment.

| Layer | Stack |
|---|---|
| Frontend | React 19, Vite 8, React Router 7, lucide-react, plain CSS design system (`src/index.css`) |
| Backend | Java 17, Spring Boot 3.2, Spring Security (JWT), JPA/Hibernate, Flyway |
| Database | MySQL 8 |

## Roles

| Role | Scope |
|---|---|
| `SUPER_ADMIN` | Platform owner. Manages colleges, admins, developers, the library, allocations, pricing, approvals, assignments, orders, permissions, audit log. |
| `ADMIN` | College administrator. Sees only their college: its allocated projects, students, requirements and orders. Reviews and forwards student requirements. |
| `PROJECT_DEVELOPER` | Sees only projects assigned to them. Accepts work, reports progress, uploads deliverables, submits for review. |
| `USER` | Student of one college. Browses and buys allocated projects, requests custom projects, pays, and downloads what they're entitled to. |

The backend enforces every rule, including college isolation, ownership checks, payment state and file access. Frontend role checks only decide what is shown.

## Project lifecycle

**Library purchase:** the student opens a project allocated to their college. The server prices it from the allocation, charges it through the payment gateway, then grants an entitlement, which unlocks the files.

**Custom development:**

```
Student submits ─▶ College admin forwards ─▶ Super Admin quotes (total + advance)
  ─▶ Student pays advance ─▶ Super Admin assigns developer (+ reviewer)
  ─▶ Developer accepts, updates progress, uploads deliverables, submits
  ─▶ Reviewer approves or requests changes
  ─▶ Student pays the balance ─▶ Deliverables unlocked
```

## Running locally

### 1. Database

Use any MySQL 8 server, or start the bundled one (it listens on host port 3308):

```bash
docker compose up -d mysql
```

### 2. Backend

```bash
cd backend
cp src/main/resources/application-local.properties.example src/main/resources/application-local.properties
# edit it: DB password, a JWT secret (openssl rand -base64 48), optional import root
mvn spring-boot:run
```

The default profile is `local`. In that profile:
- **Payment simulation:** on. Every simulated order is labelled as simulated.
- **Demo accounts:** seeded, together with a "Demo College":
  - `superadmin@academic.com` / `Superadmin123!`
  - `admin@academic.com` / `Admin123!`
  - `developer@academic.com` / `Developer123!`
  - `user@academic.com` / `User123!`

Flyway migrations V1–V14 create and upgrade the schema.

On Windows, `start-server.bat` starts MySQL, the backend and a Cloudflare tunnel. It stops with instructions if `application-local.properties` is missing.

### 3. Frontend

```bash
cp .env.example .env    # VITE_API_URL=http://localhost:8080
npm install
npm run dev             # http://localhost:5173
```

## Configuration

Secrets come from the environment, never from committed files. Key settings (Spring property → environment variable):

| Property | Env var | Notes |
|---|---|---|
| `spring.datasource.url` / `username` / `password` | `DB_URL`, `DB_USERNAME`, `DB_PASSWORD` | |
| `academic.jwt.secret` | `JWT_SECRET` | **Required.** Base64, at least 32 bytes. The app refuses to start without it, and the old publicly committed secret is rejected in `prod`. |
| `academic.cors.allowed-origins` | `CORS_ALLOWED_ORIGINS` | Comma-separated exact origins, e.g. your Vercel domain. |
| `academic.storage.root` | `STORAGE_ROOT` | Private file storage. Never served statically; files are streamed only through authorized endpoints. |
| `academic.payments.simulation-enabled` | `PAYMENTS_SIMULATION_ENABLED` | Development only. Forced off in the `prod` profile. |
| `academic.seed.demo-accounts` | `SEED_DEMO_ACCOUNTS` | Development only. Forced off in `prod`. |
| `academic.library.import-root` | `LIBRARY_IMPORT_ROOT` | Local checkout of the master project repository. |
| `academic.flyway.repair-on-start` | `FLYWAY_REPAIR_ON_START` | Off by default. |
| `spring.profiles.active` | `SPRING_PROFILES_ACTIVE` | `local` (default) or `prod`. |

Frontend: `VITE_API_URL` is required for production builds. Set it in the Vercel project settings.

## Importing the project library

The Super Admin importer reads a local checkout of the master repository. It expects one folder per project, with this layout:

```
project_NN_name/
  README.md          title (H1), "Abstract" section, quickstart/setup section
  requirements.txt   used to infer the technology stack
  docs/              DOCX/PDF/Markdown, docs/screenshots/*
  presentations/*.pptx
  walkthrough/*.mp4  demo video
  source_code/       zipped into one archive; *.db / *.sql also listed under Database
```

To import:

1. Clone the repository onto the backend machine.
2. Set `LIBRARY_IMPORT_ROOT` to the clone and restart the backend.
3. Open **Project library → Import from repository**.
4. Pick the projects, an optional default price, and whether to publish them.

How the import behaves:
- It is **idempotent**. Projects are matched by folder name, and files already present are skipped.
- Metadata edited in the UI is never overwritten.
- Screenshots, abstract PDFs and demo videos are marked as previews, so students see them before purchase. Everything else unlocks only after payment.

## Payments

`OrderService` charges every order through the `PaymentGateway` interface (`backend/.../service/payment`):

- **Amounts:** always computed on the server, from the allocation price, the requirement's quote, or the project's remaining balance.
- **Transactions:** every attempt is stored in `payment_transactions`.
- **Access:** granted only after the gateway reports success.
- **No gateway:** the purchase endpoints return 503 until one is configured.
- **Simulation:** `SimulatedPaymentGateway` is for development only. Its orders are flagged `simulatedPayment` and excluded from revenue.

**Adding a real gateway** (Razorpay, Stripe, PayU…):
1. Implement `PaymentGateway`.
2. For redirect-based flows, return `PaymentResult.pending(...)` from `charge`.
3. Add a verified webhook endpoint that marks the transaction `SUCCEEDED`, then calls the same fulfilment code.
4. Set `PAYMENT_PROVIDER` to its `name()`.

## Tests

```bash
cd backend && mvn test        # runs on in-memory H2; never touches a real database
npm run build && npx oxlint src
```

`PlatformIntegrationTest` covers:
- college isolation
- blocked privilege escalation
- marketplace scoping
- server-side pricing and idempotency
- preview vs. full file access
- payment bypass attempts
- the gateway-disabled case
- the full custom-development lifecycle

## Deployment checklist

- `SPRING_PROFILES_ACTIVE=prod` with `DB_*`, `JWT_SECRET` and `CORS_ALLOWED_ORIGINS` set. Production uses `ddl-auto=validate`; Flyway owns the schema.
- **Rotate the JWT secret and the MySQL password.** Earlier versions committed both to the public repository.
- Back up MySQL (e.g. a nightly `mysqldump --single-transaction academic_db`) and the `STORAGE_ROOT` directory together. Asset metadata and files must be restored as a pair.
- Configure a real payment gateway before taking payments; simulation is disabled in `prod`.
- Set `VITE_API_URL` on Vercel to a stable backend URL. Quick Cloudflare tunnels change URL on every restart; a named tunnel or a hosted backend avoids that.
