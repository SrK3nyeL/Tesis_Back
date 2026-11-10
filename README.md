# Churn Intelligence Backend

Backend Django/DRF para el sistema inteligente de prediccion de abandono de clientes de telecomunicaciones. Implementa autenticacion, usuarios y roles, clientes, prediccion individual y masiva, trazabilidad de modelos, explicabilidad, exportacion CSV y dashboard web.

## Arquitectura

- `usuarios`: usuario personalizado, roles, login/logout por token, perfil y administracion.
- `clientes`: CRUD de clientes con las variables no sensibles del esquema IBM Telco.
- `predicciones`: entrenamiento reproducible, inferencia, lotes CSV/JSON, resultados, riesgos, metricas y explicaciones.
- `dashboard`: resumen REST y panel web protegido por sesion.
- `ml/artifacts`: pipeline serializado con preprocesamiento y clasificador; evita inconsistencias entre entrenamiento e inferencia.

## Puesta en marcha

En PowerShell:

```powershell
cd E:\Tesis\churn-backend
.\venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python manage.py migrate
python manage.py entrenar_modelo --dataset E:\Tesis\WA_Fn-UseC_-Telco-Customer-Churn.csv
python manage.py createsuperuser
python manage.py runserver
```

El dashboard queda en `http://127.0.0.1:8000/`, la API en `http://127.0.0.1:8000/api/v1/`, el administrador en `http://127.0.0.1:8000/admin/` y la prueba de salud en `http://127.0.0.1:8000/health/`.

## Interfaz web

La interfaz usa Django Templates y sesiones. Incluye:

- resumen ejecutivo con indicadores y clientes prioritarios;
- prediccion individual desde cliente registrado o formulario manual;
- procesamiento CSV con errores identificados por fila;
- CRUD y filtros de clientes;
- historial, filtros, detalle explicable y exportacion CSV;
- metricas, matriz de confusion, importancia de variables y versiones;
- gestion de usuarios restringida al rol administrador;
- navegacion adaptable para escritorio y dispositivos moviles.

Rutas principales: `/predecir/`, `/lotes/`, `/clientes/`, `/resultados/`, `/modelo/` y `/usuarios/`.

Para PostgreSQL, copie `.env.example`, establezca `DB_ENGINE=postgresql` y complete las variables `DB_*`.

## Autenticacion API

Solicitar token:

```http
POST /api/v1/auth/login/
Content-Type: application/json

{"username":"analista","password":"su-clave"}
```

Enviar luego `Authorization: Token <token>`. El cierre de sesion revoca el token mediante `POST /api/v1/auth/logout/`.

## Endpoints principales

| Metodo | Ruta | Funcion |
|---|---|---|
| POST | `/api/v1/auth/login/` | Iniciar sesion y obtener token |
| GET/PATCH | `/api/v1/auth/perfil/` | Consultar o editar perfil |
| CRUD | `/api/v1/clientes/` | Administrar clientes |
| POST | `/api/v1/predicciones/individual/` | Generar una prediccion |
| POST | `/api/v1/predicciones/lote/` | Procesar CSV o lista JSON |
| GET | `/api/v1/predicciones/resultados/` | Historial y filtros |
| GET | `/api/v1/predicciones/resultados/{id}/explicacion/` | Factores individuales |
| GET | `/api/v1/predicciones/resultados/exportar/` | Exportar CSV |
| GET | `/api/v1/predicciones/modelo/activo/` | Metricas, matriz e importancia global |
| GET | `/api/v1/dashboard/resumen/` | Indicadores del dashboard |

Filtros disponibles en resultados: `?riesgo=alto`, `?abandono=true`, `?cliente=CODIGO` y `?lote=UUID`.

## Ejemplo de prediccion

```json
{
  "customerID": "CLI-001",
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 5,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "No",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "Yes",
  "StreamingMovies": "Yes",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 95.5,
  "TotalCharges": 477.5
}
```

Tambien se puede predecir un cliente previamente registrado enviando solamente `{"cliente": 1}`. Para lotes, adjunte un CSV en el campo multipart `archivo` o envie `{"registros": [...]}`.

## Entrenamiento y reproducibilidad

`entrenar_modelo` convierte `TotalCharges`, mantiene una prueba estratificada independiente del 20 %, ajusta imputacion/codificacion/escalado solo con entrenamiento y compara `DummyClassifier`, regresion logistica balanceada y random forest balanceado bajo la misma particion (`random_state=42`). La seleccion prioriza recall y luego F1 con precision minima de 0.45.

Resultado actual del dataset incluido:

- accuracy: 0.7381
- precision: 0.5043
- recall: 0.7834
- F1-score: 0.6136
- ROC-AUC: 0.8413
- PR-AUC: 0.6326
- Capture@20: 0.4947
- Lift@20: 2.4803

La version, configuracion, comparacion de candidatos, metricas, matriz de confusion e importancias quedan tanto en el artefacto como en la base de datos.

## Pruebas

```powershell
python manage.py check
python manage.py test --verbosity 2
```

Las pruebas cubren acceso protegido, token y revocacion, cuentas inactivas, clientes, validacion, prediccion individual, lotes parciales, consulta, exportacion, modelo y dashboard.

La trazabilidad completa de los casos CP-00 a CP-18 del documento se encuentra en
[`docs/MATRIZ_PRUEBAS.md`](docs/MATRIZ_PRUEBAS.md).
Los registros individuales con resultados, evidencias, incidencias y observaciones estan en
[`docs/REGISTRO_EJECUCION_CP00_CP18.md`](docs/REGISTRO_EJECUCION_CP00_CP18.md).
