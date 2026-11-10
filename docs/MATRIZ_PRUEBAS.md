# Registro de ejecucion de pruebas CP-00 a CP-18

<<<<<<< HEAD
Esta matriz usa literalmente los casos CP-00 a CP-18 definidos en el documento de tesis y agrega la evidencia automatizada y su estado actual.

| Codigo y nombre | Tipo | Precondicion y datos | Resultado esperado | Trazabilidad | Evidencia automatizada | Estado |
|---|---|---|---|---|---|---|
| CP-00 Disponibilidad basica | Humo | Prototipo desplegado; configuracion de prueba disponible | Los componentes esenciales responden y no se continua si alguno indispensable esta indisponible | RNF-0014; HU-02, HU-05 | `test_cp00_disponibilidad_basica` comprueba API, BD y artefacto | Aprobado |
| CP-01 Inicio de sesion | Funcional | Usuario activo; credenciales validas e invalidas | Las validas permiten acceder; las incorrectas son rechazadas | HU-01; RF-0001; CU-01 | `AutenticacionTests.test_login_y_logout_revocan_token` y `test_rechaza_credenciales_invalidas_y_cuenta_inactiva` | Aprobado |
| CP-02 Carga de datos | Funcional, integracion | Solicitud o CSV conforme al esquema esperado | El sistema acepta la carga e identifica su estructura | HU-02; RF-0002, RF-0003; CU-02 | `test_cp02_carga_csv_con_esquema_valido` | Aprobado |
| CP-03 Validacion y prediccion individual | Funcional, integracion | Modelo cargado; registro valido y registros con campos faltantes o tipos incompatibles | El valido devuelve clasificacion, probabilidad y riesgo; el invalido informa el error y no genera prediccion | HU-05; RF-0003 a RF-0007; CU-03; RNF-0009, RNF-0012 | `PrediccionAPITests.test_prediccion_individual_persiste_trazabilidad`, `test_entrada_incompleta_no_genera_prediccion` y `test_cp03_tipo_incompatible_no_ejecuta_modelo` | Aprobado |
| CP-04 Procesamiento por lotes | Funcional, integracion | CSV con varios clientes y al menos una fila invalida | Se procesan filas validas y se identifican los errores sin asignar resultados incorrectos | HU-06; RF-0002, RF-0003, RF-0008; CU-04 | `test_cp04_lote_csv_parcial_identifica_fila_invalida` | Aprobado |
| CP-05 Consulta de resultados | Funcional, integracion | Predicciones guardadas | Se presentan resultados con clasificacion, probabilidad y riesgo | HU-07; RF-0007, RF-0009; CU-05 | `test_cp05_consulta_presenta_resultado_completo` | Aprobado |
| CP-06 Consulta de clientes en riesgo | Funcional | Resultados con distintos niveles de riesgo | Se presentan solo los clientes correspondientes al filtro | HU-07; RF-0007, RF-0009, RF-0010; CU-06 | `test_cp06_filtro_devuelve_solo_clientes_del_riesgo_solicitado` | Aprobado |
| CP-07 Consulta de metricas y matriz de confusion | Funcional, evaluacion | Experimento y version identificados | Metricas y TP, TN, FP y FN corresponden a la version identificada | HU-04, HU-08; RF-0011, RF-0012; CU-07; RNF-0003, RNF-0012 | `test_cp07_metricas_y_matriz_corresponden_a_version` | Aprobado |
| CP-08 Factores y explicacion de prediccion | Funcional | Modelo con tecnica de interpretacion compatible | La explicacion se vincula a la prediccion y version; se publican factores globales | HU-09; RF-0013, RF-0014; CU-08, CU-09; RNF-0011 | `test_cp08_explicacion_individual_y_factores_globales` | Aprobado |
| CP-09 Dashboard | Funcional, sistema, inspeccion | API con predicciones y metricas | Los datos coinciden con la API y se presentan con textos, tablas y graficos comprensibles | HU-11; RF-0010, RF-0011, RF-0013, RF-0015; CU-10; RNF-0001 | `test_cp09_dashboard_coincide_con_datos_y_renderiza_indicadores` y `DashboardTests` | Aprobado |
| CP-10 Exportacion | Funcional | Resultados disponibles y usuario autorizado | Se genera CSV con columnas documentadas y resultados filtrados | HU-10; RF-0016; CU-11 | `test_cp10_exportacion_respeta_filtro_y_columnas` | Aprobado |
| CP-11 Cierre de sesion y acceso protegido | Funcional, seguridad | Sesion activa | La sesion/token se invalida y solicitudes posteriores son rechazadas | HU-01; RF-0001, RF-0017; CU-01, CU-12; RNF-0013 | `AutenticacionTests.test_login_y_logout_revocan_token` y `test_endpoint_protegido_requiere_autenticacion` | Aprobado |
| CP-12 Preparacion reproducible de datos | Integracion, inspeccion | Dataset identificado y configuracion registrada | Se conservan configuracion y particion; transformaciones dentro del pipeline y prueba separada | HU-03, HU-04; RF-0004; RNF-0002 a RNF-0005; RT-02, RT-03, RT-04 | `test_cp12_preparacion_reproducible_registra_particion_y_pipeline` | Aprobado |
| CP-13 Evaluacion independiente del modelo | Evaluacion | Candidatos, configuracion y prueba independiente | Se generan metricas; la seleccion considera recall, F1 y falsos negativos, no solo accuracy | HU-04, HU-08; RF-0011, RF-0012; RNF-0002, RNF-0003, RNF-0005, RNF-0012; RT-01, RT-05 a RT-10 | `test_cp13_evaluacion_independiente_con_baseline_y_kpis` | Aprobado |
| CP-14 Rendimiento | Rendimiento | Sistema disponible; 20 inferencias y lote de 25 registros | Promedio individual menor a 0.50 s y lote menor a 10 s en entorno local | RF-0005, RF-0008; RNF-0008 | `test_cp14_rendimiento_inferencia_bajo_umbral_declarado` | Aprobado localmente |
| CP-15 Privacidad de informacion | Inspeccion, funcional | Solicitudes, respuestas, persistencia y exportaciones de prueba | No se exponen ni persisten PII extra o credenciales | RF-0002, RF-0009, RF-0016; RNF-0010, RNF-0013 | `test_cp15_privacidad_no_expone_credenciales_ni_pii_extra` | Aprobado |
| CP-16 Portabilidad del prototipo | Sistema, inspeccion | Dependencias e instrucciones documentadas | Puede iniciarse en SQLite o PostgreSQL sin infraestructura propietaria | RNF-0007, RNF-0015 | `test_cp16_portabilidad_tiene_dependencias_y_configuracion_local` | Aprobado |
| CP-17 Revision de mantenibilidad y documentacion | Inspeccion | Codigo y documentacion disponibles | Los modulos se localizan y las etapas pueden comprenderse y reproducirse | RNF-0006, RNF-0015 | `test_cp17_mantenibilidad_y_documentacion_modular` | Aprobado |
| CP-18 Consistencia de resultados | Integracion, regresion | Mismo registro, modelo y pipeline | La probabilidad, clase, riesgo y explicacion coinciden despues de recargar el artefacto | RF-0005, RF-0006, RF-0009; RNF-0002, RNF-0012 | `test_cp18_misma_entrada_y_modelo_producen_resultado_consistente` | Aprobado |
=======
Las siguientes fichas registran la ejecucion realizada el 10/11/2026 sobre el backend Django REST v1.0. La suite completa ejecuto 29 pruebas automatizadas sin errores ni fallos.

