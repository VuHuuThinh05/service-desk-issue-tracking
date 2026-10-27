from fastapi import FastAPI
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.auth import router as auth_router
from app.api.v1.tickets import router as tickets_router

from app.api.v1.users import router as users_router

from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Service Desk & Issue Tracking API",
    description="API quản lý yêu cầu hỗ trợ và sự cố nội bộ.",
    version="0.1.0",
)

app.include_router(
    dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    tickets_router,
    prefix="/api/v1",
)


@app.get("/health", tags=["Hệ thống"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")