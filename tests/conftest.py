import pytest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.config import seed_default_configs
from app.main import app

# In-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_default_configs(db)
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def mock_qdrant(mocker):
    client = MagicMock()
    # Mock collections check
    coll_mock = MagicMock()
    coll_mock.name = "knowledge_base"
    client.get_collections.return_value.collections = [coll_mock]

    # Mock scroll
    client.scroll.return_value = ([], None)

    # Mock search
    search_hit = MagicMock()
    search_hit.score = 0.95
    search_hit.payload = {
        "file_path": "\\\\pc135\\D\\HR\\policy.docx",
        "file_name": "policy.docx",
        "file_extension": ".docx",
        "departments": ["HR"],
        "doc_types": ["CL"],
        "chunk_index": 0,
        "section_context": "Section: Leave Policy",
        "content": "computer hardware policy details"
    }
    client.search.return_value = [search_hit]

    mocker.patch("app.indexer.qdrant_ops.get_qdrant_client", return_value=client)
    mocker.patch("app.search.engine.get_qdrant_client", return_value=client)
    mocker.patch("app.routers.reclassify.get_qdrant_client", return_value=client)
    mocker.patch("app.routers.config.get_qdrant_client", return_value=client)
    return client


@pytest.fixture(scope="function")
def mock_embedder(mocker):
    embedder_mock = MagicMock()
    embedder_mock.embed_batch.side_effect = lambda texts: [[0.0] * 384 for _ in texts]
    mocker.patch("app.indexer.runner.Embedder", return_value=embedder_mock)
    mocker.patch("app.search.engine.Embedder", return_value=embedder_mock)
    return embedder_mock


@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def authenticated_client(client, db_session):
    # Login via session
    res = client.post("/api/auth/login", data={"username": "admin", "password": "admin"})
    assert res.status_code in (200, 303)
    return client
