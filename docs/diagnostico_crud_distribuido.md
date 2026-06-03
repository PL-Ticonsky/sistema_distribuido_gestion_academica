# Diagnostico para CRUD distribuido

Estado: diagnostico previo a implementacion de CRUD distribuido.

Fecha: 2026-06-02.

Rama validada: `feature/migracion-distribuida-completa`.

## Objetivo

Evaluar si la escritura distribuida puede hacerse manteniendo Django conectado
unicamente a `sga_central` como base `default`, usando las foreign tables de los
esquemas `fdw_*` para escribir hacia los nodos de facultad.

Este documento no implementa formularios, vistas CRUD ni `DatabaseRouter`.

## Verificacion inicial

| Verificacion | Resultado |
| --- | --- |
| Rama actual | `feature/migracion-distribuida-completa` |
| Estado inicial de Git | Limpio |
| Base default Django | `sga_central` |
| Conexion runtime Django | `sga_central` |
| Migraciones nuevas | No |
| `makemigrations` | No ejecutado |
| Scripts SQL | No modificados |

`backend/config/settings.py` mantiene:

```text
DATABASES["default"]["NAME"] = env("POSTGRES_DB", default="sga_central")
```

## Estado de esquemas FDW

Los cinco esquemas esperados existen en `sga_central` y exponen las tablas
operativas como foreign tables:

| Esquema | Estado |
| --- | --- |
| `fdw_ingenieria` | OK |
| `fdw_ciencias_educacion` | OK |
| `fdw_tecnologica` | OK |
| `fdw_medio_ambiente` | OK |
| `fdw_artes` | OK |

Tablas operativas encontradas en todos los esquemas:

| Tabla | `fdw_ingenieria` | `fdw_ciencias_educacion` | `fdw_tecnologica` | `fdw_medio_ambiente` | `fdw_artes` |
| --- | --- | --- | --- | --- | --- |
| `estudiante` | OK | OK | OK | OK | OK |
| `profesor` | OK | OK | OK | OK | OK |
| `administrativo` | OK | OK | OK | OK | OK |
| `programa_asignatura` | OK | OK | OK | OK | OK |
| `pre_requisito` | OK | OK | OK | OK | OK |
| `grupo` | OK | OK | OK | OK | OK |
| `matricula` | OK | OK | OK | OK | OK |
| `inscripcion` | OK | OK | OK | OK | OK |
| `homologacion` | OK | OK | OK | OK | OK |
| `decano` | OK | OK | OK | OK | OK |
| `coordinador` | OK | OK | OK | OK | OK |

## Columnas reales en `fdw_ingenieria`

### `fdw_ingenieria.estudiante`

| Columna | Tipo | Nulo |
| --- | --- | --- |
| `id_estudiante` | `uuid` | No |
| `id_usuario` | `uuid` | No |
| `id_facultad` | `character varying` | No |
| `id_programa_academico` | `character varying` | No |
| `limite_matriculas` | `integer` | No |
| `estado_estudiante` | `character varying` | No |

### `fdw_ingenieria.grupo`

| Columna | Tipo | Nulo |
| --- | --- | --- |
| `id_grupo` | `uuid` | No |
| `id_facultad` | `character varying` | No |
| `id_programa_asignatura` | `uuid` | No |
| `id_periodo_academico` | `character varying` | No |
| `id_profesor` | `uuid` | Si |
| `codigo_grupo` | `character varying` | No |
| `cupo_maximo` | `integer` | No |
| `estado_grupo` | `character varying` | No |

### `fdw_ingenieria.inscripcion`

| Columna | Tipo | Nulo |
| --- | --- | --- |
| `id_inscripcion` | `uuid` | No |
| `id_facultad` | `character varying` | No |
| `id_grupo` | `uuid` | No |
| `id_estudiante` | `uuid` | No |
| `nota1` | `numeric` | Si |
| `nota2` | `numeric` | Si |
| `nota3` | `numeric` | Si |
| `nota_final` | `numeric` | Si |
| `intento` | `integer` | No |
| `estado_inscripcion` | `character varying` | No |

### `fdw_ingenieria.homologacion`

| Columna | Tipo | Nulo |
| --- | --- | --- |
| `id_homologacion` | `uuid` | No |
| `id_facultad` | `character varying` | No |
| `id_profesor_evaluador` | `uuid` | No |
| `id_estudiante` | `uuid` | No |
| `asignatura_origen` | `character varying` | No |
| `institucion_origen` | `character varying` | No |
| `id_programa_asignatura` | `uuid` | No |
| `fecha_solicitud` | `date` | No |
| `estado_homologacion` | `character varying` | No |
| `observacion` | `character varying` | Si |
| `fecha_respuesta` | `date` | Si |
| `nota_obtenida` | `numeric` | Si |

### `fdw_ingenieria.matricula`

| Columna | Tipo | Nulo |
| --- | --- | --- |
| `id_matricula` | `uuid` | No |
| `id_facultad` | `character varying` | No |
| `id_estudiante` | `uuid` | No |
| `id_recibo` | `uuid` | No |
| `estado_matricula` | `character varying` | No |

## Comparacion entre facultades

La estructura de columnas de estas tablas se repite igual en
`fdw_ciencias_educacion`, `fdw_tecnologica`, `fdw_medio_ambiente` y `fdw_artes`:

| Tabla | Resultado |
| --- | --- |
| `estudiante` | SAME |
| `grupo` | SAME |
| `inscripcion` | SAME |
| `homologacion` | SAME |
| `matricula` | SAME |

## Prueba controlada de escritura FDW

La prueba se ejecuto sobre `fdw_ingenieria.estudiante` dentro de transaccion
manual, sin `COMMIT`.

