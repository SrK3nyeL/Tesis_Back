from django.contrib import admin

from .models import LotePrediccion, Prediccion, VersionModelo


@admin.register(VersionModelo)
class VersionModeloAdmin(admin.ModelAdmin):
    list_display = ("version", "algoritmo", "umbral", "activo", "entrenado_en")
    list_filter = ("activo", "algoritmo")
    readonly_fields = ("creado_en",)


@admin.register(Prediccion)
class PrediccionAdmin(admin.ModelAdmin):
    list_display = ("referencia_cliente", "probabilidad", "nivel_riesgo", "abandono_predicho", "creado_en")
    list_filter = ("nivel_riesgo", "abandono_predicho", "version_modelo")
    search_fields = ("referencia_cliente",)
    readonly_fields = ("creado_en",)


@admin.register(LotePrediccion)
class LotePrediccionAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre_archivo", "estado", "registros_exitosos", "registros_fallidos", "creado_en")
    list_filter = ("estado",)
