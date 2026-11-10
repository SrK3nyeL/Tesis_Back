from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Normaliza errores para que el frontend reciba siempre el mismo contrato."""
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error": True,
            "codigo": getattr(exc, "default_code", "error"),
            "detalle": response.data,
        }
    return response
