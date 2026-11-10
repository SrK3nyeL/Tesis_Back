from django import forms
from django.contrib.auth.forms import UserCreationForm

from clientes.models import Cliente
from predicciones.serializers import PrediccionEntradaSerializer
from usuarios.models import Usuario

YES_NO = (("Yes", "Si"), ("No", "No"))
INTERNET_OPTION = (("Yes", "Si"), ("No", "No"), ("No internet service", "Sin internet"))


class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class PrediccionForm(StyledFormMixin, forms.Form):
    cliente = forms.ModelChoiceField(
        queryset=Cliente.objects.none(), required=False, label="Cliente registrado",
        help_text="Si seleccionas un cliente, no necesitas completar los campos manuales.",
    )
    customerID = forms.CharField(max_length=50, required=False, label="Codigo de cliente")
    gender = forms.ChoiceField(choices=(("", "Seleccione"), ("Female", "Femenino"), ("Male", "Masculino")), required=False, label="Genero")
    SeniorCitizen = forms.TypedChoiceField(choices=(("", "Seleccione"), (0, "No"), (1, "Si")), coerce=int, empty_value=None, required=False, label="Adulto mayor")
    Partner = forms.ChoiceField(choices=(("", "Seleccione"),) + YES_NO, required=False, label="Pareja")
    Dependents = forms.ChoiceField(choices=(("", "Seleccione"),) + YES_NO, required=False, label="Dependientes")
    tenure = forms.IntegerField(min_value=0, max_value=100, required=False, label="Permanencia (meses)")
    PhoneService = forms.ChoiceField(choices=(("", "Seleccione"),) + YES_NO, required=False, label="Servicio telefonico")
    MultipleLines = forms.ChoiceField(choices=(("", "Seleccione"), ("Yes", "Si"), ("No", "No"), ("No phone service", "Sin telefono")), required=False, label="Multiples lineas")
    InternetService = forms.ChoiceField(choices=(("", "Seleccione"), ("DSL", "DSL"), ("Fiber optic", "Fibra optica"), ("No", "Sin internet")), required=False, label="Servicio de internet")
    OnlineSecurity = forms.ChoiceField(choices=(("", "Seleccione"),) + INTERNET_OPTION, required=False, label="Seguridad en linea")
    OnlineBackup = forms.ChoiceField(choices=(("", "Seleccione"),) + INTERNET_OPTION, required=False, label="Respaldo en linea")
    DeviceProtection = forms.ChoiceField(choices=(("", "Seleccione"),) + INTERNET_OPTION, required=False, label="Proteccion de dispositivo")
    TechSupport = forms.ChoiceField(choices=(("", "Seleccione"),) + INTERNET_OPTION, required=False, label="Soporte tecnico")
    StreamingTV = forms.ChoiceField(choices=(("", "Seleccione"),) + INTERNET_OPTION, required=False, label="Streaming TV")
    StreamingMovies = forms.ChoiceField(choices=(("", "Seleccione"),) + INTERNET_OPTION, required=False, label="Streaming peliculas")
    Contract = forms.ChoiceField(choices=(("", "Seleccione"), ("Month-to-month", "Mes a mes"), ("One year", "Un ano"), ("Two year", "Dos anos")), required=False, label="Contrato")
    PaperlessBilling = forms.ChoiceField(choices=(("", "Seleccione"),) + YES_NO, required=False, label="Facturacion electronica")
    PaymentMethod = forms.ChoiceField(
        choices=(("", "Seleccione"), ("Electronic check", "Cheque electronico"),
                 ("Mailed check", "Cheque por correo"),
                 ("Bank transfer (automatic)", "Transferencia automatica"),
                 ("Credit card (automatic)", "Tarjeta automatica")),
        required=False, label="Metodo de pago",
    )
    MonthlyCharges = forms.DecimalField(min_value=0, max_value=10000, required=False, label="Cargo mensual")
    TotalCharges = forms.DecimalField(min_value=0, max_value=1000000, required=False, label="Cargo total")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = Cliente.objects.filter(activo=True)
        self.apply_styles()

    def clean(self):
        cleaned = super().clean()
        if self.errors:
            return cleaned
        payload = {}
        if cleaned.get("cliente"):
            payload["cliente"] = cleaned["cliente"].pk
        else:
            for field in PrediccionEntradaSerializer.feature_fields:
                value = cleaned.get(field)
                if value not in (None, ""):
                    payload[field] = float(value) if field in {"MonthlyCharges", "TotalCharges"} else value
            if cleaned.get("customerID"):
                payload["customerID"] = cleaned["customerID"]
        serializer = PrediccionEntradaSerializer(data=payload)
        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                target = field if field in self.fields else None
                for error in errors if isinstance(errors, list) else [errors]:
                    self.add_error(target, str(error))
            return cleaned
        self.validated_data = serializer.validated_data
        return cleaned


class CargaLoteForm(StyledFormMixin, forms.Form):
    archivo = forms.FileField(
        label="Archivo CSV",
        help_text="Debe usar las columnas del dataset Telco y codificacion UTF-8.",
        widget=forms.ClearableFileInput(attrs={"accept": ".csv,text/csv"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def clean_archivo(self):
        uploaded = self.cleaned_data["archivo"]
        if not uploaded.name.lower().endswith(".csv"):
            raise forms.ValidationError("Seleccione un archivo con extension .csv.")
        return uploaded


class ClienteForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        exclude = ("creado_por", "creado_en", "actualizado_en")
        labels = {
            "customer_id": "Codigo de cliente", "gender": "Genero", "senior_citizen": "Adulto mayor",
            "partner": "Tiene pareja", "dependents": "Tiene dependientes", "tenure": "Permanencia (meses)",
            "phone_service": "Servicio telefonico", "multiple_lines": "Multiples lineas",
            "internet_service": "Servicio de internet", "online_security": "Seguridad en linea",
            "online_backup": "Respaldo en linea", "device_protection": "Proteccion de dispositivo",
            "tech_support": "Soporte tecnico", "streaming_tv": "Streaming TV",
            "streaming_movies": "Streaming peliculas", "contract": "Contrato",
            "paperless_billing": "Facturacion electronica", "payment_method": "Metodo de pago",
            "monthly_charges": "Cargo mensual", "total_charges": "Cargo total", "activo": "Cliente activo",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = {
            "multiple_lines": (("No phone service", "Sin telefono"), ("No", "No"), ("Yes", "Si")),
            "internet_service": (("No", "Sin internet"), ("DSL", "DSL"), ("Fiber optic", "Fibra optica")),
            "online_security": INTERNET_OPTION, "online_backup": INTERNET_OPTION,
            "device_protection": INTERNET_OPTION, "tech_support": INTERNET_OPTION,
            "streaming_tv": INTERNET_OPTION, "streaming_movies": INTERNET_OPTION,
            "contract": (("Month-to-month", "Mes a mes"), ("One year", "Un ano"), ("Two year", "Dos anos")),
            "payment_method": (("Electronic check", "Cheque electronico"), ("Mailed check", "Cheque por correo"),
                               ("Bank transfer (automatic)", "Transferencia automatica"),
                               ("Credit card (automatic)", "Tarjeta automatica")),
        }
        for name, field_choices in choices.items():
            self.fields[name].widget = forms.Select(choices=field_choices, attrs={"class": "form-control"})
        self.apply_styles()


class UsuarioCreateForm(StyledFormMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ("username", "email", "first_name", "last_name", "rol", "cargo")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()


class UsuarioUpdateForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ("email", "first_name", "last_name", "rol", "cargo", "is_active")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()