## CP-00 Disponibilidad basica
>>>>>>> ac6ac5856679b90107688a8ea68ddad183b7b6ec

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-00 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite; entorno virtual local |
| **Datos de entrada** | Solicitudes GET a `/health/` y `/api/v1/predicciones/modelo/activo/`; base de datos migrada y artefacto configurado. |
| **Resultado esperado** | Los componentes esenciales responden y la prueba detecta la indisponibilidad de la API, base de datos o modelo. |
| **Resultado obtenido** | `/health/` respondio HTTP 200 con `database=ok`; el endpoint del modelo respondio HTTP 200 y el archivo `churn_pipeline.joblib` fue localizado. |
| **Estado** | Aprobado |
| **Evidencia** | Prueba automatica `test_cp00_disponibilidad_basica`; ejecucion de la suite Django. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | Constituye la prueba de humo previa a las operaciones de prediccion. |

## CP-01 Inicio de sesion

<<<<<<< HEAD
CP-14 es una comprobacion local de regresion con un umbral conservador. Para presentar resultados formales de capacidad o concurrencia se recomienda complementarla con una herramienta de carga y registrar hardware, numero de usuarios, percentiles p50/p95/p99 y tasa de errores.

Las fichas completas de ejecucion se encuentran en
[`REGISTRO_EJECUCION_CP00_CP18.md`](REGISTRO_EJECUCION_CP00_CP18.md).
=======
| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-01 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | No aplica. |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite; APIClient de Django REST Framework. |
| **Datos de entrada** | Usuario activo `analista`; una contrasena valida, una incorrecta y una cuenta marcada como inactiva. |
| **Resultado esperado** | Las credenciales validas permiten acceder; las incorrectas y las cuentas inactivas son rechazadas. |
| **Resultado obtenido** | El acceso valido devolvio HTTP 200 y un token; la contrasena incorrecta y la cuenta inactiva devolvieron HTTP 401. |
| **Estado** | Aprobado |
| **Evidencia** | `AutenticacionTests.test_login_y_logout_revocan_token` y `test_rechaza_credenciales_invalidas_y_cuenta_inactiva`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | El token emitido permite acceder unicamente mientras el usuario permanece activo y el token no ha sido revocado. |

