import csv
import io

from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from clientes.models import Cliente
from predicciones.models import LotePrediccion, Prediccion
from usuarios.models import Usuario


class DashboardTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="dash", email="dash@example.com", password="pass")

    def test_dashboard_api_requiere_login_y_devuelve_indicadores(self):
        self.assertEqual(self.client.get("/api/v1/dashboard/resumen/").status_code, 401)
        self.client.force_authenticate(self.user)
        response = self.client.get("/api/v1/dashboard/resumen/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("total_predicciones", response.data)
        self.assertIn("riesgo", response.data)

    def test_dashboard_web_redirige_a_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_login_presenta_identidad_y_formulario(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Anticipa el abandono")
        self.assertContains(response, "Ingresar al sistema")
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_dashboard_web_renderiza_para_usuario_autenticado(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Churn Intelligence")


class FrontendOperativoTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="front", email="front@example.com", password="ClaveFront123!"
        )
        self.client.force_login(self.user)
        self.prediction_payload = {
            "customerID": "WEB-001", "gender": "Female", "SeniorCitizen": "0",
            "Partner": "Yes", "Dependents": "No", "tenure": "5", "PhoneService": "Yes",
            "MultipleLines": "No", "InternetService": "Fiber optic", "OnlineSecurity": "No",
            "OnlineBackup": "No", "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "Yes", "Contract": "Month-to-month",
            "PaperlessBilling": "Yes", "PaymentMethod": "Electronic check",
            "MonthlyCharges": "95.50", "TotalCharges": "477.50",
        }

    def _client_payload(self):
        return {
            "customer_id": "WEB-CLIENT", "gender": "Female", "senior_citizen": False,
            "partner": True, "dependents": False, "tenure": 12, "phone_service": True,
            "multiple_lines": "No", "internet_service": "DSL", "online_security": "Yes",
            "online_backup": "No", "device_protection": "No", "tech_support": "Yes",
            "streaming_tv": "No", "streaming_movies": "No", "contract": "One year",
            "paperless_billing": True, "payment_method": "Electronic check",
            "monthly_charges": "60.50", "total_charges": "726.00", "activo": True,
        }

    def test_paginas_principales_renderizan(self):
        for path, text in (
            ("/predecir/", "Nueva prediccion"), ("/lotes/", "Historial de lotes"),
            ("/lotes/cargar/", "Cargar archivo CSV"), ("/clientes/", "Clientes"),
            ("/resultados/", "Resultados de prediccion"), ("/modelo/", "Modelo y metricas"),
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, text)

    def test_formulario_web_genera_prediccion_y_detalle(self):
        response = self.client.post("/predecir/", self.prediction_payload)
        prediction = Prediccion.objects.get()
        self.assertRedirects(response, f"/resultados/{prediction.pk}/")
        detail = self.client.get(response.url)
        self.assertContains(detail, "Factores principales")
        self.assertContains(detail, "WEB-001")

    def test_crud_web_registra_cliente_y_preselecciona_prediccion(self):
        response = self.client.post("/clientes/nuevo/", self._client_payload())
        client = Cliente.objects.get(customer_id="WEB-CLIENT")
        self.assertRedirects(response, f"/clientes/{client.pk}/editar/")
        prediction_form = self.client.get(f"/predecir/?cliente={client.pk}")
        self.assertContains(prediction_form, 'option value="%s" selected' % client.pk, html=False)

    def test_carga_csv_web_procesa_lote_y_muestra_detalle(self):
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(self.prediction_payload))
        writer.writeheader()
        writer.writerow(self.prediction_payload)
        uploaded = SimpleUploadedFile("clientes.csv", stream.getvalue().encode("utf-8"), "text/csv")
        response = self.client.post("/lotes/cargar/", {"archivo": uploaded})
        batch = LotePrediccion.objects.get()
        self.assertRedirects(response, f"/lotes/{batch.pk}/")
        self.assertEqual(batch.registros_exitosos, 1)
        self.assertContains(self.client.get(response.url), "Predicciones generadas")

    def test_gestion_usuarios_restringida_y_operativa_para_admin(self):
        self.assertEqual(self.client.get("/usuarios/").status_code, 403)
        admin = Usuario.objects.create_user(
            username="adminweb", email="adminweb@example.com", password="ClaveAdmin123!",
            rol=Usuario.Rol.ADMINISTRADOR,
        )
        self.client.force_login(admin)
        self.assertEqual(self.client.get("/usuarios/").status_code, 200)
        response = self.client.post("/usuarios/nuevo/", {
            "username": "nuevo", "email": "nuevo@example.com", "first_name": "Nuevo",
            "last_name": "Analista", "rol": Usuario.Rol.ANALISTA, "cargo": "Analista",
            "password1": "ClaveNueva123!", "password2": "ClaveNueva123!",
        })
        self.assertRedirects(response, "/usuarios/")
        self.assertTrue(Usuario.objects.filter(username="nuevo").exists())
