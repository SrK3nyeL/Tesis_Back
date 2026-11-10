# Matriz de pruebas del prototipo

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

## Ejecucion

```powershell
cd E:\Tesis\churn-backend
.\venv\Scripts\Activate.ps1
python manage.py test --verbosity 2
```

CP-14 es una comprobacion local de regresion con un umbral conservador. Para presentar resultados formales de capacidad o concurrencia se recomienda complementarla con una herramienta de carga y registrar hardware, numero de usuarios, percentiles p50/p95/p99 y tasa de errores.

Las fichas completas de ejecucion se encuentran en
[`REGISTRO_EJECUCION_CP00_CP18.md`](REGISTRO_EJECUCION_CP00_CP18.md).
