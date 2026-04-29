"""Fixtures compartidas para pruebas.

Propósito: crear un cliente de pruebas reutilizable y una BD en memoria
para tests de integración sin necesitar PostgreSQL real.
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.app import app
from src.db.models import Base
from src.db.session import get_db
from src.services.auth_service import create_access_token

# ---------------------------------------------------------------------------
# BD SQLite en memoria para tests
# ---------------------------------------------------------------------------

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session():
    """Sesión async sobre SQLite en memoria para tests de integración."""

    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ---------------------------------------------------------------------------
# Cliente HTTP con BD sobreescrita
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """Cliente async con la BD en memoria inyectada."""

    app.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Tokens de test
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_token() -> str:
    """JWT firmado con rol admin para tests (usuario: empleado_admin)."""
    return create_access_token({"sub": "empleado_admin", "role": "admin"})


# ---------------------------------------------------------------------------
# Cliente síncrono (compatibilidad con tests legacy)
# ---------------------------------------------------------------------------

@pytest.fixture
def client() -> TestClient:
    """Cliente de pruebas síncrono para endpoints FastAPI (legacy)."""

    return TestClient(app)
