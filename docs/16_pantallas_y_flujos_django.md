# 16. Pantallas y flujos mínimos para Django

## 1. Propósito

Este documento define las pantallas mínimas del MVP del sistema de gestión académica universitaria antes de iniciar la implementación en Django.

La base de datos ya fue validada localmente en PostgreSQL mediante DBeaver. También existen scripts de DDL, inserts de catálogo, inserts operativos y consultas funcionales de validación. Por tanto, las pantallas propuestas se basan en las tablas y relaciones ya definidas.

El desarrollo se realizará primero en ambiente local con Django y PostgreSQL. La conexión a PostgreSQL en Azure se considera una etapa posterior y no hace parte de la implementación inmediata del MVP.

## 2. Criterios generales

Las pantallas deben respetar los roles funcionales definidos para el sistema:

```text
Estudiante
Profesor
Coordinador
Decano
Administrativo
Administrador funcional
```

Las operaciones de escritura deberán implementarse inicialmente desde Django, usando validaciones de aplicación y respetando las restricciones existentes en PostgreSQL.

Las consultas de `sql/04_consultas_validacion.sql` servirán como referencia para construir pantallas, reportes y dashboards sin crear vistas de base de datos en esta etapa.

## 3. Resumen de pantallas mínimas

| Pantalla | Roles principales | Operación | Prioridad |
|---|---|---|---|
| Login y logout | Todos | Escritura controlada | Alta |
| Dashboard principal por rol | Todos | Lectura | Alta |
| Perfil del usuario autenticado | Todos | Lectura / escritura limitada | Alta |
| Panel de estructura institucional | Administrativo, coordinador, decano, administrador funcional | Lectura / escritura controlada | Alta |
| Panel de asignaturas y plan de estudios | Coordinador, decano, administrativo, administrador funcional | Lectura / escritura controlada | Alta |
| Panel de grupos académicos | Profesor, coordinador, decano, administrativo | Lectura / escritura controlada | Alta |
| Inscripciones y notas del estudiante | Estudiante | Lectura | Alta |
| Gestión docente de notas | Profesor | Lectura / escritura controlada | Alta |
| Matrícula y recibos | Estudiante, administrativo | Lectura / escritura controlada | Alta |
| Homologaciones | Estudiante, profesor, coordinador, administrativo | Lectura / escritura controlada | Media |
| Dashboard de coordinador | Coordinador | Lectura | Alta |
| Dashboard de decano | Decano | Lectura | Media |
| Auditoría | Administrativo, administrador funcional | Lectura | Media |

## 4. Pantallas del MVP

### 4.1. Login y logout

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Login y logout |
| Objetivo | Permitir el ingreso y salida segura de usuarios autenticados. |
| Roles con acceso | Todos los usuarios registrados. |
| Tablas consumidas | `usuario` y tablas internas de autenticación de Django. |
| Datos principales a mostrar | Campo de correo, campo de contraseña, mensajes de error de autenticación y estado de sesión. |
| Acciones permitidas | Iniciar sesión, cerrar sesión y redirigir al dashboard correspondiente. |
| Tipo de operación | Escritura controlada sobre sesión; lectura de usuario para autenticación. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | Debe usar el sistema de autenticación de Django y el futuro modelo personalizado basado en `usuario`. El login debe realizarse por `correo`. Las contraseñas reales no deben cargarse por SQL operativo, sino gestionarse desde Django. Las credenciales demo para pruebas locales estarán documentadas en `docs/17_usuarios_y_credenciales_demo.md`. |

### 4.2. Dashboard principal por rol

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Dashboard principal por rol |
| Objetivo | Presentar una vista inicial adaptada al rol funcional del usuario autenticado. |
| Roles con acceso | Estudiante, profesor, coordinador, decano, administrativo y administrador funcional. |
| Tablas consumidas | `usuario`, `estudiante`, `profesor`, `administrativo`, `coordinador`, `decano`, `programa_academico`, `facultad`, `grupo`, `inscripcion`, `recibo`, `matricula`, `homologacion`, `auditoria`. |
| Datos principales a mostrar | Nombre del usuario, roles detectados, accesos directos, conteos básicos, alertas académicas o financieras según el rol. |
| Acciones permitidas | Navegar hacia módulos disponibles según permisos. |
| Tipo de operación | Lectura. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | La detección de rol debe basarse en las tablas de especialización. Si un usuario tiene más de un rol, la interfaz debe permitir seleccionar o mostrar accesos combinados. |

