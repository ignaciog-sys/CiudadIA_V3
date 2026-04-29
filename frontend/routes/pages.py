from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from httpx import HTTPStatusError, RequestError

from services.api_client import api_client

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/")
async def home(request: Request):
    if request.session.get("access_token"):
        # Redirigir según rol
        role = request.session.get("role")
        if role == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        else:
            return RedirectResponse(url="/citizen/dashboard", status_code=303)
    return RedirectResponse(url="/login", status_code=303)


@router.get("/dashboard")
async def dashboard(request: Request):
    token = request.session.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)

    try:
        current_user = await api_client.me(token)
        items = await api_client.items(token)
    except (HTTPStatusError, RequestError):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)

    context = {
        "request": request,
        "current_user": current_user,
        "items": items.items,
    }
    return templates.TemplateResponse("dashboard.html", context)


# ============ RUTAS ADMIN ============

@router.get("/admin/dashboard")
async def admin_dashboard(request: Request):
    token = request.session.get("access_token")
    role = request.session.get("role")
    
    if not token or role != "admin":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        current_user = await api_client.me(token)
        # Llamar al endpoint de admin
        import httpx
        async with httpx.AsyncClient(base_url=api_client.base_url, timeout=10.0) as client:
            response = await client.get(
                "/api/v1/admin/dashboard",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            admin_data = response.json()
    except (HTTPStatusError, RequestError):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)
    
    context = {
        "request": request,
        "current_user": current_user,
        "admin_data": admin_data,
    }
    return templates.TemplateResponse("admin_dashboard.html", context)


# ============ RUTAS CIUDADANO ============

@router.get("/citizen/dashboard")
async def citizen_dashboard(request: Request):
    token = request.session.get("access_token")
    role = request.session.get("role")
    
    if not token or role != "citizen":
        return RedirectResponse(url="/login", status_code=303)
    
    try:
        current_user = await api_client.me(token)
        # Llamar al endpoint de ciudadano
        import httpx
        async with httpx.AsyncClient(base_url=api_client.base_url, timeout=10.0) as client:
            response = await client.get(
                "/api/v1/citizen/dashboard",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            citizen_data = response.json()
    except (HTTPStatusError, RequestError):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)
    
    context = {
        "request": request,
        "current_user": current_user,
        "citizen_data": citizen_data,
    }
    return templates.TemplateResponse("citizen_dashboard.html", context)
