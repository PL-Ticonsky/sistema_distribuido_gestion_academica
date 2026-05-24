# 12. Modelo relacional ajustado para Django

## 1. Propósito del documento

Este documento presenta el modelo relacional ajustado para que la base de datos pueda ser usada correctamente por una aplicación Django.

El documento no reemplaza el modelo conceptual original. Su propósito es adaptar el modelo relacional a las necesidades técnicas de Django, especialmente en autenticación, nombres de campos, tipos de datos, restricciones y separación de responsabilidades entre base de datos y aplicación.

## 2. Criterios generales de ajuste

Los ajustes se hacen con los siguientes criterios:

```text
Mantener el dominio académico del documento original.
Conservar las entidades principales.
Conservar UUID en tablas operativas.
Conservar VARCHAR en catálogos institucionales.
Ajustar usuario para compatibilidad con Django.
Evitar triggers y funciones en el DDL inicial.
Usar restricciones simples cuando sean suficientes.
Dejar reglas complejas para Django o para una fase posterior.
```

## 3. Cambios principales frente al modelo original

| Elemento | Modelo original | Modelo ajustado |
|---|---|---|
| Contraseña de usuario | `hashed_password` | `password`, manejado por Django |
| Fecha de creación de usuario | `fecha_de_creacion` | `date_joined`, compatible con Django |
| Estado del usuario | No explícito | `is_active`, `is_staff`, `is_superuser` |
| Login | No definido técnicamente | Login por `correo` |
| Enums | Enum conceptual | `varchar + check constraint` |
| Triggers | No implementados en esta fase | Se dejan para etapa posterior |
| Funciones | No implementadas en esta fase | Se dejan para etapa posterior |
| Vistas | No hacen parte del DDL inicial | Se crearán luego en archivo separado |

## 4. Convenciones de nombres

### 4.1. Tablas

Las tablas se mantienen en español y en minúscula:

```text
usuario
estudiante
profesor
administrativo
facultad
programa_academico
periodo_academico
asignatura
programa_asignatura
pre_requisito
grupo
inscripcion
tarifa_matricula
recibo
matricula
homologacion
decano
coordinador
auditoria
```

### 4.2. Llaves primarias

Se usará el patrón:

```text
id_usuario
id_estudiante
id_profesor
id_administrativo
id_programa_academico
id_periodo_academico
cod_asignatura
```

### 4.3. Llaves foráneas

Se usará el nombre de la llave primaria referenciada cuando sea posible.

Ejemplo:

```text
estudiante.id_usuario → usuario.id_usuario
profesor.id_usuario → usuario.id_usuario
programa_academico.id_facultad → facultad.id_facultad
```

## 5. Tabla `usuario`

### 5.1. Justificación del ajuste

La tabla `usuario` es la tabla más importante para integrar el modelo con Django.

Django necesita campos específicos para manejar autenticación, permisos, sesiones y administración. Por eso no se usará `hashed_password`; se usará `password`.

### 5.2. Estructura propuesta

```text
usuario (
    id_usuario uuid primary key default gen_random_uuid(),
    password varchar(128) not null,
    last_login timestamptz null,
    is_superuser boolean not null default false,
    is_staff boolean not null default false,
    is_active boolean not null default true,
    date_joined timestamptz not null default now(),

    nombre varchar(80) not null,
    tipo_de_documento varchar(2) not null,
    numero_de_documento varchar(20) not null,
    correo varchar(120) not null,
    direccion varchar(120),

    unique(tipo_de_documento, numero_de_documento),
    unique(correo),
    check(tipo_de_documento in ('CC', 'TI', 'CE'))
)
```

### 5.3. Notas para Django

En Django se implementará como modelo personalizado:

```python
class CustomUser(AbstractUser):
    id_usuario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    correo = models.EmailField(unique=True)
    nombre = models.CharField(max_length=80)
    tipo_de_documento = models.CharField(max_length=2, choices=TipoDocumento.choices)
    numero_de_documento = models.CharField(max_length=20)
    direccion = models.CharField(max_length=120, blank=True, null=True)

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'tipo_de_documento', 'numero_de_documento']

    class Meta:
        db_table = 'usuario'
```

