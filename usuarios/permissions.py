from rest_framework.permissions import BasePermission

from .models import Usuario


class EsInvestigadorOAdministrador(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user.is_authenticated
            and request.user.rol in {Usuario.Rol.INVESTIGADOR, Usuario.Rol.ADMINISTRADOR}
        )
