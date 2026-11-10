import csv
import io

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, TemplateView, UpdateView
from rest_framework.response import Response
from rest_framework.views import APIView

from clientes.models import Cliente
from predicciones.models import LotePrediccion, Prediccion, VersionModelo
from predicciones.services.model_service import ChurnModelService, ModeloNoDisponible
from predicciones.services.prediction_service import guardar_prediccion, procesar_lote
from usuarios.models import Usuario

from .forms import CargaLoteForm, ClienteForm, PrediccionForm, UsuarioCreateForm, UsuarioUpdateForm


class NavigationMixin:
    active_section = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_section"] = self.active_section
        return context


class AdministradorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_staff or user.rol == Usuario.Rol.ADMINISTRADOR


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


class DashboardView(LoginRequiredMixin, NavigationMixin, TemplateView):
    template_name = "dashboard/index.html"
    active_section = "dashboard"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **dashboard_data()}


class PrediccionNuevaView(LoginRequiredMixin, NavigationMixin, FormView):
    template_name = "dashboard/predicciones/form.html"
    form_class = PrediccionForm
    active_section = "predecir"

    def get_initial(self):
        initial = super().get_initial()
        if client_id := self.request.GET.get("cliente"):
            initial["cliente"] = Cliente.objects.filter(pk=client_id, activo=True).first()
        return initial

    def form_valid(self, form):
        try:
            prediction = guardar_prediccion(
                user=self.request.user,
                validated_data=form.validated_data,
            )
        except ModeloNoDisponible as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)
        messages.success(self.request, "Prediccion generada y almacenada correctamente.")
        return redirect("dashboard:prediccion-detalle", pk=prediction.pk)


class CargaLoteView(LoginRequiredMixin, NavigationMixin, FormView):
    template_name = "dashboard/lotes/form.html"
    form_class = CargaLoteForm
    active_section = "lotes"

    def form_valid(self, form):
        uploaded = form.cleaned_data["archivo"]
        try:
            rows = list(csv.DictReader(io.StringIO(uploaded.read().decode("utf-8-sig"))))
        except UnicodeDecodeError:
            form.add_error("archivo", "El archivo debe estar codificado en UTF-8.")
            return self.form_invalid(form)
        if not rows:
            form.add_error("archivo", "El archivo no contiene registros.")
            return self.form_invalid(form)
        if len(rows) > settings.CHURN_MAX_BATCH_ROWS:
            form.add_error("archivo", f"El maximo permitido es {settings.CHURN_MAX_BATCH_ROWS} registros.")
            return self.form_invalid(form)
        batch = procesar_lote(
            user=self.request.user,
            rows=rows,
            file_name=uploaded.name,
            first_row=2,
        )
        if batch.estado == LotePrediccion.Estado.FALLIDO:
            messages.error(self.request, "No se pudo procesar el lote. Revisa el detalle.")
        elif batch.registros_fallidos:
            messages.warning(
                self.request,
                f"Lote completado: {batch.registros_exitosos} exitosos y {batch.registros_fallidos} con error.",
            )
        else:
            messages.success(self.request, f"Se procesaron {batch.registros_exitosos} clientes correctamente.")
        return redirect("dashboard:lote-detalle", pk=batch.pk)


class LoteListView(LoginRequiredMixin, NavigationMixin, ListView):
    template_name = "dashboard/lotes/list.html"
    context_object_name = "lotes"
    paginate_by = 20
    active_section = "lotes"
    queryset = LotePrediccion.objects.select_related("creado_por")


class LoteDetailView(LoginRequiredMixin, NavigationMixin, DetailView):
    template_name = "dashboard/lotes/detail.html"
    context_object_name = "lote"
    active_section = "lotes"
    queryset = LotePrediccion.objects.select_related("creado_por").prefetch_related("predicciones")


