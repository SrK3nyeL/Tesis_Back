from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

from clientes.models import Cliente
from predicciones.models import Prediccion, VersionModelo


def dashboard_data():
    predictions = Prediccion.objects.all()
    total = predictions.count()
    churn_count = predictions.filter(abandono_predicho=True).count()
    risk_counts = {
        value: predictions.filter(nivel_riesgo=value).count()
        for value in (Prediccion.NivelRiesgo.BAJO, Prediccion.NivelRiesgo.MEDIO, Prediccion.NivelRiesgo.ALTO)
    }
    risk = {
        **risk_counts,
        **{f"{name}_pct": round(count * 100 / total, 1) if total else 0 for name, count in risk_counts.items()},
    }
    trend = list(
        predictions.annotate(fecha=TruncDate("creado_en"))
        .values("fecha")
        .annotate(total=Count("id"), probabilidad_promedio=Avg("probabilidad"))
        .order_by("fecha")
    )[-14:]
    contracts = list(Cliente.objects.values("contract").annotate(total=Count("id")).order_by("contract"))
    model = VersionModelo.objects.filter(activo=True).first()
    return {
        "total_predicciones": total,
        "clientes_registrados": Cliente.objects.filter(activo=True).count(),
        "abandono_predicho": churn_count,
        "tasa_abandono": round(churn_count * 100 / total, 1) if total else 0,
        "probabilidad_promedio": round((predictions.aggregate(value=Avg("probabilidad"))["value"] or 0) * 100, 1),
        "riesgo": risk,
        "tendencia": trend,
        "contratos": contracts,
        "modelo": model,
        "recientes": predictions.select_related("version_modelo").filter(
            nivel_riesgo=Prediccion.NivelRiesgo.ALTO
        )[:8],
    }


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **dashboard_data()}


class DashboardAPIView(APIView):
    def get(self, request):
        data = dashboard_data()
        model = data.pop("modelo")
        recent = data.pop("recientes")
        data["modelo"] = None if model is None else {
            "version": model.version,
            "algoritmo": model.algoritmo,
            "metricas": model.metricas,
            "matriz_confusion": model.matriz_confusion,
            "importancia_variables": model.importancia_variables,
        }
        data["recientes"] = [
            {
                "id": item.id, "cliente": item.referencia_cliente,
                "probabilidad": item.probabilidad, "nivel_riesgo": item.nivel_riesgo,
                "fecha": item.creado_en,
            }
            for item in recent
        ]
        return Response(data)
