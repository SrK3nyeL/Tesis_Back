from rest_framework.test import APITestCase

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

    def test_dashboard_web_renderiza_para_usuario_autenticado(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Churn Intelligence")