## CP-02 Carga de datos

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-02 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite. |
| **Datos de entrada** | Archivo CSV UTF-8 con cabecera del esquema Telco y dos clientes validos. |
| **Resultado esperado** | El sistema acepta la carga e identifica correctamente la estructura del archivo. |
| **Resultado obtenido** | La API devolvio HTTP 201; registro `total_registros=2`, `registros_exitosos=2` y `registros_fallidos=0`. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp02_carga_csv_con_esquema_valido` y lote persistido en la base de datos de prueba. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | La misma operacion admite alternativamente una lista JSON en el campo `registros`. |

## CP-03 Validacion y prediccion individual

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-03 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada; umbral 0.50 |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; scikit-learn 1.9.1; SQLite. |
| **Datos de entrada** | Un cliente valido; un registro incompleto; un registro con `tenure="cinco"`. |
| **Resultado esperado** | El registro valido devuelve clase, probabilidad y riesgo; los invalidos informan el error y no generan prediccion. |
| **Resultado obtenido** | El valido devolvio HTTP 201, probabilidad entre 0 y 1, nivel de riesgo y version del modelo. Los invalidos devolvieron HTTP 400 y no fueron persistidos. |
| **Estado** | Aprobado |
| **Evidencia** | `test_prediccion_individual_persiste_trazabilidad`, `test_entrada_incompleta_no_genera_prediccion` y `test_cp03_tipo_incompatible_no_ejecuta_modelo`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | La validacion se ejecuta antes de invocar el pipeline, evitando resultados sobre datos incompatibles. |

## CP-04 Procesamiento por lotes

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-04 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite. |
| **Datos de entrada** | CSV con dos filas: una valida y otra con `MonthlyCharges="no-numerico"`. |
| **Resultado esperado** | Se procesan los registros validos y se identifican los errores por fila sin asignar resultados incorrectos. |
| **Resultado obtenido** | Se registro un resultado exitoso y un fallo; el error quedo asociado a la fila 3 del CSV y solo se persistio una prediccion. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp04_lote_csv_parcial_identifica_fila_invalida`; respuesta del lote con detalle de errores. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | El lote finaliza como `completado_errores`, conservando los resultados validos y la trazabilidad de los fallos. |