También se requerirá un `CustomUserManager` para crear usuarios y superusuarios correctamente.

### 5.4. Configuración requerida en Django

En `settings.py` debe existir:

```python
AUTH_USER_MODEL = 'accounts.CustomUser'
```

Esta configuración debe existir antes de ejecutar las primeras migraciones.

## 6. Tabla `facultad`

```text
facultad (
    id_facultad varchar(10) primary key,
    nombre_facultad varchar(80) not null,
    ubicacion varchar(80),
    correo_institucional varchar(120) unique
)
```

### Observaciones

- Es una tabla de catálogo institucional estable.
- Mantiene llave primaria `varchar`.
- Puede ser usada como criterio futuro para distribución por facultad.

## 7. Tabla `programa_academico`

```text
programa_academico (
    id_programa_academico varchar(20) primary key,
    id_facultad varchar(10) not null references facultad(id_facultad),
    nombre_programa varchar(100) not null,
    estado varchar(20) not null,
    modalidad varchar(20) not null,
    nivel_formacion varchar(30) not null,

    check(estado in ('Activo', 'Inactivo')),
    check(modalidad in ('Presencial', 'Virtual', 'Hibrida')),
    check(nivel_formacion in ('Tecnico', 'Tecnologico', 'Pregrado', 'Especializacion', 'Maestria', 'Doctorado'))
)
```

### Observaciones

- Un programa pertenece a una única facultad.
- Una facultad puede tener muchos programas.

## 8. Tabla `periodo_academico`

```text
periodo_academico (
    id_periodo_academico varchar(10) primary key,
    fecha_inicio date not null,
    fecha_final date not null,
    estado varchar(20) not null,

    check(fecha_final > fecha_inicio),
    check(estado in ('Planeado', 'Activo', 'Finalizado', 'Cancelado'))
)
```

### Observaciones

- Es catálogo institucional temporal.
- Se relaciona con grupos, tarifas, coordinadores y decanos.

## 9. Tabla `estudiante`

```text
estudiante (
    id_estudiante uuid primary key default gen_random_uuid(),
    id_usuario uuid not null unique references usuario(id_usuario),
    id_programa_academico varchar(20) not null references programa_academico(id_programa_academico),
    limite_matriculas int not null default 15,
    estado_estudiante varchar(20) not null,

    check(limite_matriculas > 0),
    check(estado_estudiante in ('Activo', 'Inactivo', 'Suspendido', 'Retirado', 'Egresado'))
)
```

### Observaciones

- Es una especialización de usuario.
- Un usuario puede tener como máximo un registro en estudiante.
- El avance académico no se almacena aquí; se calcula mediante consultas o vistas.

## 10. Tabla `profesor`

```text
profesor (
    id_profesor uuid primary key default gen_random_uuid(),
    id_usuario uuid not null unique references usuario(id_usuario),
    id_facultad varchar(10) not null references facultad(id_facultad),
    categoria varchar(20),
    vinculacion varchar(20),

    check(categoria is null or categoria in ('Auxiliar', 'Asistente', 'Asociado', 'Titular')),
    check(vinculacion is null or vinculacion in ('Planta', 'Catedra', 'Ocasional'))
)
```

### Observaciones

- Es una especialización de usuario.
- Un profesor puede dictar grupos.
- Un profesor puede ejercer como coordinador o decano.

## 11. Tabla `administrativo`

```text
administrativo (
    id_administrativo uuid primary key default gen_random_uuid(),
    id_usuario uuid not null unique references usuario(id_usuario),
    id_facultad varchar(10) not null references facultad(id_facultad),
    detalles varchar(255)
)
```

### Observaciones

- Es una especialización de usuario.
- Está asociado a una facultad.

## 12. Tabla `asignatura`

