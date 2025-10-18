from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...core.config import settings
from ...services.metrics import metrics_response
from .. import deps

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/healthz")
def healthcheck(db: Session = Depends(deps.get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@router.get("/version")
def version() -> dict[str, str]:
    return {
        "name": settings.project_name,
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> PlainTextResponse:
    data = metrics_response()
    return PlainTextResponse(content=data.decode("utf-8"), media_type="text/plain")
