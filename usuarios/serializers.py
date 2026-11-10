from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = Usuario
        fields = (
            "id", "username", "email", "first_name", "last_name", "nombre",
            "rol", "cargo", "is_active", "date_joined", "last_login",
        )
        read_only_fields = ("id", "username", "is_active", "date_joined", "last_login")


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = Usuario
        fields = ("id", "username", "email", "first_name", "last_name", "rol", "cargo", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        return Usuario.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