```text
asignatura (
    cod_asignatura varchar(20) primary key,
    nombre_asignatura varchar(100) not null,
    creditos int not null,
    estado varchar(20) not null,
    horas_teoria int not null,
    horas_pract int not null,
    homologable boolean not null default false,

    check(creditos > 0),
    check(horas_teoria >= 0),
    check(horas_pract >= 0),
    check(estado in ('Activa', 'Inactiva')),
    check(homologable = false or horas_pract = 0)
)
```

### Observaciones

- Una asignatura puede pertenecer a varios programas.
- La relación con programas se modela mediante `programa_asignatura`.
- La regla de homologación básica sí puede ir como `check` porque solo depende de la misma fila.

## 13. Tabla `programa_asignatura`

```text
programa_asignatura (
    id_programa_asignatura uuid primary key default gen_random_uuid(),
    id_programa_academico varchar(20) not null references programa_academico(id_programa_academico),
    cod_asignatura varchar(20) not null references asignatura(cod_asignatura),
    semestre_sugerido int not null,
    tipo_asignatura varchar(20) not null,
    estado varchar(20) not null,

    unique(id_programa_academico, cod_asignatura),
    check(semestre_sugerido > 0),
    check(tipo_asignatura in ('Obligatoria', 'Electiva')),
    check(estado in ('Activa', 'Inactiva'))
)
```

### Observaciones

- Representa la relación muchos a muchos entre programas y asignaturas.
- Aquí pertenecen el semestre sugerido y el tipo de asignatura.

## 14. Tabla `pre_requisito`

```text
pre_requisito (
    id_pre_requisito uuid primary key default gen_random_uuid(),
    id_programa_academico varchar(20) not null references programa_academico(id_programa_academico),
    id_programa_asignatura uuid not null references programa_asignatura(id_programa_asignatura),
    id_programa_asignatura_requisito uuid not null references programa_asignatura(id_programa_asignatura),

    unique(id_programa_asignatura, id_programa_asignatura_requisito),
    check(id_programa_asignatura <> id_programa_asignatura_requisito)
)
```

### Observaciones

- Evita que una asignatura sea prerrequisito de sí misma.
- Evita repetir el mismo prerrequisito.
- No evita ciclos complejos de prerrequisitos. Esa validación se hará inicialmente en Django y podrá reforzarse luego con función recursiva.

## 15. Tabla `grupo`

```text
grupo (
    id_grupo uuid primary key default gen_random_uuid(),
    id_programa_asignatura uuid not null references programa_asignatura(id_programa_asignatura),
    id_periodo_academico varchar(10) not null references periodo_academico(id_periodo_academico),
    id_profesor uuid references profesor(id_profesor),
    codigo_grupo varchar(20) not null,
    cupo_maximo int not null,
    estado_grupo varchar(20) not null,

    unique(id_programa_asignatura, id_periodo_academico, codigo_grupo),
    check(cupo_maximo > 0),
    check(estado_grupo in ('Abierto', 'En curso', 'Finalizado', 'Cancelado'))
)
```

### Ajuste aplicado

En el modelo original aparecía `id_docente` referenciando a `profesor`. Para mantener consistencia de nombres, se recomienda usar `id_profesor`.

### Observaciones

- Un grupo puede existir sin profesor asignado.
- El código del grupo puede repetirse en periodos diferentes.
- No puede repetirse el mismo código para la misma asignatura-programa dentro del mismo periodo.
- El control de cupos no se resuelve con un `check` porque requiere contar inscripciones. Se hará inicialmente en Django.

## 16. Tabla `inscripcion`

