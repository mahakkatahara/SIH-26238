from fastapi import FastAPI
from app.core.database import engine

app = FastAPI(title="TribalSetu API")


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