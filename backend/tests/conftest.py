"""Pytest configuration and fixtures. Isolated DB per test via session override."""
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Avoid touching real data dir; use a dummy path so app can be imported
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.adapters.persistence.database import Base, get_session
from app.adapters.persistence import models  # noqa: F401 - register tables with Base
from app.api.app import create_app
from app.api.dependencies import get_matching_service


def _mock_matching_service():
    """Return a mock MatchingService so create_opportunity doesn't call real AI/Chroma."""
    mock = MagicMock()
    mock.find_matches = AsyncMock(return_value=[])
    mock.get_matches = MagicMock(return_value=[])
    return mock


@pytest.fixture
def client():
    """Fresh app and isolated DB per test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        engine = create_engine(
            f"sqlite:///{path}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(bind=engine)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        def _override_get_session():
            db = session_factory()
            try:
                yield db
            finally:
                db.close()

        app = create_app()
        app.dependency_overrides[get_session] = _override_get_session
        app.dependency_overrides[get_matching_service] = _mock_matching_service
        with TestClient(app) as c:
            yield c
    finally:
        Base.metadata.drop_all(bind=engine)
        try:
            os.unlink(path)
        except OSError:
            pass