```text
inscripcion (
    id_inscripcion uuid primary key default gen_random_uuid(),
    id_grupo uuid not null references grupo(id_grupo),
    id_estudiante uuid not null references estudiante(id_estudiante),
    nota1 numeric(3,2),
    nota2 numeric(3,2),
    nota3 numeric(3,2),
    nota_final numeric(3,2),
    intento int not null,
    estado_inscripcion varchar(20) not null,

    unique(id_grupo, id_estudiante),
    check(nota1 is null or nota1 between 0 and 5),
    check(nota2 is null or nota2 between 0 and 5),
    check(nota3 is null or nota3 between 0 and 5),
    check(nota_final is null or nota_final between 0 and 5),
    check(intento > 0),
    check(estado_inscripcion in ('Cursando', 'Aprobada', 'Reprobada', 'Cancelada')),
    check(estado_inscripcion in ('Cursando', 'Cancelada') or nota_final is not null)
)
```

### Observaciones

- Evita que un estudiante se inscriba dos veces al mismo grupo.
- La regla de no inscribirse en dos grupos de la misma asignatura-programa durante el mismo periodo requiere revisar la tabla `grupo`, por tanto se manejará inicialmente en Django.
- La regla de matrícula activa también se manejará inicialmente en Django.
- La nota final se exige cuando la inscripción está aprobada o reprobada.

## 17. Tabla `tarifa_matricula`

```text
tarifa_matricula (
    id_tarifa_matricula uuid primary key default gen_random_uuid(),
    id_programa_academico varchar(20) not null references programa_academico(id_programa_academico),
    id_periodo_academico varchar(10) not null references periodo_academico(id_periodo_academico),
    valor_matricula numeric(12,2) not null,
    fecha_limite_ordinaria date not null,
    fecha_limite_extraordinaria date not null,
    estado varchar(20) not null,

    unique(id_programa_academico, id_periodo_academico),
    check(valor_matricula >= 0),
    check(fecha_limite_extraordinaria >= fecha_limite_ordinaria),
    check(estado in ('Activa', 'Inactiva'))
)
```

### Observaciones

- Un programa solo puede tener una tarifa por periodo.

## 18. Tabla `recibo`

```text
recibo (
    id_recibo uuid primary key default gen_random_uuid(),
    id_estudiante uuid not null references estudiante(id_estudiante),
    id_tarifa_matricula uuid not null references tarifa_matricula(id_tarifa_matricula),
    fecha_pago date,
    valor_pagado numeric(12,2),
    metodo_pago varchar(20),
    estado_pago varchar(20) not null,
    extras numeric(12,2) not null default 0,

    unique(id_estudiante, id_tarifa_matricula),
    check(valor_pagado is null or valor_pagado >= 0),
    check(extras >= 0),
    check(metodo_pago is null or metodo_pago in ('Efectivo', 'Tarjeta', 'PSE', 'Transferencia', 'Consignacion')),
    check(estado_pago in ('Pendiente', 'Pagado', 'Vencido', 'Anulado')),
    check(estado_pago <> 'Pagado' or (fecha_pago is not null and valor_pagado is not null))
)
```

### Observaciones

- El recibo representa el proceso financiero.
- El estado de pago es independiente del estado de matrícula.
- Si el recibo está pagado, debe tener fecha de pago y valor pagado.

## 19. Tabla `matricula`

```text
matricula (
    id_matricula uuid primary key default gen_random_uuid(),
    id_recibo uuid not null unique references recibo(id_recibo),
    estado_matricula varchar(20) not null,

    check(estado_matricula in ('Pendiente', 'Activa', 'Finalizada', 'Cancelada', 'Anulada'))
)
```

### Observaciones

- La matrícula representa el proceso académico-administrativo.
- Una matrícula nace a partir de un recibo.
- La activación automática de matrícula al pagar recibo se deja para lógica de Django o trigger posterior.

## 20. Tabla `homologacion`

