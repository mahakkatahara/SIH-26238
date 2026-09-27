import os
from pathlib import Path


def load_env_file() -> None:
    """Load key-value pairs from .env file into os.environ if not already set."""
    search_paths = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
    ]
    for env_path in search_paths:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.strip().strip("'\"")
                        if key and key not in os.environ:
                            os.environ[key] = val
                break
            except Exception:
                pass


# Initialize environment on import
load_env_file()

DEFAULT_DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/tribalsetu"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

DEFAULT_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]


def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "")
    if raw_origins.strip():
        parsed = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
        if parsed:
            return parsed
    return DEFAULT_CORS_ORIGINS
