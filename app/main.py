from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="LexiGuard AI",
    description="Smart Contract Analyzer API",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "LexiGuard AI is running"}