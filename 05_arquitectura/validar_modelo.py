# 05_arquitectura/validar_modelo.py
# Caso: EPS AGUAS DEL SUR S.A. — Empresa 08
# SI-886 Planeamiento Estratégico de TI · Semana 10 · Paso F — Validar y corregir
#
# Ejecuta las tres comprobaciones del taller sobre arquitectura.archimate y los CSV:
#   1. Cada elemento está en la capa (carpeta) que le corresponde.
#   2. Cada aplicación del modelo actual existe de verdad en la organización.
#   3. Cada brecha del análisis se puede señalar en los dos modelos (actual y objetivo).
# Más las cifras que exige la sección 5 y la lista de comprobación 3.2.
#
# Uso:  cd 05_arquitectura && python validar_modelo.py

import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NS = {"x": "http://www.w3.org/2001/XMLSchema-instance"}
XSI = "{http://www.w3.org/2001/XMLSchema-instance}type"

CARPETA_DE_TIPO = {
    "BusinessActor": "business", "BusinessRole": "business", "BusinessProcess": "business",
    "BusinessService": "business", "BusinessObject": "business",
    "ApplicationComponent": "application", "ApplicationService": "application",
    "ApplicationInterface": "application", "DataObject": "application",
    "Node": "technology", "Device": "technology", "CommunicationNetwork": "technology",
    "TechnologyService": "technology", "Principle": "motivation",
    "WorkPackage": "implementation_migration", "Plateau": "implementation_migration",
    "Gap": "implementation_migration",
}

# Inventario real de la organización (arquitectura-actual.md §2, FICHA.md §C y AR02):
# clave que debe aparecer en el nombre del componente -> dónde consta en los documentos.
INVENTARIO = {
    "Sistema comercial": "arquitectura-actual §2 · FICHA §C",
    "SCADA": "arquitectura-actual §2 · FICHA §C",
    "Micromedición": "arquitectura-actual §2 · FICHA §C",
    "SIAF": "arquitectura-actual §2 · FICHA §C",
    "Atención de reclamos": "arquitectura-actual §2 · FICHA §C",
    "Conciliación catastro–facturación": "arquitectura-actual §2 (hoja de cálculo)",
    "Libro de reclamos": "arquitectura-actual §2 (hoja de cálculo · Reclamos) · AR02",
    "Indicadores para SUNASS": "arquitectura-actual §2 (hoja de cálculo)",
    "Sistema de planilla": "arquitectura-actual §5 y AR02 (entidad Trabajador)",
    "AIRHSP": "arquitectura-actual §5 y AR02 (entidad Trabajador)",
    "Biométrico": "arquitectura-actual §5 y AR02 (entidad Trabajador)",
}

fallos = []


def comprobar(ok, texto):
    print(("  [OK]    " if ok else "  [FALLA] ") + texto)
    if not ok:
        fallos.append(texto)


def leer_modelo():
    raiz = ET.parse(AQUI / "arquitectura.archimate").getroot()
    elementos, relaciones = {}, []

    def recorrer(carpeta, tipo_carpeta):
        for hijo in carpeta:
            if hijo.tag == "folder":
                recorrer(hijo, tipo_carpeta)
            elif hijo.tag == "element":
                t = hijo.get(XSI).split(":")[1]
                props = {p.get("key"): p.get("value") for p in hijo.findall("property")}
                if t.endswith("Relationship"):
                    relaciones.append(dict(tipo=t, src=hijo.get("source"), tgt=hijo.get("target"),
                                           nombre=hijo.get("name", "")))
                elif t != "ArchimateDiagramModel":
                    elementos[hijo.get("id")] = dict(tipo=t, nombre=hijo.get("name"), props=props,
                                                    carpeta=tipo_carpeta)

    for carpeta in raiz.findall("folder"):
        recorrer(carpeta, carpeta.get("type"))
    vistas = [e.get("name") for f in raiz.findall("folder") if f.get("type") == "diagrams"
              for e in f.findall("element")]
    return elementos, relaciones, vistas


