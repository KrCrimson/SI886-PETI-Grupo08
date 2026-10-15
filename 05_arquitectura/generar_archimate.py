# 05_arquitectura/generar_archimate.py
# Caso: EPS AGUAS DEL SUR S.A. — Empresa 08
# SI-886 Planeamiento Estratégico de TI · Semana 10 · Pasos B, C y E
#
# Genera arquitectura.archimate (ArchiMate 3.2, formato Archi) con:
#   - arquitectura ACTUAL (as-is): negocio, aplicación, datos y tecnología
#   - arquitectura OBJETIVO (to-be), derivada de AR01 (principios) y AR03 (brechas)
#   - 15 brechas, 8 paquetes de trabajo y su secuencia por dependencias
# Todo el contenido sale del inventario de la organización (arquitectura-actual.md,
# FICHA.md) y de AR01/AR02/AR03. El script es determinista: mismos datos, mismos IDs.
#
# Uso:  cd 05_arquitectura && python generar_archimate.py

import csv
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "arquitectura.archimate"

NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_A = "http://www.archimatetool.com/archimate"
ET.register_namespace("xsi", NS_XSI)
ET.register_namespace("archimate", NS_A)
XSI_TYPE = "{%s}type" % NS_XSI


def nid(seed):
    return "id-" + uuid.uuid5(uuid.NAMESPACE_URL, "si886-g08-eps-aguas-del-sur/" + seed).hex


# ── Capas según el tipo de elemento ───────────────────────────────────────────
CAPA_DE = {
    "BusinessActor": "Business", "BusinessRole": "Business", "BusinessProcess": "Business",
    "BusinessService": "Business", "BusinessObject": "Business",
    "ApplicationComponent": "Application", "ApplicationService": "Application",
    "ApplicationInterface": "Application", "DataObject": "Application",
    "Node": "Technology", "Device": "Technology", "CommunicationNetwork": "Technology",
    "TechnologyService": "Technology",
    "Principle": "Motivation",
    "WorkPackage": "Implementation", "Plateau": "Implementation", "Gap": "Implementation",
}

ELEM = {}   # clave -> dict
RELS = []   # lista de dict


def E(key, tipo, nombre, ambito, props=None, doc=""):
    """ambito: 'asis' (solo actual / retirado), 'tobe' (solo objetivo), 'both' (se conserva)."""
    assert key not in ELEM, key
    ELEM[key] = dict(key=key, tipo=tipo, nombre=nombre, ambito=ambito,
                     props=list((props or {}).items()), doc=doc, id=nid("e:" + key))
    return key


def R(tipo, src, tgt, ambito="both", nombre="", acceso=None, grp=""):
    assert src in ELEM and tgt in ELEM, (src, tgt)
    if tipo == "FlowRelationship" and src.startswith("c_") and tgt.startswith("c_") and not grp:
        grp = "integracion"   # las integraciones tienen sus propias vistas
    if tipo == "CompositionRelationship" and not grp:
        grp = "composicion"
    RELS.append(dict(tipo=tipo, src=src, tgt=tgt, ambito=ambito, nombre=nombre,
                     acceso=acceso, grp=grp,
                     id=nid(f"r:{tipo}:{src}:{tgt}:{nombre}:{ambito}")))


# ══════════════════════════════════════════════════════════════════════════════
# CAPA DE NEGOCIO  (FICHA D · arquitectura-actual §3)
# ══════════════════════════════════════════════════════════════════════════════
E("a_usuario", "BusinessActor", "Usuario del servicio (titular de conexión)", "both")
E("a_gcom", "BusinessActor", "Gerencia Comercial", "both")
E("a_atu", "BusinessActor", "Atención al Usuario", "both")
E("a_mic", "BusinessActor", "Jefe de Micromedición", "both")
E("a_est", "BusinessActor", "Profesional responsable de estadística", "both")
E("a_ti", "BusinessActor", "Jefe de TI (6 personas)", "both")
E("a_sunass", "BusinessActor", "SUNASS (regulador)", "both")
E("a_comite", "BusinessActor", "Comité de Gobierno Digital (sin actas; Líder no designado)", "asis",
  {"estado": "se modifica", "brecha": "B14"})
E("a_comite2", "BusinessActor", "Comité de Gobierno Digital (con actas calendarizadas)", "tobe",
  {"estado": "nuevo", "origen": "Sección B y E FICHA · R.M. 119-2018-PCM", "principio": "P5", "brecha": "B14"})
E("a_lider2", "BusinessActor", "Líder de Gobierno Digital (designado)", "tobe",
  {"estado": "nuevo", "origen": "R.M. 119-2018-PCM exigible", "principio": "P5", "brecha": "B14"})
E("r_lector", "BusinessRole", "Lector de medidores", "both")

NIVEL = "nivel_soporte"
E("p1", "BusinessProcess", "P1 Catastro comercial de usuarios", "both", {NIVEL: "Parcial"},
  "Soportado por el sistema comercial. Parcial: 3 100 conexiones con categoría tarifaria distinta entre catastro y facturación.")
E("p2", "BusinessProcess", "P2 Lectura de medidores y facturación", "both", {NIVEL: "Deficiente"},
  "Micromedición y lectura + sistema comercial. Deficiente: archivo de carga sin trazabilidad; 11 200 conexiones facturadas por estimación en tres ciclos.")
E("p3", "BusinessProcess", "P3 Cobranza y corte/reconexión", "both", {NIVEL: "Parcial"},
  "Sistema comercial. Parcial: la recaudación se digita a mano en el SIAF.")
E("p4", "BusinessProcess", "P4 Atención de reclamos comerciales", "both", {NIVEL: "Deficiente"},
  "Formulario web + hoja de cálculo, sin soporte desde 2021; plazos distintos entre libro y reporte a SUNASS.")
E("p5", "BusinessProcess", "P5 Operación de plantas y redes", "both", {NIVEL: "Bueno"},
  "SCADA con soporte vigente. El riesgo está en la red (capa de tecnología), no en el soporte aplicativo.")
E("p6", "BusinessProcess", "P6 Contrataciones y presupuesto público", "both", {NIVEL: "Bueno"},
  "SIAF y patrimonio (MEF), con soporte del MEF.")
E("p7", "BusinessProcess", "P7 Conciliación catastro–facturación (mensual)", "both", {NIVEL: "Deficiente"},
  "Proceso que corre sobre una hoja de cálculo sin soporte, mantenida por un área por su cuenta.")
E("p8", "BusinessProcess", "P8 Informe de indicadores para SUNASS", "both", {NIVEL: "Deficiente"},
  "Hoja de cálculo manual, sin versionado, calculada sobre fuentes con discrepancias.")
E("p9", "BusinessProcess", "P9 Gestión de incidentes y seguridad de la información", "both", {NIVEL: "Sin soporte"},
  "Registro de incidentes por correo, sin clasificación ni tiempos; no existe política de seguridad (FICHA F).")

E("bs_sum", "BusinessService", "Suministro de agua potable y alcantarillado", "both")
E("bs_fac", "BusinessService", "Facturación y cobranza del servicio", "both")
E("bs_rec", "BusinessService", "Atención de reclamos comerciales", "both")

