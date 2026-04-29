"""Motor async y gestión de sesiones SQLAlchemy.

Propósito: centralizar la creación del motor y la fábrica de sesiones para
que la dependencia `get_db` pueda inyectarse en cualquier endpoint.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

# El motor async gestiona el pool de conexiones a PostgreSQL.
# pool_pre_ping=True detecta conexiones caídas antes de reutilizarlas.
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=(settings.app_env == "dev"),
)

# La fábrica de sesiones reutiliza el motor y garantiza que las sesiones
# se cierren correctamente después de cada request.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia de FastAPI que entrega una sesión de BD por request.

    Garantiza que la sesión se cierre aunque ocurra un error.
    Uso: `db: AsyncSession = Depends(get_db)` en cualquier endpoint.
    """

    async with AsyncSessionLocal() as session:
        yield session
