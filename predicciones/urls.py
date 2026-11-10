from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    HistorialModelosView,
    LotePrediccionListView,
    ModeloActivoView,
    PrediccionIndividualView,
    PrediccionLoteView,
    PrediccionViewSet,
)

app_name = "predicciones"
router = DefaultRouter()
router.register("resultados", PrediccionViewSet, basename="resultado")

urlpatterns = [
    path("individual/", PrediccionIndividualView.as_view(), name="individual"),
    path("lote/", PrediccionLoteView.as_view(), name="lote"),
    path("lotes/", LotePrediccionListView.as_view(), name="lotes"),
    path("modelo/activo/", ModeloActivoView.as_view(), name="modelo-activo"),
    path("modelos/", HistorialModelosView.as_view(), name="modelos"),
    path("", include(router.urls)),
]