class PrediccionListView(LoginRequiredMixin, NavigationMixin, ListView):
    template_name = "dashboard/predicciones/list.html"
    context_object_name = "predicciones"
    paginate_by = 20
    active_section = "resultados"

    def get_queryset(self):
        queryset = Prediccion.objects.select_related("cliente", "version_modelo", "creado_por")
        if risk := self.request.GET.get("riesgo"):
            queryset = queryset.filter(nivel_riesgo=risk)
        if churn := self.request.GET.get("abandono"):
            queryset = queryset.filter(abandono_predicho=churn == "1")
        if reference := self.request.GET.get("cliente"):
            queryset = queryset.filter(referencia_cliente__icontains=reference)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtros"] = self.request.GET
        context["export_query"] = self.request.GET.urlencode()
        return context


class PrediccionDetailView(LoginRequiredMixin, NavigationMixin, DetailView):
    template_name = "dashboard/predicciones/detail.html"
    context_object_name = "prediccion"
    active_section = "resultados"
    queryset = Prediccion.objects.select_related("cliente", "version_modelo", "creado_por", "lote")


class ClienteListView(LoginRequiredMixin, NavigationMixin, ListView):
    template_name = "dashboard/clientes/list.html"
    context_object_name = "clientes"
    paginate_by = 20
    active_section = "clientes"

    def get_queryset(self):
        queryset = Cliente.objects.select_related("creado_por")
        if search := self.request.GET.get("buscar"):
            queryset = queryset.filter(customer_id__icontains=search)
        if contract := self.request.GET.get("contrato"):
            queryset = queryset.filter(contract=contract)
        if active := self.request.GET.get("activo"):
            queryset = queryset.filter(activo=active == "1")
        return queryset


class ClienteCreateView(LoginRequiredMixin, NavigationMixin, CreateView):
    template_name = "dashboard/clientes/form.html"
    form_class = ClienteForm
    active_section = "clientes"

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, "Cliente registrado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dashboard:cliente-editar", args=[self.object.pk])


class ClienteUpdateView(LoginRequiredMixin, NavigationMixin, UpdateView):
    template_name = "dashboard/clientes/form.html"
    form_class = ClienteForm
    model = Cliente
    active_section = "clientes"

    def form_valid(self, form):
        messages.success(self.request, "Cliente actualizado correctamente.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("dashboard:cliente-editar", args=[self.object.pk])


class ModeloView(LoginRequiredMixin, NavigationMixin, TemplateView):
    template_name = "dashboard/modelo/detail.html"
    active_section = "modelo"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["modelo"] = ChurnModelService.version_modelo()
        except ModeloNoDisponible as exc:
            context["modelo_error"] = str(exc)
        context["historial"] = VersionModelo.objects.all()[:10]
        return context


class UsuarioListView(AdministradorRequiredMixin, NavigationMixin, ListView):
    template_name = "dashboard/usuarios/list.html"
    context_object_name = "usuarios"
    paginate_by = 20
    active_section = "usuarios"
    queryset = Usuario.objects.all()


class UsuarioCreateView(AdministradorRequiredMixin, NavigationMixin, CreateView):
    template_name = "dashboard/usuarios/form.html"
    form_class = UsuarioCreateForm
    success_url = reverse_lazy("dashboard:usuarios")
    active_section = "usuarios"

    def form_valid(self, form):
        messages.success(self.request, "Usuario creado correctamente.")
        return super().form_valid(form)


class UsuarioUpdateView(AdministradorRequiredMixin, NavigationMixin, UpdateView):
    template_name = "dashboard/usuarios/form.html"
    form_class = UsuarioUpdateForm
    model = Usuario
    success_url = reverse_lazy("dashboard:usuarios")
    active_section = "usuarios"

    def form_valid(self, form):
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)


class UsuarioToggleActiveView(AdministradorRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(Usuario, pk=pk)
        if user == request.user:
            messages.error(request, "No puedes desactivar tu propia cuenta.")
        else:
            user.is_active = not user.is_active
            user.save(update_fields=["is_active"])
            messages.success(request, "Estado del usuario actualizado.")
        return redirect("dashboard:usuarios")


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
