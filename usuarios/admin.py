from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "email", "rol", "is_active", "is_staff")
    list_filter = ("rol", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Perfil", {"fields": ("rol", "cargo")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Perfil", {"fields": ("email", "rol", "cargo")}),
    )