```text
homologacion (
    id_homologacion uuid primary key default gen_random_uuid(),
    id_profesor_evaluador uuid not null references profesor(id_profesor),
    id_estudiante uuid not null references estudiante(id_estudiante),
    asignatura_origen varchar(100) not null,
    institucion_origen varchar(100) not null,
    id_programa_asignatura uuid not null references programa_asignatura(id_programa_asignatura),
    fecha_solicitud date not null,
    estado_homologacion varchar(20) not null,
    observacion varchar(255),
    fecha_respuesta date,
    nota_obtenida numeric(3,2),

    check(estado_homologacion in ('Solicitada', 'En revision', 'Aprobada', 'Rechazada', 'Cancelada')),
    check(nota_obtenida is null or nota_obtenida between 0 and 5),
    check(estado_homologacion <> 'Aprobada' or nota_obtenida is not null),
    check(fecha_respuesta is null or fecha_respuesta >= fecha_solicitud)
)
```

### Observaciones

- La asignatura de origen se almacena como texto porque viene de otra institución.
- La institución de origen se almacena como texto.
- La regla de permitir homologación solo para asignaturas homologables requiere consultar `asignatura`, por tanto se manejará inicialmente en Django.
- La regla de no tener más de una homologación aprobada para la misma asignatura requiere una condición parcial. Puede implementarse después con índice único parcial o validación de aplicación.

## 21. Tabla `decano`

```text
decano (
    id_decano uuid primary key default gen_random_uuid(),
    id_profesor uuid not null references profesor(id_profesor),
    id_periodo_academico varchar(10) not null references periodo_academico(id_periodo_academico),
    id_facultad varchar(10) not null references facultad(id_facultad),

    unique(id_facultad, id_periodo_academico)
)
```

### Observaciones

- Todo decano debe ser profesor.
- Una facultad tiene un único decano por periodo.
- La regla de que el profesor pertenezca a la misma facultad puede validarse inicialmente en Django y reforzarse después si se requiere.

## 22. Tabla `coordinador`

```text
coordinador (
    id_coordinador uuid primary key default gen_random_uuid(),
    id_profesor uuid not null references profesor(id_profesor),
    id_periodo_academico varchar(10) not null references periodo_academico(id_periodo_academico),
    id_programa_academico varchar(20) not null references programa_academico(id_programa_academico),

    unique(id_programa_academico, id_periodo_academico)
)
```

### Observaciones

- Todo coordinador debe ser profesor.
- Un programa tiene un único coordinador por periodo.
- La regla de que el profesor pertenezca a la facultad del programa se validará inicialmente en Django.

## 23. Tabla `auditoria`

```text
auditoria (
    id_auditoria uuid primary key default gen_random_uuid(),
    id_usuario uuid not null references usuario(id_usuario),
    accion_realizada varchar(100) not null,
    fecha_hora timestamptz not null default now(),
    descripcion varchar(255)
)
```

### Observaciones

- La auditoría automática no se hará todavía con triggers.
- En la primera versión se puede registrar desde Django cuando se ejecuten acciones relevantes.
- Después se puede reforzar con triggers si el alcance del proyecto lo exige.

## 24. Tablas que Django creará adicionalmente

Django puede crear tablas internas para autenticación, permisos, sesiones y administración.

Ejemplos:

```text
auth_group
auth_permission
django_content_type
django_session
django_admin_log
```

Estas tablas no pertenecen directamente al modelo académico, pero son necesarias para el funcionamiento del framework.

No se recomienda escribir manualmente estas tablas en el DDL académico. Deben ser creadas por las migraciones de Django.

## 25. Relaciones principales del modelo ajustado

```text
usuario 1 ─── 0..1 estudiante
usuario 1 ─── 0..1 profesor
usuario 1 ─── 0..1 administrativo
facultad 1 ─── N programa_academico
facultad 1 ─── N profesor
facultad 1 ─── N administrativo
programa_academico 1 ─── N estudiante
programa_academico N ─── M asignatura mediante programa_asignatura
programa_asignatura 1 ─── N grupo
periodo_academico 1 ─── N grupo
grupo 1 ─── N inscripcion
estudiante 1 ─── N inscripcion
programa_academico 1 ─── N tarifa_matricula
periodo_academico 1 ─── N tarifa_matricula
tarifa_matricula 1 ─── N recibo
estudiante 1 ─── N recibo
recibo 1 ─── 1 matricula
estudiante 1 ─── N homologacion
profesor 1 ─── N homologacion
profesor 1 ─── N coordinador
profesor 1 ─── N decano
usuario 1 ─── N auditoria
```