## CP-05 Consulta de resultados

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-05 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite. |
| **Datos de entrada** | Una prediccion individual previamente generada y almacenada. |
| **Resultado esperado** | La consulta presenta clasificacion, probabilidad, nivel de riesgo, version y fecha. |
| **Resultado obtenido** | El detalle respondio HTTP 200 e incluyo `abandono_predicho`, `probabilidad`, `nivel_riesgo`, `version_modelo` y `creado_en`. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp05_consulta_presenta_resultado_completo`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | La consulta mantiene la relacion entre el resultado, usuario creador y version del modelo. |

## CP-06 Consulta de clientes en riesgo

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-06 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite. |
| **Datos de entrada** | Dos predicciones: `ALTO-001` con riesgo alto y `BAJO-001` con riesgo bajo; filtro `riesgo=alto`. |
| **Resultado esperado** | Se presentan unicamente los clientes que corresponden al nivel solicitado. |
| **Resultado obtenido** | La consulta devolvio un solo registro y su referencia fue `ALTO-001`; el registro de riesgo bajo fue excluido. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp06_filtro_devuelve_solo_clientes_del_riesgo_solicitado`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | Los filtros pueden combinarse con abandono, lote y referencia de cliente. |

## CP-07 Consulta de metricas y matriz de confusion

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-07 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; scikit-learn 1.9.1; SQLite. |
| **Datos de entrada** | Artefacto entrenado y version activa registrada en base de datos. |
| **Resultado esperado** | Las metricas y los valores TP, TN, FP y FN corresponden al modelo y experimento identificados. |
| **Resultado obtenido** | Accuracy 0.738112, precision 0.504303, recall 0.783422, F1 0.613613, ROC-AUC 0.841298; TN=747, FP=288, FN=81 y TP=293. Los valores del endpoint coincidieron con el artefacto. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp07_metricas_y_matriz_corresponden_a_version`; metadatos del archivo Joblib y registro `VersionModelo`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | Tambien se registraron PR-AUC=0.632578, Capture@20=0.494652 y Lift@20=2.480303. |

## CP-08 Factores y explicacion de prediccion

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-08 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; scikit-learn 1.9.1; SQLite. |
| **Datos de entrada** | Prediccion individual generada con un cliente Telco valido y modelo lineal interpretable. |
| **Resultado esperado** | La explicacion se vincula a la prediccion y version; se muestran factores globales e individuales. |
| **Resultado obtenido** | El endpoint devolvio el ID correcto, la misma version, probabilidad y una lista no vacia de contribuciones con direccion `aumenta` o `reduce`. El endpoint del modelo devolvio importancia global. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp08_explicacion_individual_y_factores_globales`; respuestas de explicacion y modelo activo. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | Las contribuciones individuales se calculan a partir de variables transformadas y coeficientes de la regresion logistica. |

## CP-09 Dashboard

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-09 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; plantillas Django; SQLite. |
| **Datos de entrada** | Dos predicciones de prueba, una de riesgo alto y otra de riesgo bajo, mas las metricas del modelo activo. |
| **Resultado esperado** | Los indicadores coinciden con la API y se presentan mediante textos, tablas y elementos graficos comprensibles. |
| **Resultado obtenido** | La API informo dos predicciones, una alta y una baja. La vista autenticada respondio HTTP 200 y mostro las secciones `Niveles de riesgo` y `Clientes con riesgo alto`. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp09_dashboard_coincide_con_datos_y_renderiza_indicadores` y `dashboard.tests.DashboardTests`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | El dashboard utiliza los mismos datos persistidos que los endpoints REST, evitando indicadores duplicados o inconsistentes. |

## CP-10 Exportacion

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-10 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite. |
| **Datos de entrada** | Dos predicciones con riesgos alto y bajo; usuario autenticado; filtro `riesgo=alto`. |
| **Resultado esperado** | Se genera un CSV con las columnas documentadas y solo los resultados correspondientes al filtro. |
| **Resultado obtenido** | Se genero un CSV con `id`, `cliente`, `abandono_predicho`, `probabilidad`, `nivel_riesgo`, `modelo` y `fecha`; solo incluyo `EXPORT-ALTO`. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp10_exportacion_respeta_filtro_y_columnas`; contenido CSV inspeccionado por `csv.DictReader`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | La exportacion reutiliza los filtros de consulta para mantener coherencia con los resultados visualizados. |

