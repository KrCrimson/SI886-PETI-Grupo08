# 05_arquitectura/AR03_brechas.py
# Caso: EPS AGUAS DEL SUR S.A. — Empresa 08
# SI-886 Planeamiento Estratégico de TI · Semana 10

import pandas as pd

b = pd.DataFrame([
    # capa, elemento_actual, elemento_objetivo, tipo_brecha, esfuerzo, dependencias, origen
    # ── DATOS ──────────────────────────────────────────────────────────────────
    ("Datos",
     "Lectura sin fuente autoritativa; archivo de carga se borra",
     "Fuente autoritativa única en sistema comercial; archivo conservado con hash",
     "Nuevo + Migrar", "Alto", "—",
     "Incidente SUNASS (Sección G FICHA) · Principio dato único"),

    ("Datos",
     "Conexión/usuario con discrepancia catastro–facturación (3 100 registros)",
     "Maestro único en catastro del sistema comercial, conciliación automatizada",
     "Consolidar", "Medio", "—",
     "Sección 5 arquitectura-actual · Principio dato único"),

    ("Datos",
     "Reclamo en 4 fuentes (formulario, libro, comercial, SUNASS); plazos distintos",
     "Fuente autoritativa en sistema comercial; reporte a SUNASS generado automáticamente",
     "Consolidar", "Medio", "PT-01 Maestro de lecturas",
     "Riesgo H-3 FICHA · Obligación regulatoria SUNASS"),

    ("Datos",
     "Trabajador: 58 por servicios no figuran en el AIRHSP",
     "Registro completo en el AIRHSP como fuente autoritativa; integración con biométrico",
     "Consolidar", "Bajo", "—",
     "Sección 5 arquitectura-actual · Marco ANPD (datos personales)"),

    ("Datos",
     "Sin inventario de activos de TI ni de servicios digitales",
     "Inventario de activos y servicios digitales con responsable y revisión periódica",
     "Nuevo", "Bajo", "—",
     "Sección F FICHA · D.S. 029-2021-PCM gobierno digital"),

    ("Datos",
     "Sin registro de tratamiento de datos personales (conexión, reclamo, trabajador)",
     "Registro de actividades de tratamiento conforme a Ley 29733",
     "Nuevo", "Bajo", "—",
     "Sección F FICHA · ANPD obligación normativa"),

    # ── APLICACIÓN ─────────────────────────────────────────────────────────────
    ("Aplicación",
     "Integración micromedición→comercial por archivo plano sin trazabilidad",
     "API de carga con registro inmutable del lote (hash + timestamp)",
     "Reemplazar", "Alto", "—",
     "Incidente SUNASS (Sección G FICHA) · Principio integración por servicios"),

    ("Aplicación",
     "Integración comercial→SIAF manual (digitación de recaudación)",
     "Interfaz publicada comercial→SIAF; eliminación del paso manual",
     "Nuevo", "Medio", "API de carga micromedición",
     "Sección 4 arquitectura-actual · Principio integración por servicios"),

    ("Aplicación",
     "Atención de reclamos en formulario web + hoja de cálculo (sin soporte desde 2021)",
     "Módulo de reclamos integrado al sistema comercial con trazabilidad y SLA",
     "Reemplazar", "Medio", "Maestro de conexión/usuario",
     "Sección 2 arquitectura-actual · Riesgo H-3 FICHA · ITIL DSS02"),

    ("Aplicación",
     "Conciliación catastro–facturación en hoja de cálculo mensual (manual)",
     "Proceso automático diario integrado al sistema comercial",
     "Reemplazar", "Medio", "Maestro de conexión/usuario",
     "Sección 2 arquitectura-actual · Principio dato único"),

    ("Aplicación",
     "Indicadores para SUNASS en hoja de cálculo (elaboración manual)",
     "Tablero regulatorio generado sobre fuentes autoritativas del sistema comercial",
     "Nuevo", "Medio", "Maestro de lecturas; maestro reclamo",
     "Sección 2 arquitectura-actual · Obligación regulatoria SUNASS"),

    # ── TECNOLOGÍA ─────────────────────────────────────────────────────────────
    ("Tecnología",
     "Red industrial (SCADA) sin segmentación; unida a red administrativa desde 2023",
     "Red industrial en VLAN separada con firewall industrial; sin acceso cruzado",
     "Modificar", "Alto", "—",
     "Riesgo H-1 FICHA · Objetivo declarado TI · COBIT DSS05"),

    ("Tecnología",
     "Respaldos solo a disco local; restauración nunca probada",
     "Respaldo con copia inmutable offsite y prueba de restauración semestral documentada",
     "Modificar", "Medio", "—",
     "Sección F FICHA · COBIT DSS04"),

    # ── NEGOCIO ────────────────────────────────────────────────────────────────
    ("Negocio",
     "Comité de Gobierno Digital sin actas; Líder de GD no designado",
     "Comité con sesiones calendarizadas y actas; Líder de GD designado formalmente",
     "Nuevo", "Bajo", "—",
     "Sección B y E FICHA · R.M. 119-2018-PCM exigible"),

    ("Negocio",
     "Sin política de seguridad de la información ni gestión formal de incidentes",
     "Política aprobada; registro de incidentes clasificado con tiempos de respuesta",
     "Nuevo", "Bajo", "—",
     "Sección F FICHA · COBIT DSS02 · COBIT APO12"),

], columns=["capa", "actual", "objetivo", "tipo_brecha", "esfuerzo", "dependencias", "origen"])

