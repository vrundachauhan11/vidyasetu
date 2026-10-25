# VidyaSetu (विद्यासेतु)

> **"An explainable, privacy-aware enrolment integrity and regulatory intelligence platform for AICTE-approved institutions."**  
> *Developed for Smart India Hackathon (SIH) 2026 — Problem Statement 26263*

---

## 🏛️ Executive Summary & Product Positioning

**VidyaSetu** provides regulatory councils (such as the All India Council for Technical Education — AICTE) and approved technical institutions with an explainable, non-punitive, and privacy-first enrolment integrity audit engine.

Unlike opaque scoring mechanisms, VidyaSetu operates on a **deterministic rule engine** mapped directly to the statutory clauses of the AICTE Approval Process Handbook (APH) and conforms to the **Digital Personal Data Protection (DPDP) Act 2023** purpose limitation principles.

---

## ⚡ The Seven-Stage Enrolment Integrity Pipeline

VidyaSetu organizes technical education enrolment governance into seven distinct stages:

```
[1. Data Intake] ──> [2. Schema Validation] ──> [3. APAAR Handshake] ──> [4. Rule Registry]
      │                                                │                        │
      ▼                                                ▼                        ▼
Institutional CSV                            Simulated DigiLocker      Sanctioned Capacity,
Ingestion & Parsing                          Adapter (Non-punitive)    Dual-Enrolment Checks
                                                       │
                                                       ▼
[7. Cryptographic Audit] <── [6. Evidence & Review] <── [5. Explainable Findings]
      │                                  │                              │
      ▼                                  ▼                              ▼
Versioned Ledger with             Human-in-the-Loop             Clear Mathematical &
SHA-256 Tamper Hash               Triage & Adjudication         Statutory Justifications
```

1. **Data Intake & Ingestion:** Upload institutional student rosters via CSV.
2. **Schema & Type Validation:** Strict field typing and column formatting validation.
3. **Simulated APAAR Validation (Visibly Distinct Stage):** Asynchronous lookup against a deterministic simulated DigiLocker/APAAR adapter. *Note: Pending or missing APAAR status is an operational transition state, never a presumption of fraud.*
4. **Intake Integrity Rules:** Evaluation of sanctioned intake ceilings, concurrent full-time degree enrolments, and quota limits.
5. **Explainable Findings:** Plain-text mathematical breakdowns and APH clause citations for each flagged anomaly.
6. **Evidence & Human Reviewer Desk:** Triage queue enabling registrars and compliance officers to submit justifications, verify secondary documents, or mandate seat adjustments.
7. **Versioned Repository & Cryptographic Audit:** Immutable append-only audit trail chained with SHA-256 tamper hashes.

---

## 🧭 Navigation Destinations (Application Shell)

The platform provides 11 purpose-built navigation destinations:

| # | View | Purpose |
|---|---|---|
| 1 | **Overview** | High-level regulatory KPIs, 7-stage pipeline diagram, recent batch activity, and active triage tickets |
| 2 | **Institutions** | AICTE approved institutions directory with approved programmes and sanctioned intake limits |
| 3 | **Student Records** | Versioned student enrolment repository with APAAR match status and integrity filters |
| 4 | **Data Intake** | CSV intake upload dropzone, pre-built synthetic test generator, and schema checker |
| 5 | **APAAR Validation** | **Visibly distinct stage**: Simulated adapter telemetry, latency tuning, and single-ID lookup simulator |
| 6 | **Intake Integrity** | Deterministic AICTE rule registry (R01–R06) with statutory clause citations and active signals |
| 7 | **Evidence & Review** | Reviewer triage desk for adjudicating signals and stamping decisions to the audit trail |
| 8 | **Verification** | Public tamper-evident credential & enrolment verification portal by Enrolment # or APAAR ID |
| 9 | **Reports** | National Technical Education Enrolment Integrity Scrutiny Report with executive KPIs |
| 10 | **Audit Log** | Immutable cryptographic audit ledger with SHA-256 tamper hashes |
| 11 | **Settings** | Simulation parameters, mock gateway toggles, and DPDP Act purpose limitation notices |

