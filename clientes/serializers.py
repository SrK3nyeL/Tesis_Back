from rest_framework import serializers

from .models import Cliente


class ClienteSerializer(serializers.ModelSerializer):
    creado_por_nombre = serializers.CharField(source="creado_por.username", read_only=True)
    ultima_prediccion = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        exclude = ("creado_por",)
        read_only_fields = ("id", "creado_en", "actualizado_en", "creado_por_nombre", "ultima_prediccion")

    def validate(self, attrs):
        tenure = attrs.get("tenure", getattr(self.instance, "tenure", 0))
        monthly = attrs.get("monthly_charges", getattr(self.instance, "monthly_charges", 0))
        total = attrs.get("total_charges", getattr(self.instance, "total_charges", 0))
        if tenure > 0 and total == 0 and monthly > 0:
            raise serializers.ValidationError({"total_charges": "Debe ser mayor que cero cuando existe permanencia."})
        return attrs

    def get_ultima_prediccion(self, obj):
        prediction = obj.predicciones.order_by("-creado_en").first()
        if not prediction:
            return None
        return {"id": prediction.id, "probabilidad": prediction.probabilidad,
                "nivel_riesgo": prediction.nivel_riesgo, "creado_en": prediction.creado_en}
