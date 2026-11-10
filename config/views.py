from django.db import connection
from django.urls import reverse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    """Comprobacion liviana para despliegues y pruebas de humo."""
    try:
        connection.ensure_connection()
        database, status_code = "ok", 200
    except Exception:
        database, status_code = "error", 503
    return Response(
        {"status": "ok" if status_code == 200 else "degraded", "database": database, "time": timezone.now()},
        status=status_code,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response(
        {
            "nombre": "API de prediccion de abandono de clientes",
            "version": "1.0",
            "autenticacion": request.build_absolute_uri(reverse("usuarios:login")),
            "salud": request.build_absolute_uri(reverse("health")),
        }
    )
