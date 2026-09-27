# TribalSetu (SIH-26238)

TribalSetu is an integrated platform designed to streamline tribal scholarship discovery, student application tracking, document management, DigiLocker import simulation, and verification workflows.

---

## 1. Project Structure

```text
SIH-26238/
├── .env.example                  # Root environment template
├── README.md                     # Project startup & architecture documentation
├── backend/                      # FastAPI Backend
│   ├── .env.example              # Backend-local environment template
│   ├── alembic.ini               # Alembic database migration configuration
│   ├── pytest.ini                # Pytest configuration
│   ├── requirements.txt          # Python package dependencies
│   ├── alembic/                  # Database migration versions
│   │   ├── env.py                # Dynamic environment-aware migration runner
│   │   └── versions/             # Migration revision files
│   ├── app/                      # Application source code
│   │   ├── api/                  # FastAPI router endpoints (/api/v1/...)
│   │   ├── core/                 # Config, DB connection, dependencies, security
│   │   ├── integrations/         # Mock adapter interfaces (DigiLocker, verification)
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── repositories/         # Database persistence layers
│   │   ├── schemas/              # Pydantic request and response schemas
│   │   ├── services/             # Core business logic
│   │   ├── main.py               # FastAPI application entrypoint & health checks
│   │   └── seed.py               # Deterministic demo database seeder
│   └── tests/                    # Pytest test suite (health, catalogue, flows)
├── docs/                         # Project & API specifications
│   └── api/                      # Domain API contracts & frontend integration guides
│       ├── frontend-integration.md # Flutter integration handshake document
│       ├── scholarships.md       # Scholarship catalogue contract
│       ├── eligibility.md        # Eligibility module contract
│       ├── applications.md       # Application contract
│       ├── documents.md          # Document metadata contract
│       ├── application_documents.md # Document linking contract
│       ├── verification.md       # Verification & adapter contract
│       ├── manual_review.md      # Manual review exception queue contract
│       └── digilocker.md         # Simulated DigiLocker contract
└── frontend/                     # Flutter mobile & web application
```

---

## 2. Prerequisites & Python Version

- **Python:** Python 3.11+ recommended (Python 3.11 to 3.13 supported)
- **PostgreSQL:** Version 14 or higher (local installation, Docker, or remote managed instance)
- **Git**

---

## 3. Backend Setup Step-by-Step

### Step 3.1: Navigate to Backend Directory
Open your terminal and enter the `backend` directory:
```bash
cd backend
```

### Step 3.2: Create and Activate Virtual Environment
Create a clean virtual environment named `.venv`:

**Windows (PowerShell / Command Prompt):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3.3: Install Dependencies
Install all required packages and test utilities:
```bash
pip install -r requirements.txt
```

### Step 3.4: Configure Environment Variables
Copy the template configuration to create `.env`:

**Windows:**
```powershell
copy .env.example .env
```

**macOS / Linux:**
```bash
cp .env.example .env
```

Edit `.env` to supply your local PostgreSQL database credentials:
```ini
# Format: postgresql+psycopg2://<user>:<password>@<host>:<port>/<dbname>
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/tribalsetu

# Safe local origins for Flutter web / desktop / emulator
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080
```

### Step 3.5: Set Up PostgreSQL Database
Ensure your PostgreSQL server is running, and create the `tribalsetu` database if it does not already exist:

**Using psql CLI:**
```sql
CREATE DATABASE tribalsetu;
```

### Step 3.6: Run Database Migrations
Apply all schema migrations to your database using Alembic:
```bash
alembic upgrade head
```

### Step 3.7: Seed Deterministic Demo Data (Optional but Recommended)
Populate the database with synthetic demo data for frontend testing:
```bash
python -m app.seed
```
To wipe and re-seed demo records at any time:
```bash
python -m app.seed --reset
```

### Step 3.8: Start the FastAPI Server
Run the local development server with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 4. Verifying Backend & Swagger Docs

Once running:
- **Interactive Swagger Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Liveness Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Database Connectivity Check:** [http://localhost:8000/health/db](http://localhost:8000/health/db)

---

## 5. Frontend Connection Guide

- **Base URL:** `http://localhost:8000`
- **Android Emulator Base URL:** `http://10.0.2.2:8000` (Android emulators route host machine `localhost` through `10.0.2.2`)
- **iOS Simulator Base URL:** `http://localhost:8000`
- **Frontend Integration Handshake:** Refer to [docs/api/frontend-integration.md](docs/api/frontend-integration.md) for full endpoint schemas, sample payloads, and status codes.

---

## 6. Running Tests

The test suite runs against an isolated, fast in-memory SQLite database and does not require an active PostgreSQL instance or external network connections:

```bash
# In backend/ directory with .venv activated:
pytest -v
```

To run a specific test module:
```bash
pytest tests/test_health.py
pytest tests/test_scholarships.py
pytest tests/test_applications.py
```

---

## 7. Environment Variables Reference

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+psycopg2://postgres:postgres@localhost:5432/tribalsetu` | Full SQLAlchemy PostgreSQL connection string |
| `CORS_ORIGINS` | Standard local development origins | Comma-separated list of allowed HTTP origins |
| `HOST` | `0.0.0.0` | Default server binding host |
| `PORT` | `8000` | Default server listening port |

---

## 8. Common Troubleshooting

### 1. `ModuleNotFoundError: No module named 'app'`
Make sure you are executing commands from within the `backend/` directory, or set your `PYTHONPATH`:
```powershell
$env:PYTHONPATH = "."
```

### 2. `could not connect to server: Connection refused (0x0000274D / 5432)`
Ensure your PostgreSQL service is running and accessible on port 5432:
- On Windows: Check Services (`services.msc`) for `postgresql-x64-<version>`.
- Check credentials in `.env` (`DATABASE_URL`).
- Verify `/health/db` endpoint output.

### 3. `AttributeError` or missing packages
Reactivate your virtual environment and verify dependencies are up-to-date:
```bash
pip install -r requirements.txt
```

### 4. CORS errors from Flutter Web or browser
Check `CORS_ORIGINS` in your `.env` file and add the frontend origin (e.g. `http://localhost:port`).