## CP-11 Cierre de sesion y acceso protegido

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-11 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | No aplica. |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; autenticacion Token y Session. |
| **Datos de entrada** | Token valido de usuario activo; solicitud de cierre; nueva solicitud con el token revocado; solicitud anonima. |
| **Resultado esperado** | La sesion o token se invalida y las solicitudes sin acceso valido son rechazadas. |
| **Resultado obtenido** | El cierre devolvio HTTP 204 y elimino el token; la consulta posterior y el acceso anonimo a clientes devolvieron HTTP 401. |
| **Estado** | Aprobado |
| **Evidencia** | `test_login_y_logout_revocan_token` y `test_endpoint_protegido_requiere_autenticacion`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | La revocacion impide reutilizar credenciales de sesion finalizadas. |

## CP-12 Preparacion reproducible de datos

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-12 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Comando `entrenar_modelo` del backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; pandas 3.1.1; scikit-learn 1.9.1. |
| **Datos de entrada** | `WA_Fn-UseC_-Telco-Customer-Churn.csv`, 7,043 registros; `random_state=42`; division estratificada 80/20. |
| **Resultado esperado** | Se registra la configuracion; las transformaciones se ajustan con entrenamiento y la prueba permanece separada. |
| **Resultado obtenido** | Se registraron 5,634 filas de entrenamiento y 1,409 de prueba, `test_size=0.20`, estratificacion y semilla 42. El artefacto conserva `preprocess` y `model`; `customerID` y `Churn` no forman parte de las variables predictoras. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp12_preparacion_reproducible_registra_particion_y_pipeline`; configuracion almacenada dentro del artefacto Joblib. |
| **Incidencia** | Se detectaron valores no numericos/vacios en `TotalCharges` durante el desarrollo. |
| **Observaciones** | La incidencia se trata con conversion numerica e imputacion dentro del pipeline, ajustado unicamente con entrenamiento. |

## CP-13 Evaluacion independiente del modelo

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-13 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Comando `entrenar_modelo` del backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; scikit-learn 1.9.1. |
| **Datos de entrada** | Conjunto independiente de 1,409 registros; DummyClassifier, LogisticRegression balanceada y RandomForest balanceado; umbral 0.50. |
| **Resultado esperado** | Se comparan candidatos bajo condiciones equivalentes y la seleccion considera recall y falsos negativos, no solo accuracy. |
| **Resultado obtenido** | Se conservaron resultados de los tres candidatos. La regresion logistica fue seleccionada con recall 0.783422, precision 0.504303, F1 0.613613, ROC-AUC 0.841298 y tasa de falsos negativos 0.216578. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp13_evaluacion_independiente_con_baseline_y_kpis`; `candidate_results` y `selection_rule` del artefacto. |
| **Incidencia** | No se identificaron incidencias durante la ejecucion final. |
| **Observaciones** | Random Forest obtuvo mayor accuracy, pero no fue elegido porque el proyecto prioriza recall y reduccion de falsos negativos. |

## CP-14 Rendimiento

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-14 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite; ejecucion local sin concurrencia externa. |
| **Datos de entrada** | Calentamiento del modelo, 20 inferencias individuales iguales y un lote JSON de 25 clientes. Umbrales definidos antes de la prueba: promedio individual menor a 0.50 s y lote menor a 10 s. |
| **Resultado esperado** | Los tiempos se registran y permanecen dentro de los umbrales establecidos. |
| **Resultado obtenido** | Las 20 inferencias y las 25 filas del lote fueron procesadas correctamente; ambos limites temporales fueron satisfechos y el lote registro 25 exitosos. |
| **Estado** | Aprobado en entorno local |
| **Evidencia** | `test_cp14_rendimiento_inferencia_bajo_umbral_declarado`; medicion con `perf_counter`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | Esta prueba detecta regresiones locales. Una evaluacion de carga formal debe agregar concurrencia, p50, p95, p99 y tasa de errores mediante Locust o JMeter. |