## 26. Reglas implementadas en el DDL inicial

Las siguientes reglas sí se implementarán en el DDL inicial:

```text
Usuario con correo único.
Usuario con documento único por tipo y número.
Estudiante asociado a un usuario único.
Profesor asociado a un usuario único.
Administrativo asociado a un usuario único.
Programa asociado a una facultad.
Asignatura con créditos positivos.
Asignatura homologable solo si tiene horas prácticas en cero.
Programa-asignatura único por programa y asignatura.
Prerrequisito no repetido.
Asignatura no puede ser prerrequisito de sí misma.
Grupo único por asignatura-programa, periodo y código.
Cupo máximo positivo.
Inscripción única por estudiante y grupo.
Notas entre 0 y 5.
Inscripción aprobada o reprobada con nota final.
Tarifa única por programa y periodo.
Recibo único por estudiante y tarifa.
Recibo pagado con fecha y valor pagado.
Matrícula asociada a un único recibo.
Homologación aprobada con nota obtenida.
Decano único por facultad y periodo.
Coordinador único por programa y periodo.
```

## 27. Reglas pendientes para Django o fase avanzada

Las siguientes reglas no se implementarán en el DDL inicial:

```text
Controlar cupo real del grupo.
Validar matrícula activa antes de inscribir asignaturas.
Validar prerrequisitos aprobados antes de inscribir.
Evitar ciclos complejos de prerrequisitos.
Validar que la homologación apunte a una asignatura homologable.
Evitar más de una homologación aprobada por estudiante y asignatura-programa.
Calcular matrículas restantes.
Calcular rendimiento académico.
Calcular avance de carrera.
Calcular riesgo de deserción.
Auditoría automática por triggers.
Activación automática de matrícula al pagar recibo.
```

## 28. Recomendación para el DDL siguiente

El siguiente archivo debe ser:

```text
sql/01_ddl.sql
```

Ese archivo debe contener únicamente:

```text
create extension if not exists pgcrypto;
create table ...;
primary key;
foreign key;
unique;
check;
not null;
```

No debe contener:

```text
create trigger;
create function;
create view;
create procedure;
create role;
grant;
insert;
```

## 29. Orden recomendado de creación de tablas

El orden recomendado para evitar errores de claves foráneas es:

```text
1. usuario
2. facultad
3. programa_academico
4. periodo_academico
5. estudiante
6. profesor
7. administrativo
8. asignatura
9. programa_asignatura
10. pre_requisito
11. grupo
12. tarifa_matricula
13. recibo
14. matricula
15. inscripcion
16. homologacion
17. decano
18. coordinador
19. auditoria
```

## 30. Observación importante sobre Django y el DDL

Hay dos caminos posibles:

```text
Camino 1: Django crea las tablas mediante migraciones.
Camino 2: Se crea la base manualmente con DDL y Django se adapta a ella.
```

Para este proyecto se recomienda un camino mixto controlado:

```text
1. Se escribe el DDL como evidencia académica y como contrato de diseño.
2. Se implementan los modelos de Django respetando ese contrato.
3. Django crea la base real mediante migraciones.
4. Se compara la estructura creada por Django con el DDL esperado.
```

Esto reduce el riesgo de incompatibilidad con autenticación, permisos y tablas internas de Django.

## 31. Decisión final del modelo ajustado

El modelo relacional ajustado conserva el diseño académico original, pero adapta la tabla `usuario` y las restricciones para que el sistema pueda desarrollarse correctamente con Django.

La primera versión de la base de datos será simple, estable y orientada a desarrollo local.

Los triggers, funciones, vistas, roles avanzados y distribución física se implementarán después, en archivos separados y con pruebas específicas.
