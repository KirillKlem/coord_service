import os
import shutil
import tempfile

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("GEORAG_SECRET_KEY", "test-secret")
os.environ.setdefault("GEORAG_DATABASE_URL", "sqlite:///./test_georag.db")
TEMP_STORAGE = tempfile.mkdtemp(prefix="georag_test_storage_")
os.environ.setdefault("GEORAG_STORAGE_DIR", TEMP_STORAGE)
os.environ.setdefault("GEORAG_DEFAULT_ADMIN_PASSWORD", "admin123")
os.environ.setdefault("GEORAG_DEFAULT_ADMIN_USERNAME", "admin")

from backend.app.main import app  # noqa: E402
from backend.app.db.base import Base  # noqa: E402
from backend.app.db.session import SessionLocal, engine  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    shutil.rmtree(TEMP_STORAGE, ignore_errors=True)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