E("bo_conx", "BusinessObject", "Conexión y usuario", "both")
E("bo_lect", "BusinessObject", "Lectura de medidor", "both")
E("bo_recl", "BusinessObject", "Reclamo comercial", "both")
E("bo_trab", "BusinessObject", "Trabajador / personal", "both")
E("bo_ind", "BusinessObject", "Indicador operativo para SUNASS", "both")
E("bo_pol", "BusinessObject", "Política de seguridad de la información (aprobada)", "tobe",
  {"estado": "nuevo", "origen": "Sección F FICHA · COBIT DSS02 · APO12", "principio": "P5", "brecha": "B15"})
E("bo_inc", "BusinessObject", "Registro de incidentes clasificado con tiempos de respuesta", "tobe",
  {"estado": "nuevo", "origen": "Sección F FICHA · COBIT DSS02", "principio": "P5", "brecha": "B15"})

# Relaciones de negocio
for a, p in [("a_gcom", "p1"), ("a_gcom", "p3"), ("a_gcom", "p7"), ("a_mic", "p2"), ("a_atu", "p4"),
             ("a_est", "p8"), ("a_ti", "p9")]:
    R("AssignmentRelationship", a, p)
R("AssignmentRelationship", "r_lector", "p2")
R("AssignmentRelationship", "a_comite", "p9", "asis")
R("AssignmentRelationship", "a_comite2", "p9", "tobe")
R("AssignmentRelationship", "a_lider2", "p9", "tobe")
for p1_, p2_ in [("p1", "p2"), ("p2", "p3")]:
    R("TriggeringRelationship", p1_, p2_)
for p, s in [("p2", "bs_fac"), ("p3", "bs_fac"), ("p4", "bs_rec"), ("p5", "bs_sum")]:
    R("RealizationRelationship", p, s)
R("ServingRelationship", "bs_fac", "a_usuario")
R("ServingRelationship", "bs_rec", "a_usuario")
R("ServingRelationship", "bs_sum", "a_usuario")
R("FlowRelationship", "p8", "a_sunass", nombre="Indicadores mensuales")
for p, o, acc in [("p1", "bo_conx", 3), ("p2", "bo_lect", 3), ("p2", "bo_conx", 1), ("p3", "bo_conx", 1),
                  ("p4", "bo_recl", 3), ("p7", "bo_conx", 1), ("p8", "bo_ind", 3)]:
    R("AccessRelationship", p, o, acceso=acc)
R("AccessRelationship", "p9", "bo_pol", "tobe", acceso=1)
R("AccessRelationship", "p9", "bo_inc", "tobe", acceso=3)

# ══════════════════════════════════════════════════════════════════════════════
# CAPA DE APLICACIÓN  (arquitectura-actual §2, §4 · AR03 columna «objetivo»)
# ══════════════════════════════════════════════════════════════════════════════
E("c_sc", "ApplicationComponent", "Sistema comercial (catastro, facturación y cobranza)", "both",
  {"soporte_vigente": "Sí", "desde": "2014"})
E("c_scada", "ApplicationComponent", "SCADA de plantas y reservorios", "both",
  {"soporte_vigente": "Sí", "desde": "2019"})
E("c_mm", "ApplicationComponent", "Micromedición y lectura (terminales portátiles)", "both",
  {"soporte_vigente": "Sí", "desde": "2018"})
E("c_siaf", "ApplicationComponent", "SIAF y patrimonio (MEF)", "both",
  {"soporte_vigente": "MEF", "desde": "2010"})
E("c_rec", "ApplicationComponent", "Atención de reclamos (formulario web)", "asis",
  {"soporte_vigente": "No", "desde": "2021", "estado": "retirado", "brecha": "B09"})
E("c_hcc", "ApplicationComponent", "Hoja de cálculo · Conciliación catastro–facturación (mensual)", "asis",
  {"tipo": "Hoja de cálculo", "soporte_vigente": "No", "estado": "retirado", "brecha": "B10"})
E("c_hcr", "ApplicationComponent", "Hoja de cálculo · Libro de reclamos", "asis",
  {"tipo": "Hoja de cálculo", "soporte_vigente": "No", "estado": "retirado", "brecha": "B09"})
E("c_hci", "ApplicationComponent", "Hoja de cálculo · Indicadores para SUNASS", "asis",
  {"tipo": "Hoja de cálculo", "soporte_vigente": "No", "estado": "retirado", "brecha": "B11"})
E("c_plan", "ApplicationComponent", "Sistema de planilla", "both")
E("c_air", "ApplicationComponent", "AIRHSP del MEF", "both")
E("c_bio", "ApplicationComponent", "Biométrico", "both")

E("c_api", "ApplicationComponent", "API de carga de lecturas con registro inmutable (hash + timestamp)", "tobe",
  {"estado": "nuevo", "reemplaza": "Archivo plano micromedición→comercial",
   "origen": "Incidente SUNASS (Sección G FICHA) · Principio 2 y 3", "principio": "P2, P3", "brecha": "B07"})
E("c_mrec", "ApplicationComponent", "Módulo de reclamos integrado al sistema comercial (SLA y trazabilidad)", "tobe",
  {"estado": "nuevo", "reemplaza": "Formulario web + libro de reclamos",
   "origen": "Riesgo H-3 FICHA · ITIL DSS02", "principio": "P1, P3, P6", "brecha": "B09"})
E("c_conc", "ApplicationComponent", "Módulo de conciliación automática diaria catastro–facturación", "tobe",
  {"estado": "nuevo", "reemplaza": "Hoja de conciliación mensual",
   "origen": "Sección 2 arquitectura-actual · Principio 1", "principio": "P1, P3", "brecha": "B10"})
E("c_tab", "ApplicationComponent", "Tablero regulatorio SUNASS sobre fuentes autoritativas", "tobe",
  {"estado": "nuevo", "reemplaza": "Hoja de indicadores para SUNASS",
   "origen": "Obligación regulatoria SUNASS · Principio 1", "principio": "P1, P6", "brecha": "B11"})
E("i_siaf", "ApplicationInterface", "Interfaz publicada comercial→SIAF", "tobe",
  {"estado": "nuevo", "reemplaza": "Digitación manual de la recaudación",
   "origen": "Sección 4 arquitectura-actual · Principio 3", "principio": "P3", "brecha": "B08"})

# Servicios de aplicación
E("s_cat", "ApplicationService", "Gestión de catastro de usuarios", "both")
E("s_lect", "ApplicationService", "Captura de lecturas en terminal portátil", "both")
E("s_fac", "ApplicationService", "Facturación y cobranza", "both")
E("s_carga2", "ApplicationService", "Carga de lecturas con registro inmutable", "tobe", {"estado": "nuevo"})
E("s_recf", "ApplicationService", "Recepción de reclamos por formulario web", "asis")
E("s_recl", "ApplicationService", "Libro de reclamos (hoja de cálculo)", "asis")
E("s_rec2", "ApplicationService", "Gestión de reclamos con SLA y trazabilidad", "tobe", {"estado": "nuevo"})
E("s_scada", "ApplicationService", "Supervisión y control de plantas y reservorios", "both")
E("s_siaf", "ApplicationService", "Registro presupuestal y de recaudación", "both")
E("s_conc", "ApplicationService", "Conciliación mensual manual", "asis")
E("s_conc2", "ApplicationService", "Conciliación automática diaria", "tobe", {"estado": "nuevo"})
E("s_ind", "ApplicationService", "Cálculo manual de indicadores", "asis")
E("s_tab", "ApplicationService", "Tablero regulatorio generado automáticamente", "tobe", {"estado": "nuevo"})

