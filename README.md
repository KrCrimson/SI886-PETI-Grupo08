# SI886 · Plan Estratégico de Tecnologías de Información
## EPS AGUAS DEL SUR S.A. — Empresa 08 · Grupo 08

**Curso:** SI-886 Planeamiento Estratégico de TI  
**Universidad:** Universidad Privada de Tacna  
**Escuela:** Ingeniería de Sistemas  
**Docente:** Dr. Oscar Juan Jimenez Flores

> Repositorio privado. Contiene información restringida de arquitectura empresarial.

---

## Estructura del repositorio

```
.
├── 05_arquitectura/
│   ├── AR01_principios.md                  # 6 principios de arquitectura
│   ├── AR02_entidades.csv                  # Estructura de la información (8 entidades)
│   ├── AR03_brechas.py                     # Script de análisis de brechas
│   ├── AR03_brechas.csv                    # Salida: 15 brechas, 8 paquetes de trabajo
│   ├── arquitectura.archimate              # Modelo Archi — as-is, to-be y brechas
│   ├── generar_archimate.py                # Genera el modelo a partir de AR01-AR03
│   ├── exportar_vistas.py                  # Exporta las vistas a PNG con Archi
│   ├── validar_modelo.py                   # Paso F: validación del modelo
│   └── SECCION_5_arquitectura_empresarial.md  # Sección 5 del PETI
└── evidencias/
    └── S10/
        ├── graficos/                       # 13 vistas del modelo en PNG
        └── salidas/
            ├── AR03_brechas_salida.txt     # Salida del script de brechas
            └── validacion_modelo.txt       # Salida de la validación (Paso F)
```

## Semana 10 — Arquitectura empresarial

| Artefacto | Descripción |
|---|---|
| `AR01_principios.md` | Principios que gobiernan las decisiones del plan |
| `AR02_entidades.csv` | Entidades de datos, fuentes autoritativas y dueños |
| `AR03_brechas.csv` | 15 brechas entre as-is y to-be → 8 paquetes de trabajo |
| `arquitectura.archimate` | Modelo completo en ArchiMate 3.2: 122 elementos, 13 vistas |
| `SECCION_5_arquitectura_empresarial.md` | Sección 5 del PETI (5.1 a 5.4) |

## Etiquetas

| Etiqueta | Significado |
|---|---|
| `taller-10` | Commit entregado para calificación — Semana 10 |
| `v0.10` | Estado del PETI tras la Semana 10 |
