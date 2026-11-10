import csv
import io

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LotePrediccion, Prediccion, VersionModelo
from .serializers import (
    LotePrediccionSerializer,
    PrediccionEntradaSerializer,
    PrediccionSerializer,
    VersionModeloSerializer,
)
from .services.model_service import ChurnModelService, ModeloNoDisponible


def guardar_prediccion(*, user, validated_data, lote=None, version=None):
    payload = PrediccionEntradaSerializer.model_payload(validated_data)
    result = ChurnModelService.predecir(payload)
    cliente = validated_data.get("cliente")
    reference = cliente.customer_id if cliente else validated_data.get("customerID", "")
    return Prediccion.objects.create(
        cliente=cliente,
        referencia_cliente=reference,
        datos_entrada=payload,
        lote=lote,
        version_modelo=version or ChurnModelService.version_modelo(),
        creado_por=user,
        **result,
    )


class PrediccionIndividualView(APIView):
    def post(self, request):
        serializer = PrediccionEntradaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            prediction = guardar_prediccion(user=request.user, validated_data=serializer.validated_data)
        except ModeloNoDisponible as exc:
            return Response({"detalle": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(PrediccionSerializer(prediction).data, status=status.HTTP_201_CREATED)


class PrediccionLoteView(APIView):
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def post(self, request):
        uploaded = request.FILES.get("archivo")
        if uploaded:
            if not uploaded.name.lower().endswith(".csv"):
                return Response({"detalle": "El archivo debe tener extension CSV."}, status=400)
            try:
                content = uploaded.read().decode("utf-8-sig")
            except UnicodeDecodeError:
                return Response({"detalle": "El CSV debe estar codificado en UTF-8."}, status=400)
            rows = list(csv.DictReader(io.StringIO(content)))
            file_name = uploaded.name
        else:
            rows = request.data.get("registros", [])
            file_name = "solicitud-json"
        if not isinstance(rows, list) or not rows:
            return Response({"detalle": "Envie un archivo CSV o una lista no vacia en 'registros'."}, status=400)
        from django.conf import settings
        if len(rows) > settings.CHURN_MAX_BATCH_ROWS:
            return Response({"detalle": f"El lote supera el maximo de {settings.CHURN_MAX_BATCH_ROWS} filas."}, status=400)

        batch = LotePrediccion.objects.create(
            nombre_archivo=file_name, total_registros=len(rows), creado_por=request.user
        )
        errors, successful = [], 0
        try:
            version = ChurnModelService.version_modelo()
            for row_number, row in enumerate(rows, start=2 if uploaded else 1):
                serializer = PrediccionEntradaSerializer(data=row)
                if serializer.is_valid():
                    guardar_prediccion(
                        user=request.user, validated_data=serializer.validated_data, lote=batch, version=version
                    )
                    successful += 1
                else:
                    errors.append({"fila": row_number, "errores": serializer.errors})
            batch.registros_exitosos = successful
            batch.registros_fallidos = len(rows) - successful
            batch.errores = errors[:200]
            batch.estado = (
                LotePrediccion.Estado.COMPLETADO if not errors else LotePrediccion.Estado.COMPLETADO_ERRORES
            )
        except ModeloNoDisponible as exc:
            batch.estado = LotePrediccion.Estado.FALLIDO
            batch.errores = [{"detalle": str(exc)}]
        finally:
            batch.finalizado_en = timezone.now()
            batch.save()
        response_status = 201 if batch.estado != LotePrediccion.Estado.FALLIDO else 503
        return Response(LotePrediccionSerializer(batch).data, status=response_status)


class PrediccionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PrediccionSerializer

    def get_queryset(self):
        queryset = Prediccion.objects.select_related("cliente", "version_modelo", "creado_por")
        if risk := self.request.query_params.get("riesgo"):
            queryset = queryset.filter(nivel_riesgo=risk)
        if churn := self.request.query_params.get("abandono"):
            queryset = queryset.filter(abandono_predicho=churn.lower() in {"1", "true", "si"})
        if batch := self.request.query_params.get("lote"):
            queryset = queryset.filter(lote_id=batch)
        if reference := self.request.query_params.get("cliente"):
            queryset = queryset.filter(referencia_cliente__icontains=reference)
        return queryset

    @action(detail=True, methods=["get"])
    def explicacion(self, request, pk=None):
        prediction = self.get_object()
        return Response({
            "prediccion_id": prediction.id,
            "version_modelo": prediction.version_modelo.version,
            "probabilidad": prediction.probabilidad,
            "factores": prediction.explicacion,
        })

    @action(detail=False, methods=["get"])
    def exportar(self, request):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="predicciones_churn.csv"'
        writer = csv.writer(response)
        writer.writerow(["id", "cliente", "abandono_predicho", "probabilidad", "nivel_riesgo", "modelo", "fecha"])
        for item in self.filter_queryset(self.get_queryset()).iterator():
            writer.writerow([
                item.id, item.referencia_cliente, item.abandono_predicho, item.probabilidad,
                item.nivel_riesgo, item.version_modelo.version, item.creado_en.isoformat(),
            ])
        return response


class LotePrediccionListView(generics.ListAPIView):
    queryset = LotePrediccion.objects.select_related("creado_por")
    serializer_class = LotePrediccionSerializer


class ModeloActivoView(APIView):
    def get(self, request):
        try:
            model = ChurnModelService.version_modelo()
        except ModeloNoDisponible as exc:
            return Response({"detalle": str(exc)}, status=503)
        return Response(VersionModeloSerializer(model).data)


class HistorialModelosView(generics.ListAPIView):
    queryset = VersionModelo.objects.all()
    serializer_class = VersionModeloSerializer
