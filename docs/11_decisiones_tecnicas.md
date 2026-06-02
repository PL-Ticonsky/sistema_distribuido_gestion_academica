# 11. Decisiones técnicas para el desarrollo local con Django

## 1. Propósito del documento

Este documento define las decisiones técnicas que se tomarán antes de construir el DDL y antes de iniciar el desarrollo del sistema en Django.

La finalidad es evitar que el proyecto empiece con una base de datos incompatible con el sistema de autenticación de Django o con una estructura difícil de mantener después.

Este documento debe leerse junto con:

- `01_portada_y_datos_generales.md`
- `02_introduccion_y_descripcion.md`
- `03_alcance_del_documento.md`
- `04_reglas_de_negocio.md`
- `06_modelo_relacional_original.md`
- `12_modelo_relacional_ajustado_django.md`

## 2. Contexto general del sistema

El sistema corresponde a una aplicación local de gestión académica universitaria. Su objetivo es permitir la administración de usuarios, estudiantes, profesores, administrativos, facultades, programas académicos, asignaturas, grupos, inscripciones, matrículas, pagos, homologaciones y auditoría.

Aunque el documento original plantea el sistema como una base de datos distribuida, esta fase del proyecto se desarrollará inicialmente en un entorno local. La distribución física, la fragmentación de datos y las vistas institucionales distribuidas se dejan para una fase posterior.

## 3. Decisión principal de arquitectura

La arquitectura inicial será:

```text
Aplicación web local
        ↓
Django
        ↓
PostgreSQL local
```

No se desplegará en servidor remoto durante esta fase. El sistema se ejecutará en la máquina local de desarrollo.

## 3.1. Estrategia de ambientes

El proyecto se desarrollará inicialmente en un ambiente local, usando Django conectado a una base PostgreSQL instalada en la máquina de desarrollo. DBeaver se usará como herramienta de apoyo para ejecutar scripts SQL, revisar tablas, validar restricciones y generar evidencias académicas.

La primera configuración de conexión será local:

```text
Django local
        ↓
PostgreSQL local
        ↓
DBeaver para administración y verificación
```

Posteriormente, cuando el sistema tenga una base funcional y validada, se preparará un ambiente cloud con PostgreSQL administrado. La opción esperada será Azure Database for PostgreSQL Flexible Server, manteniendo la misma estructura lógica de base de datos y ajustando únicamente los parámetros de conexión, seguridad y despliegue.

El ambiente cloud esperado será:

```text
Django
        ↓
Azure Database for PostgreSQL Flexible Server
```

Las credenciales de base de datos no deben quedar hardcodeadas en el código fuente, archivos Python, scripts SQL ni documentación operativa. Cada ambiente debe definir sus propios valores mediante variables de entorno o archivos `.env` locales no versionados.

