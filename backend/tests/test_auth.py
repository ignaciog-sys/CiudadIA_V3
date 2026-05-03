"""Pruebas del flujo de autenticación mock.

Propósito: comprobar login, acceso autorizado y rechazo de tokens inválidos.
Ejemplo de uso: mostrar cómo se testean endpoints públicos y protegidos.
"""


def test_login_returns_token_for_valid_credentials(client):
    """El login debe devolver un bearer token JWT cuando las credenciales son correctas."""

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "empleado_admin", "password": "change_me"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_protected_endpoint_requires_valid_token(client):
    """Un endpoint protegido debe funcionar con un JWT real válido."""

    # Primero obtenemos un token real haciendo login
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "empleado_admin", "password": "change_me"},
    )
    token = login_resp.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "empleado_admin"


def test_protected_endpoint_rejects_invalid_token(client):
    """Un endpoint protegido debe rechazar un token no reconocido."""

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer token-invalido"},
    )

    assert response.status_code == 401