### 4.3. Perfil del usuario autenticado

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Perfil del usuario autenticado |
| Objetivo | Mostrar la información básica del usuario y sus roles funcionales dentro del sistema. |
| Roles con acceso | Todos los usuarios autenticados. |
| Tablas consumidas | `usuario`, `estudiante`, `profesor`, `administrativo`, `programa_academico`, `facultad`. |
| Datos principales a mostrar | Nombre, tipo de documento, número de documento, correo, dirección, estado activo, roles, programa académico si es estudiante y facultad si es profesor o administrativo. |
| Acciones permitidas | Consultar perfil y actualizar campos permitidos como dirección, si se habilita. |
| Tipo de operación | Lectura / escritura limitada. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | La edición de correo, documento, roles y estado activo debe quedar restringida a perfiles administrativos. |

### 4.4. Panel de estructura institucional

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Panel de estructura institucional |
| Objetivo | Administrar y consultar facultades, programas académicos y periodos académicos. |
| Roles con acceso | Administrativo, coordinador, decano y administrador funcional. |
| Tablas consumidas | `facultad`, `programa_academico`, `periodo_academico`. |
| Datos principales a mostrar | Facultades, ubicación, correo institucional, programas por facultad, estado del programa, modalidad, nivel de formación y periodos académicos. |
| Acciones permitidas | Crear, consultar y actualizar catálogos institucionales según permisos. |
| Tipo de operación | Lectura / escritura controlada. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | Debe respetar códigos institucionales existentes. Los cambios de catálogos deben ser controlados porque afectan estudiantes, tarifas, grupos y cargos académicos. |

### 4.5. Panel de asignaturas y plan de estudios

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Panel de asignaturas y plan de estudios |
| Objetivo | Consultar y administrar asignaturas, asociación con programas y prerrequisitos. |
| Roles con acceso | Coordinador, decano, administrativo y administrador funcional. |
| Tablas consumidas | `asignatura`, `programa_asignatura`, `pre_requisito`, `programa_academico`, `facultad`. |
| Datos principales a mostrar | Código de asignatura, nombre, créditos, horas teóricas, horas prácticas, homologable, programa, semestre sugerido, tipo de asignatura, estado y prerrequisitos. |
| Acciones permitidas | Crear y actualizar asignaturas, asociarlas a programas y registrar prerrequisitos. |
| Tipo de operación | Lectura / escritura controlada. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | Debe validar que una asignatura homologable tenga horas prácticas iguales a cero. La detección de ciclos de prerrequisitos no está resuelta en el DDL y debe manejarse inicialmente desde Django. |

### 4.6. Panel de grupos académicos

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Panel de grupos académicos |
| Objetivo | Consultar y administrar la oferta de grupos por periodo académico. |
| Roles con acceso | Profesor, coordinador, decano, administrativo y administrador funcional. |
| Tablas consumidas | `grupo`, `programa_asignatura`, `asignatura`, `programa_academico`, `periodo_academico`, `profesor`, `usuario`, `inscripcion`. |
| Datos principales a mostrar | Periodo, programa, asignatura, código de grupo, profesor asignado, cupo máximo, cantidad de inscritos, cupos disponibles y estado del grupo. |
| Acciones permitidas | Crear grupos, asignar profesor, actualizar cupo y estado según permisos. |
| Tipo de operación | Lectura / escritura controlada. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | El control de cupos requiere contar inscripciones y debe validarse desde Django. Un grupo puede existir sin profesor asignado. |

