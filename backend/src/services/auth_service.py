"""Servicio de autenticación exclusivo para Empleados Municipales.

Propósito: Validar credenciales de empleados, generar tokens JWT firmados
y proteger las rutas de gestión administrativa. Los ciudadanos no utilizan
este servicio ya que interactúan de forma anónima.
"""

import logging
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from src.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Base de datos de empleados (Admins)
# Se ha eliminado el 'citizen_user' ya que los ciudadanos no se autentican.
# ---------------------------------------------------------------------------
USERS_DB: dict[str, dict] = {
    "empleado_admin": {
        "username": "empleado_admin",
        "hashed_password": "$2b$12$GPDu9U9rF0tqcEgjFq6sme8z/dLZ0zjl.puYM5yQXCbPhTVDmgUa6", # pass: change_me
        "role": "admin",
    }
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña de empleado contra su hash bcrypt."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def authenticate_user(username: str, password: str) -> dict | None:
    """Valida credenciales de empleado. Retorna None si fallan."""
    user = USERS_DB.get(username)
    if user is None:
        logger.warning("Intento de login fallido: usuario '%s' no existe.", username)
        return None
    if not verify_password(password, user["hashed_password"]):
        logger.warning("Contraseña incorrecta para el empleado: %s", username)
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un JWT para la sesión del empleado."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """Valida el token JWT del empleado en cada petición protegida."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        username: str | None = payload.get("sub")
        role: str | None = payload.get("role")
        if username is None or role is None:
            return None
        return {"username": username, "role": role}
    except JWTError as exc:
        logger.debug("Token JWT inválido o expirado: %s", exc)
        return None

# --- Helpers para compatibilidad con Routers ---

def authenticate_demo_user(username: str, password: str) -> dict | None:
    """Procesa el login y devuelve el token listo para el cliente (Empleado)."""
    user = authenticate_user(username, password)
    if user is None:
        return None
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,
    }