for comp, serv, amb in [("c_sc", "s_cat", "both"), ("c_sc", "s_fac", "both"), ("c_mm", "s_lect", "both"),
                        ("c_api", "s_carga2", "tobe"), ("c_rec", "s_recf", "asis"), ("c_hcr", "s_recl", "asis"),
                        ("c_mrec", "s_rec2", "tobe"), ("c_scada", "s_scada", "both"), ("c_siaf", "s_siaf", "both"),
                        ("c_hcc", "s_conc", "asis"), ("c_conc", "s_conc2", "tobe"), ("c_hci", "s_ind", "asis"),
                        ("c_tab", "s_tab", "tobe")]:
    R("RealizationRelationship", comp, serv, amb)
for serv, proc, amb in [("s_cat", "p1", "both"), ("s_lect", "p2", "both"), ("s_fac", "p2", "both"),
                        ("s_fac", "p3", "both"), ("s_carga2", "p2", "tobe"), ("s_recf", "p4", "asis"),
                        ("s_recl", "p4", "asis"), ("s_rec2", "p4", "tobe"), ("s_scada", "p5", "both"),
                        ("s_siaf", "p6", "both"), ("s_conc", "p7", "asis"), ("s_conc2", "p7", "tobe"),
                        ("s_ind", "p8", "asis"), ("s_tab", "p8", "tobe")]:
    R("ServingRelationship", serv, proc, amb)

# Integraciones (arquitectura-actual §4)
R("FlowRelationship", "c_mm", "c_sc", "asis", "Archivo de lecturas por lote (no se conserva)")
R("FlowRelationship", "c_sc", "c_siaf", "asis", "Digitación manual de la recaudación")
R("FlowRelationship", "c_rec", "c_hcr", "asis", "El formulario carga al libro")
R("FlowRelationship", "c_hcr", "c_sc", "asis", "Paso manual al comercial")
R("FlowRelationship", "c_mm", "c_api", "tobe", "Lectura + hash + timestamp")
R("FlowRelationship", "c_api", "c_sc", "tobe", "Carga por interfaz publicada")
R("CompositionRelationship", "c_sc", "i_siaf", "tobe")
R("ServingRelationship", "i_siaf", "c_siaf", "tobe", "Interfaz publicada", grp="iface")
R("CompositionRelationship", "c_sc", "c_mrec", "tobe")
R("CompositionRelationship", "c_sc", "c_conc", "tobe")
R("FlowRelationship", "c_sc", "c_tab", "tobe", "Fuente autoritativa")
R("FlowRelationship", "c_bio", "c_plan", "tobe", "Integración con biométrico")
R("FlowRelationship", "c_plan", "c_air", "tobe", "Conciliación con AIRHSP")

# ══════════════════════════════════════════════════════════════════════════════
# DATOS  (AR02_entidades.csv)
# ══════════════════════════════════════════════════════════════════════════════
FUENTE = "fuente_autoritativa"
E("d_conx", "DataObject", "Conexión y usuario", "asis",
  {FUENTE: "Catastro del comercial (declarada)", "dueno": "Gerencia Comercial", "registros": "86 000 · 86 000 · 84 100 · 4 800",
   "clasificacion": "Confidencial", "datos_personales": "Sí", "estado": "se modifica", "brecha": "B02"},
  "3 100 conexiones con categoría tarifaria distinta entre catastro y facturación.")
E("d_lect", "DataObject", "Lectura de medidor", "asis",
  {FUENTE: "Ninguna", "dueno": "Jefe de Micromedición", "registros": "1 030 000 al año",
   "clasificacion": "Interna", "datos_personales": "No", "estado": "se modifica", "brecha": "B01"},
  "11 200 conexiones facturadas por estimación en tres ciclos; no se puede auditar el lote.")
E("d_carga", "DataObject", "Archivo de carga de lecturas (transitorio; se borra)", "asis",
  {FUENTE: "Ninguna", "dueno": "Jefe de Micromedición", "estado": "retirado", "brecha": "B01"})
E("d_recl", "DataObject", "Reclamo comercial", "asis",
  {FUENTE: "Libro de cálculo (declarada, no validada)", "dueno": "Atención al Usuario", "registros": "4 800 al año",
   "clasificacion": "Confidencial", "datos_personales": "Sí", "estado": "se modifica", "brecha": "B03"})
E("d_trab", "DataObject", "Trabajador / personal", "asis",
  {FUENTE: "AIRHSP del MEF (por norma)", "dueno": "Recursos Humanos", "registros": "312 · 312 · 370",
   "clasificacion": "Restringida", "datos_personales": "Sí (sensibles)", "estado": "se modifica", "brecha": "B04"},
  "58 trabajadores por servicios no figuran en el AIRHSP; el biométrico tiene 58 registros sin contrapartida en planilla.")
E("d_act", "DataObject", "Activo de TI (sin inventario formal)", "asis",
  {FUENTE: "Ninguna", "dueno": "Jefe de TI (de facto)", "clasificacion": "Interna", "datos_personales": "No",
   "estado": "se modifica", "brecha": "B05"})
E("d_ctr", "DataObject", "Servicio digital / contrato TI", "asis",
  {FUENTE: "Ninguna", "dueno": "Jefe de TI (de facto)", "registros": "5 contratos; 2 vencidos",
   "clasificacion": "Interna", "datos_personales": "No", "estado": "se modifica", "brecha": "B05"})
E("d_nodo", "DataObject", "Nodo de red industrial (SCADA)", "asis",
  {FUENTE: "Ninguna", "dueno": "Jefe de TI", "clasificacion": "Restringida", "datos_personales": "No",
   "estado": "se modifica", "brecha": "B12"})
E("d_ind", "DataObject", "Indicador operativo para SUNASS", "asis",
  {FUENTE: "Ninguna (hoja manual)", "dueno": "Profesional responsable de estadística", "clasificacion": "Confidencial",
   "datos_personales": "No", "estado": "se modifica", "brecha": "B11"})

E("d_conx2", "DataObject", "Maestro único de conexión y usuario", "tobe",
  {FUENTE: "Catastro del sistema comercial (validada)", "dueno": "Gerencia Comercial", "clasificacion": "Confidencial",
   "datos_personales": "Sí", "estado": "nuevo", "origen": "Sección 5 arquitectura-actual · Principio 1", "principio": "P1", "brecha": "B02"})
E("d_lect2", "DataObject", "Lectura de medidor · fuente autoritativa en sistema comercial", "tobe",
  {FUENTE: "Sistema comercial", "dueno": "Jefe de Micromedición", "clasificacion": "Interna", "datos_personales": "No",
   "estado": "nuevo", "origen": "Incidente SUNASS (Sección G FICHA) · Principio 1", "principio": "P1, P2", "brecha": "B01"})
E("d_lote", "DataObject", "Registro de lote de carga (hash + timestamp, 5 años)", "tobe",
  {FUENTE: "Sistema comercial", "dueno": "Jefe de Micromedición", "clasificacion": "Interna", "datos_personales": "No",
   "estado": "nuevo", "origen": "Incidente SUNASS · Principio 2", "principio": "P2", "brecha": "B01"})
E("d_recl2", "DataObject", "Reclamo comercial · fuente autoritativa en sistema comercial", "tobe",
  {FUENTE: "Sistema comercial", "dueno": "Atención al Usuario", "clasificacion": "Confidencial", "datos_personales": "Sí",
   "estado": "nuevo", "origen": "Riesgo H-3 FICHA · SUNASS", "principio": "P1", "brecha": "B03"})
