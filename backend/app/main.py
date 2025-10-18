from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .api.routes import analysis, auth, export, images, projects, system
from .core.config import settings
from .core.security import get_password_hash
from .db.base import Base
from .db.session import SessionLocal, engine
from .models import User
from .models.enums import UserRole


def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name, version="1.0.0", openapi_url=f"{settings.api_prefix}/openapi.json")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(projects.router, prefix=settings.api_prefix)
    app.include_router(analysis.router, prefix=settings.api_prefix)
    app.include_router(export.router, prefix=settings.api_prefix)
    app.include_router(images.router, prefix=settings.api_prefix)
    app.include_router(system.router, prefix=settings.api_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        db: Session = SessionLocal()
        try:
            ensure_default_admin(db)
        finally:
            db.close()

    return app


def ensure_default_admin(db: Session) -> None:
    username = settings.default_admin_username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        admin = User(
            username=username,
            full_name="Administrator",
            hashed_password=get_password_hash(settings.default_admin_password),
            role=UserRole.admin.value,
        )
        db.add(admin)
        db.commit()


app = create_app()