b.to_csv("AR03_brechas.csv", index=False)
print("=== RESUMEN POR CAPA Y TIPO DE BRECHA ===")
print(b.groupby(["capa", "tipo_brecha"]).size().to_string())
print(f"\nBrechas totales: {len(b)}")
print(f"Esfuerzo alto:  {(b.esfuerzo == 'Alto').sum()} "
      f"| medio: {(b.esfuerzo == 'Medio').sum()} "
      f"| bajo:  {(b.esfuerzo == 'Bajo').sum()}")

# ── Paquetes de trabajo ────────────────────────────────────────────────────────
PAQUETES = {
    "PT-01 Gobierno del dato maestro (lecturas y conexión)": [
        "Lectura sin fuente autoritativa; archivo de carga se borra",
        "Conexión/usuario con discrepancia catastro–facturación (3 100 registros)",
    ],
    "PT-02 Trazabilidad del ciclo comercial": [
        "Integración micromedición→comercial por archivo plano sin trazabilidad",
        "Integración comercial→SIAF manual (digitación de recaudación)",
        "Conciliación catastro–facturación en hoja de cálculo mensual (manual)",
    ],
    "PT-03 Gestión de reclamos integrada": [
        "Reclamo en 4 fuentes (formulario, libro, comercial, SUNASS); plazos distintos",
        "Atención de reclamos en formulario web + hoja de cálculo (sin soporte desde 2021)",
    ],
    "PT-04 Segmentación de red industrial": [
        "Red industrial (SCADA) sin segmentación; unida a red administrativa desde 2023",
    ],
    "PT-05 Continuidad y respaldo": [
        "Respaldos solo a disco local; restauración nunca probada",
    ],
    "PT-06 Tablero regulatorio SUNASS": [
        "Indicadores para SUNASS en hoja de cálculo (elaboración manual)",
    ],
    "PT-07 Cumplimiento de datos personales": [
        "Sin registro de tratamiento de datos personales (conexión, reclamo, trabajador)",
        "Trabajador: 58 por servicios no figuran en el AIRHSP",
    ],
    "PT-08 Gobierno digital y seguridad": [
        "Comité de Gobierno Digital sin actas; Líder de GD no designado",
        "Sin política de seguridad de la información ni gestión formal de incidentes",
        "Sin inventario de activos de TI ni de servicios digitales",
    ],
}

print("\n=== PAQUETES DE TRABAJO (insumo del portafolio Sección 7) ===")
for p, items in PAQUETES.items():
    sub = b[b.actual.isin(items)]
    dep = ", ".join(sorted({d for d in sub.dependencias if d != "—"})) or "ninguna"
    esfuerzo_num = sub.esfuerzo.map({"Bajo": 1, "Medio": 2, "Alto": 3})
    print(f"\n{p}")
    print(f"   brechas: {len(sub)} | esfuerzo máx: {esfuerzo_num.max()} | dependencias externas: {dep}")

# ── Secuencia obligada ────────────────────────────────────────────────────────
print("\n=== SECUENCIA OBLIGADA POR DEPENDENCIAS ===")
print("  1. PT-01 Gobierno del dato maestro       (prerequisito de PT-02, PT-03 y PT-06)")
print("  2. PT-04 Segmentación de red industrial  (riesgo crítico; independiente)")
print("  3. PT-08 Gobierno digital y seguridad    (habilitador institucional; independiente)")
print("  4. PT-05 Continuidad y respaldo          (independiente; esfuerzo medio)")
print("  5. PT-02 Trazabilidad del ciclo comercial (depende de PT-01)")
print("  6. PT-03 Gestión de reclamos integrada   (depende de PT-01)")
print("  7. PT-07 Cumplimiento datos personales   (depende de PT-01)")
print("  8. PT-06 Tablero regulatorio SUNASS      (depende de PT-01, PT-02 y PT-03)")
print("\n==> Esta secuencia condiciona la hoja de ruta (Seccion 7.3).")