E("d_trab2", "DataObject", "Trabajador · registro completo en AIRHSP (integrado a biométrico)", "tobe",
  {FUENTE: "AIRHSP del MEF", "dueno": "Recursos Humanos", "clasificacion": "Restringida", "datos_personales": "Sí (sensibles)",
   "estado": "nuevo", "origen": "Sección 5 arquitectura-actual · ANPD", "principio": "P1, P5", "brecha": "B04"})
E("d_inv", "DataObject", "Inventario de activos y servicios digitales (con responsable)", "tobe",
  {FUENTE: "Inventario institucional", "dueno": "Jefe de TI", "clasificacion": "Interna", "datos_personales": "No",
   "estado": "nuevo", "origen": "Sección F FICHA · D.S. 029-2021-PCM", "principio": "P1, P5", "brecha": "B05"})
E("d_rat", "DataObject", "Registro de actividades de tratamiento de datos personales", "tobe",
  {FUENTE: "Registro institucional", "dueno": "Líder de Gobierno Digital", "clasificacion": "Confidencial",
   "datos_personales": "Sí", "estado": "nuevo", "origen": "Ley 29733 · ANPD", "principio": "P5", "brecha": "B06"})
E("d_ind2", "DataObject", "Indicadores regulatorios sobre fuentes autoritativas", "tobe",
  {FUENTE: "Sistema comercial", "dueno": "Profesional responsable de estadística", "clasificacion": "Confidencial",
   "datos_personales": "No", "estado": "nuevo", "origen": "Obligación regulatoria SUNASS", "principio": "P1", "brecha": "B11"})

for comp, d, acc, amb in [
    ("c_sc", "d_conx", 3, "asis"), ("c_sc", "d_lect", 3, "asis"), ("c_sc", "d_recl", 3, "asis"),
    ("c_mm", "d_lect", 3, "asis"), ("c_mm", "d_conx", 1, "asis"), ("c_mm", "d_carga", 0, "asis"),
    ("c_rec", "d_recl", 0, "asis"), ("c_hcr", "d_recl", 3, "asis"), ("c_hci", "d_ind", 3, "asis"),
    ("c_hcc", "d_conx", 1, "asis"), ("c_scada", "d_nodo", 1, "asis"),
    ("c_plan", "d_trab", 3, "asis"), ("c_air", "d_trab", 3, "asis"), ("c_bio", "d_trab", 3, "asis"),
    ("c_sc", "d_conx2", 3, "tobe"), ("c_sc", "d_lect2", 3, "tobe"), ("c_mm", "d_lect2", 1, "tobe"),
    ("c_api", "d_lote", 0, "tobe"), ("c_mrec", "d_recl2", 3, "tobe"), ("c_conc", "d_conx2", 3, "tobe"),
    ("c_tab", "d_ind2", 1, "tobe"), ("c_plan", "d_trab2", 3, "tobe"), ("c_air", "d_trab2", 3, "tobe"),
    ("c_bio", "d_trab2", 3, "tobe"),
]:
    R("AccessRelationship", comp, d, amb, acceso=acc)
for d, b, amb in [("d_conx", "bo_conx", "asis"), ("d_lect", "bo_lect", "asis"), ("d_recl", "bo_recl", "asis"),
                  ("d_trab", "bo_trab", "asis"), ("d_ind", "bo_ind", "asis"),
                  ("d_conx2", "bo_conx", "tobe"), ("d_lect2", "bo_lect", "tobe"), ("d_recl2", "bo_recl", "tobe"),
                  ("d_trab2", "bo_trab", "tobe"), ("d_ind2", "bo_ind", "tobe")]:
    R("RealizationRelationship", d, b, amb)

# ══════════════════════════════════════════════════════════════════════════════
# CAPA DE TECNOLOGÍA  (arquitectura-actual §6 · FICHA F)
# ══════════════════════════════════════════════════════════════════════════════
E("n_srv", "Node", "Servidor propio del sistema comercial", "both")
E("n_term", "Device", "Terminales portátiles de lectura", "both")
E("n_host", "Node", "Hosting propio (formulario de reclamos)", "asis", {"estado": "retirado"})
E("n_cli", "Node", "Cliente local del SIAF", "both")
E("n_est", "Device", "Estaciones de trabajo (140)", "both")
E("n_ind", "Node", "Equipos de la red industrial del SCADA (plantas y reservorios)", "both")
E("n_sw", "Device", "Switches compartidos red industrial / administrativa (desde 2023)", "asis",
  {"estado": "retirado", "riesgo": "H-1 FICHA · sin segmentación efectiva", "brecha": "B12"})
E("net_adm", "CommunicationNetwork", "Red administrativa", "both")
E("net_ind", "CommunicationNetwork", "Red industrial (unida a la administrativa)", "asis",
  {"estado": "se modifica", "brecha": "B12"})
E("net_ind2", "CommunicationNetwork", "Red industrial segmentada en VLAN propia", "tobe",
  {"estado": "nuevo", "origen": "Riesgo H-1 FICHA · COBIT DSS05", "principio": "P4", "brecha": "B12"})
E("net_rad", "CommunicationNetwork", "Radioenlace de plantas y reservorios", "both")
E("fw", "Device", "Firewall industrial", "tobe",
  {"estado": "nuevo", "origen": "Riesgo H-1 FICHA · COBIT DSS05", "principio": "P4", "brecha": "B12"})
E("ts_resp", "TechnologyService", "Respaldo a disco local (restauración nunca probada)", "asis",
  {"estado": "retirado", "brecha": "B13"})
E("ts_resp2", "TechnologyService", "Respaldo con copia inmutable offsite y prueba de restauración semestral", "tobe",
  {"estado": "nuevo", "origen": "Sección F FICHA · COBIT DSS04", "principio": "P4", "brecha": "B13"})
E("n_off", "Node", "Almacenamiento offsite inmutable", "tobe",
  {"estado": "nuevo", "origen": "COBIT DSS04", "principio": "P4", "brecha": "B13"})

for n, c, amb in [("n_srv", "c_sc", "both"), ("n_term", "c_mm", "both"), ("n_host", "c_rec", "asis"),
                  ("n_cli", "c_siaf", "both"), ("n_ind", "c_scada", "both"), ("n_est", "c_hcc", "asis"),
                  ("n_est", "c_hcr", "asis"), ("n_est", "c_hci", "asis"), ("n_srv", "c_api", "tobe"),
                  ("n_srv", "c_mrec", "tobe"), ("n_srv", "c_conc", "tobe"), ("n_srv", "c_tab", "tobe")]:
    R("ServingRelationship", n, c, amb)
for a, b, amb in [("n_srv", "net_adm", "both"), ("n_est", "net_adm", "both"), ("n_cli", "net_adm", "both"),
                  ("n_ind", "net_ind", "asis"), ("n_sw", "net_adm", "asis"), ("n_sw", "net_ind", "asis"),
                  ("net_rad", "net_ind", "asis"), ("n_ind", "net_ind2", "tobe"), ("fw", "net_ind2", "tobe"),
                  ("fw", "net_adm", "tobe"), ("net_rad", "net_ind2", "tobe")]:
    R("AssociationRelationship", a, b, amb)
R("RealizationRelationship", "n_srv", "ts_resp", "asis")
R("RealizationRelationship", "n_off", "ts_resp2", "tobe")
R("ServingRelationship", "ts_resp2", "n_srv", "tobe", "respalda")

