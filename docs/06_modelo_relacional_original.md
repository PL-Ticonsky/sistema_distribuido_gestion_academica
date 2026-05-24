# Modelo relacional original del documento base

## 6. Modelo relacional

El modelo relacional corresponde a la transformación del diseño conceptual en un conjunto de tablas, atributos, claves primarias, claves foráneas y restricciones.

En esta etapa se define cómo se representará la información dentro de la base de datos.

## 6.1. Estrategia de identificación de registros

Para la identificación de registros se adopta una estrategia mixta:

- Se utilizan llaves internas de tipo `uuid` para tablas operativas, transaccionales y de personas.
- Se utilizan llaves de tipo `varchar` para catálogos institucionales estables.

Los identificadores `uuid` serán generados automáticamente por la base de datos mediante `gen_random_uuid()`, evitando el uso de llaves autoincrementales y reduciendo la dependencia de consecutivos globales.

## 6.2. Diagrama relacional

El documento base indica que en esta sección se debe insertar el diagrama relacional final de la base de datos.

## 6.3. Esquema de tablas

> Nota: Este archivo conserva el modelo relacional original del documento. En la siguiente fase se construirá una versión ajustada para Django, especialmente en la tabla `usuario`.

### Tabla `usuario`

```text
usuario (
  PK id_usuario uuid default gen_random_uuid(),
  nombre varchar(50) not null,
  tipo_de_documento enum('CC', 'TI', 'CE') not null,
  numero_de_documento varchar(10) not null,
  correo varchar(30) not null,
  direccion varchar(30),
  hashed_password varchar(255) not null,
  fecha_de_creacion date not null,
  unique(tipo_de_documento, numero_de_documento),
  unique(correo)
)
```

### Tabla `estudiante`

```text
estudiante (
  PK id_estudiante uuid default gen_random_uuid(),
  FK id_usuario(usuario.id_usuario) not null unique,
  FK id_programa_academico(programa_academico.id_programa_academico) not null,
  limite_matriculas int default 15 not null,
  estado_estudiante enum('Activo', 'Inactivo', 'Suspendido', 'Retirado', 'Egresado') not null
)
```

### Tabla `profesor`

```text
profesor (
  PK id_profesor uuid default gen_random_uuid(),
  FK id_usuario(usuario.id_usuario) not null unique,
  FK id_facultad(facultad.id_facultad) not null,
  categoria enum('Auxiliar', 'Asistente', 'Asociado', 'Titular'),
  vinculacion enum('Planta', 'Catedra', 'Ocasional')
)
```

### Tabla `administrativo`

```text
administrativo (
  PK id_administrativo uuid default gen_random_uuid(),
  FK id_usuario(usuario.id_usuario) not null unique,
  FK id_facultad(facultad.id_facultad) not null,
  detalles varchar(255)
)
```

### Tabla `auditoria`

```text
auditoria (
  PK id_auditoria uuid default gen_random_uuid(),
  FK id_usuario(usuario.id_usuario) not null,
  accion_realizada varchar(100) not null,
  fecha_hora timestamp not null,
  descripcion varchar(255)
)
```

### Tabla `facultad`

```text
facultad (
  PK id_facultad varchar(10),
  ubicacion varchar(80),
  nombre_facultad varchar(80) not null,
  correo_institucional varchar(80) unique
)
```

### Tabla `programa_academico`

```text
programa_academico (
  PK id_programa_academico varchar(20),
  FK id_facultad(facultad.id_facultad) not null,
  nombre_programa varchar(80) not null,
  estado enum('Activo', 'Inactivo') not null,
  modalidad enum('Presencial', 'Virtual', 'Hibrida') not null,
  nivel_formacion enum('Tecnico', 'Tecnologico', 'Pregrado', 'Especializacion', 'Maestria', 'Doctorado') not null
)
```

### Tabla `periodo_academico`

```text
periodo_academico (
  PK id_periodo_academico varchar(10),
  fecha_inicio date not null,
  fecha_final date not null,
  estado enum('Planeado', 'Activo', 'Finalizado', 'Cancelado') not null,
  check(fecha_final > fecha_inicio)
)
```

### Tabla `tarifa_matricula`

```text
tarifa_matricula (
  PK id_tarifa_matricula uuid default gen_random_uuid(),
  FK id_programa_academico(programa_academico.id_programa_academico) not null,
  FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
  valor_matricula numeric(12,2) not null,
  fecha_limite_ordinaria date not null,
  fecha_limite_extraordinaria date not null,
  estado enum('Activa', 'Inactiva') not null,
  unique(id_programa_academico, id_periodo_academico),
  check(valor_matricula >= 0),
  check(fecha_limite_extraordinaria >= fecha_limite_ordinaria)
)
```

### Tabla `recibo`

