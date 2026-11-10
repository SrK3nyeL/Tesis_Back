"""Casos automatizables CP-00 a CP-18 definidos en el documento de tesis."""

import csv
import io
from pathlib import Path
from time import perf_counter

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from usuarios.models import Usuario
from .models import Prediccion
from .services.model_service import ChurnModelService


class CasosPruebaDocumentoTests(APITestCase):
    max_inference_seconds = 0.50

    def setUp(self):
        self.user = Usuario.objects.create_user(
            username="cp_analista", email="cp@example.com", password="ClaveCP123!"
        )
        self.client.force_authenticate(self.user)
        self.payload = {
            "customerID": "CP-CLIENTE-001", "gender": "Female", "SeniorCitizen": 0,
            "Partner": "Yes", "Dependents": "No", "tenure": 5, "PhoneService": "Yes",
            "MultipleLines": "No", "InternetService": "Fiber optic", "OnlineSecurity": "No",
            "OnlineBackup": "No", "DeviceProtection": "No", "TechSupport": "No",
            "StreamingTV": "Yes", "StreamingMovies": "Yes", "Contract": "Month-to-month",
            "PaperlessBilling": "Yes", "PaymentMethod": "Electronic check",
            "MonthlyCharges": 95.5, "TotalCharges": 477.5,
        }

    def _csv_upload(self, rows, name="clientes.csv"):
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(self.payload))
        writer.writeheader()
        writer.writerows(rows)
        return SimpleUploadedFile(name, stream.getvalue().encode("utf-8"), content_type="text/csv")

    def _crear_prediccion(self, reference, risk, probability, churn):
        version = ChurnModelService.version_modelo()
        return Prediccion.objects.create(
            referencia_cliente=reference,
            datos_entrada={},
            abandono_predicho=churn,
            probabilidad=probability,
            nivel_riesgo=risk,
            explicacion=[{"variable": "Contract", "contribucion": 0.5, "direccion": "aumenta"}],
            version_modelo=version,
            creado_por=self.user,
        )

    def test_cp00_disponibilidad_basica(self):
        health = self.client.get("/health/")
        model = self.client.get("/api/v1/predicciones/modelo/activo/")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.data["database"], "ok")
        self.assertEqual(model.status_code, 200)
        self.assertTrue(Path(settings.CHURN_MODEL_PATH).is_file())

    def test_cp02_carga_csv_con_esquema_valido(self):
        second = {**self.payload, "customerID": "CP-CLIENTE-002"}
        response = self.client.post(
            "/api/v1/predicciones/lote/", {"archivo": self._csv_upload([self.payload, second])}, format="multipart"
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["total_registros"], 2)
        self.assertEqual(response.data["registros_exitosos"], 2)
        self.assertEqual(response.data["registros_fallidos"], 0)

    def test_cp03_tipo_incompatible_no_ejecuta_modelo(self):
        invalid = {**self.payload, "tenure": "cinco"}
        response = self.client.post("/api/v1/predicciones/individual/", invalid, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Prediccion.objects.count(), 0)
        self.assertIn("tenure", str(response.data))

    def test_cp04_lote_csv_parcial_identifica_fila_invalida(self):
        invalid = {**self.payload, "customerID": "CP-INVALIDO", "MonthlyCharges": "no-numerico"}
        response = self.client.post(
            "/api/v1/predicciones/lote/", {"archivo": self._csv_upload([self.payload, invalid])}, format="multipart"
        )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data["registros_exitosos"], 1)
        self.assertEqual(response.data["registros_fallidos"], 1)
        self.assertEqual(response.data["errores"][0]["fila"], 3)
        self.assertEqual(Prediccion.objects.count(), 1)

    def test_cp05_consulta_presenta_resultado_completo(self):
        created = self.client.post("/api/v1/predicciones/individual/", self.payload, format="json")
        response = self.client.get(f"/api/v1/predicciones/resultados/{created.data['id']}/")
        self.assertEqual(response.status_code, 200)
        for field in ("abandono_predicho", "probabilidad", "nivel_riesgo", "version_modelo", "creado_en"):
            self.assertIn(field, response.data)

    def test_cp06_filtro_devuelve_solo_clientes_del_riesgo_solicitado(self):
        self._crear_prediccion("ALTO-001", Prediccion.NivelRiesgo.ALTO, 0.91, True)
        self._crear_prediccion("BAJO-001", Prediccion.NivelRiesgo.BAJO, 0.08, False)
        response = self.client.get("/api/v1/predicciones/resultados/?riesgo=alto")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["referencia_cliente"], "ALTO-001")

    def test_cp07_metricas_y_matriz_corresponden_a_version(self):
        artifact = ChurnModelService.artifact()
        response = self.client.get("/api/v1/predicciones/modelo/activo/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["version"], artifact["version"])
        self.assertEqual(response.data["metricas"], artifact["metrics"])
        self.assertEqual(response.data["matriz_confusion"], artifact["confusion_matrix"])
        self.assertEqual(set(response.data["matriz_confusion"]), {"tp", "tn", "fp", "fn"})

    def test_cp08_explicacion_individual_y_factores_globales(self):
        prediction = self.client.post("/api/v1/predicciones/individual/", self.payload, format="json")
        explanation = self.client.get(
            f"/api/v1/predicciones/resultados/{prediction.data['id']}/explicacion/"
        )
        model = self.client.get("/api/v1/predicciones/modelo/activo/")
        self.assertEqual(explanation.status_code, 200)
        self.assertEqual(explanation.data["prediccion_id"], prediction.data["id"])
        self.assertEqual(explanation.data["version_modelo"], prediction.data["version_modelo"])
        self.assertTrue(explanation.data["factores"])
        self.assertTrue(model.data["importancia_variables"])

    def test_cp09_dashboard_coincide_con_datos_y_renderiza_indicadores(self):
        self._crear_prediccion("DASH-ALTO", Prediccion.NivelRiesgo.ALTO, 0.90, True)
        self._crear_prediccion("DASH-BAJO", Prediccion.NivelRiesgo.BAJO, 0.10, False)
        api = self.client.get("/api/v1/dashboard/resumen/")
        self.client.force_login(self.user)
        web = self.client.get("/")
        self.assertEqual(api.data["total_predicciones"], 2)
        self.assertEqual(api.data["riesgo"]["alto"], 1)
        self.assertEqual(api.data["riesgo"]["bajo"], 1)
        self.assertContains(web, "Niveles de riesgo")
        self.assertContains(web, "Clientes con riesgo alto")

    def test_cp10_exportacion_respeta_filtro_y_columnas(self):
        self._crear_prediccion("EXPORT-ALTO", Prediccion.NivelRiesgo.ALTO, 0.93, True)
        self._crear_prediccion("EXPORT-BAJO", Prediccion.NivelRiesgo.BAJO, 0.07, False)
        response = self.client.get("/api/v1/predicciones/resultados/exportar/?riesgo=alto")
        rows = list(csv.DictReader(io.StringIO(response.content.decode("utf-8"))))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(rows[0]), [
            "id", "cliente", "abandono_predicho", "probabilidad", "nivel_riesgo", "modelo", "fecha"
        ])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["cliente"], "EXPORT-ALTO")

    def test_cp12_preparacion_reproducible_registra_particion_y_pipeline(self):
        artifact = ChurnModelService.artifact()
        config = artifact["configuration"]
        self.assertEqual(config["random_state"], 42)
        self.assertTrue(config["stratified"])
        self.assertEqual(config["test_size"], 0.20)
        self.assertEqual(config["train_rows"] + config["test_rows"], config["rows"])
        self.assertIn("preprocess", artifact["pipeline"].named_steps)
        self.assertIn("model", artifact["pipeline"].named_steps)
        self.assertNotIn("customerID", artifact["feature_names"])
        self.assertNotIn("Churn", artifact["feature_names"])

    def test_cp13_evaluacion_independiente_con_baseline_y_kpis(self):
        artifact = ChurnModelService.artifact()
        candidates = artifact["configuration"]["candidate_results"]
        self.assertIn("DummyClassifier", candidates)
        self.assertIn("LogisticRegression", candidates)
        self.assertIn("RandomForestClassifier", candidates)
        self.assertIn("recall", artifact["configuration"]["selection_rule"])
        for metric in ("accuracy", "precision", "recall", "f1_score", "roc_auc", "pr_auc", "false_negative_rate"):
            self.assertIn(metric, artifact["metrics"])
        self.assertLessEqual(artifact["metrics"]["false_negative_rate"], 0.25)

    def test_cp14_rendimiento_inferencia_bajo_umbral_declarado(self):
        model_payload = {key: value for key, value in self.payload.items() if key != "customerID"}
        ChurnModelService.predecir(model_payload)  # Calentamiento fuera de la medicion.
        started = perf_counter()
        results = [ChurnModelService.predecir(model_payload) for _ in range(20)]
        average = (perf_counter() - started) / len(results)
        self.assertLess(average, self.max_inference_seconds)
        self.assertTrue(all(item["duracion_ms"] <= self.max_inference_seconds * 1000 for item in results))

    def test_cp15_privacidad_no_expone_credenciales_ni_pii_extra(self):
        private_payload = {
            **self.payload, "email": "persona@example.com", "password": "NoDebePersistir",
            "nombre_completo": "Persona de Prueba",
        }
        response = self.client.post("/api/v1/predicciones/individual/", private_payload, format="json")
        saved = Prediccion.objects.get()
        serialized = str(response.data).lower()
        self.assertNotIn("password", serialized)
        self.assertNotIn("persona@example.com", serialized)
        self.assertNotIn("email", saved.datos_entrada)
        self.assertNotIn("password", saved.datos_entrada)
        export = self.client.get("/api/v1/predicciones/resultados/exportar/").content.decode("utf-8").lower()
        self.assertNotIn("persona@example.com", export)
        self.assertNotIn("nodebepersistir", export)

    def test_cp16_portabilidad_tiene_dependencias_y_configuracion_local(self):
        requirements = (settings.BASE_DIR / "requirements.txt").read_text(encoding="utf-8")
        env_example = (settings.BASE_DIR / ".env.example").read_text(encoding="utf-8")
        readme = (settings.BASE_DIR / "README.md").read_text(encoding="utf-8")
        self.assertIn("Django==", requirements)
        self.assertIn("scikit-learn==", requirements)
        self.assertIn("DB_ENGINE=sqlite", env_example)
        self.assertIn("python manage.py migrate", readme)
        self.assertIn("python manage.py runserver", readme)

    def test_cp17_mantenibilidad_y_documentacion_modular(self):
        expected = ["usuarios", "clientes", "predicciones", "dashboard", "config"]
        self.assertTrue(all((settings.BASE_DIR / folder).is_dir() for folder in expected))
        readme = (settings.BASE_DIR / "README.md").read_text(encoding="utf-8")
        for section in ("## Arquitectura", "## Endpoints principales", "## Entrenamiento y reproducibilidad", "## Pruebas"):
            self.assertIn(section, readme)

    def test_cp18_misma_entrada_y_modelo_producen_resultado_consistente(self):
        model_payload = {key: value for key, value in self.payload.items() if key != "customerID"}
        first = ChurnModelService.predecir(model_payload)
        ChurnModelService._artifact = None
        ChurnModelService._mtime = None
        second = ChurnModelService.predecir(model_payload)
        for field in ("probabilidad", "abandono_predicho", "nivel_riesgo", "explicacion"):
            self.assertEqual(first[field], second[field])