# ══════════════════════════════════════════════════════════════════════════════
# MOTIVACIÓN: los 6 principios de AR01
# ══════════════════════════════════════════════════════════════════════════════
PRINCIPIOS = [
    ("pr1", "P1 Dato único con dueño designado"),
    ("pr2", "P2 Trazabilidad del ciclo comercial ante el regulador"),
    ("pr3", "P3 Integración por servicios publicados"),
    ("pr4", "P4 Seguridad desde el diseño con separación OT/IT"),
    ("pr5", "P5 Cumplimiento normativo no negociable"),
    ("pr6", "P6 Proporcionalidad y complejidad justificada"),
]
for k, n in PRINCIPIOS:
    E(k, "Principle", n, "both", {"fuente": "AR01_principios.md"})
for e in list(ELEM.values()):
    if e["ambito"] == "tobe" and any(p[0] == "principio" for p in e["props"]):
        for pr in dict(e["props"])["principio"].replace(" ", "").split(","):
            R("AssociationRelationship", "pr" + pr[1], e["key"], "tobe", grp="principio")

# ══════════════════════════════════════════════════════════════════════════════
# BRECHAS Y PAQUETES DE TRABAJO  (AR03_brechas.csv / AR03_brechas.py)
# ══════════════════════════════════════════════════════════════════════════════
CSV_BRECHAS = AQUI / "AR03_brechas.csv"
with open(CSV_BRECHAS, encoding="utf-8", newline="") as f:
    FILAS = list(csv.DictReader(f))
assert len(FILAS) == 15, "AR03_brechas.csv debe tener 15 brechas; ejecute primero AR03_brechas.py"

# idx: (título corto, claves en el modelo actual, claves en el modelo objetivo, PT)
BRECHAS = [
    ("Lectura sin fuente autoritativa", ["d_lect", "d_carga"], ["d_lect2", "d_lote"], "PT-01"),
    ("Discrepancia catastro–facturación", ["d_conx"], ["d_conx2"], "PT-01"),
    ("Reclamo en 4 fuentes", ["d_recl"], ["d_recl2"], "PT-03"),
    ("Trabajadores fuera del AIRHSP", ["d_trab"], ["d_trab2"], "PT-07"),
    ("Sin inventario de activos de TI", ["d_act", "d_ctr"], ["d_inv"], "PT-08"),
    ("Sin registro de datos personales", ["d_conx", "d_recl", "d_trab"], ["d_rat"], "PT-07"),
    ("Carga de lecturas por archivo plano", ["c_mm"], ["c_api"], "PT-02"),
    ("Comercial→SIAF manual", ["c_siaf"], ["i_siaf"], "PT-02"),
    ("Reclamos en formulario + hoja", ["c_rec", "c_hcr"], ["c_mrec"], "PT-03"),
    ("Conciliación manual en hoja", ["c_hcc"], ["c_conc"], "PT-02"),
    ("Indicadores SUNASS en hoja", ["c_hci"], ["c_tab"], "PT-06"),
    ("Red industrial sin segmentar", ["n_sw", "net_ind"], ["fw", "net_ind2"], "PT-04"),
    ("Respaldos sin restauración probada", ["ts_resp"], ["ts_resp2", "n_off"], "PT-05"),
    ("Comité sin actas; Líder no designado", ["a_comite"], ["a_comite2", "a_lider2"], "PT-08"),
    ("Sin política de seguridad ni incidentes", ["p9"], ["bo_pol", "bo_inc"], "PT-08"),
]
assert len(BRECHAS) == 15

PAQUETES = [
    ("PT-01", "PT-01 Gobierno del dato maestro (lecturas y conexión)"),
    ("PT-02", "PT-02 Trazabilidad del ciclo comercial"),
    ("PT-03", "PT-03 Gestión de reclamos integrada"),
    ("PT-04", "PT-04 Segmentación de red industrial"),
    ("PT-05", "PT-05 Continuidad y respaldo"),
    ("PT-06", "PT-06 Tablero regulatorio SUNASS"),
    ("PT-07", "PT-07 Cumplimiento de datos personales"),
    ("PT-08", "PT-08 Gobierno digital y seguridad"),
]
E("pl_a", "Plateau", "Arquitectura actual (as-is)", "both")
E("pl_t", "Plateau", "Arquitectura objetivo (to-be)", "both")
R("TriggeringRelationship", "pl_a", "pl_t", "both", grp="plateau")
for k, n in PAQUETES:
    E("wp" + k[-2:], "WorkPackage", n, "both")
for a, b in [("01", "02"), ("01", "03"), ("01", "06"), ("01", "07"), ("02", "06"), ("03", "06")]:
    R("TriggeringRelationship", "wp" + a, "wp" + b, "both", "depende", grp="wp-seq")

for i, (corto, asis, tobe, pt) in enumerate(BRECHAS, start=1):
    fila = FILAS[i - 1]
    gk = f"g{i:02d}"
    E(gk, "Gap", f"B{i:02d} {corto}", "both",
      {"capa": fila["capa"], "tipo_brecha": fila["tipo_brecha"], "esfuerzo": fila["esfuerzo"],
       "dependencias": fila["dependencias"], "origen": fila["origen"], "paquete": pt,
       "actual": fila["actual"], "objetivo": fila["objetivo"]},
      f"ACTUAL: {fila['actual']}\nOBJETIVO: {fila['objetivo']}")
    R("AssociationRelationship", gk, "wp" + pt[-2:], "both", grp="gap-wp")
    R("AssociationRelationship", gk, "pl_a", "both", grp="gap-plateau")
    R("AssociationRelationship", gk, "pl_t", "both", grp="gap-plateau")
    for a in asis:
        R("AssociationRelationship", a, gk, "both", "actual", grp="gap-elem")
    for t in tobe:
        R("AssociationRelationship", gk, t, "both", "objetivo", grp="gap-elem")


# ══════════════════════════════════════════════════════════════════════════════
# VISTAS
# ══════════════════════════════════════════════════════════════════════════════
W, H, GX, GY, X0, Y0 = 230, 62, 80, 26, 30, 70
COL_NIVEL = {"Bueno": "#B8E0A8", "Parcial": "#FFE08A", "Deficiente": "#F4A6A6", "Sin soporte": "#E57373"}
COL_FUENTE = {"ok": "#B8E0A8", "dudosa": "#FFE08A", "ninguna": "#F4A6A6"}
COL_CAPA = {"Datos": "#BBD8F5", "Aplicación": "#B5E5F9", "Tecnología": "#C9E7B7", "Negocio": "#FFFFB5"}
VISTAS = []


class Vista:
    def __init__(self, key, nombre, ambito, grps=("",)):
        self.key, self.nombre, self.ambito, self.grps = key, nombre, ambito, grps
        self.objs, self.notas = {}, []
        VISTAS.append(self)

    def add(self, ek, col, row, h=H, fill=None, label=None, w=W):
        e = ELEM[ek]
        assert self.ambito == "both" or e["ambito"] in ("both", self.ambito), \
            f"{ek} ({e['ambito']}) no va en vista {self.ambito}"
        self.objs[ek] = dict(id=nid(f"v:{self.key}:{ek}"), x=int(X0 + col * (W + GX)), y=int(Y0 + row * (H + GY)),
                             w=w, h=h, fill=fill, label=label)

    def nota(self, texto, x, y, w=420, h=70, fill="#FFFFFF"):
        self.notas.append(dict(id=nid(f"n:{self.key}:{len(self.notas)}"), x=x, y=y, w=w, h=h, texto=texto, fill=fill))