Django debe leer la conexión a PostgreSQL desde variables de entorno, por ejemplo:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
POSTGRES_PORT
POSTGRES_SSLMODE
```

En desarrollo local, `POSTGRES_HOST` normalmente será `localhost` y `POSTGRES_SSLMODE` podrá estar desactivado o usar un valor compatible con la instalación local. En Azure PostgreSQL, `POSTGRES_HOST` apuntará al servidor flexible y la conexión deberá prepararse para SSL, usualmente mediante `POSTGRES_SSLMODE=require`.

El archivo `.env.example` solo debe contener valores de ejemplo o placeholders. El archivo real `.env` no debe versionarse.

El DDL inicial seguirá siendo independiente del ambiente. Por tanto, `sql/01_ddl.sql` debe conservar únicamente la extensión necesaria, tablas y restricciones simples. No debe incluir triggers, funciones, procedimientos almacenados, vistas, roles, grants ni inserts. Esos objetos se crearán en archivos SQL separados cuando el modelo esté estable.

## 4. Tecnologías seleccionadas

| Componente | Tecnología | Justificación |
|---|---|---|
| Lenguaje principal | Python | Es el lenguaje base de Django y permite un desarrollo rápido y mantenible. |
| Framework web | Django | Incluye autenticación, sesiones, permisos, panel administrativo, ORM y migraciones. |
| Base de datos | PostgreSQL | Es robusta, compatible con restricciones avanzadas y adecuada para el proyecto de bases de datos. |
| Administración de base de datos | DBeaver | Permite ejecutar scripts, revisar tablas, consultar datos y generar evidencias. |
| Editor de código | VS Code | Permite trabajar con Codex, Git, terminal y estructura del proyecto. |
| Control de versiones | Git | Permite organizar avances, ramas y cambios del proyecto. |
| Asistente de desarrollo | Codex | Se usará para crear estructura, implementar código por módulos y acelerar tareas repetitivas. |

## 5. Decisión sobre el flujo de desarrollo

El proyecto se desarrollará por etapas. No se debe pedir a Codex que construya todo el sistema de una sola vez.

El flujo recomendado será:

```text
1. Crear documentación técnica.
2. Crear estructura de carpetas y archivos base.
3. Ajustar el modelo relacional para Django.
4. Crear DDL inicial solo con tablas y restricciones simples.
5. Crear inserciones de catálogos.
6. Crear inserciones de prueba.
7. Crear proyecto Django.
8. Implementar autenticación y usuario personalizado.
9. Implementar módulos por apps.
10. Implementar vistas, reportes, consultas, triggers y funciones avanzadas en fases posteriores.
```

## 6. Decisión sobre el modelo de usuario

La tabla `usuario` del documento original no se usará exactamente igual en la implementación con Django.

El documento original plantea una tabla `usuario` con campos como:

```text
id_usuario
nombre
tipo_de_documento
numero_de_documento
correo
direccion
hashed_password
fecha_de_creacion
```

Para integrarla correctamente con Django, se ajustará como un usuario personalizado compatible con el sistema de autenticación.

La decisión técnica es:

```text
La tabla usuario será representada en Django mediante un modelo CustomUser.
CustomUser deberá integrarse con el sistema de autenticación de Django.
El login se realizará con correo institucional o correo registrado.
La contraseña no se manejará manualmente en un campo hashed_password.
Django manejará el hash en el campo password.
```

Por tanto, el campo `hashed_password` será reemplazado por el campo estándar `password` usado por Django.

## 7. Decisión sobre roles funcionales

El sistema maneja roles académicos y administrativos. Estos roles no deben confundirse con los roles técnicos de PostgreSQL.

### 7.1. Roles funcionales de la aplicación

Los roles funcionales serán:

```text
Estudiante
Profesor
Coordinador
Decano
Administrativo
Administrador funcional
```

Estos roles se manejarán principalmente desde Django mediante grupos y permisos.

### 7.2. Roles técnicos de PostgreSQL

Los roles técnicos de PostgreSQL serán mínimos en esta fase:

```text
postgres / superusuario técnico
app_user / usuario usado por Django para conectarse a la base de datos
read_only_user / usuario opcional de consulta para evidencias
```

El administrador técnico de PostgreSQL será el único con capacidad para crear, modificar o eliminar estructuras de base de datos.

## 8. Decisión sobre tablas de especialización

El documento original establece que un usuario puede ser estudiante, profesor o administrativo, y que estas especializaciones no son totalmente excluyentes.

Por tanto, se mantendrán tablas separadas:

```text
usuario
estudiante
profesor
administrativo
coordinador
decano
```

La relación será:

```text
usuario 1 ─── 0..1 estudiante
usuario 1 ─── 0..1 profesor
usuario 1 ─── 0..1 administrativo
profesor 1 ─── 0..N coordinador
profesor 1 ─── 0..N decano
```

Esto permite representar casos como:

```text
Un usuario que solo es estudiante.
Un usuario que solo es profesor.
Un usuario que es estudiante y profesor al mismo tiempo.
Un profesor que también puede ser coordinador o decano.
```

## 9. Decisión sobre nombres de tablas

Se mantendrán nombres de tablas en español para respetar el modelo académico del proyecto.

Ejemplos:

```text
usuario
estudiante
profesor
facultad
programa_academico
asignatura
programa_asignatura
grupo
inscripcion
recibo
matricula
homologacion
auditoria
```

En Django, los modelos podrán tener nombres en estilo Python:

```python
CustomUser
Estudiante
Profesor
Facultad
ProgramaAcademico
Asignatura
ProgramaAsignatura
Grupo
Inscripcion
Recibo
Matricula
Homologacion
Auditoria
```

Cada modelo deberá declarar explícitamente `db_table` para que el nombre real de la tabla en PostgreSQL coincida con la documentación.

## 10. Decisión sobre tipos `enum`

No se recomienda usar tipos `enum` nativos de PostgreSQL en esta primera versión.

Aunque los enum de PostgreSQL son válidos, pueden generar más trabajo cuando se necesite cambiar valores posteriormente. Para mantener compatibilidad directa con Django, se usará:

```text
varchar + check constraint
```

En Django, estos campos se representarán con `TextChoices`.

Ejemplo conceptual:

```sql
estado_estudiante varchar(20) not null
check (estado_estudiante in ('Activo', 'Inactivo', 'Suspendido', 'Retirado', 'Egresado'))
```

En Django:

```python
class EstadoEstudiante(models.TextChoices):
    ACTIVO = 'Activo', 'Activo'
    INACTIVO = 'Inactivo', 'Inactivo'
    SUSPENDIDO = 'Suspendido', 'Suspendido'
    RETIRADO = 'Retirado', 'Retirado'
    EGRESADO = 'Egresado', 'Egresado'
