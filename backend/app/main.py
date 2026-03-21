from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import engine, Base
from app.auth import router as auth_router
from app.credits import router as credits_router
from app.courses import router as courses_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bloom Learning API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(credits_router)
app.include_router(courses_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# Serve frontend static files if they exist (must be last — catch-all mount)
frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
