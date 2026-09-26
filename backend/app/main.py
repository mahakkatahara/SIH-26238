from fastapi import FastAPI

app = FastAPI(title="TribalSetu API")


@app.get("/")
def root():
    return {"message": "TribalSetu API is running"}