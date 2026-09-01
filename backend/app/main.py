from contextlib import asynccontextmanager

import models  # noqa: F401 — register ORM models with Base.metadata
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from database.database import Base, engine
from routers.ai import router as ai_router
from routers.alert import router as alert_router
from routers.analytics import router as analytics_router
from routers.asset import router as asset_router
from routers.dashboard import router as dashboard_router
from routers.health import router as health_router
from routers.maintenance import router as maintenance_router
from routers.operator import router as operator_router
from routers.recommendation import router as recommendation_router
from routers.rental import router as rental_router
from routers.site import router as site_router
from routers.telemetry import router as telemetry_router
from routers.workflow import router as workflow_router

CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(asset_router)
app.include_router(site_router)
app.include_router(operator_router)
app.include_router(rental_router)
app.include_router(telemetry_router)
app.include_router(maintenance_router)
app.include_router(alert_router)
app.include_router(recommendation_router)
app.include_router(workflow_router)
app.include_router(dashboard_router)
app.include_router(analytics_router)
app.include_router(ai_router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }
