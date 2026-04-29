"""Inicialización de la base de datos.

Propósito: crear todas las tablas definidas en los modelos ORM al arrancar
el servicio. En un proyecto con Alembic esto se sustituiría por las migraciones.
"""

import logging

from src.db.models import Base
from src.db.session import engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Crea todas las tablas si no existen.

    Seguro de ejecutar en cada arranque: `CREATE TABLE IF NOT EXISTS`.
    """

    logger.info("Inicializando esquema de base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Esquema de base de datos listo.")
