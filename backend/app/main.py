from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import get_cors_origins
from app.core.database import engine
from app.api.student import router as student_router
from app.api.user import router as user_router
from app.api.scholarship import router as scholarship_router
from app.api.application import router as application_router
from app.api.document import router as document_router
from app.api.eligibility import router as eligibility_router
from app.api.verification import router as verification_router
from app.api.manual_review import router as manual_review_router
from app.api.digilocker import router as digilocker_router

app = FastAPI(title="TribalSetu API")

# Safe CORS configuration for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core API routes
app.include_router(student_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(scholarship_router, prefix="/api/v1")
app.include_router(application_router, prefix="/api/v1")
app.include_router(document_router, prefix="/api/v1")
app.include_router(eligibility_router, prefix="/api/v1")
app.include_router(verification_router, prefix="/api/v1")
app.include_router(manual_review_router, prefix="/api/v1")
app.include_router(digilocker_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "TribalSetu API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/health/db")
def health_db(response: Response):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return {
                "status": "ok",
                "database": "connected",
            }
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "database": "disconnected",
        }


# Retained for backward compatibility
@app.get("/db-test")
def db_test(response: Response):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            return {"status": "ok", "database": "connected"}
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "error", "database": "disconnected"}