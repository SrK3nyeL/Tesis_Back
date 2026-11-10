from django.contrib import admin

from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("customer_id", "contract", "tenure", "monthly_charges", "activo", "actualizado_en")
    list_filter = ("activo", "contract", "internet_service")
    search_fields = ("customer_id",)
    readonly_fields = ("creado_en", "actualizado_en")
