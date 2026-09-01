from fastapi import FastAPI

from config.settings import settings
from routers.alert import router as alert_router
from routers.analytics import router as analytics_router
from routers.asset import router as asset_router
from routers.dashboard import router as dashboard_router
from routers.maintenance import router as maintenance_router
from routers.operator import router as operator_router
from routers.recommendation import router as recommendation_router
from routers.rental import router as rental_router
from routers.site import router as site_router
from routers.telemetry import router as telemetry_router
from routers.workflow import router as workflow_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

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


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": settings.app_name,
        "version": settings.app_version,
    }
