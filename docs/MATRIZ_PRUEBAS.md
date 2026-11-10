# Matriz de pruebas del prototipo

Esta matriz relaciona los casos CP-00 a CP-18 definidos en el documento de tesis con su evidencia automatizada en Django.

| Caso | Cobertura implementada | Evidencia |
|---|---|---|
| CP-00 | Salud de API, conexion a base de datos y artefacto disponible | `test_cp00_disponibilidad_basica` |
| CP-01 | Credenciales validas, invalidas y cuenta inactiva | `usuarios.tests.AutenticacionTests` |
| CP-02 | Carga CSV con esquema Telco valido | `test_cp02_carga_csv_con_esquema_valido` |
| CP-03 | Prediccion valida; campos faltantes y tipos incompatibles | `predicciones.tests` y `test_cp03_tipo_incompatible_no_ejecuta_modelo` |
| CP-04 | CSV mixto, procesamiento parcial y error asociado a fila | `test_cp04_lote_csv_parcial_identifica_fila_invalida` |
| CP-05 | Consulta con clasificacion, probabilidad, riesgo y version | `test_cp05_consulta_presenta_resultado_completo` |
| CP-06 | Filtro exacto por nivel de riesgo | `test_cp06_filtro_devuelve_solo_clientes_del_riesgo_solicitado` |
| CP-07 | Metricas y matriz TP/TN/FP/FN vinculadas a la version | `test_cp07_metricas_y_matriz_corresponden_a_version` |
| CP-08 | Importancia global y explicacion individual trazable | `test_cp08_explicacion_individual_y_factores_globales` |
| CP-09 | Coherencia dashboard/API y presencia de indicadores visuales | `test_cp09_dashboard_coincide_con_datos_y_renderiza_indicadores` |
| CP-10 | CSV con columnas documentadas y respeto de filtros | `test_cp10_exportacion_respeta_filtro_y_columnas` |
| CP-11 | Revocacion del token y rechazo de recursos protegidos | `usuarios.tests.AutenticacionTests` |
| CP-12 | Particion estratificada, semilla, pipeline y exclusion de objetivo/ID | `test_cp12_preparacion_reproducible_registra_particion_y_pipeline` |
| CP-13 | Baseline, candidatos, KPIs, recall y falsos negativos | `test_cp13_evaluacion_independiente_con_baseline_y_kpis` |
| CP-14 | Tiempo medio de inferencia comparado con umbral de 0.50 s | `test_cp14_rendimiento_inferencia_bajo_umbral_declarado` |
| CP-15 | PII extra y credenciales ausentes de persistencia/respuesta/exportacion | `test_cp15_privacidad_no_expone_credenciales_ni_pii_extra` |
| CP-16 | Dependencias, entorno SQLite/PostgreSQL e instrucciones de arranque | `test_cp16_portabilidad_tiene_dependencias_y_configuracion_local` |
| CP-17 | Separacion modular y secciones minimas de documentacion | `test_cp17_mantenibilidad_y_documentacion_modular` |
| CP-18 | Igualdad de resultados antes y despues de recargar el artefacto | `test_cp18_misma_entrada_y_modelo_producen_resultado_consistente` |

## Ejecucion

```powershell
cd E:\Tesis\churn-backend
.\venv\Scripts\Activate.ps1
python manage.py test --verbosity 2
```

CP-14 es una comprobacion local de regresion con un umbral conservador. Para presentar resultados formales de capacidad o concurrencia se recomienda complementarla con una herramienta de carga y registrar hardware, numero de usuarios, percentiles p50/p95/p99 y tasa de errores.