```text
recibo (
  PK id_recibo uuid default gen_random_uuid(),
  FK id_estudiante(estudiante.id_estudiante) not null,
  FK id_tarifa_matricula(tarifa_matricula.id_tarifa_matricula) not null,
  fecha_pago date,
  valor_pagado numeric(12,2),
  metodo_pago enum('Efectivo', 'Tarjeta', 'PSE', 'Transferencia', 'Consignacion'),
  estado_pago enum('Pendiente', 'Pagado', 'Vencido', 'Anulado') not null,
  extras numeric(12,2) default 0,
  unique(id_estudiante, id_tarifa_matricula),
  check(valor_pagado >= 0),
  check(extras >= 0)
)
```

### Tabla `matricula`

```text
matricula (
  PK id_matricula uuid default gen_random_uuid(),
  FK id_recibo(recibo.id_recibo) not null unique,
  estado_matricula enum('Pendiente', 'Activa', 'Finalizada', 'Cancelada', 'Anulada') not null
)
```

### Tabla `asignatura`

```text
asignatura (
  PK cod_asignatura varchar(20),
  nombre_asignatura varchar(80) not null,
  creditos int not null,
  estado enum('Activa', 'Inactiva') not null,
  horas_teoria int not null,
  horas_pract int not null,
  homologable boolean not null,
  check(creditos > 0),
  check(horas_teoria >= 0),
  check(horas_pract >= 0),
  check(homologable = false or horas_pract = 0)
)
```

### Tabla `programa_asignatura`

```text
programa_asignatura (
  PK id_programa_asignatura uuid default gen_random_uuid(),
  FK id_programa_academico(programa_academico.id_programa_academico) not null,
  FK cod_asignatura(asignatura.cod_asignatura) not null,
  semestre_sugerido int not null,
  tipo_asignatura enum('Obligatoria', 'Electiva') not null,
  estado enum('Activa', 'Inactiva') not null,
  unique(id_programa_academico, cod_asignatura),
  check(semestre_sugerido > 0)
)
```

### Tabla `pre_requisitos`

```text
pre_requisitos (
  PK id_pre_requisito uuid default gen_random_uuid(),
  FK id_programa_academico(programa_academico.id_programa_academico) not null,
  FK id_programa_asignatura(programa_asignatura.id_programa_asignatura) not null,
  FK id_programa_asignatura_requisito(programa_asignatura.id_programa_asignatura) not null,
  unique(id_programa_asignatura, id_programa_asignatura_requisito),
  check(id_programa_asignatura <> id_programa_asignatura_requisito)
)
```

### Tabla `grupo`

```text
grupo (
  PK id_grupo uuid default gen_random_uuid(),
  FK id_programa_asignatura(programa_asignatura.id_programa_asignatura) not null,
  FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
  FK id_docente(profesor.id_profesor),
  codigo_grupo varchar(20) not null,
  cupo_maximo int not null,
  estado_grupo enum('Abierto', 'En curso', 'Finalizado', 'Cancelado') not null,
  unique(id_programa_asignatura, id_periodo_academico, codigo_grupo),
  check(cupo_maximo > 0)
)
```

### Tabla `inscripcion`

```text
inscripcion (
  PK id_inscripcion uuid default gen_random_uuid(),
  FK id_grupo(grupo.id_grupo) not null,
  FK id_estudiante(estudiante.id_estudiante) not null,
  nota1 numeric(3,2),
  nota2 numeric(3,2),
  nota3 numeric(3,2),
  nota_final numeric(3,2),
  intento int not null,
  estado_inscripcion enum('Cursando', 'Aprobada', 'Reprobada', 'Cancelada') not null,
  unique(id_grupo, id_estudiante),
  check(nota1 between 0 and 5),
  check(nota2 between 0 and 5),
  check(nota3 between 0 and 5),
  check(nota_final between 0 and 5),
  check(intento > 0)
)
```

### Tabla `homologacion`

```text
homologacion (
  PK id_homologacion uuid default gen_random_uuid(),
  FK id_profesor_evaluador(profesor.id_profesor) not null,
  FK id_estudiante(estudiante.id_estudiante) not null,
  asignatura_origen varchar(100) not null,
  institucion_origen varchar(100) not null,
  FK id_programa_asignatura(programa_asignatura.id_programa_asignatura) not null,
  fecha_solicitud date not null,
  estado_homologacion enum('Solicitada', 'En revision', 'Aprobada', 'Rechazada', 'Cancelada') not null,
  observacion varchar(255),
  fecha_respuesta date,
  nota_obtenida numeric(3,2),
  check(nota_obtenida between 0 and 5)
)
```

### Tabla `decano`

```text
decano (
  PK id_decano uuid default gen_random_uuid(),
  FK id_profesor(profesor.id_profesor) not null,
  FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
  FK id_facultad(facultad.id_facultad) not null,
  unique(id_facultad, id_periodo_academico)
)
```

### Tabla `coordinador`

```text
coordinador (
  PK id_coordinador uuid default gen_random_uuid(),
  FK id_profesor(profesor.id_profesor) not null,
  FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
  FK id_programa_academico(programa_academico.id_programa_academico) not null,
  unique(id_programa_academico, id_periodo_academico)
)
```
