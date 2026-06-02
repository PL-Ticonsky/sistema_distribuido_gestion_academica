# 14. Validación local del DDL inicial

## 1. Objetivo de la validación

El objetivo de esta validación es comprobar que el script `sql/01_ddl.sql` puede ejecutarse correctamente en una base PostgreSQL local vacía y que crea las tablas iniciales del sistema de gestión académica universitaria.

Esta validación permite confirmar que el DDL inicial contiene únicamente la extensión necesaria, tablas y restricciones simples, sin incluir triggers, funciones, vistas, roles, grants, procedimientos almacenados ni inserciones de datos.

## 2. Ambiente usado

La validación se realizó en un ambiente local de desarrollo:

```text
Base de datos: gestion_academica_local
Motor: PostgreSQL local
Herramienta de administración: DBeaver
Esquema usado: public
```

Este ambiente corresponde a la primera fase del proyecto, orientada a desarrollo y validación local antes de preparar una configuración cloud.

## 3. Script ejecutado

El script ejecutado fue:

```text
sql/01_ddl.sql
```

El archivo contiene el DDL inicial del sistema y debe ejecutarse sobre una base PostgreSQL vacía.

## 4. Resultado esperado

El resultado esperado es la creación de todas las tablas iniciales dentro del esquema `public` de la base `gestion_academica_local`.

Además, se espera que PostgreSQL cree las restricciones definidas en el DDL:

```text
primary key
foreign key
unique
check
not null
```

## 5. Tablas esperadas

Después de ejecutar `sql/01_ddl.sql`, deben existir las siguientes tablas en el esquema `public`:

```text
usuario
facultad
programa_academico
periodo_academico
estudiante
profesor
administrativo
asignatura
programa_asignatura
pre_requisito
grupo
tarifa_matricula
recibo
matricula
inscripcion
homologacion
decano
coordinador
auditoria
```

## 6. Consultas SQL de verificación

### 6.1. Verificar tablas creadas en el esquema public

```sql
select
    table_name
from information_schema.tables
where table_schema = 'public'
  and table_type = 'BASE TABLE'
order by table_name;
```

### 6.2. Verificar cantidad de tablas del modelo académico

```sql
select
    count(*) as total_tablas
from information_schema.tables
where table_schema = 'public'
  and table_type = 'BASE TABLE'
  and table_name in (
      'usuario',
      'facultad',
      'programa_academico',
      'periodo_academico',
      'estudiante',
      'profesor',
      'administrativo',
      'asignatura',
      'programa_asignatura',
      'pre_requisito',
      'grupo',
      'tarifa_matricula',
      'recibo',
      'matricula',
      'inscripcion',
      'homologacion',
      'decano',
      'coordinador',
      'auditoria'
  );
```

El valor esperado de `total_tablas` es:

```text
19
```

### 6.3. Verificar tablas faltantes

```sql
with tablas_esperadas(table_name) as (
    values
        ('usuario'),
        ('facultad'),
        ('programa_academico'),
        ('periodo_academico'),
        ('estudiante'),
        ('profesor'),
        ('administrativo'),
        ('asignatura'),
        ('programa_asignatura'),
        ('pre_requisito'),
        ('grupo'),
        ('tarifa_matricula'),
        ('recibo'),
        ('matricula'),
        ('inscripcion'),
        ('homologacion'),
        ('decano'),
        ('coordinador'),
        ('auditoria')
)
select
    te.table_name
from tablas_esperadas te
left join information_schema.tables t
    on t.table_schema = 'public'
   and t.table_type = 'BASE TABLE'
   and t.table_name = te.table_name
where t.table_name is null
order by te.table_name;
```

El resultado esperado es:

```text
0 filas
```

### 6.4. Verificar restricciones creadas

```sql
select
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
from information_schema.table_constraints tc
where tc.table_schema = 'public'
  and tc.table_name in (
      'usuario',
      'facultad',
      'programa_academico',
      'periodo_academico',
      'estudiante',
      'profesor',
      'administrativo',
      'asignatura',
      'programa_asignatura',
      'pre_requisito',
      'grupo',
      'tarifa_matricula',
      'recibo',
      'matricula',
      'inscripcion',
      'homologacion',
      'decano',
      'coordinador',
      'auditoria'
  )
order by
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name;
```

### 6.5. Verificar extensión pgcrypto

```sql
select
    extname
from pg_extension
where extname = 'pgcrypto';
```

El resultado esperado es:

```text
pgcrypto
```

## 7. Nota sobre ambiente cloud

Esta validación local confirma que el DDL inicial funciona sobre PostgreSQL local usando DBeaver y la base `gestion_academica_local`.

Sin embargo, esta validación no reemplaza la futura configuración cloud. En una etapa posterior, el proyecto deberá preparar y validar la conexión hacia Azure Database for PostgreSQL Flexible Server usando variables de entorno, credenciales no versionadas y configuración segura de conexión.
