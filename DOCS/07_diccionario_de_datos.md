# Diccionario de datos preliminar

## 7. Diccionario de datos

El diccionario de datos describe los atributos principales del modelo relacional.

| Dato examinado | Tabla de origen | Tipo de dato | ¿Nulo? | ¿PK? | Descripción |
|---|---|---:|:---:|:---:|---|
| id_usuario | usuario | uuid | No | Sí | Identificador interno único del usuario. |
| nombre | usuario | varchar(50) | No | No | Nombre completo del usuario. |
| tipo_de_documento | usuario | enum | No | No | Tipo de documento del usuario. |
| numero_de_documento | usuario | varchar(10) | No | No | Número de documento del usuario. |
| correo | usuario | varchar(30) | No | No | Correo electrónico del usuario. |
| direccion | usuario | varchar(30) | Sí | No | Dirección de residencia o contacto del usuario. |
| hashed_password | usuario | varchar(255) | No | No | Hash seguro de la contraseña. |
| fecha_de_creacion | usuario | date | No | No | Fecha de creación del usuario en el sistema. |
| id_estudiante | estudiante | uuid | No | Sí | Identificador interno del estudiante. |
| id_usuario | estudiante | uuid | No | No | Referencia al usuario asociado al estudiante. |
| id_programa_academico | estudiante | varchar(20) | No | No | Programa académico al que pertenece el estudiante. |
| limite_matriculas | estudiante | int | No | No | Número máximo de matrículas permitidas. |
| estado_estudiante | estudiante | enum | No | No | Estado académico-administrativo del estudiante. |
| id_profesor | profesor | uuid | No | Sí | Identificador interno del profesor. |
| id_usuario | profesor | uuid | No | No | Referencia al usuario asociado al profesor. |
| id_facultad | profesor | varchar(10) | No | No | Facultad a la que pertenece el profesor. |
| categoria | profesor | enum | Sí | No | Categoría académica del profesor. |
| vinculacion | profesor | enum | Sí | No | Tipo de vinculación del profesor. |
| id_administrativo | administrativo | uuid | No | Sí | Identificador interno del administrativo. |
| id_usuario | administrativo | uuid | No | No | Referencia al usuario asociado al administrativo. |
| id_facultad | administrativo | varchar(10) | No | No | Facultad a la que se encuentra afiliado. |
| detalles | administrativo | varchar(255) | Sí | No | Descripción del cargo, área o funciones administrativas. |
| id_facultad | facultad | varchar(10) | No | Sí | Código institucional de la facultad. |
| ubicacion | facultad | varchar(80) | Sí | No | Ubicación física o sede de la facultad. |
| nombre_facultad | facultad | varchar(80) | No | No | Nombre oficial de la facultad. |
| correo_institucional | facultad | varchar(80) | Sí | No | Correo institucional de la facultad. |
| id_programa_academico | programa_academico | varchar(20) | No | Sí | Código institucional del programa académico. |
| id_facultad | programa_academico | varchar(10) | No | No | Facultad a la que pertenece el programa. |
| nombre_programa | programa_academico | varchar(80) | No | No | Nombre oficial del programa académico. |
| estado | programa_academico | enum | No | No | Estado del programa académico. |
| modalidad | programa_academico | enum | No | No | Modalidad de oferta del programa. |
| nivel_formacion | programa_academico | enum | No | No | Nivel académico del programa. |
| id_periodo_academico | periodo_academico | varchar(10) | No | Sí | Código del periodo académico. |
| fecha_inicio | periodo_academico | date | No | No | Fecha de inicio del periodo académico. |
| fecha_final | periodo_academico | date | No | No | Fecha de finalización del periodo académico. |
| estado | periodo_academico | enum | No | No | Estado del periodo académico. |
| id_tarifa_matricula | tarifa_matricula | uuid | No | Sí | Identificador interno de la tarifa. |
| id_programa_academico | tarifa_matricula | varchar(20) | No | No | Programa al que aplica la tarifa. |
| id_periodo_academico | tarifa_matricula | varchar(10) | No | No | Periodo al que aplica la tarifa. |
| valor_matricula | tarifa_matricula | numeric(12,2) | No | No | Valor base de matrícula del programa en el periodo. |
| fecha_limite_ordinaria | tarifa_matricula | date | No | No | Fecha límite de pago ordinario. |
| fecha_limite_extraordinaria | tarifa_matricula | date | No | No | Fecha límite de pago extraordinario. |
| estado | tarifa_matricula | enum | No | No | Estado de la tarifa. |
| id_recibo | recibo | uuid | No | Sí | Identificador interno del recibo. |
| id_estudiante | recibo | uuid | No | No | Estudiante al que pertenece el recibo. |
| id_tarifa_matricula | recibo | uuid | No | No | Tarifa asociada al recibo. |
| fecha_pago | recibo | date | Sí | No | Fecha en la que se realizó el pago. |
| valor_pagado | recibo | numeric(12,2) | Sí | No | Valor efectivamente pagado por el estudiante. |
| metodo_pago | recibo | enum | Sí | No | Medio utilizado para realizar el pago. |
| estado_pago | recibo | enum | No | No | Estado financiero del recibo. |
| extras | recibo | numeric(12,2) | Sí | No | Valor adicional aplicado al recibo. |
| id_matricula | matricula | uuid | No | Sí | Identificador interno de la matrícula. |
| id_recibo | matricula | uuid | No | No | Recibo que origina la matrícula. |
| estado_matricula | matricula | enum | No | No | Estado académico-administrativo de la matrícula. |
| cod_asignatura | asignatura | varchar(20) | No | Sí | Código institucional de la asignatura. |
| nombre_asignatura | asignatura | varchar(80) | No | No | Nombre oficial de la asignatura. |
| creditos | asignatura | int | No | No | Número de créditos académicos. |
| estado | asignatura | enum | No | No | Estado de la asignatura. |
| horas_teoria | asignatura | int | No | No | Número de horas teóricas. |
| horas_pract | asignatura | int | No | No | Número de horas prácticas. |
| homologable | asignatura | boolean | No | No | Indica si la asignatura puede ser homologada. |
| id_programa_asignatura | programa_asignatura | uuid | No | Sí | Identificador interno de la relación programa-asignatura. |
| id_programa_academico | programa_asignatura | varchar(20) | No | No | Programa académico asociado. |
| cod_asignatura | programa_asignatura | varchar(20) | No | No | Asignatura asociada. |
| semestre_sugerido | programa_asignatura | int | No | No | Semestre sugerido dentro del programa. |
| tipo_asignatura | programa_asignatura | enum | No | No | Tipo de asignatura dentro del programa. |
| estado | programa_asignatura | enum | No | No | Estado de la asignatura dentro del programa. |
| id_pre_requisito | pre_requisitos | uuid | No | Sí | Identificador interno del prerrequisito. |
| id_programa_academico | pre_requisitos | varchar(20) | No | No | Programa académico asociado al prerrequisito. |
| id_programa_asignatura | pre_requisitos | uuid | No | No | Asignatura que exige el prerrequisito. |
| id_programa_asignatura_requisito | pre_requisitos | uuid | No | No | Asignatura que debe aprobarse previamente. |
| id_grupo | grupo | uuid | No | Sí | Identificador interno del grupo. |
| id_programa_asignatura | grupo | uuid | No | No | Asignatura del programa que se oferta. |
| id_periodo_academico | grupo | varchar(10) | No | No | Periodo en el que se oferta el grupo. |
| id_docente | grupo | uuid | Sí | No | Profesor asignado al grupo. |
| codigo_grupo | grupo | varchar(20) | No | No | Código visible institucional del grupo. |
| cupo_maximo | grupo | int | No | No | Cupo máximo autorizado para el grupo. |
| estado_grupo | grupo | enum | No | No | Estado del grupo. |
| id_inscripcion | inscripcion | uuid | No | Sí | Identificador interno de la inscripción. |
| id_grupo | inscripcion | uuid | No | No | Grupo inscrito por el estudiante. |
| id_estudiante | inscripcion | uuid | No | No | Estudiante inscrito en el grupo. |
| nota1 | inscripcion | numeric(3,2) | Sí | No | Primera nota parcial. |
| nota2 | inscripcion | numeric(3,2) | Sí | No | Segunda nota parcial. |
| nota3 | inscripcion | numeric(3,2) | Sí | No | Tercera nota parcial. |
| nota_final | inscripcion | numeric(3,2) | Sí | No | Nota final de la inscripción. |
| intento | inscripcion | int | No | No | Número de intento de la asignatura. |
| estado_inscripcion | inscripcion | enum | No | No | Estado académico de la inscripción. |
| id_homologacion | homologacion | uuid | No | Sí | Identificador interno de la homologación. |
| id_profesor_evaluador | homologacion | uuid | No | No | Profesor encargado de evaluar la solicitud. |
| id_estudiante | homologacion | uuid | No | No | Estudiante que solicita la homologación. |
| asignatura_origen | homologacion | varchar(100) | No | No | Asignatura cursada en otra institución. |
| institucion_origen | homologacion | varchar(100) | No | No | Institución de origen de la asignatura. |
| id_programa_asignatura | homologacion | uuid | No | No | Asignatura del programa que se desea homologar. |
| fecha_solicitud | homologacion | date | No | No | Fecha de solicitud de homologación. |
| estado_homologacion | homologacion | enum | No | No | Estado del proceso de homologación. |
| observacion | homologacion | varchar(255) | Sí | No | Comentarios del proceso de homologación. |
| fecha_respuesta | homologacion | date | Sí | No | Fecha de respuesta de la solicitud. |
| nota_obtenida | homologacion | numeric(3,2) | Sí | No | Nota reconocida en caso de aprobación. |
| id_decano | decano | uuid | No | Sí | Identificador interno de la asignación del decano. |
| id_profesor | decano | uuid | No | No | Profesor que ejerce como decano. |
| id_periodo_academico | decano | varchar(10) | No | No | Periodo de asignación del decano. |
| id_facultad | decano | varchar(10) | No | No | Facultad dirigida por el decano. |
| id_coordinador | coordinador | uuid | No | Sí | Identificador interno de la asignación del coordinador. |
| id_profesor | coordinador | uuid | No | No | Profesor que ejerce como coordinador. |
| id_periodo_academico | coordinador | varchar(10) | No | No | Periodo de asignación del coordinador. |
| id_programa_academico | coordinador | varchar(20) | No | No | Programa académico coordinado. |
| id_auditoria | auditoria | uuid | No | Sí | Identificador interno del registro de auditoría. |
| id_usuario | auditoria | uuid | No | No | Usuario que realizó la acción. |
| accion_realizada | auditoria | varchar(100) | No | No | Acción registrada por el sistema. |
| fecha_hora | auditoria | timestamp | No | No | Fecha y hora de la acción. |
| descripcion | auditoria | varchar(255) | Sí | No | Descripción adicional de la acción. |
