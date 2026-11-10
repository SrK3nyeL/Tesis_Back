from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Usuario


class AutenticacionTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="analista", email="analista@example.com", password="ClaveSegura123!"
        )

    def test_login_y_logout_revocan_token(self):
        """CP-01 y CP-11: acceso valido, revocacion y rechazo posterior."""
        response = self.client.post("/api/v1/auth/login/", {"username": "analista", "password": "ClaveSegura123!"})
        self.assertEqual(response.status_code, 200)
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(self.client.get("/api/v1/auth/perfil/").status_code, 200)
        self.assertEqual(self.client.post("/api/v1/auth/logout/").status_code, 204)
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        self.assertEqual(self.client.get("/api/v1/auth/perfil/").status_code, 401)

    def test_rechaza_credenciales_invalidas_y_cuenta_inactiva(self):
        """CP-01: credenciales incorrectas o cuenta inactiva no acceden."""
        self.assertEqual(self.client.post("/api/v1/auth/login/", {"username": "analista", "password": "mal"}).status_code, 401)
        self.user.is_active = False
        self.user.save()
        response = self.client.post("/api/v1/auth/login/", {"username": "analista", "password": "ClaveSegura123!"})
        self.assertEqual(response.status_code, 401)

    def test_endpoint_protegido_requiere_autenticacion(self):
        """CP-11: los recursos protegidos no aceptan solicitudes anonimas."""
        self.assertEqual(self.client.get("/api/v1/clientes/").status_code, 401)
