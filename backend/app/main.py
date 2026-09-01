from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database.database import init_db
from routers import health_router

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.on_event("startup")
async def on_startup() -> None:
    init_db()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": settings.app_title,
        "version": settings.app_version,
        "docs": "/docs",
    }