```

## 11. Decisión sobre llaves primarias

Se conserva la estrategia mixta del documento original:

```text
UUID para tablas operativas, transaccionales y de personas.
VARCHAR para catálogos institucionales estables.
```

### 11.1. Tablas con UUID

```text
usuario
estudiante
profesor
administrativo
tarifa_matricula
recibo
matricula
programa_asignatura
pre_requisito
grupo
inscripcion
homologacion
decano
coordinador
auditoria
```

### 11.2. Tablas con VARCHAR

```text
facultad
programa_academico
periodo_academico
asignatura
```

## 12. Decisión sobre UUID

En PostgreSQL se usará `gen_random_uuid()` para generar UUID.

Esto requiere habilitar la extensión:

```sql
create extension if not exists pgcrypto;
```

En Django, los UUID se representarán con:

```python
models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

Aunque PostgreSQL puede generar el UUID, Django también debe poder generar el identificador desde el ORM. Para mantener coherencia con Django, la generación principal se manejará desde Django y el DDL conservará `default gen_random_uuid()` como respaldo a nivel de base de datos.

## 13. Decisión sobre el DDL inicial

El DDL inicial solo tendrá:

```text
extensiones necesarias
tablas
claves primarias
claves foráneas
restricciones unique
restricciones check simples
restricciones not null
```

No tendrá en esta fase:

```text
triggers
funciones almacenadas
procedimientos almacenados
vistas
roles avanzados
permisos detallados
particionamiento
fragmentación física distribuida
```

## 14. Decisión sobre triggers y funciones avanzadas

Los triggers y funciones avanzadas no deben ir en el DDL inicial.

La mejor práctica para este proyecto será separarlos en una fase posterior, cuando ya exista:

```text
DDL estable
Datos de prueba
Modelos de Django funcionando
Flujos principales definidos
```

Los triggers y funciones se documentarán y construirán después en archivos separados, por ejemplo:

```text
sql/06_funciones.sql
sql/07_triggers.sql
sql/08_pruebas_triggers.sql
```

También se podrá crear una carpeta:

```text
sql/avanzado/
├── 01_funciones_validacion.sql
├── 02_triggers_auditoria.sql
├── 03_triggers_cupos.sql
├── 04_pruebas_triggers.sql
└── README.md
```

## 15. Qué reglas van en la base de datos ahora

En esta primera fase, deben ir en la base de datos las reglas que pueden expresarse directamente con restricciones simples.

Ejemplos:

```text
Documento único por tipo y número.
Correo único.
Un programa pertenece a una facultad.
Una tarifa es única por programa y periodo.
Una asignatura homologable debe tener cero horas prácticas.
Una nota debe estar entre 0 y 5.
Un cupo máximo debe ser mayor que 0.
Una asignatura no puede ser prerrequisito de sí misma.
```

Estas reglas se pueden implementar con:

```text
primary key
foreign key
unique
check
not null
```

## 16. Qué reglas no van en el DDL inicial

No todas las reglas del negocio son convenientes para el DDL inicial.

Las siguientes reglas requieren lógica más compleja porque dependen de consultas, conteos, estados cruzados o recorridos de relaciones:

```text
Controlar que el número de inscritos no supere el cupo máximo.
Validar que el estudiante haya aprobado prerrequisitos antes de inscribir.
Evitar ciclos completos de prerrequisitos.
Validar que el estudiante tenga matrícula activa antes de inscribir asignaturas.
Validar que una homologación solo se haga sobre asignaturas homologables.
Calcular avance de carrera.
Calcular rendimiento académico.
Calcular riesgo de deserción.
Registrar auditoría automática de operaciones.
```

Estas reglas se manejarán inicialmente desde Django, mediante servicios, formularios, validaciones y consultas. Después podrán reforzarse con funciones, triggers o vistas.

## 17. Criterio para decidir entre Django y trigger

La regla práctica será:

```text
Si la regla solo valida una fila, puede ir como CHECK.
Si la regla valida existencia o relación directa, puede ir como FOREIGN KEY o UNIQUE.
Si la regla requiere contar filas, consultar varias tablas o validar estados complejos, va primero en Django.
Si la regla debe cumplirse incluso si alguien modifica la base por fuera de Django, se refuerza después con trigger o función.
```

## 18. Ejemplos de reglas por capa

