from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        INVESTIGADOR = "investigador", "Investigador"
        ANALISTA = "analista", "Analista"

    email = models.EmailField("correo electronico", unique=True)
    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ANALISTA)
    cargo = models.CharField(max_length=100, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["username"]
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_full_name() or self.username
