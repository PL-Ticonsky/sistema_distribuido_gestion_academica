# Identificación de claves y consideraciones de distribución

## 8. Identificación de claves primarias y claves foráneas

### 8.1. Criterio de selección de claves primarias

Las claves primarias se definieron mediante una estrategia mixta.

Las tablas operativas, transaccionales o de personas utilizan identificadores `uuid`.

Las tablas de catálogo institucional estable utilizan identificadores de tipo `varchar`.

| Tipo de tabla | Tipo de clave | Justificación |
|---|---|---|
| Tablas operativas | uuid | Evita consecutivos globales, permite generación automática y no expone información institucional. |
| Catálogos institucionales | varchar | Permite usar códigos oficiales, pequeños, estables y entendibles dentro del contexto académico. |

## 8.2. Resumen de claves primarias

| Tabla | Clave primaria | Tipo de dato |
|---|---|---|
| usuario | id_usuario | uuid |
| estudiante | id_estudiante | uuid |
| profesor | id_profesor | uuid |
| administrativo | id_administrativo | uuid |
| facultad | id_facultad | varchar(10) |
| programa_academico | id_programa_academico | varchar(20) |
| periodo_academico | id_periodo_academico | varchar(10) |
| asignatura | cod_asignatura | varchar(20) |
| tarifa_matricula | id_tarifa_matricula | uuid |
| recibo | id_recibo | uuid |
| matricula | id_matricula | uuid |
| programa_asignatura | id_programa_asignatura | uuid |
| pre_requisitos | id_pre_requisito | uuid |
| grupo | id_grupo | uuid |
| inscripcion | id_inscripcion | uuid |
| homologacion | id_homologacion | uuid |
| decano | id_decano | uuid |
| coordinador | id_coordinador | uuid |
| auditoria | id_auditoria | uuid |

## 9. Consideraciones preliminares sobre distribución

La estrategia de distribución se desarrollará en una etapa posterior del proyecto.

Sin embargo, el modelo fue planteado de forma que permita distribuir la información por facultad o programa académico.

De manera preliminar, la distribución podría considerar:

- Fragmentación horizontal de estudiantes por facultad o programa.
- Fragmentación horizontal de grupos por facultad y periodo académico.
- Fragmentación horizontal de inscripciones a partir de los grupos.
- Centralización de usuarios, auditoría, periodos académicos, pagos y matrículas.
- Construcción de vistas institucionales para integrar datos entre facultades.

## 10. Conclusiones

El modelo propuesto permite representar los principales procesos académicos, administrativos y financieros de una universidad organizada por facultades.

La separación entre usuarios, roles, facultades, programas, asignaturas, grupos, inscripciones, pagos, matrículas y homologaciones permite mantener un diseño coherente y extensible.

El diseño relacional permite controlar reglas fundamentales como:

- La unicidad de documentos.
- La asignación de programas a facultades.
- La relación muchos a muchos entre programas y asignaturas.
- Los prerrequisitos.
- El control de cupos.
- Los estados de matrícula.
- Los pagos de matrícula.
- Los procesos de homologación.

La estrategia mixta de llaves primarias permite evitar identificadores autoincrementales en las tablas operativas, manteniendo códigos institucionales únicamente en catálogos estables.

Esta decisión favorece una futura implementación distribuida y reduce problemas asociados a consecutivos globales o claves primarias excesivamente descriptivas.