| Regla | Capa inicial | Capa posterior opcional |
|---|---|---|
| Correo único | Base de datos | No requiere trigger |
| Documento único | Base de datos | No requiere trigger |
| Nota entre 0 y 5 | Base de datos | No requiere trigger |
| Cupo máximo positivo | Base de datos | No requiere trigger |
| No superar cupo de grupo | Django | Trigger para control concurrente |
| Validar prerrequisitos aprobados | Django | Función o trigger |
| Evitar ciclos de prerrequisitos | Django | Función recursiva |
| Auditoría automática | Django al inicio | Trigger posterior |
| Activar matrícula por pago | Django | Trigger posterior si se requiere |
| Indicadores académicos | Consultas o vistas | Vistas materializadas si se requiere |

## 19. Decisión sobre vistas

Las vistas no harán parte del DDL inicial.

Se crearán después en un archivo separado:

```text
sql/04_vistas.sql
```

Las vistas serán útiles para:

```text
Consultar estudiantes con programa y facultad.
Consultar notas finales por estudiante.
Consultar grupos ofertados por periodo.
Consultar matrículas activas.
Consultar pagos pendientes.
Consultar homologaciones por estado.
Calcular avance académico.
Calcular rendimiento académico.
```

## 20. Decisión sobre inserciones

Las inserciones no irán dentro del DDL.

Se separarán así:

```text
sql/01_ddl.sql
sql/02_inserts_catalogos.sql
sql/03_inserts_prueba.sql
```

### 20.1. Inserts de catálogos

Incluyen datos estables:

```text
facultades
programas académicos
periodos académicos
asignaturas
programa_asignatura
pre_requisitos
```

### 20.2. Inserts de prueba

Incluyen datos operativos:

```text
usuarios
estudiantes
profesores
administrativos
tarifas
recibos
matrículas
grupos
inscripciones
homologaciones
auditoría
```

## 21. Decisión sobre Django Admin

Django Admin se usará como herramienta de administración inicial.

Será útil para:

```text
Crear usuarios de prueba.
Asignar grupos y permisos.
Revisar registros.
Administrar catálogos.
Validar que las relaciones funcionen.
```

No será necesariamente la interfaz final para estudiantes y profesores, pero permitirá avanzar rápido en una primera versión funcional.

## 22. Decisión sobre interfaz de usuario

La primera versión tendrá una interfaz web sencilla, local y funcional.

Prioridad:

```text
Funcionalidad correcta.
Validaciones claras.
Navegación por rol.
Consultas y reportes útiles.
Diseño limpio, pero no excesivamente complejo.
```

No se priorizará una interfaz visual avanzada en la primera etapa.

## 23. Decisión sobre apps de Django

La estructura modular recomendada será:

```text
apps/accounts
apps/estructura
apps/academica
apps/financiera
apps/homologaciones
apps/auditoria
```

### 23.1. accounts

Responsable de:

```text
usuario personalizado
estudiante
profesor
administrativo
coordinador
decano
grupos funcionales
permisos iniciales
```

### 23.2. estructura

Responsable de:

```text
facultad
programa_academico
periodo_academico
```

### 23.3. academica

Responsable de:

```text
asignatura
programa_asignatura
pre_requisito
grupo
inscripcion
notas
```

### 23.4. financiera

Responsable de:

```text
tarifa_matricula
recibo
matricula
```

### 23.5. homologaciones

Responsable de:

```text
homologacion
solicitud de homologación
evaluación de homologación
```

### 23.6. auditoria

Responsable de:

```text
registro de acciones relevantes
consultas de auditoría
```

## 24. Decisión sobre Codex

Codex se usará de manera controlada. No debe modificar todo el proyecto al mismo tiempo.

Cada prompt debe indicar:

```text
qué archivos puede modificar
qué archivos no puede modificar
qué tarea puntual debe resolver
qué documentación debe leer antes de actuar
qué resultado se espera
```

## 25. Orden de trabajo recomendado después de este documento

El siguiente orden de trabajo será:

```text
1. Revisar este documento.
2. Revisar `12_modelo_relacional_ajustado_django.md`.
3. Pedir a Codex que cree la estructura de carpetas del proyecto.
4. Crear el DDL inicial solo con tablas.
5. Crear inserts de catálogos.
6. Crear inserts de prueba.
7. Crear el proyecto Django.
8. Implementar `accounts` con usuario personalizado.
9. Implementar `estructura`.
10. Implementar `academica`.
11. Implementar `financiera`.
12. Implementar `homologaciones`.
13. Implementar `auditoria`.
14. Crear vistas y consultas.
15. Crear triggers y funciones avanzadas, si el alcance final lo requiere.
```

## 26. Decisión final

La base de datos se ajustará para funcionar correctamente con Django desde el inicio.

El DDL inicial no contendrá triggers ni funciones. Solo tendrá tablas y restricciones estructurales básicas.

La lógica avanzada se documentará y desarrollará después, cuando el modelo esté estable y el sistema Django pueda consumir correctamente los datos.