---

## 💻 Tech Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide React
- **Backend:** Python 3.14 / 3.11+, FastAPI, SQLAlchemy 2.x (Async), Alembic, Pydantic v2, Pytest
- **Database:** PostgreSQL 16 (production/Docker) & SQLite / aiosqlite (zero-config local dev & tests)
- **Containerization:** Docker & Docker Compose

---

## 🚀 Windows Setup Instructions (Step-by-Step)

Open **PowerShell** in the project directory: `C:\Users\chauh\OneDrive\Documents\SIH-26263`

### Step 1: Environment Variables
Create your local environment file from the template:
```powershell
Copy-Item .env.example .env
```

### Step 2: Backend Setup
Create a Python virtual environment and install dependencies:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install requirements
pip install -r backend\requirements.txt

# Run initial Alembic database migration
python -m alembic -c backend\alembic.ini upgrade head

# Run automated backend test suite
python -m pytest backend\tests -v
```

### Step 3: Frontend Setup
In a new terminal or within the same project:
```powershell
cd frontend
npm install
npm run build
```

---

## 🏃 Running the Application Locally

### Option A: Run Directly in Windows PowerShell

**1. Launch Backend API (Terminal 1):**
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000/api`
- Interactive Swagger Docs: `http://127.0.0.1:8000/api/docs`
- Health Probe: `http://127.0.0.1:8000/api/health`

**2. Launch Frontend Dev Server (Terminal 2):**
```powershell
cd frontend
npm run dev
```
- Open browser at: `http://localhost:5173`

---

### Option B: Run with Docker Compose (Containerized)
When Docker Desktop is installed:
```powershell
docker-compose up --build
```
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000/api`
- PostgreSQL: `localhost:5432`

---

## 🧪 Automated Backend Tests

The automated test suite verifies:
- `GET /api/health` reports `healthy` when the database is connected.
- `GET /api/health` reports `degraded` (HTTP 503) when the database is unavailable.
- `GET /api/version` returns exact product positioning and problem statement information.
- `GET /api/dashboard/overview` returns telemetry and the 7-stage workflow pipeline.
- `GET /api/rules` and `GET /api/apaar/status` return deterministic rule definitions and mock adapter settings.

To execute tests at any time:
```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -v
```

---

## 🎬 How to Demonstrate the Core End-to-End Workflow

For evaluators and judges during demonstration:

1. **Overview Dashboard:** View the real-time KPIs, 7-stage pipeline diagram, and role switcher in the top bar. Switch between **AICTE Council Regulator**, **Institution Registrar**, and **Compliance Reviewer**.
2. **Data Intake:** Click **"1-Click: Test Pre-Built Synthetic CSV"** (or upload your own CSV). Observe schema validation and batch ingestion.
3. **APAAR Validation (Stage 3):** Navigate to the distinct APAAR view. Use the **Interactive APAAR Identity Handshake Simulator** to test direct matches, asynchronous pending states, and spelling variations.
4. **Intake Integrity (Stage 4 & 5):** Review the deterministic rule registry (R01 to R06). Observe how the 121st student in B.Tech CSE triggers `R01_SANCTIONED_INTAKE_EXCEEDED` with clear mathematical justification.
5. **Evidence & Review (Stage 6):** Open the Review Queue. Click **"Accept Institutional Justification"** or **"Verify Secondary Certificate"**. Enter a reviewer note and submit.
6. **Repository & Audit Trail (Stage 7):** Watch the student record version increment to `v2` and inspect the new cryptographic entry stamped with a SHA-256 tamper hash in the **Audit Log**.
7. **Public Credential Verification:** Go to **Verification**, enter `ENR-2025-CSE-001`, and view the public tamper-evident certificate.

---

## 🔒 Ethical & Security Principles

- **Synthetic Data Exclusively:** All student names, enrolment numbers, and APAAR IDs are synthetic demo data.
- **No Official Endorsement Implied:** This project does not use official government crests or claim live connectivity to the production DigiLocker or AICTE registries.
- **Signals ≠ Fraud:** An integrity flag is an indicator for institutional verification, not a disciplinary determination.
