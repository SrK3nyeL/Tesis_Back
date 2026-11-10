from rest_framework.test import APITestCase

from .models import Prediccion
from usuarios.models import Usuario


class PrediccionAPITests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="predictor", email="predictor@example.com", password="pass")
        self.client.force_authenticate(self.user)
        self.payload = {
            "customerID": "TEST-001", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "No", "tenure": 5, "PhoneService": "Yes",
            "MultipleLines": "No", "InternetService": "Fiber optic", "OnlineSecurity": "No",
            "OnlineBackup": "No", "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "Yes", "Contract": "Month-to-month",
            "PaperlessBilling": "Yes", "PaymentMethod": "Electronic check",
            "MonthlyCharges": 95.5, "TotalCharges": 477.5,
        }

    def test_prediccion_individual_persiste_trazabilidad(self):
        response = self.client.post("/api/v1/predicciones/individual/", self.payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertIn(response.data["nivel_riesgo"], {"bajo", "medio", "alto"})
        self.assertGreaterEqual(response.data["probabilidad"], 0)
        saved = Prediccion.objects.get()
        self.assertEqual(saved.referencia_cliente, "TEST-001")
        self.assertTrue(saved.version_modelo.activo)

    def test_entrada_incompleta_no_genera_prediccion(self):
        response = self.client.post("/api/v1/predicciones/individual/", {"gender": "Female"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Prediccion.objects.count(), 0)

    def test_lote_procesa_validos_y_reporta_errores(self):
        response = self.client.post(
            "/api/v1/predicciones/lote/",
            {"registros": [self.payload, {"customerID": "INVALIDO"}]},
            format="json",
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["registros_exitosos"], 1)
        self.assertEqual(response.data["registros_fallidos"], 1)

    def test_consulta_filtro_exportacion_y_modelo(self):
        self.client.post("/api/v1/predicciones/individual/", self.payload, format="json")
        listing = self.client.get("/api/v1/predicciones/resultados/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data["count"], 1)
        exported = self.client.get("/api/v1/predicciones/resultados/exportar/")
        self.assertEqual(exported.status_code, 200)
        self.assertIn("text/csv", exported["Content-Type"])
        model = self.client.get("/api/v1/predicciones/modelo/activo/")
        self.assertEqual(model.status_code, 200)
        self.assertIn("recall", model.data["metricas"])
