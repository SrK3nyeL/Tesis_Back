from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from predicciones.models import VersionModelo


class Command(BaseCommand):
    help = "Entrena, compara y almacena un pipeline reproducible para churn."

    def add_arguments(self, parser):
        parser.add_argument("--dataset", default=str(settings.BASE_DIR.parent / "WA_Fn-UseC_-Telco-Customer-Churn.csv"))
        parser.add_argument("--threshold", type=float, default=0.50)

    def handle(self, *args, **options):
        dataset_path = Path(options["dataset"])
        threshold = options["threshold"]
        if not dataset_path.exists():
            raise CommandError(f"No se encontro el dataset: {dataset_path}")
        if not 0 < threshold < 1:
            raise CommandError("--threshold debe encontrarse entre 0 y 1.")

        frame = pd.read_csv(dataset_path)
        required = {"customerID", "Churn", "TotalCharges"}
        if not required.issubset(frame.columns):
            raise CommandError(f"El dataset no contiene: {sorted(required - set(frame.columns))}")
        frame = frame.copy()
        frame["TotalCharges"] = pd.to_numeric(frame["TotalCharges"], errors="coerce")
        y = frame.pop("Churn").map({"No": 0, "Yes": 1})
        frame.pop("customerID")

        numeric = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]
        categorical = [column for column in frame.columns if column not in numeric]
        preprocess = ColumnTransformer(
            transformers=[
                ("num", Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]), numeric),
                ("cat", Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]), categorical),
            ]
        )
        x_train, x_test, y_train, y_test = train_test_split(
            frame, y, test_size=0.20, stratify=y, random_state=42
        )
        candidates = {
            "DummyClassifier": DummyClassifier(strategy="prior"),
            "LogisticRegression": LogisticRegression(
                class_weight="balanced", max_iter=2000, random_state=42
            ),
            "RandomForestClassifier": RandomForestClassifier(
                n_estimators=300, min_samples_leaf=3, class_weight="balanced_subsample",
                random_state=42, n_jobs=-1,
            ),
        }
        results, fitted = {}, {}
        for name, estimator in candidates.items():
            self.stdout.write(f"Entrenando {name}...")
            pipeline = Pipeline([("preprocess", preprocess), ("model", estimator)])
            pipeline.fit(x_train, y_train)
            probability = pipeline.predict_proba(x_test)[:, 1]
            metrics, matrix = self._metrics(y_test, probability, threshold)
            results[name] = {**metrics, "matriz_confusion": matrix}
            fitted[name] = pipeline

        eligible = [
            name for name, value in results.items()
            if name != "DummyClassifier" and value["recall"] >= 0.70 and value["precision"] >= 0.45
        ]
        pool = eligible or [name for name in candidates if name != "DummyClassifier"]
        selected = max(pool, key=lambda name: (results[name]["recall"], results[name]["f1_score"], results[name]["roc_auc"]))
        pipeline = fitted[selected]
        selected_metrics = results[selected].copy()
        matrix = selected_metrics.pop("matriz_confusion")
        importances = self._feature_importances(pipeline, frame.columns)
        now = datetime.now(timezone.utc)
        artifact = {
            "name": "Modelo predictivo de abandono Telco",
            "version": now.strftime("%Y%m%dT%H%M%SZ"),
            "algorithm": selected,
            "pipeline": pipeline,
            "threshold": threshold,
            "feature_names": list(frame.columns),
            "metrics": selected_metrics,
            "confusion_matrix": matrix,
            "feature_importances": importances,
            "trained_at": now.isoformat(),
            "configuration": {
                "dataset": dataset_path.name,
                "rows": len(frame),
                "train_rows": len(x_train),
                "test_rows": len(x_test),
                "test_size": 0.20,
                "random_state": 42,
                "stratified": True,
                "selection_rule": "recall, luego F1, con precision minima de 0.45",
                "candidate_results": results,
            },
        }
        output = Path(settings.CHURN_MODEL_PATH)
        output.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(artifact, output)
        VersionModelo.objects.update_or_create(
            version=artifact["version"],
            defaults={
                "nombre": artifact["name"], "algoritmo": selected, "umbral": threshold,
                "metricas": selected_metrics, "matriz_confusion": matrix,
                "importancia_variables": importances, "configuracion": artifact["configuration"],
                "ruta_artefacto": str(output), "activo": True, "entrenado_en": now,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Modelo seleccionado: {selected}"))
        self.stdout.write(self.style.SUCCESS(f"Artefacto: {output}"))
        self.stdout.write(self.style.SUCCESS(f"Metricas: {selected_metrics}"))

    @staticmethod
    def _metrics(y_true, probability, threshold):
        predicted = (probability >= threshold).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, predicted).ravel()
        order = np.argsort(probability)[::-1]
        top_count = max(1, int(len(y_true) * 0.20))
        top_positives = int(np.asarray(y_true)[order[:top_count]].sum())
        total_positives = int(np.asarray(y_true).sum())
        capture = top_positives / total_positives if total_positives else 0
        base_rate = total_positives / len(y_true) if len(y_true) else 0
        top_rate = top_positives / top_count
        return (
            {
                "accuracy": round(accuracy_score(y_true, predicted), 6),
                "precision": round(precision_score(y_true, predicted, zero_division=0), 6),
                "recall": round(recall_score(y_true, predicted, zero_division=0), 6),
                "f1_score": round(f1_score(y_true, predicted, zero_division=0), 6),
                "roc_auc": round(roc_auc_score(y_true, probability), 6),
                "pr_auc": round(average_precision_score(y_true, probability), 6),
                "false_negative_rate": round(float(fn / (fn + tp)), 6) if fn + tp else 0,
                "capture_at_20": round(capture, 6),
                "lift_at_20": round(top_rate / base_rate, 6) if base_rate else 0,
            },
            {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        )

    @staticmethod
    def _feature_importances(pipeline, raw_names):
        preprocess = pipeline.named_steps["preprocess"]
        model = pipeline.named_steps["model"]
        names = preprocess.get_feature_names_out()
        if hasattr(model, "coef_"):
            weights = np.abs(model.coef_[0])
        elif hasattr(model, "feature_importances_"):
            weights = model.feature_importances_
        else:
            return []
        aggregated = {name: 0.0 for name in raw_names}
        for transformed_name, weight in zip(names, weights):
            clean = transformed_name.split("__", 1)[-1]
            matches = [name for name in raw_names if clean == name or clean.startswith(f"{name}_")]
            if matches:
                aggregated[max(matches, key=len)] += float(weight)
        total = sum(aggregated.values()) or 1
        return [
            {"variable": name, "importancia": round(value / total, 6)}
            for name, value in sorted(aggregated.items(), key=lambda item: item[1], reverse=True)
        ]
