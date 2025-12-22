from fastapi import FastAPI
from app.core.config import settings
from app.routers.auth import router as auth_router
from app.routers.admin import router as admin_router
from app.routers.users import router as user_router

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(user_router)

@app.get("/health")
def health():
    return {"status": "ok", "env": settings.env}