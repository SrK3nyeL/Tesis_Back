from rest_framework import serializers

from clientes.models import Cliente
from .models import LotePrediccion, Prediccion, VersionModelo

YES_NO = ("Yes", "No")
INTERNET_OPTION = ("Yes", "No", "No internet service")


class PrediccionEntradaSerializer(serializers.Serializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.filter(activo=True), required=False, write_only=True)
    customerID = serializers.CharField(max_length=50, required=False, allow_blank=True)
    gender = serializers.ChoiceField(choices=("Female", "Male"), required=False)
    SeniorCitizen = serializers.IntegerField(min_value=0, max_value=1, required=False)
    Partner = serializers.ChoiceField(choices=YES_NO, required=False)
    Dependents = serializers.ChoiceField(choices=YES_NO, required=False)
    tenure = serializers.IntegerField(min_value=0, max_value=100, required=False)
    PhoneService = serializers.ChoiceField(choices=YES_NO, required=False)
    MultipleLines = serializers.ChoiceField(choices=("Yes", "No", "No phone service"), required=False)
    InternetService = serializers.ChoiceField(choices=("DSL", "Fiber optic", "No"), required=False)
    OnlineSecurity = serializers.ChoiceField(choices=INTERNET_OPTION, required=False)
    OnlineBackup = serializers.ChoiceField(choices=INTERNET_OPTION, required=False)
    DeviceProtection = serializers.ChoiceField(choices=INTERNET_OPTION, required=False)
    TechSupport = serializers.ChoiceField(choices=INTERNET_OPTION, required=False)
    StreamingTV = serializers.ChoiceField(choices=INTERNET_OPTION, required=False)
    StreamingMovies = serializers.ChoiceField(choices=INTERNET_OPTION, required=False)
    Contract = serializers.ChoiceField(choices=("Month-to-month", "One year", "Two year"), required=False)
    PaperlessBilling = serializers.ChoiceField(choices=YES_NO, required=False)
    PaymentMethod = serializers.ChoiceField(
        choices=("Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"),
        required=False,
    )
    MonthlyCharges = serializers.FloatField(min_value=0, max_value=10000, required=False)
    TotalCharges = serializers.FloatField(min_value=0, max_value=1000000, required=False)

    feature_fields = (
        "gender", "SeniorCitizen", "Partner", "Dependents", "tenure", "PhoneService",
        "MultipleLines", "InternetService", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies", "Contract", "PaperlessBilling",
        "PaymentMethod", "MonthlyCharges", "TotalCharges",
    )

    def validate(self, attrs):
        if "cliente" in attrs:
            return attrs
        missing = [field for field in self.feature_fields if field not in attrs]
        if missing:
            raise serializers.ValidationError({"campos_faltantes": missing})
        if attrs["tenure"] > 0 and attrs["TotalCharges"] == 0 and attrs["MonthlyCharges"] > 0:
            raise serializers.ValidationError({"TotalCharges": "No puede ser cero cuando tenure es mayor que cero."})
        return attrs

    @classmethod
    def model_payload(cls, validated_data):
        if cliente := validated_data.get("cliente"):
            return cliente.to_model_payload()
        return {field: validated_data[field] for field in cls.feature_fields}


class VersionModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = VersionModelo
        fields = (
            "id", "version", "nombre", "algoritmo", "umbral", "metricas",
            "matriz_confusion", "importancia_variables", "configuracion", "activo", "entrenado_en",
        )


class PrediccionSerializer(serializers.ModelSerializer):
    version_modelo = serializers.CharField(source="version_modelo.version", read_only=True)
    cliente_id = serializers.IntegerField(source="cliente.id", read_only=True, allow_null=True)
    creado_por = serializers.CharField(source="creado_por.username", read_only=True)

    class Meta:
        model = Prediccion
        fields = (
            "id", "cliente_id", "referencia_cliente", "abandono_predicho", "probabilidad",
            "nivel_riesgo", "explicacion", "version_modelo", "duracion_ms", "creado_por", "creado_en",
        )


class LotePrediccionSerializer(serializers.ModelSerializer):
    creado_por = serializers.CharField(source="creado_por.username", read_only=True)

    class Meta:
        model = LotePrediccion
        fields = "__all__"
