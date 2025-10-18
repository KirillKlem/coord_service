from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ...models import Image, User
from ...services.storage import storage_service
from .. import deps

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/{image_id}/download")
def download_image(
    image_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    path = storage_service.open_file(image.storage_path)
    return FileResponse(path, filename=image.filename, media_type=image.content_type)
