import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class VersionModelo(models.Model):
    version = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=120)
    algoritmo = models.CharField(max_length=100)
    umbral = models.FloatField(default=0.5, validators=[MinValueValidator(0), MaxValueValidator(1)])
    metricas = models.JSONField(default=dict)
    matriz_confusion = models.JSONField(default=dict)
    importancia_variables = models.JSONField(default=list)
    configuracion = models.JSONField(default=dict)
    ruta_artefacto = models.CharField(max_length=500)
    activo = models.BooleanField(default=False, db_index=True)
    entrenado_en = models.DateTimeField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entrenado_en"]
        verbose_name = "version del modelo"
        verbose_name_plural = "versiones del modelo"

    def save(self, *args, **kwargs):
        if self.activo:
            VersionModelo.objects.exclude(pk=self.pk).update(activo=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.version})"


class LotePrediccion(models.Model):
    class Estado(models.TextChoices):
        PROCESANDO = "procesando", "Procesando"
        COMPLETADO = "completado", "Completado"
        COMPLETADO_ERRORES = "completado_errores", "Completado con errores"
        FALLIDO = "fallido", "Fallido"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_archivo = models.CharField(max_length=255, blank=True)
    estado = models.CharField(max_length=30, choices=Estado.choices, default=Estado.PROCESANDO)
    total_registros = models.PositiveIntegerField(default=0)
    registros_exitosos = models.PositiveIntegerField(default=0)
    registros_fallidos = models.PositiveIntegerField(default=0)
    errores = models.JSONField(default=list)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="lotes_prediccion")
    creado_en = models.DateTimeField(auto_now_add=True)
    finalizado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creado_en"]


class Prediccion(models.Model):
    class NivelRiesgo(models.TextChoices):
        BAJO = "bajo", "Bajo"
        MEDIO = "medio", "Medio"
        ALTO = "alto", "Alto"

    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.SET_NULL, null=True, blank=True, related_name="predicciones"
    )
    referencia_cliente = models.CharField(max_length=64, blank=True, db_index=True)
    datos_entrada = models.JSONField(default=dict)
    abandono_predicho = models.BooleanField(db_index=True)
    probabilidad = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    nivel_riesgo = models.CharField(max_length=10, choices=NivelRiesgo.choices, db_index=True)
    explicacion = models.JSONField(default=list)
    version_modelo = models.ForeignKey(VersionModelo, on_delete=models.PROTECT, related_name="predicciones")
    lote = models.ForeignKey(LotePrediccion, on_delete=models.SET_NULL, null=True, blank=True, related_name="predicciones")
    duracion_ms = models.PositiveIntegerField(default=0)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="predicciones")
    creado_en = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-creado_en"]
        indexes = [
            models.Index(fields=["nivel_riesgo", "-creado_en"]),
            models.Index(fields=["abandono_predicho", "-creado_en"]),
        ]
        verbose_name = "prediccion"
        verbose_name_plural = "predicciones"

    def __str__(self):
        return f"{self.referencia_cliente or self.pk}: {self.probabilidad:.2%}"
