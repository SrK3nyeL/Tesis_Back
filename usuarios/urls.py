from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LoginView, LogoutView, PerfilView, UsuarioViewSet

app_name = "usuarios"
router = DefaultRouter()
router.register("usuarios", UsuarioViewSet, basename="usuario")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("perfil/", PerfilView.as_view(), name="perfil"),
    path("", include(router.urls)),
]
