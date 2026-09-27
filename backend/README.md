# TribalSetu Backend

FastAPI + PostgreSQL + Alembic backend for the TribalSetu platform.

---

## Prerequisites

- **Python 3.10+** (Python 3.11, 3.12, or 3.13 recommended)
- **PostgreSQL 14+** running locally or accessible over the network
- **Git**

---

## Step-by-Step Local Setup

### 1. Navigate to the Backend Directory

```bash
cd backend
```

### 2. Create and Activate a Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate

# On Windows (PowerShell):
# .venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
# .venv\Scripts\activate.bat
```

### 3. Install Dependencies

Install all required Python packages (including `email-validator` and `python-dotenv`):

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the sample environment file to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` in your editor and update `DATABASE_URL` with your local PostgreSQL credentials:
   ```env
   DATABASE_URL=postgresql+psycopg2://<username>:<password>@localhost:5432/tribalsetu
   ```

> **Note:** `.env` is ignored by Git and will not be committed to version control.

### 5. Create the PostgreSQL Database

If the database does not already exist, create it:

```bash
# Using PostgreSQL command line
createdb tribalsetu

# Or using psql:
psql -U postgres -c "CREATE DATABASE tribalsetu;"
```

### 6. Run Database Migrations

Apply all Alembic database migrations up to the latest head:

```bash
alembic upgrade head
```

To verify the migration status:

```bash
alembic current
```

### 7. Run the FastAPI Development Server

Start the local server with auto-reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will now be running at:
- **API Base URL:** `http://localhost:8000`
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Alternative Docs:** `http://localhost:8000/redoc`

---

## API Overview & Key Modules

| Module | Route Prefix | Description |
| :--- | :--- | :--- |
| **Authentication** | `/api/v1/auth` | User registration, login, and JWT access tokens |
| **Student Profiles** | `/api/v1/students` | Demographic, category, and income profile |
| **Scholarships** | `/api/v1/scholarships` | MoTA scholarship scheme catalogue |
| **Applications** | `/api/v1/applications` | Application draft, submission, and status management |
| **Application Timeline** | `/api/v1/applications/{id}/timeline` | Immutable status transition audit trail |
| **Documents** | `/api/v1/documents` | Document upload and application attachments |
| **DigiLocker Integration** | `/api/v1/integrations/digilocker` | Certificate catalogue discovery and auto-import |
| **Verification Engine** | `/api/v1/verification` | Automated document verification records |
| **Manual Review** | `/api/v1/manual-review` | Exception queue for verification mismatches |
| **Payments / DBT** | `/api/v1/applications/{id}/payments` | PFMS / DBT disbursement tracking |

---

## Project Structure

```
backend/
├── alembic/              # Alembic database migration scripts
│   ├── env.py            # Migration runtime environment
│   └── versions/         # Revision migration scripts
├── app/
│   ├── api/              # FastAPI router endpoints
│   ├── core/             # Configuration & database session
│   ├── integrations/     # External adapter boundaries (DigiLocker, Payments, Verification)
│   ├── models/           # SQLAlchemy ORM models
│   ├── repositories/     # Database queries and persistence logic
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Application business logic
│   └── main.py           # Application entrypoint
├── docs/api/             # Detailed API contracts & specifications
├── .env.example          # Sample environment configuration
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
└── README.md             # This setup guide
```