## CP-15 Privacidad de informacion

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-15 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; SQLite. |
| **Datos de entrada** | Prediccion valida acompañada deliberadamente por `email`, `password` y `nombre_completo`; consulta de respuesta, persistencia y CSV. |
| **Resultado esperado** | La informacion personal innecesaria y las credenciales no se exponen ni persisten. |
| **Resultado obtenido** | Correo, contrasena y nombre adicional no aparecieron en la respuesta, `datos_entrada` ni exportacion CSV. Solo se conservaron variables requeridas por el modelo. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp15_privacidad_no_expone_credenciales_ni_pii_extra`; inspeccion automatica de respuesta, JSON persistido y CSV. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | El identificador de cliente se utiliza como referencia operativa; no se almacenan nombres, documentos, telefonos ni credenciales. |

## CP-16 Portabilidad del prototipo

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-16 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; entorno virtual; SQLite por defecto; configuracion opcional de PostgreSQL. |
| **Datos de entrada** | `requirements.txt`, `.env.example`, `README.md` y configuracion de base de datos. |
| **Resultado esperado** | El sistema puede ponerse en marcha con dependencias e instrucciones registradas, sin infraestructura propietaria. |
| **Resultado obtenido** | Se verificaron versiones de Django y scikit-learn, configuracion SQLite local, variables PostgreSQL e instrucciones de migracion, entrenamiento y servidor. El backend se ejecuto completamente con SQLite. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp16_portabilidad_tiene_dependencias_y_configuracion_local`; archivos de configuracion y documentacion. |
| **Incidencia** | No se identificaron incidencias en SQLite. |
| **Observaciones** | La conexion PostgreSQL queda disponible para despliegue final y debera validarse en el ambiente donde se publique. |

## CP-17 Revision de mantenibilidad y documentacion

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-17 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Repositorio local del backend; documentacion Markdown; Django 6.1.3. |
| **Datos de entrada** | Estructura de directorios y secciones de arquitectura, endpoints, entrenamiento y pruebas del README. |
| **Resultado esperado** | Los componentes principales se localizan y la documentacion permite entender y reproducir las etapas. |
| **Resultado obtenido** | Se localizaron los modulos `usuarios`, `clientes`, `predicciones`, `dashboard` y `config`; el README contiene las cuatro secciones requeridas y comandos reproducibles. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp17_mantenibilidad_y_documentacion_modular`, `README.md` y `docs/MATRIZ_PRUEBAS.md`. |
| **Incidencia** | No se identificaron incidencias. |
| **Observaciones** | La separacion modular permite sustituir el modelo o modificar presentacion, validacion y persistencia de manera independiente. |

## CP-18 Consistencia de resultados

| Campo | Registro |
|---|---|
| **Codigo de prueba** | CP-18 |
| **Fecha de ejecucion** | 10/11/2026 |
| **Version de codigo** | Backend Django REST v1.0 |
| **Version de modelo** | `20261110T181346Z` - LogisticRegression balanceada |
| **Entorno** | Windows; Python 3.14.3; Django 6.1.3; scikit-learn 1.9.1; Joblib 1.6.0. |
| **Datos de entrada** | Mismo registro Telco procesado con el mismo pipeline, modelo, umbral y configuracion `random_state=42`. |
| **Resultado esperado** | Una entrada procesada con la misma version debe producir resultados consistentes; el artefacto recargado debe conservar su comportamiento. |
| **Resultado obtenido** | Se genero una prediccion, se limpio la cache, se recargo `churn_pipeline.joblib` y se proceso nuevamente la misma entrada. Probabilidad, clasificacion, nivel de riesgo y explicacion fueron exactamente iguales. |
| **Estado** | Aprobado |
| **Evidencia** | `test_cp18_misma_entrada_y_modelo_producen_resultado_consistente`; comparaciones `assertEqual` antes y despues de la recarga Joblib. |
| **Incidencia** | No se identificaron incidencias durante la prueba. |
| **Observaciones** | Se comprobo que el artefacto conserva conjuntamente el preprocesamiento y el comportamiento del modelo requerido por la API REST. |
>>>>>>> ac6ac5856679b90107688a8ea68ddad183b7b6ec