def lbl_proc(v, ek, col, row, nivel_objetivo=None):
    nivel = dict(ELEM[ek]["props"]).get(NIVEL, "")
    if nivel_objetivo:
        v.add(ek, col, row, fill=COL_NIVEL["Bueno"], label="${name}\n[objetivo: %s]" % nivel_objetivo)
    else:
        v.add(ek, col, row, fill=COL_NIVEL[nivel], label="${name}\n[soporte: ${property:%s}]" % NIVEL)


LEYENDA_NIVEL = ("Nivel de soporte del proceso:  VERDE = Bueno · AMARILLO = Parcial · ROJO CLARO = Deficiente · "
                 "ROJO = Sin soporte")


def fuente_color(ek):
    f = dict(ELEM[ek]["props"]).get(FUENTE, "Ninguna")
    if f.startswith("Ninguna"):
        return COL_FUENTE["ninguna"]
    if "no validada" in f:
        return COL_FUENTE["dudosa"]
    return COL_FUENTE["ok"]


LBL_DATO = "${name}\nFuente: ${property:%s}\nDueño: ${property:dueno}" % FUENTE

# 1 · AS-IS negocio
v = Vista("a_neg", "AS-IS 1 · Capa de negocio", "asis")
for i, k in enumerate(["a_usuario", "a_gcom", "a_atu", "a_mic", "a_est", "a_ti", "a_comite", "a_sunass", "r_lector"]):
    v.add(k, 0, i)
for i in range(9):
    lbl_proc(v, f"p{i+1}", 1, i)
for i, k in enumerate(["bs_sum", "bs_fac", "bs_rec"]):
    v.add(k, 2, 1 + i * 2)
for i, k in enumerate(["bo_conx", "bo_lect", "bo_recl", "bo_trab", "bo_ind"]):
    v.add(k, 3, i * 1.6 + 0.4)
v.nota(LEYENDA_NIVEL, X0, 6 + 9 * (H + GY), 900, 40)

# 2 · AS-IS cooperación proceso-aplicación
v = Vista("a_coop", "AS-IS 2 · Cooperación proceso-aplicación", "asis")
fila_proc = {"p1": 0, "p2": 1, "p3": 2, "p4": 3.5, "p5": 5, "p6": 6, "p7": 7, "p8": 8, "p9": 9}
for p, r in fila_proc.items():
    lbl_proc(v, p, 0, r)
for k, r in {"s_cat": 0, "s_lect": 1, "s_fac": 2, "s_recf": 3, "s_recl": 4, "s_scada": 5, "s_siaf": 6,
             "s_conc": 7, "s_ind": 8}.items():
    v.add(k, 1, r)
for k, r in {"c_sc": 0, "c_mm": 1, "c_rec": 3, "c_hcr": 4, "c_scada": 5, "c_siaf": 6, "c_hcc": 7, "c_hci": 8}.items():
    v.add(k, 2, r, fill="#FFD7A8" if "Hoja" in ELEM[k]["nombre"] else None)
v.nota("Las HOJAS DE CÁLCULO (naranja) son componentes de aplicación: sin ellas P4, P7 y P8 no operan.\n"
       "P9 no tiene sistema que lo soporte (incidentes por correo). El SCADA no se integra con nadie.",
       X0 + 2 * (W + GX), Y0 + 9 * (H + GY), 520, 70)
v.nota(LEYENDA_NIVEL, X0, Y0 + 10.2 * (H + GY), 900, 40)

# 3 · AS-IS estructura de la información
v = Vista("a_info", "AS-IS 3 · Estructura de la información", "asis")
for k, r in {"c_sc": 0, "c_hcc": 1.45, "c_mm": 2.9, "c_rec": 4.35, "c_hcr": 5.8, "c_plan": 7.25, "c_air": 8.7,
             "c_bio": 10.15, "c_scada": 11.6, "c_hci": 13.05}.items():
    v.add(k, 0, r * 0.9, fill="#FFD7A8" if "Hoja" in ELEM[k]["nombre"] else None)
for i, k in enumerate(["d_conx", "d_lect", "d_carga", "d_recl", "d_trab", "d_act", "d_ctr", "d_nodo", "d_ind"]):
    v.add(k, 1.4, i * 1.45 * 1.15, h=84, fill=fuente_color(k), label=LBL_DATO)
v.nota("Fuente autoritativa:  VERDE = declarada y válida · AMARILLO = declarada pero no validada · ROJO CLARO = ninguna.\n"
       "Entidades sin fuente autoritativa: 5 de 8 (lectura, activo de TI, contrato TI, nodo SCADA e\n"
       "indicador SUNASS); el archivo de carga es parte de «lectura». Sin dueño formal (solo «de facto»):\n"
       "activo de TI y contrato TI. Reclamo: fuente declarada pero no validada.",
       X0, Y0 + 15.4 * (H + GY), 900, 80)

# 4 · AS-IS infraestructura
v = Vista("a_inf", "AS-IS 4 · Infraestructura tecnológica", "asis")
for k, c in {"c_sc": 0, "c_mm": 1, "c_rec": 2, "c_siaf": 3, "c_scada": 4, "c_hcc": 5, "c_hcr": 6, "c_hci": 7}.items():
    v.add(k, c, 0, fill="#FFD7A8" if "Hoja" in ELEM[k]["nombre"] else None)
for k, c in {"n_srv": 0, "n_term": 1, "n_host": 2, "n_cli": 3, "n_ind": 4, "n_est": 6}.items():
    v.add(k, c, 2, h=76)
v.add("n_sw", 4.2, 7.7, h=84, fill="#F4A6A6")
v.add("net_adm", 3.0, 6)
v.add("net_ind", 5.5, 6)
v.add("net_rad", 7, 6)
v.add("ts_resp", 0, 6, h=76, fill="#F4A6A6")
v.nota("ROJO: switches compartidos entre la red industrial y la administrativa (desde 2023) y respaldo\n"
       "solo a disco local, sin restauración probada. Riesgo H-1 de la FICHA, no tratado.",
       X0, Y0 + 9.6 * (H + GY), 760, 60)

# 5 · TO-BE negocio
v = Vista("t_neg", "TO-BE 1 · Capa de negocio", "tobe")
for i, k in enumerate(["a_usuario", "a_gcom", "a_atu", "a_mic", "a_est", "a_ti", "a_comite2", "a_lider2", "a_sunass",
                       "r_lector"]):
    v.add(k, 0, i)
for i in range(9):
    lbl_proc(v, f"p{i+1}", 1, i, nivel_objetivo="Bueno")
for i, k in enumerate(["bs_sum", "bs_fac", "bs_rec"]):
    v.add(k, 2, 1 + i * 2)
for i, k in enumerate(["bo_conx", "bo_lect", "bo_recl", "bo_trab", "bo_ind", "bo_pol", "bo_inc"]):
    v.add(k, 3, i * 1.3 + 0.4, fill="#B8E0A8" if k in ("bo_pol", "bo_inc") else None)

# 6 · TO-BE cooperación proceso-aplicación
v = Vista("t_coop", "TO-BE 2 · Cooperación proceso-aplicación", "tobe", grps=("", "iface"))
fila_proc_t = {"p1": 0, "p2": 1.5, "p3": 3, "p4": 4.5, "p5": 6, "p6": 7, "p7": 8, "p8": 9, "p9": 10}
for p, r in fila_proc_t.items():
    lbl_proc(v, p, 0, r, nivel_objetivo="Bueno")