### 4.7. Pantalla de inscripciones y notas del estudiante

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Inscripciones y notas del estudiante |
| Objetivo | Permitir al estudiante consultar sus grupos inscritos, estados y notas. |
| Roles con acceso | Estudiante. |
| Tablas consumidas | `estudiante`, `usuario`, `inscripcion`, `grupo`, `programa_asignatura`, `asignatura`, `programa_academico`, `periodo_academico`. |
| Datos principales a mostrar | Programa, periodo, asignatura, grupo, estado de inscripción, notas parciales, nota final e intento. |
| Acciones permitidas | Consultar historial e inscripciones del periodo. En fases posteriores podría solicitar inscripción o cancelación si se habilita el flujo. |
| Tipo de operación | Lectura en MVP. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | Las reglas de matrícula activa, prerrequisitos aprobados y no duplicidad por asignatura-periodo deben validarse desde Django antes de permitir escritura. |

### 4.8. Pantalla docente para gestión de notas

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Gestión docente de notas |
| Objetivo | Permitir al profesor consultar sus grupos y registrar notas de estudiantes inscritos. |
| Roles con acceso | Profesor. |
| Tablas consumidas | `profesor`, `usuario`, `grupo`, `inscripcion`, `estudiante`, `programa_asignatura`, `asignatura`, `programa_academico`, `periodo_academico`. |
| Datos principales a mostrar | Grupos asignados, estudiantes inscritos, notas parciales, nota final, estado de inscripción e intento. |
| Acciones permitidas | Actualizar notas y estado de inscripción para grupos asignados. |
| Tipo de operación | Lectura / escritura controlada. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | Debe restringirse a grupos del profesor autenticado. Las notas deben permanecer entre 0 y 5, y las inscripciones aprobadas o reprobadas deben tener nota final. |

### 4.9. Pantalla de matrícula y recibos

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Matrícula y recibos |
| Objetivo | Consultar el estado financiero y académico-administrativo de matrícula del estudiante. |
| Roles con acceso | Estudiante, administrativo y administrador funcional. |
| Tablas consumidas | `recibo`, `matricula`, `tarifa_matricula`, `estudiante`, `usuario`, `programa_academico`, `periodo_academico`. |
| Datos principales a mostrar | Periodo, programa, valor de matrícula, estado de pago, valor pagado, método de pago, fecha de pago, extras y estado de matrícula. |
| Acciones permitidas | Consultar recibos y matrículas. El personal administrativo podrá registrar o actualizar estados financieros y académicos según permisos. |
| Tipo de operación | Lectura / escritura controlada. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | Si un recibo se marca como pagado, debe tener fecha de pago y valor pagado. La activación automática de matrícula se deja para lógica de Django o fase posterior. |

### 4.10. Pantalla de homologaciones

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Homologaciones |
| Objetivo | Gestionar solicitudes de homologación de asignaturas cursadas en otras instituciones. |
| Roles con acceso | Estudiante, profesor, coordinador, administrativo y administrador funcional. |
| Tablas consumidas | `homologacion`, `estudiante`, `usuario`, `profesor`, `programa_asignatura`, `asignatura`, `programa_academico`. |
| Datos principales a mostrar | Estudiante, asignatura de origen, institución de origen, asignatura homologada, profesor evaluador, estado, observación, fecha de solicitud, fecha de respuesta y nota obtenida. |
| Acciones permitidas | El estudiante puede consultar o solicitar. El profesor evaluador puede registrar respuesta, estado y nota. Coordinador o administrativo puede hacer seguimiento. |
| Tipo de operación | Lectura / escritura controlada. |
| Prioridad | Media. |
| Observaciones para implementación en Django | Las homologaciones aprobadas deben tener nota obtenida. La validación de que la asignatura sea homologable requiere consultar `asignatura` y debe implementarse desde Django. |

