# AR01_principios.md
# Caso: EPS AGUAS DEL SUR S.A. — Empresa 08
# SI-886 Planeamiento Estratégico de TI · Semana 10 · Sección 5.1

## Principios de Arquitectura — EPS AGUAS DEL SUR S.A.

---

### Principio 1 — Dato único con dueño designado

| Campo | Contenido |
|---|---|
| **Nombre** | Dato único con dueño designado |
| **Declaración** | Cada entidad de negocio tiene una única fuente autoritativa y un dueño de dato designado por cargo. Ningún proceso puede crear una segunda base de la misma entidad. |
| **Razón** | El diagnóstico detectó 5 entidades sin fuente autoritativa o con discrepancias activas: la entidad *Lectura* no tiene fuente autoritativa y su archivo de carga se borra; *Conexión/usuario* presenta 3 100 registros con categoría tarifaria distinta entre catastro y facturación; *Reclamo* vive en cuatro sistemas con plazos distintos. La facturación estimada a 11 200 conexiones y el procedimiento de SUNASS son consecuencia directa de este problema. |
| **Implicancias** | Ningún proyecto puede crear una segunda base de una entidad ya existente. Todo proyecto que consuma una entidad debe usar su fuente autoritativa declarada. El proyecto PT-01 (Gobierno del dato maestro) debe ejecutarse antes que PT-02, PT-03 y PT-06. |
| **Trazabilidad** | Hallazgo Sección 5 arquitectura-actual · Incidente G de la FICHA · Sección H riesgo H-2 |

---

### Principio 2 — Trazabilidad del ciclo comercial ante el regulador

| Campo | Contenido |
|---|---|
| **Nombre** | Trazabilidad del ciclo comercial ante el regulador |
| **Declaración** | Todo paso del ciclo lectura–facturación–cobranza debe quedar registrado de forma inmutable y auditable. Ningún archivo de carga puede eliminarse sin conservar su hash de verificación y su marca de tiempo. |
| **Razón** | El archivo de carga de lecturas se borra tras cada ciclo. Cuando fallaron tres ciclos consecutivos, no fue posible determinar qué lote falló. SUNASS abrió procedimiento por la facturación estimada a 11 200 conexiones. La organización no pudo defenderse porque no había evidencia. |
| **Implicancias** | Todo sistema que transfiera datos entre etapas del ciclo comercial debe usar una interfaz publicada con registro inmutable. Se prohíbe la integración por archivo plano sin trazabilidad. Los registros de carga deben conservarse un mínimo de cinco años. |
| **Trazabilidad** | Objetivo declarado de TI (FICHA sección A) · Incidente G de la FICHA · Riesgo H-2 |

---

### Principio 3 — Integración por servicios publicados

| Campo | Contenido |
|---|---|
| **Nombre** | Integración por servicios publicados |
| **Declaración** | Los sistemas se integran exclusivamente por interfaces publicadas y documentadas. Se prohíbe la integración por archivo plano sin trazabilidad, la consulta directa a tablas de otro sistema y el paso manual de datos entre sistemas. |
| **Razón** | Hoy existen cuatro integraciones: dos por archivo plano (micromedición→comercial, reclamos→hoja), una manual (comercial→SIAF) y una sin integración (SCADA→nadie). Las integraciones por archivo plano no conservan evidencia y las manuales introducen error. La integración inexistente del SCADA impide la supervisión operativa integrada. |
| **Implicancias** | Ningún proyecto puede implementar una integración por archivo plano sin trazabilidad ni por paso manual. Todo proyecto de integración debe incluir el diseño de la interfaz publicada. La eliminación del paso manual comercial→SIAF requiere coordinación con el MEF. |
| **Trazabilidad** | Sección 4 arquitectura-actual · Principio homólogo del curso (Teoría, Sección 2) |

---

### Principio 4 — Seguridad desde el diseño con separación de redes OT/IT

| Campo | Contenido |
|---|---|
| **Nombre** | Seguridad desde el diseño con separación de redes OT/IT |
| **Declaración** | La red industrial (OT) que soporta el SCADA de plantas y reservorios debe estar segregada físicamente o por VLAN de la red administrativa (IT). Ningún cambio de infraestructura puede unirlas sin aprobación documentada del comité y evaluación de riesgos. |
| **Razón** | Desde 2023 la red del SCADA comparte switches con la red administrativa. Esto expone la infraestructura de operación de agua potable a ataques desde la red de oficinas. Es el riesgo H-1 reconocido por la organización y no tratado. El diseño original las separaba; la ampliación de 2023 revirtió esa decisión sin evaluación de riesgos. |
| **Implicancias** | PT-04 (Segmentación de red industrial) es de ejecución inmediata y no requiere dependencias previas. Ningún proyecto de infraestructura puede modificar el límite OT/IT sin evaluación de riesgos documentada y aprobación del Jefe de TI y la Gerencia. |
| **Trazabilidad** | Riesgo H-1 FICHA · Objetivo declarado de TI (FICHA sección A) · COBIT 2019 DSS05 |

---

### Principio 5 — Cumplimiento normativo no negociable

| Campo | Contenido |
|---|---|
| **Nombre** | Cumplimiento normativo no negociable |
| **Declaración** | Las obligaciones exigibles por norma (gobierno digital, protección de datos personales, regulación sectorial SUNASS) tienen prioridad sobre cualquier iniciativa discrecional. Ningún proyecto puede postergarse si su ausencia genera incumplimiento verificable. |
| **Razón** | La organización tiene obligaciones vencidas: el Comité y el Líder de Gobierno Digital no han sido designados (R.M. 119-2018-PCM), no existe política de seguridad, no existe registro de tratamiento de datos personales (Ley 29733 y ANPD), y SUNASS ya abrió procedimiento por el incidente de facturación. El D.S. 029-2021-PCM exige arquitectura digital documentada. |
| **Implicancias** | PT-08 (Gobierno digital y seguridad) y PT-07 (Cumplimiento de datos personales) se ejecutan en paralelo con los proyectos técnicos, no después. Cada nuevo proyecto debe incluir en su diseño la evaluación de protección de datos si maneja información personal. |
| **Trazabilidad** | Secciones B, E y F de la FICHA · D.Leg. 1412 · D.S. 029-2021-PCM · Ley 29733 · R.M. 119-2018-PCM |

---

### Principio 6 — Proporcionalidad y complejidad justificada

| Campo | Contenido |
|---|---|
| **Nombre** | Proporcionalidad y complejidad justificada |
| **Declaración** | La complejidad de la solución técnica debe ser proporcional al problema que resuelve. Se prefiere la solución simple y mantenible sobre la solución elegante pero frágil. Toda adquisición o desarrollo debe justificar por qué no es suficiente una solución más sencilla. |
| **Razón** | EPS Aguas del Sur tiene 6 personas en TI, presupuesto de S/ 1 080 000 (1.46 % de la facturación) y varios contratos vencidos. Las soluciones complejas sin capacidad de mantenimiento interno generan dependencia de proveedor y nueva deuda arquitectónica. Varios problemas actuales (hoja de conciliación, hoja de indicadores) tienen raíz en soluciones adoptadas sin considerar su mantenibilidad. |
| **Implicancias** | Todo proyecto debe declarar quién lo mantendrá internamente y con qué capacidad. Se exige plan de salida en cada contrato de proveedor de plataforma. Los proyectos de analítica (PT-06) no se inician sin resolver primero las fuentes de datos (PT-01). |
| **Trazabilidad** | Sección B FICHA (capacidad de TI) · Principio homólogo del curso (Teoría, Sección 2) · Sección F FICHA (contratos vencidos) |