Primera prueba:

| Operacion | Resultado |
| --- | --- |
| `INSERT` con `limite_matriculas = 0` | Falla por `CHECK` remoto |
| `ROLLBACK` | OK |
| Filas dummy despues de prueba | `0` |

El error remoto fue:

```text
new row for relation "estudiante" violates check constraint "estudiante_limite_matriculas_check"
```

Segunda prueba con `limite_matriculas = 1`:

| Operacion | Resultado |
| --- | --- |
| `INSERT` dummy | OK |
| `UPDATE` dummy | OK |
| `DELETE` dummy | OK |
| `ROLLBACK` | OK |
| Filas dummy despues de prueba | `0` |

Conclusion: `postgres_fdw` permite `INSERT`, `UPDATE` y `DELETE` hacia
`fdw_ingenieria.estudiante`, siempre que se respeten las reglas remotas.

## Dependencias por CRUD

| CRUD | Dependencias requeridas | Ubicacion esperada |
| --- | --- | --- |
| `estudiante` | `usuario`, `programa_academico`, `facultad` | `public.usuario` para login/identidad Django; `institucional.programa_academico` y `institucional.facultad`; escritura operativa en `fdw_* .estudiante`. |
| `grupo` | `programa_asignatura`, `periodo_academico`, `profesor` opcional | `fdw_* .programa_asignatura`; `institucional.periodo_academico`; `fdw_* .profesor`; escritura en `fdw_* .grupo`. |
| `inscripcion` | `estudiante`, `grupo`, validacion academica y posible matricula activa | `fdw_* .estudiante`, `fdw_* .grupo`, `fdw_* .matricula`; escritura en `fdw_* .inscripcion`. |
| `homologacion` | `estudiante`, `profesor` evaluador, `programa_asignatura` | `fdw_* .estudiante`, `fdw_* .profesor`, `fdw_* .programa_asignatura`; escritura en `fdw_* .homologacion`. |
| `matricula` | `estudiante`, `recibo` | `fdw_* .estudiante`; recibos/finanzas segun contrato financiero; escritura en `fdw_* .matricula`. |
| `programa_asignatura` | `programa_academico`, `asignatura` | Catalogo central `institucional.*`; si se replica por facultad, escritura en `fdw_* .programa_asignatura`. |
| `pre_requisito` | `programa_asignatura` y requisito | `fdw_* .programa_asignatura`; escritura en `fdw_* .pre_requisito`. |
| `profesor`, `administrativo`, `decano`, `coordinador` | `usuario`, `facultad`, periodo/programa segun tabla | `public.usuario`, `institucional.*`; escritura operativa en `fdw_*`. |

## Mapeo de facultad a esquema

| `id_facultad` | Esquema FDW |
| --- | --- |
| `FING` | `fdw_ingenieria` |
| `FCE` | `fdw_ciencias_educacion` |
| `FTEC` | `fdw_tecnologica` |
| `FMA` | `fdw_medio_ambiente` |
| `FART` | `fdw_artes` |

La seleccion del esquema debe derivarse de `id_facultad`, no de entrada libre
del usuario.

## Estrategia recomendada de escritura

1. Implementar primero CRUD de `estudiante` en una sola facultad piloto
   (`FING`), porque ya se comprobo `INSERT/UPDATE/DELETE` con rollback sobre
   `fdw_ingenieria.estudiante`.
2. Extender `estudiante` a las demas facultades usando el mismo mapeo
   `id_facultad -> fdw_*`, validando que cada nodo acepte la misma transaccion.
3. Implementar CRUD de `grupo`, porque sus dependencias son claras y
   `id_profesor` es opcional.
4. Implementar CRUD de `homologacion` en modo controlado, validando primero que
   estudiante, profesor y programa_asignatura pertenezcan al mismo esquema FDW.
5. Implementar CRUD de `inscripcion` despues de tener reglas explicitas para
   cupos, intentos, prerrequisitos y estado de matricula.
6. Implementar CRUD de `matricula` despues de cerrar el contrato con recibos y
   financiera, porque depende de `id_recibo`.

## Tablas centrales vs distribuidas

| Tipo de dato | Escritura recomendada |
| --- | --- |
| Login, grupos Django y sesiones | `public.*` en `sga_central` |
| Catalogos institucionales globales | `institucional.*` en `sga_central` |
| Tarifas y recibos centrales | `financiero.*` en `sga_central`, si el contrato financiero se mantiene central |
| Estudiante, profesor, administrativo | `fdw_*` segun facultad |
| Grupo, inscripcion, homologacion, matricula | `fdw_*` segun facultad |
| Reportes y vistas | Solo lectura |

## Riesgos

- Las foreign tables no exponen en `information_schema` local todas las
  constraints remotas; las reglas se manifiestan al ejecutar la operacion.
- Los formularios deben validar reglas remotas antes de escribir para evitar
  errores tardios de FDW.
- Debe evitarse construir nombres de esquema con texto libre; usar siempre un
  mapeo cerrado de `id_facultad`.
- Si una operacion necesita escribir en tabla central y tabla FDW en la misma
  accion, debe definirse estrategia transaccional y manejo de rollback.
- `inscripcion` y `matricula` requieren validaciones funcionales mas fuertes
  que `estudiante`.
- No se debe introducir `DatabaseRouter` todavia; la conexion sigue siendo
  unica hacia `sga_central`.

## Validaciones posteriores requeridas

```bash
uv run python backend/manage.py check
uv run ruff check backend/apps backend/config
```

Nota de entorno: si `uv` no puede escribir en `~/.cache/uv`, usar una cache
temporal local, por ejemplo:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run python backend/manage.py check
```
