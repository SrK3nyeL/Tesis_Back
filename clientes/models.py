from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Cliente(models.Model):
    """Variables no sensibles del esquema IBM Telco usado por el modelo."""

    customer_id = models.CharField("codigo de cliente", max_length=50, unique=True, db_index=True)
    gender = models.CharField(max_length=10, choices=[("Female", "Femenino"), ("Male", "Masculino")])
    senior_citizen = models.BooleanField(default=False)
    partner = models.BooleanField(default=False)
    dependents = models.BooleanField(default=False)
    tenure = models.PositiveSmallIntegerField("meses de permanencia", default=0)
    phone_service = models.BooleanField(default=False)
    multiple_lines = models.CharField(max_length=20, default="No phone service")
    internet_service = models.CharField(max_length=20, default="No")
    online_security = models.CharField(max_length=20, default="No internet service")
    online_backup = models.CharField(max_length=20, default="No internet service")
    device_protection = models.CharField(max_length=20, default="No internet service")
    tech_support = models.CharField(max_length=20, default="No internet service")
    streaming_tv = models.CharField(max_length=20, default="No internet service")
    streaming_movies = models.CharField(max_length=20, default="No internet service")
    contract = models.CharField(max_length=20, default="Month-to-month")
    paperless_billing = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=40)
    monthly_charges = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_charges = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    activo = models.BooleanField(default=True, db_index=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="clientes_creados")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-actualizado_en"]
        indexes = [models.Index(fields=["contract", "activo"])]

    def __str__(self):
        return self.customer_id

    def to_model_payload(self):
        yes_no = lambda value: "Yes" if value else "No"
        return {
            "gender": self.gender, "SeniorCitizen": int(self.senior_citizen),
            "Partner": yes_no(self.partner), "Dependents": yes_no(self.dependents),
            "tenure": self.tenure, "PhoneService": yes_no(self.phone_service),
            "MultipleLines": self.multiple_lines, "InternetService": self.internet_service,
            "OnlineSecurity": self.online_security, "OnlineBackup": self.online_backup,
            "DeviceProtection": self.device_protection, "TechSupport": self.tech_support,
            "StreamingTV": self.streaming_tv, "StreamingMovies": self.streaming_movies,
            "Contract": self.contract, "PaperlessBilling": yes_no(self.paperless_billing),
            "PaymentMethod": self.payment_method, "MonthlyCharges": float(self.monthly_charges),
            "TotalCharges": float(self.total_charges),
        }
