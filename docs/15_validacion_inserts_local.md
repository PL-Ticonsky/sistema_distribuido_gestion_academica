# 15. Validación local de inserts y consultas funcionales

## 1. Propósito

Esta validación documenta la revisión funcional de los datos de prueba cargados en PostgreSQL local antes de iniciar el desarrollo de modelos, pantallas y flujos en Django.

El objetivo es confirmar que el DDL, los catálogos y los datos operativos permiten consultar información académica, financiera, administrativa, de homologaciones y auditoría de forma coherente.

## 2. Ambiente de validación

Los scripts fueron ejecutados localmente en PostgreSQL mediante DBeaver, usando la base de datos local de validación del proyecto.

El ambiente usado corresponde a la fase local del sistema:

```text
PostgreSQL local
DBeaver
Esquema public
```

La base sigue siendo local. La configuración de Azure Database for PostgreSQL Flexible Server se realizará en una etapa posterior, cuando el modelo y la aplicación Django estén más estables.

## 3. Scripts ejecutados

Los scripts considerados en esta validación son:

```text
sql/01_ddl.sql
sql/02_inserts_catalogos.sql
sql/03_inserts_operativos.sql
sql/04_consultas_validacion.sql
```

El script `sql/01_ddl.sql` crea la estructura inicial de tablas y restricciones.

El script `sql/02_inserts_catalogos.sql` carga datos base de facultades, programas, periodos, asignaturas, asociaciones programa-asignatura y prerrequisitos.

El script `sql/03_inserts_operativos.sql` carga usuarios, profesores, estudiantes, administrativos, cargos académicos, tarifas, recibos, matrículas, grupos, inscripciones, homologaciones y auditoría.

El script `sql/04_consultas_validacion.sql` contiene consultas de lectura para comprobar que los datos cargados se relacionan correctamente.

## 4. Grupos de consultas de validación

### 4.1. Conteos por tabla

Valida que las tablas principales tengan registros después de ejecutar los scripts de carga.

Sirve para detectar cargas incompletas o scripts ejecutados en orden incorrecto.

### 4.2. Usuarios y roles funcionales

Valida que los usuarios puedan especializarse como estudiantes, profesores y administrativos.

También permite comprobar el caso permitido de un usuario con doble rol estudiante-profesor.

### 4.3. Estructura académica

Incluye consultas de estudiantes por programa y facultad, profesores por facultad, programas por facultad y asignaturas por programa académico.

Estas consultas verifican que la organización universitaria por facultades y programas quedó correctamente representada.

### 4.4. Prerrequisitos y planes de estudio

Valida las relaciones entre asignaturas de un mismo programa y sus prerrequisitos.

Este grupo ayuda a revisar la consistencia inicial de los planes de estudio antes de implementar validaciones desde Django.

### 4.5. Grupos, cupos e inscripciones

Incluye consultas de grupos ofertados por periodo académico, cupos máximos, cantidad de inscritos y cupos disponibles.

También valida inscripciones por estudiante, asignatura, grupo, estado y nota final.

Estas consultas serán útiles para futuras pantallas de inscripción, gestión de grupos y control académico.

### 4.6. Rendimiento académico

Calcula el promedio académico por estudiante a partir de `inscripcion.nota_final`.

También resume asignaturas aprobadas, reprobadas, en curso y canceladas por estudiante.

Estas consultas servirán como base para reportes académicos y tableros de seguimiento.

### 4.7. Recibos y matrículas

Valida recibos por estudiante, estado de pago, valor pagado y fecha de pago.

También relaciona matrículas con recibos, programas y periodos académicos.

Estas consultas servirán como base para pantallas financieras y reportes de matrícula.

### 4.8. Homologaciones

Valida solicitudes de homologación por estudiante, institución de origen, asignatura homologada, estado y nota obtenida.

Este grupo ayuda a comprobar que el módulo de homologaciones tiene datos suficientes para futuras pantallas de solicitud, evaluación y consulta.

### 4.9. Cargos académicos

Valida decanos por facultad y periodo, y coordinadores por programa y periodo.

Estas consultas permiten comprobar las responsabilidades académicas definidas para profesores.

### 4.10. Auditoría

Valida registros de auditoría por usuario, acción, fecha y descripción.

Estas consultas servirán como punto de partida para futuras pantallas de trazabilidad.

## 5. Resultado esperado

El resultado esperado es que todas las consultas de `sql/04_consultas_validacion.sql` se ejecuten sin errores sobre una base local en la que ya se hayan ejecutado los scripts `01`, `02` y `03`.

También se espera que las consultas devuelvan datos coherentes, por ejemplo:

```text
Usuarios con roles funcionales asignados.
Estudiantes asociados a programas existentes.
Profesores asociados a facultades existentes.
Programas agrupados por facultad.
Asignaturas asociadas a programas.
Prerrequisitos legibles por asignatura.
Grupos ofertados en periodos existentes.
Cupos calculados desde inscripciones.
Notas finales y promedios académicos.
Recibos y matrículas relacionados.
Homologaciones asociadas a estudiantes y asignaturas.
Decanos y coordinadores vigentes por periodo.
Auditoría asociada a usuarios existentes.
```

Si una consulta no devuelve datos o muestra relaciones incompletas, se debe revisar primero que los scripts hayan sido ejecutados en el orden correcto:

```text
1. sql/01_ddl.sql
2. sql/02_inserts_catalogos.sql
3. sql/03_inserts_operativos.sql
4. sql/04_consultas_validacion.sql
```

## 6. Relación con el futuro desarrollo en Django

Estas consultas funcionarán como base para diseñar pantallas, reportes y dashboards del sistema.

En Django, los modelos deberán respetar las tablas, relaciones y restricciones definidas en el DDL. Luego, las vistas, servicios o consultas del ORM podrán reproducir la lógica de estas consultas para construir funcionalidades como:

```text
Panel de estudiantes.
Panel de profesores.
Consulta de grupos por periodo.
Control de cupos.
Historial académico.
Promedio académico.
Estado financiero del estudiante.
Estado de matrícula.
Seguimiento de homologaciones.
Auditoría de acciones.
Reportes institucionales por facultad y programa.
```

Estas consultas no reemplazan la lógica futura de Django, pero ayudan a validar que el modelo de datos ya puede responder preguntas funcionales importantes antes de implementar la aplicación web.

La integración cloud con Azure PostgreSQL se mantiene como una fase posterior. En esa etapa se deberá validar nuevamente la conexión, las variables de entorno, las credenciales seguras y la ejecución de estos scripts en un ambiente administrado.
