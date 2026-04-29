"""Router de panel de administración.

Propósito: rutas exclusivas para usuarios administradores.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.deps import get_current_user
from src.models.auth import CurrentUser
from src.common.responses import COMMON_ERROR_RESPONSES
from src.constants import API_TAGS

admin_router = APIRouter(prefix="/admin", tags=[API_TAGS.get("admin", "admin")])


@admin_router.get(
    "/dashboard",
    responses=COMMON_ERROR_RESPONSES,
)
async def admin_dashboard(user: CurrentUser = Depends(get_current_user)):
    """Acceso exclusivo para administradores."""
    
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a este recurso.",
        )
    
    return {
        "message": "⚠️ ERES ADMIN - CONTENIDO CONFIDENCIAL",
        "username": user.username,
        "role": user.role,
        "content": {
            "title": "Panel de Control Administrativo",
            "description": "Acceso exclusivo para administradores del sistema"
        }
    }
