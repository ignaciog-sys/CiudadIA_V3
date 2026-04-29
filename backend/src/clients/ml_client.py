"""Cliente HTTP para el servicio de inferencia ML.

Propósito: encapsular la comunicación con el microservicio de ML y desacoplar
al backend de los detalles del transporte.

=============================================================================
CONTRATO DEL SERVICIO ML (definido por el equipo de backend para que el
compañero de ML lo implemente):

  Endpoint:  POST {ML_SERVICE_URL}/predict
  Content-Type: application/json

  Request body:
    {
      "description": "Texto libre de la incidencia",
      "categoria":   "movilidad"   // valor del enum TicketCategory
    }

  Response body (200 OK):
    {
      "urgency":       3,                        // int 1-5
      "category":      "movilidad",              // str, valor del enum
      "model_name":    "random_forest_ciudadia", // str
      "model_version": "1.0.0"                   // str
    }

  Errores esperados:
    - 422 si el body no es válido
    - 500 si el modelo no puede predecir

  Si el servicio no está disponible o responde con error, el cliente
  retorna None y el ticket se guarda con status "pending_classification".
=============================================================================
"""

import logging

import httpx

from src.config import settings
from src.models.tickets import TicketCategory, TicketClassificationResult, TicketUrgency

logger = logging.getLogger(__name__)


async def call_ml_predict(
    description: str,
    categoria: TicketCategory,
) -> TicketClassificationResult | None:
    """Llama al servicio ML y devuelve la predicción de urgencia y categoría.

    Retorna None si el servicio no está disponible o devuelve un error,
    de forma que el backend pueda continuar sin bloquear la creación del ticket.

    Args:
        description: Texto libre de la incidencia.
        categoria: Categoría seleccionada por el ciudadano (pista para el modelo).

    Returns:
        TicketClassificationResult con urgencia y categoría predichas,
        o None si el servicio no responde.
    """

    url = f"{settings.ml_service_url}/predict"
    payload = {
        "description": description,
        "categoria": str(categoria),
    }

    try:
        async with httpx.AsyncClient(timeout=settings.ml_service_timeout) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

            return TicketClassificationResult(
                urgency=TicketUrgency(data["urgency"]),
                category=TicketCategory(data["category"]),
                model_name=data.get("model_name", "unknown"),
                model_version=data.get("model_version", "unknown"),
            )

    except httpx.TimeoutException:
        logger.warning("Timeout al llamar al servicio ML (%s). Ticket en pending.", url)
        return None
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "El servicio ML respondió con error %s. Ticket en pending.",
            exc.response.status_code,
        )
        return None
    except httpx.RequestError as exc:
        logger.warning(
            "No se pudo conectar con el servicio ML: %s. Ticket en pending.", exc
        )
        return None
    except (KeyError, ValueError) as exc:
        logger.warning(
            "Respuesta inesperada del servicio ML: %s. Ticket en pending.", exc
        )
        return None
