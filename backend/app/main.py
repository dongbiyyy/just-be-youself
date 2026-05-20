from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import User  # noqa: F401  ensure all models are imported

# Importing the models package registers every table with the Base metadata.
from app import models  # noqa: F401

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(
                User(
                    username=settings.init_admin_username,
                    email=settings.init_admin_email,
                    full_name="系统管理员",
                    hashed_password=hash_password(settings.init_admin_password),
                    role="superadmin",
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}


app.include_router(api_router)