for k, r in {"s_cat": 0, "s_lect": 1, "s_carga2": 2, "s_fac": 3, "s_rec2": 4.5, "s_scada": 6, "s_siaf": 7,
             "s_conc2": 8, "s_tab": 9}.items():
    v.add(k, 1, r, fill="#B8E0A8" if ELEM[k]["ambito"] == "tobe" else None)
for k, r in {"c_sc": 1.2, "c_mm": 0, "c_api": 2, "c_mrec": 4.5, "c_scada": 6, "c_siaf": 7.5, "c_conc": 8,
             "c_tab": 9}.items():
    v.add(k, 2, r, fill="#B8E0A8" if ELEM[k]["ambito"] == "tobe" else None)
v.add("i_siaf", 3, 6.4, fill="#B8E0A8")
v.nota("VERDE = elemento nuevo en la arquitectura objetivo. Las tres hojas de cálculo y el formulario web\n"
       "se retiran. La integración micromedición→comercial pasa por una API con registro inmutable.",
       X0, Y0 + 11.3 * (H + GY), 760, 60)

# 7 · TO-BE estructura de la información
v = Vista("t_info", "TO-BE 3 · Estructura de la información", "tobe")
for k, r in {"c_mm": 0, "c_api": 1.4, "c_sc": 2.8, "c_conc": 4.2, "c_mrec": 5.6, "c_tab": 7, "c_plan": 8.4,
             "c_air": 9.8, "c_bio": 11.2}.items():
    v.add(k, 0, r, fill="#B8E0A8" if ELEM[k]["ambito"] == "tobe" else None)
for i, k in enumerate(["d_conx2", "d_lect2", "d_lote", "d_recl2", "d_trab2", "d_inv", "d_rat", "d_ind2"]):
    v.add(k, 1.4, i * 1.45, h=84, fill=COL_FUENTE["ok"], label=LBL_DATO)
v.nota("Cada entidad tiene fuente autoritativa y dueño designado por cargo (Principio 1):\n"
       "entidades sin fuente autoritativa: 0 de 8. Las entidades con datos personales quedan\n"
       "inscritas en el registro de actividades de tratamiento (Ley 29733).",
       X0, Y0 + 12 * (H + GY), 900, 70)

# 8 · TO-BE infraestructura
v = Vista("t_inf", "TO-BE 4 · Infraestructura tecnológica", "tobe")
for k, c in {"c_sc": 0, "c_mm": 1, "c_api": 2, "c_mrec": 3, "c_tab": 4, "c_siaf": 5, "c_scada": 6}.items():
    v.add(k, c, 0, fill="#B8E0A8" if ELEM[k]["ambito"] == "tobe" else None)
for k, c in {"n_srv": 1, "n_term": 2, "n_cli": 4, "n_ind": 6, "n_est": 3}.items():
    v.add(k, c, 2, h=76)
v.add("fw", 5.5, 4, h=76, fill="#B8E0A8")
v.add("net_adm", 2.5, 4)
v.add("net_ind2", 6.2, 6, fill="#B8E0A8")
v.add("net_rad", 4.2, 6)
v.add("n_off", 0, 4, h=76, fill="#B8E0A8")
v.add("ts_resp2", 0, 6, h=84, fill="#B8E0A8")
v.nota("VERDE = nuevo. La red industrial queda en VLAN propia detrás de un firewall industrial; el\n"
       "respaldo tiene copia inmutable offsite con prueba de restauración semestral.",
       X0, Y0 + 7.4 * (H + GY), 760, 60)

# 9 · AS-IS / TO-BE integraciones entre aplicaciones
v = Vista("a_integ", "AS-IS 5 · Integraciones entre aplicaciones", "asis", grps=("integracion",))
for k, c, r in [("c_mm", 0, 0), ("c_sc", 1.3, 0), ("c_siaf", 2.6, 0), ("c_rec", 0, 2.2), ("c_hcr", 1.3, 2.2),
                ("c_scada", 2.6, 2.2)]:
    v.add(k, c, r, fill="#FFD7A8" if "Hoja" in ELEM[k]["nombre"] else None)
v.nota("Cuatro integraciones hoy: dos por archivo plano sin trazabilidad (micromedición→comercial, formulario→libro),\n"
       "una manual (comercial→SIAF) y una inexistente: el SCADA no se integra con ningún sistema.",
       X0, Y0 + 4.2 * (H + GY), 900, 60)

v = Vista("t_integ", "TO-BE 6 · Integraciones entre aplicaciones", "tobe", grps=("integracion", "composicion", "iface"))
for k, c, r in [("c_mm", 0, 0), ("c_api", 1.3, 0), ("c_sc", 2.6, 0), ("c_tab", 3.9, 0), ("c_bio", 0, 4.4),
                ("c_plan", 1.3, 4.4), ("c_air", 2.6, 4.4), ("c_mrec", 1.3, 2.2), ("c_conc", 2.6, 2.2),
                ("i_siaf", 3.9, 2.2), ("c_siaf", 3.9, 4.4)]:
    v.add(k, c, r, fill="#B8E0A8" if ELEM[k]["ambito"] == "tobe" else None)
v.nota("Toda integración pasa por una interfaz publicada y con registro (Principio 3): la carga de lecturas\n"
       "conserva hash y marca de tiempo; el tablero lee de las fuentes autoritativas; planilla se concilia con AIRHSP.\n"
       "El sistema comercial compone los módulos de reclamos y conciliación y publica la interfaz hacia el SIAF.",
       X0, Y0 + 6.6 * (H + GY), 960, 70)

# 9 · Brechas: trazabilidad actual → brecha → objetivo
v = Vista("brechas", "BRECHAS 1 · Trazabilidad actual → brecha → objetivo", "both", grps=("gap-elem",))
usados_a, usados_t = [], []
for _, a_, t_, _ in BRECHAS:
    for k in a_:
        if k not in usados_a:
            usados_a.append(k)
    for k in t_:
        if k not in usados_t:
            usados_t.append(k)
for i, k in enumerate(usados_a):
    v.add(k, 0, i * 0.85, h=52, fill="#F4C7A8" if ELEM[k]["ambito"] == "asis" else None)
for i in range(15):
    v.add(f"g{i+1:02d}", 1.2, i * 1.1 + 0.2, h=52, fill=COL_CAPA[FILAS[i]["capa"]])
for i, k in enumerate(usados_t):
    v.add(k, 2.4, i * 1.05, h=52, fill="#B8E0A8" if ELEM[k]["ambito"] == "tobe" else None)
v.nota("Columna izquierda: elementos de la arquitectura ACTUAL · centro: brecha (color = capa) · derecha: "
       "elementos de la arquitectura OBJETIVO.", X0, 12, 1100, 40)

# 10 · Brechas: paquetes de trabajo y secuencia
v = Vista("paquetes", "BRECHAS 2 · Paquetes de trabajo y secuencia obligada", "both", grps=("gap-wp", "wp-seq"))
orden_wp = ["01", "04", "08", "05", "02", "03", "07", "06"]
nivel_wp = {"01": 1.5, "04": 1.5, "08": 1.5, "05": 1.5, "02": 3.0, "03": 3.0, "07": 3.0, "06": 4.5}
gaps_ord = sorted(range(1, 16), key=lambda g: orden_wp.index(BRECHAS[g - 1][3][-2:]))
for i, g in enumerate(gaps_ord):
    v.add(f"g{g:02d}", 0, i * 0.95, h=52, fill=COL_CAPA[FILAS[g - 1]["capa"]])
