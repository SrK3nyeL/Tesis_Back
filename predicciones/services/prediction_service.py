from django.utils import timezone

from predicciones.models import LotePrediccion, Prediccion
from predicciones.serializers import PrediccionEntradaSerializer

from .model_service import ChurnModelService, ModeloNoDisponible


def guardar_prediccion(*, user, validated_data, lote=None, version=None):
    """Punto unico de escritura usado por la API y las vistas HTML."""
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


def procesar_lote(*, user, rows, file_name, first_row=1):
    """Procesa parcialmente un lote y conserva los errores por numero de fila."""
    batch = LotePrediccion.objects.create(
        nombre_archivo=file_name,
        total_registros=len(rows),
        creado_por=user,
    )
    errors, successful = [], 0
    try:
        version = ChurnModelService.version_modelo()
        for row_number, row in enumerate(rows, start=first_row):
            serializer = PrediccionEntradaSerializer(data=row)
            if serializer.is_valid():
                guardar_prediccion(
                    user=user,
                    validated_data=serializer.validated_data,
                    lote=batch,
                    version=version,
                )
                successful += 1
            else:
                errors.append({"fila": row_number, "errores": serializer.errors})
        batch.registros_exitosos = successful
        batch.registros_fallidos = len(rows) - successful
        batch.errores = errors[:200]
        batch.estado = (
            LotePrediccion.Estado.COMPLETADO
            if not errors
            else LotePrediccion.Estado.COMPLETADO_ERRORES
        )
    except ModeloNoDisponible as exc:
        batch.estado = LotePrediccion.Estado.FALLIDO
        batch.errores = [{"detalle": str(exc)}]
    finally:
        batch.finalizado_en = timezone.now()
        batch.save()
    return batch
