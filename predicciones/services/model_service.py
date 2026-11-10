import math
import threading
from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.utils.dateparse import parse_datetime

from predicciones.models import Prediccion, VersionModelo


class ModeloNoDisponible(RuntimeError):
    pass


class ChurnModelService:
    """Carga perezosa y cacheada del artefacto; evita leerlo en cada solicitud."""

    _artifact = None
    _mtime = None
    _lock = threading.Lock()

    @classmethod
    def artifact(cls):
        path = Path(settings.CHURN_MODEL_PATH)
        if not path.exists():
            raise ModeloNoDisponible("No existe un modelo entrenado. Ejecute: python manage.py entrenar_modelo")
        mtime = path.stat().st_mtime
        if cls._artifact is None or cls._mtime != mtime:
            with cls._lock:
                if cls._artifact is None or cls._mtime != mtime:
                    loaded = joblib.load(path)
                    if not isinstance(loaded, dict) or "pipeline" not in loaded:
                        raise ModeloNoDisponible("El artefacto no contiene un pipeline compatible.")
                    cls._artifact, cls._mtime = loaded, mtime
        return cls._artifact

    @classmethod
    def version_modelo(cls):
        artifact = cls.artifact()
        trained_at = parse_datetime(artifact["trained_at"])
        version, _ = VersionModelo.objects.update_or_create(
            version=artifact["version"],
            defaults={
                "nombre": artifact.get("name", "Modelo churn"),
                "algoritmo": artifact["algorithm"],
                "umbral": artifact["threshold"],
                "metricas": artifact["metrics"],
                "matriz_confusion": artifact["confusion_matrix"],
                "importancia_variables": artifact.get("feature_importances", []),
                "configuracion": artifact.get("configuration", {}),
                "ruta_artefacto": str(settings.CHURN_MODEL_PATH),
                "activo": True,
                "entrenado_en": trained_at,
            },
        )
        return version

    @classmethod
    def predecir(cls, payload):
        artifact = cls.artifact()
        started = perf_counter()
        frame = pd.DataFrame([{name: payload[name] for name in artifact["feature_names"]}])
        probability = float(artifact["pipeline"].predict_proba(frame)[0, 1])
        threshold = float(artifact["threshold"])
        if probability < settings.CHURN_LOW_RISK_MAX:
            risk = Prediccion.NivelRiesgo.BAJO
        elif probability >= settings.CHURN_HIGH_RISK_MIN:
            risk = Prediccion.NivelRiesgo.ALTO
        else:
            risk = Prediccion.NivelRiesgo.MEDIO
        return {
            "probabilidad": round(probability, 6),
            "abandono_predicho": probability >= threshold,
            "nivel_riesgo": risk,
            "explicacion": cls._explicar(frame, artifact),
            "duracion_ms": max(1, round((perf_counter() - started) * 1000)),
        }

    @staticmethod
    def _explicar(frame, artifact):
        pipeline = artifact["pipeline"]
        model = pipeline.named_steps.get("model")
        preprocess = pipeline.named_steps.get("preprocess")
        if preprocess is None or model is None or not hasattr(model, "coef_"):
            return artifact.get("feature_importances", [])[:5]
        transformed = preprocess.transform(frame)
        values = transformed.toarray()[0] if hasattr(transformed, "toarray") else np.asarray(transformed)[0]
        names = preprocess.get_feature_names_out()
        contributions = values * model.coef_[0]
        factors = []
        for index in np.argsort(np.abs(contributions))[::-1][:8]:
            value = float(contributions[index])
            if not math.isclose(value, 0.0):
                factors.append({
                    "variable": str(names[index]).replace("cat__", "").replace("num__", ""),
                    "contribucion": round(value, 5),
                    "direccion": "aumenta" if value > 0 else "reduce",
                })
        return factors
