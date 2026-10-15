# 05_arquitectura/exportar_vistas.py
# SI-886 · Semana 10 · Paso E — Exporta las vistas de arquitectura.archimate a PNG.
#
# Usa la línea de comandos de Archi (informe HTML) para que las imágenes sean las que
# Archi dibuja, no un render propio. Copia cada vista a evidencias/S10/graficos/.
#
# Uso:  cd 05_arquitectura && python exportar_vistas.py

import shutil
import subprocess
import sys
from pathlib import Path

import generar_archimate as g

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
DESTINO = RAIZ / "evidencias" / "S10" / "graficos"
TMP = AQUI / "_informe_html"
ARCHI = Path(r"C:\Program Files\Archi\Archi.exe")

NOMBRES = {
    "a_neg": "as-is_1_negocio",
    "a_coop": "vista_proceso_aplicacion",
    "a_info": "vista_estructura_informacion",
    "a_inf": "vista_infraestructura",
    "a_integ": "as-is_5_integraciones",
    "t_integ": "to-be_6_integraciones",
    "t_neg": "to-be_1_negocio",
    "t_coop": "to-be_2_proceso_aplicacion",
    "t_info": "to-be_3_estructura_informacion",
    "t_inf": "to-be_4_infraestructura",
    "brechas": "brechas_1_trazabilidad",
    "paquetes": "brechas_2_paquetes_trabajo",
    "principios": "to-be_5_principios",
}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if TMP.exists():
        shutil.rmtree(TMP)
    subprocess.run([str(ARCHI), "-application", "com.archimatetool.commandline.app", "-consoleLog", "-nosplash",
                    "--loadModel", str(AQUI / "arquitectura.archimate"), "--html.createReport", str(TMP)],
                   check=False, capture_output=True)
    DESTINO.mkdir(parents=True, exist_ok=True)
    copiadas = 0
    for v in g.VISTAS:
        id_vista = g.nid("vista:" + v.key)
        origen = next(TMP.rglob(f"{id_vista}.png"), None)
        if origen is None:
            print(f"  FALTA  {v.nombre}")
            continue
        destino = DESTINO / f"{NOMBRES[v.key]}.png"
        shutil.copyfile(origen, destino)
        copiadas += 1
        print(f"  OK     {destino.name}  <-  {v.nombre}")
    shutil.rmtree(TMP, ignore_errors=True)
    print(f"{copiadas} de {len(g.VISTAS)} vistas exportadas a {DESTINO}")