def main():
    elementos, relaciones, vistas = leer_modelo()
    por_tipo = lambda t: [e for e in elementos.values() if e["tipo"] == t]
    actual = lambda e: e["props"].get("ambito") in ("actual", "actual y objetivo")
    objetivo = lambda e: e["props"].get("ambito") in ("objetivo", "actual y objetivo")

    print("=" * 74)
    print("VALIDACIÓN DEL MODELO · arquitectura.archimate")
    print("=" * 74)
    print(f"Elementos: {len(elementos)} · Relaciones: {len(relaciones)} · Vistas: {len(vistas)}")

    # ── Comprobación 1: elementos en la capa que les corresponde ───────────────
    print("\n[1] Cada elemento está en la capa (carpeta de Archi) que le corresponde")
    mal = [e["nombre"] for e in elementos.values() if CARPETA_DE_TIPO[e["tipo"]] != e["carpeta"]]
    comprobar(not mal, f"{len(elementos)} elementos revisados; fuera de su capa: {len(mal)}" +
              (f" -> {mal[:3]}" if mal else ""))
    for capa in ("business", "application", "technology"):
        n_a = sum(1 for e in elementos.values() if e["carpeta"] == capa and actual(e))
        n_o = sum(1 for e in elementos.values() if e["carpeta"] == capa and objetivo(e))
        comprobar(n_a > 0 and n_o > 0, f"Capa {capa}: {n_a} elementos en el modelo actual · {n_o} en el objetivo")
    hojas = [e for e in por_tipo("ApplicationComponent") if e["props"].get("tipo") == "Hoja de cálculo" and actual(e)]
    comprobar(len(hojas) >= 1, f"Las hojas de cálculo están modeladas como componentes de aplicación: {len(hojas)}")

    # ── Comprobación 2: toda aplicación del modelo actual existe de verdad ─────
    print("\n[2] Toda aplicación del modelo actual existe en la organización")
    comps = [e for e in por_tipo("ApplicationComponent") if actual(e)]
    sin_respaldo = []
    for c in comps:
        clave = next((k for k in INVENTARIO if k in c["nombre"]), None)
        if clave is None:
            sin_respaldo.append(c["nombre"])
        else:
            print(f"        {c['nombre'][:62]:<62} <- {INVENTARIO[clave]}")
    comprobar(not sin_respaldo, f"{len(comps)} aplicaciones actuales; sin respaldo documental: {len(sin_respaldo)}" +
              (f" -> {sin_respaldo}" if sin_respaldo else ""))
    sin_origen = [e["nombre"] for e in elementos.values() if e["props"].get("ambito") == "objetivo"
                  and not e["props"].get("origen") and e["tipo"] not in ("ApplicationService",)]
    comprobar(not sin_origen, f"Cada elemento objetivo declara su origen (trazabilidad): sin origen: {len(sin_origen)}" +
              (f" -> {sin_origen[:3]}" if sin_origen else ""))

    # ── Comprobación 3: cada brecha se señala en los dos modelos ──────────────
    print("\n[3] Cada brecha de AR03_brechas.csv se señala en el modelo actual y en el objetivo")
    with open(AQUI / "AR03_brechas.csv", encoding="utf-8", newline="") as f:
        brechas = list(csv.DictReader(f))
    ids_gap = {id_: e for id_, e in elementos.items() if e["tipo"] == "Gap"}
    for i, b in enumerate(brechas, start=1):
        g_id = next((k for k, g in ids_gap.items() if g["props"].get("actual") == b["actual"]), None)
        if g_id is None:
            comprobar(False, f"B{i:02d}: no existe el Gap en el modelo")
            continue
        izq = [elementos[r["src"]] for r in relaciones if r["tgt"] == g_id and r["nombre"] == "actual"]
        der = [elementos[r["tgt"]] for r in relaciones if r["src"] == g_id and r["nombre"] == "objetivo"]
        ok = bool(izq) and bool(der) and all(actual(e) for e in izq) and all(objetivo(e) for e in der)
        comprobar(ok, f"B{i:02d} [{b['capa']:<10}] actual: {len(izq)} elemento(s) · objetivo: {len(der)} elemento(s) "
                      f"· {b['actual'][:44]}…")

    # ── Cifras para la sección 5 y la lista 3.2 ──────────────────────────────
    print("\n[4] Cifras para la sección 5 y la lista de comprobación 3.2")
    with open(AQUI / "AR02_entidades.csv", encoding="utf-8", newline="") as f:
        entidades = list(csv.DictReader(f))
    sin_fuente = [e["entidad"] for e in entidades if e["fuente_autoritativa"].startswith("Ninguna")]
    de_facto = [e["entidad"] for e in entidades if "de facto" in e["dueno_dato_cargo"]]
    sin_validar = [e["entidad"] for e in entidades if "no validada" in e["fuente_autoritativa"]]
    datos_pers = [e["entidad"] for e in entidades if e["datos_personales"].startswith("Sí")]
    comprobar(len(entidades) >= 6, f"#5  Entidades en AR02: {len(entidades)} (mínimo 6)")
    print(f"        Entidades sin fuente autoritativa: {len(sin_fuente)} de {len(entidades)} -> {', '.join(sin_fuente)}")
    print(f"        Fuente declarada pero no validada: {len(sin_validar)} -> {', '.join(sin_validar)}")
    print(f"        Dueño solo «de facto» (sin designación formal): {len(de_facto)} -> {', '.join(de_facto)}")
    print(f"        Entidades con datos personales: {len(datos_pers)} -> {', '.join(datos_pers)}")
    procesos = [e for e in por_tipo("BusinessProcess")]
    niv = {}
    for p in procesos:
        niv.setdefault(p["props"].get("nivel_soporte"), []).append(p["nombre"].split(" ")[0])
    malos = len(niv.get("Deficiente", [])) + len(niv.get("Sin soporte", []))
    print(f"        Procesos sin soporte o con soporte deficiente: {malos} de {len(procesos)}")
    for n, l in niv.items():
        print(f"          - {n}: {', '.join(l)}")
    comprobar(len(brechas) >= 10, f"#9  Brechas en AR03: {len(brechas)} (mínimo 10)")
    comprobar(len(por_tipo("WorkPackage")) >= 1, f"#10 Paquetes de trabajo en el modelo: {len(por_tipo('WorkPackage'))}")
    comprobar(len(vistas) >= 3, f"#12 Vistas en el modelo: {len(vistas)} (mínimo 3 a exportar en PNG)")

    print("\n" + "=" * 74)
    if fallos:
        print(f"RESULTADO: {len(fallos)} comprobación(es) fallaron. Corregir antes de cerrar la sesión.")
        sys.exit(1)
    print("RESULTADO: todas las comprobaciones pasaron.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
