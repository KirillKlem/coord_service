import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile

from ..core.config import settings


class StorageService:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or settings.storage_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, upload_file: UploadFile, subdir: str = "images") -> Path:
        destination_dir = self.base_dir / subdir
        destination_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(upload_file.filename or "upload.bin").suffix
        filename = f"{uuid.uuid4().hex}{suffix}"
        destination_path = destination_dir / filename
        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        upload_file.file.seek(0)
        return destination_path

    def open_file(self, relative_path: str) -> Path:
        path = Path(relative_path)
        if not path.is_absolute():
            path = self.base_dir / relative_path
        if not path.exists():
            raise FileNotFoundError(relative_path)
        return path

    def get_public_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.base_dir))
        except ValueError:
            return str(path)


storage_service = StorageService()