for n in orden_wp:
    filas_g = [i for i, g in enumerate(gaps_ord) if BRECHAS[g - 1][3][-2:] == n]
    v.add("wp" + n, nivel_wp[n], (sum(filas_g) / len(filas_g)) * 0.95 - 0.05, h=62)
v.nota("Secuencia obligada por dependencias (de izquierda a derecha):\n"
       "1º PT-01 (dato maestro), PT-04, PT-05 y PT-08, que no dependen de nada;\n"
       "2º PT-02, PT-03 y PT-07, que dependen de PT-01;\n"
       "3º PT-06 (tablero), que depende de PT-01, PT-02 y PT-03.",
       X0 + int(3.3 * (W + GX)), Y0, 470, 90)

# 11 · Principios → elementos objetivo
v = Vista("principios", "TO-BE 5 · Principios que gobiernan los cambios", "tobe", grps=("principio",))
for i, (k, _) in enumerate(PRINCIPIOS):
    v.add(k, 0, i * 3.3 + 0.5, h=70)
tobe_keys = [e["key"] for e in ELEM.values()
             if e["ambito"] == "tobe" and any(p[0] == "principio" for p in e["props"])]
for i, k in enumerate(tobe_keys):
    v.add(k, 1.4, i * 0.9, h=52, fill="#B8E0A8")


# ══════════════════════════════════════════════════════════════════════════════
# ESCRITURA DEL XML
# ══════════════════════════════════════════════════════════════════════════════
def carpeta(padre, nombre, tipo=None, seed=None):
    a = {"name": nombre, "id": nid("f:" + (seed or nombre))}
    if tipo:
        a["type"] = tipo
    return ET.SubElement(padre, "folder", a)


def construir():
    modelo = ET.Element("{%s}model" % NS_A, {"name": "PETI · EPS AGUAS DEL SUR S.A. — Arquitectura empresarial (Grupo 08)",
                                             "id": nid("modelo"), "version": "5.0.0"})
    carpeta(modelo, "Strategy", "strategy")
    negocio = carpeta(modelo, "Business", "business")
    app = carpeta(modelo, "Application", "application")
    tec = carpeta(modelo, "Technology & Physical", "technology")
    mot = carpeta(modelo, "Motivation", "motivation")
    imp = carpeta(modelo, "Implementation & Migration", "implementation_migration")
    carpeta(modelo, "Other", "other")
    rel = carpeta(modelo, "Relations", "relations")
    vis = carpeta(modelo, "Views", "diagrams")

    contenedor = {"Business": negocio, "Application": app, "Technology": tec, "Motivation": mot, "Implementation": imp}
    sub = {}
    for capa, padre in contenedor.items():
        if capa in ("Business", "Application", "Technology"):
            sub[(capa, "asis")] = carpeta(padre, "Actual (as-is) y elementos que se conservan", seed=f"{capa}-asis")
            sub[(capa, "tobe")] = carpeta(padre, "Objetivo (to-be) · elementos nuevos", seed=f"{capa}-tobe")

    for e in ELEM.values():
        capa = CAPA_DE[e["tipo"]]
        if (capa, "asis") in sub:
            padre = sub[(capa, "tobe" if e["ambito"] == "tobe" else "asis")]
        else:
            padre = contenedor[capa]
        x = ET.SubElement(padre, "element", {XSI_TYPE: "archimate:" + e["tipo"], "name": e["nombre"], "id": e["id"]})
        if e["doc"]:
            ET.SubElement(x, "documentation").text = e["doc"]
        for k, val in e["props"] + [("ambito", {"asis": "actual", "tobe": "objetivo", "both": "actual y objetivo"}[e["ambito"]])]:
            ET.SubElement(x, "property", {"key": k, "value": val})

    for r in RELS:
        a = {XSI_TYPE: "archimate:" + r["tipo"], "id": r["id"], "source": ELEM[r["src"]]["id"], "target": ELEM[r["tgt"]]["id"]}
        if r["nombre"]:
            a["name"] = r["nombre"]
        if r["acceso"] is not None and r["acceso"] != 0:
            a["accessType"] = str(r["acceso"])
        ET.SubElement(rel, "element", a)

    for v in VISTAS:
        d = ET.SubElement(vis, "element", {XSI_TYPE: "archimate:ArchimateDiagramModel", "name": v.nombre,
                                          "id": nid("vista:" + v.key)})
        conex = []
        for r in RELS:
            if r["src"] in v.objs and r["tgt"] in v.objs and r["ambito"] in ("both", v.ambito) and r["grp"] in v.grps:
                conex.append(r)
        entrantes = {}
        for r in conex:
            entrantes.setdefault(r["tgt"], []).append(nid(f"c:{v.key}:{r['id']}"))
        for ek, o in v.objs.items():
            a = {XSI_TYPE: "archimate:DiagramObject", "id": o["id"], "textAlignment": "2",
                 "archimateElement": ELEM[ek]["id"]}
            if o["fill"]:
                a["fillColor"] = o["fill"]
            if ek in entrantes:
                a["targetConnections"] = " ".join(entrantes[ek])
            c = ET.SubElement(d, "child", a)
            ET.SubElement(c, "bounds", {"x": str(o["x"]), "y": str(o["y"]), "width": str(o["w"]), "height": str(o["h"])})
            for r in conex:
                if r["src"] == ek:
                    ca = {XSI_TYPE: "archimate:Connection", "id": nid(f"c:{v.key}:{r['id']}"),
                          "source": o["id"], "target": v.objs[r["tgt"]]["id"], "archimateRelationship": r["id"]}
                    ET.SubElement(c, "sourceConnection", ca)
            if o["label"]:
                ET.SubElement(c, "feature", {"name": "labelExpression", "value": o["label"]})
        for n in v.notas:
            c = ET.SubElement(d, "child", {XSI_TYPE: "archimate:Note", "id": n["id"], "textAlignment": "1",
                                           "fillColor": n["fill"]})
            ET.SubElement(c, "bounds", {"x": str(n["x"]), "y": str(int(n["y"])), "width": str(n["w"]), "height": str(n["h"])})
            ET.SubElement(c, "content").text = n["texto"]

    ET.SubElement(modelo, "purpose").text = (
        "Modelo ArchiMate 3.2 de EPS AGUAS DEL SUR S.A. (Empresa 08, Grupo 08). Contiene la arquitectura actual "
        "(as-is) de las capas de negocio, aplicación, datos y tecnología, la arquitectura objetivo (to-be) derivada "
        "de los principios AR01 y las brechas AR03, y los paquetes de trabajo con su secuencia. "
        "SI-886 Planeamiento Estratégico de TI · Semana 10.")
    return modelo


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raiz = construir()
    ET.indent(raiz, space="  ")
    ET.ElementTree(raiz).write(SALIDA, encoding="utf-8", xml_declaration=True)
    n_asis = sum(e["ambito"] in ("asis", "both") for e in ELEM.values())
    n_tobe = sum(e["ambito"] in ("tobe", "both") for e in ELEM.values())
    print(f"Modelo escrito en {SALIDA.name}")
    print(f"  elementos: {len(ELEM)} (actual: {n_asis} · objetivo: {n_tobe})")
    print(f"  relaciones: {len(RELS)} · vistas: {len(VISTAS)}")
    for vv in VISTAS:
        print(f"    - {vv.nombre}: {len(vv.objs)} elementos")
