from fastapi import FastAPI
from app.core.database import engine
from app.api.student import router as student_router
from app.api.user import router as user_router
from app.api.scholarship import router as scholarship_router
from app.api.application import router as application_router
from app.api.document import router as document_router

app = FastAPI(title="TribalSetu API")
app.include_router(student_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(scholarship_router, prefix="/api/v1")
app.include_router(application_router, prefix="/api/v1")
app.include_router(document_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "TribalSetu API is running"}


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            return {"database": "connected"}
    except Exception as e:
        return {"database": "error", "details": str(e)}