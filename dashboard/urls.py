from django.urls import path

from .views import (
    CargaLoteView,
    ClienteCreateView,
    ClienteListView,
    ClienteUpdateView,
    DashboardView,
    LoteDetailView,
    LoteListView,
    ModeloView,
    PrediccionDetailView,
    PrediccionListView,
    PrediccionNuevaView,
    UsuarioCreateView,
    UsuarioListView,
    UsuarioToggleActiveView,
    UsuarioUpdateView,
)

app_name = "dashboard"
urlpatterns = [
    path("", DashboardView.as_view(), name="web"),
    path("predecir/", PrediccionNuevaView.as_view(), name="predecir"),
    path("lotes/", LoteListView.as_view(), name="lotes"),
    path("lotes/cargar/", CargaLoteView.as_view(), name="lote-cargar"),
    path("lotes/<uuid:pk>/", LoteDetailView.as_view(), name="lote-detalle"),
    path("resultados/", PrediccionListView.as_view(), name="resultados"),
    path("resultados/<int:pk>/", PrediccionDetailView.as_view(), name="prediccion-detalle"),
    path("clientes/", ClienteListView.as_view(), name="clientes"),
    path("clientes/nuevo/", ClienteCreateView.as_view(), name="cliente-nuevo"),
    path("clientes/<int:pk>/editar/", ClienteUpdateView.as_view(), name="cliente-editar"),
    path("modelo/", ModeloView.as_view(), name="modelo"),
    path("usuarios/", UsuarioListView.as_view(), name="usuarios"),
    path("usuarios/nuevo/", UsuarioCreateView.as_view(), name="usuario-nuevo"),
    path("usuarios/<int:pk>/editar/", UsuarioUpdateView.as_view(), name="usuario-editar"),
    path("usuarios/<int:pk>/estado/", UsuarioToggleActiveView.as_view(), name="usuario-estado"),
]