### 4.11. Dashboard de coordinador

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Dashboard de coordinador |
| Objetivo | Presentar información consolidada del programa académico bajo responsabilidad del coordinador. |
| Roles con acceso | Coordinador y administrador funcional. |
| Tablas consumidas | `coordinador`, `profesor`, `usuario`, `programa_academico`, `facultad`, `periodo_academico`, `estudiante`, `programa_asignatura`, `asignatura`, `grupo`, `inscripcion`, `homologacion`. |
| Datos principales a mostrar | Programa asignado, periodo, estudiantes del programa, asignaturas del plan, grupos ofertados, cupos, estados de inscripción, rendimiento académico y homologaciones del programa. |
| Acciones permitidas | Consultar indicadores y navegar a gestión de grupos, plan de estudios y homologaciones. |
| Tipo de operación | Lectura en MVP. |
| Prioridad | Alta. |
| Observaciones para implementación en Django | Debe filtrar la información por el programa asociado al coordinador en el periodo vigente. Las acciones de escritura se harán desde pantallas específicas. |

### 4.12. Dashboard de decano

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Dashboard de decano |
| Objetivo | Presentar información consolidada de una facultad y sus programas académicos. |
| Roles con acceso | Decano y administrador funcional. |
| Tablas consumidas | `decano`, `profesor`, `usuario`, `facultad`, `periodo_academico`, `programa_academico`, `estudiante`, `grupo`, `inscripcion`, `recibo`, `matricula`, `homologacion`. |
| Datos principales a mostrar | Facultad, periodo, programas, estudiantes por programa, profesores, grupos ofertados, cupos, matrículas, recibos y homologaciones. |
| Acciones permitidas | Consultar indicadores institucionales de la facultad y navegar a módulos relacionados. |
| Tipo de operación | Lectura en MVP. |
| Prioridad | Media. |
| Observaciones para implementación en Django | Debe filtrar los datos por la facultad asociada al decano. No debe permitir cambios masivos desde el dashboard en el MVP. |

### 4.13. Pantalla de auditoría

| Campo | Descripción |
|---|---|
| Nombre de la pantalla | Auditoría |
| Objetivo | Consultar acciones registradas en el sistema para trazabilidad operativa. |
| Roles con acceso | Administrativo y administrador funcional. |
| Tablas consumidas | `auditoria`, `usuario`. |
| Datos principales a mostrar | Usuario, correo, acción realizada, fecha y hora, descripción. |
| Acciones permitidas | Consultar, filtrar por usuario, fecha o tipo de acción. |
| Tipo de operación | Lectura. |
| Prioridad | Media. |
| Observaciones para implementación en Django | La auditoría automática por triggers no se implementa en esta etapa. En el MVP, los registros podrán generarse desde Django cuando se ejecuten acciones relevantes. |

## 5. Flujos mínimos recomendados

### 5.1. Flujo de estudiante

```text
Login
Dashboard de estudiante
Perfil
Inscripciones y notas
Matrícula y recibos
Homologaciones
Logout
```

### 5.2. Flujo de profesor

```text
Login
Dashboard de profesor
Perfil
Panel de grupos académicos
Gestión docente de notas
Homologaciones asignadas
Logout
```

### 5.3. Flujo de coordinador

```text
Login
Dashboard de coordinador
Panel de estructura institucional
Panel de asignaturas y plan de estudios
Panel de grupos académicos
Seguimiento de homologaciones
Logout
```

### 5.4. Flujo de decano

```text
Login
Dashboard de decano
Programas de la facultad
Grupos y cupos
Indicadores académicos
Homologaciones de la facultad
Logout
```

### 5.5. Flujo administrativo

```text
Login
Dashboard administrativo
Estructura institucional
Matrícula y recibos
Auditoría
Logout
```

## 6. Consideraciones para implementación en Django

La primera implementación debe enfocarse en que las pantallas consulten correctamente la información ya validada mediante SQL.

Las operaciones de escritura deben agregarse de forma controlada, empezando por flujos simples y usando validaciones de Django antes de guardar datos.

No se deben crear triggers, funciones, procedimientos, vistas, roles ni grants como parte de esta etapa de pantallas.

No se debe proponer Docker en esta fase.

La conexión a Azure PostgreSQL será una etapa posterior. En el MVP, el sistema debe funcionar localmente con Django y PostgreSQL.

Las consultas documentadas en `sql/04_consultas_validacion.sql` deben servir como referencia para construir consultas del ORM, servicios de dominio y reportes. No es obligatorio convertirlas en vistas de base de datos en esta etapa.
