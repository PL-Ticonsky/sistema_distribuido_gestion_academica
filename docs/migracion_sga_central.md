# Migracion a sga_central

Estado: validacion final de la version distribuida en modo lectura.

Rama validada: `feature/migracion-distribuida-completa`.

## Objetivo

Documentar la migracion distribuida usada por Django para operar sobre
`sga_central` como base principal, conservar el login operativo centralizado y
consumir informacion academica, financiera, institucional y de reportes sin
modificar las bases fisicas de facultad desde la aplicacion.

## Arquitectura usada por Django

La base `default` de Django es `sga_central`, configurada en
`backend/config/settings.py` mediante:

```text
POSTGRES_DB=sga_central
```

Si la variable `POSTGRES_DB` no se define, el valor por defecto tambien es
`sga_central`. No se debe volver a usar `gestion_academica_local` como base
`default` para esta fase.

La aplicacion consume principalmente estas fuentes:

| Dominio | Fuente en `sga_central` | Uso en Django |
| --- | --- | --- |
| Login operativo | `public.usuario`, `public.usuario_groups`, `public.auth_group`, `public.django_session` | Autenticacion, roles y sesiones de Django. |
| Estructura | `institucional.*` | Facultades, programas, periodos y asignaturas. |
| Academica consolidada | `reportes.*` y vistas globales | Listados de estudiantes, profesores, grupos e inscripciones. |
| Financiera | `financiero.*` y `reportes.*` | Tarifas, recibos y matriculas. |
| Homologaciones | `reportes.vw_homologaciones_global` | Consulta global de solicitudes y pendientes. |
| Reportes institucionales | `reportes.*` | Consultas 1 a 20 y vistas consolidadas. |
| Auditoria | `auditoria.auditoria` | Consulta de trazabilidad para superadmin. |
| Indicadores | `reportes.vw_estudiantes_detalle`, `reportes.vw_inscripciones_detalle`, `reportes.vw_programa_asignatura_global`, `reportes.vw_homologaciones_global` | Calculo de indicadores en modo lectura. |

Los modelos que consumen estas fuentes se mantienen como `managed = False`.
Esto evita que Django intente crear, borrar o modificar tablas y vistas
distribuidas.

## Comandos de preparacion local

Estos comandos fueron definidos para preparar usuarios y roles centrales en un
entorno local o academico:

```bash
uv run python backend/manage.py ensure_central_demo_user
uv run python backend/manage.py sync_legacy_users_to_central --apply
uv run python backend/manage.py reset_demo_users_passwords --password 'Demo12345*' --all-users --apply
uv run python backend/manage.py sync_central_roles --apply
```

Advertencia: los comandos demo son solo para entorno local o academico. En
especial, `reset_demo_users_passwords` cambia contrasenas de usuarios
seleccionados y no debe ejecutarse en produccion.

## Validacion ejecutada

Se valido login real con:

```text
admin.fing@universidad.edu / Demo12345*
```

La autenticacion fue correcta y la conexion activa confirmo:

```text
DB_DEFAULT_NAME sga_central
DB_CONNECTION_NAME sga_central
```

Rutas principales validadas:

| Ruta | Estado |
| --- | --- |
| `/login/` | OK, redirige a `/dashboard/` si el usuario ya esta autenticado. |
| `/dashboard/` | OK |
| `/estructura/facultades/` | OK |
| `/estructura/programas/` | OK |
| `/estructura/periodos/` | OK |
| `/estructura/asignaturas/` | OK |
| `/academica/estudiantes/` | OK |
| `/academica/profesores/` | OK |
| `/academica/docentes/` | OK |
| `/academica/grupos/` | OK |
| `/academica/inscripciones/` | OK |
| `/financiera/tarifas/` | OK |
| `/financiera/recibos/` | OK |
| `/financiera/matriculas/` | OK |
| `/homologaciones/` | OK |
| `/homologaciones/solicitudes/` | OK |
| `/homologaciones/pendientes/` | OK |
| `/reportes/` | OK |
| `/reportes/consultas/` | OK |
| `/reportes/consultas/1/` a `/reportes/consultas/20/` | OK |
| `/auditoria/` | OK |
| `/indicadores/` | OK |

## Apps pendientes revisadas

`backend/apps/auditoria` quedo ajustada a solo lectura sobre
`auditoria.auditoria`. Antes apuntaba a una tabla desnuda `auditoria`, que en
`sga_central` resolvia como `public.auditoria` y fallaba porque esa relacion no
existe.

`backend/apps/indicadores` quedo ajustada a solo lectura sobre vistas
`reportes.*`. Antes dependia de modelos academicos que buscaban relaciones
desnudas como `public.estudiante`; en `sga_central` esas relaciones se exponen
por vistas globales y no por tablas `public.*`.

## Limitaciones actuales

- Escritura distribuida no implementada.
- Django no debe tocar bases fisicas de facultad.
- No se modificaron scripts SQL.
- No se crearon migraciones nuevas.
- Homologaciones usa `reportes.vw_homologaciones_global`; la vista actual no
  expone nombres legibles de estudiante o profesor evaluador.
- `django_admin_log` puede quedar pendiente si `/admin/` no se usa en esta fase.
- La validacion de login crea/usa sesion Django y puede actualizar campos
  operativos propios de autenticacion; los modulos funcionales validados se
  mantienen en modo lectura.

## Comandos de validacion final

```bash
uv run python backend/manage.py check
uv run ruff check backend/apps backend/config
```

Nota de entorno: dentro del sandbox, `uv run` fallo al intentar escribir en
`~/.cache/uv`. La validacion se ejecuto fuera del sandbox con aprobacion para que
`uv` usara su cache local; ese fallo inicial fue del entorno, no del proyecto.
