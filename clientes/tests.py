from rest_framework.test import APITestCase

from usuarios.models import Usuario


class ClienteAPITests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username="user", email="user@example.com", password="pass")
        self.client.force_authenticate(self.user)
        self.payload = {
            "customer_id": "C-001", "gender": "Female", "senior_citizen": False,
            "partner": True, "dependents": False, "tenure": 12, "phone_service": True,
            "multiple_lines": "No", "internet_service": "DSL", "online_security": "Yes",
            "online_backup": "No", "device_protection": "No", "tech_support": "Yes",
            "streaming_tv": "No", "streaming_movies": "No", "contract": "One year",
            "paperless_billing": True, "payment_method": "Electronic check",
            "monthly_charges": "60.50", "total_charges": "726.00",
        }

    def test_crear_y_consultar_cliente(self):
        response = self.client.post("/api/v1/clientes/", self.payload, format="json")
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["customer_id"], "C-001")
        listing = self.client.get("/api/v1/clientes/?contrato=One%20year")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data["count"], 1)

    def test_valida_cargos_totales_inconsistentes(self):
        self.payload["total_charges"] = 0
        response = self.client.post("/api/v1/clientes/", self.payload, format="json")
        self.assertEqual(response.status_code, 400)
