# Migracion a sga_central

Estado: version distribuida funcional validada.

Rama validada: `feature/migracion-distribuida-completa`.

Fecha de validacion: 2026-06-03.

## Objetivo

Documentar la arquitectura final usada por Django para operar sobre
`sga_central` como base principal, con lectura global por vistas y escritura
distribuida a traves de esquemas FDW controlados desde la aplicacion.

## Arquitectura final

La base `default` de Django es `sga_central`. En
`backend/config/settings.py`, el valor por defecto de `POSTGRES_DB` es:

```text
sga_central
```

No se usa `gestion_academica_local` como base default y no se agrego
`DatabaseRouter`.

| Dominio | Fuente o destino | Uso |
| --- | --- | --- |
| Login Django | `public.usuario`, `public.auth_group`, `public.usuario_groups`, `public.django_session` | Autenticacion, roles y sesiones. |
| Estructura | `institucional.*` | Facultades, programas, periodos y asignaturas. |
| Lectura academica | `reportes.vw_estudiantes_detalle`, `reportes.vw_profesores_detalle`, `reportes.vw_grupos_detalle`, `reportes.vw_inscripciones_detalle` | Listados y detalles globales. |
| Escritura academica | `fdw_*.estudiante`, `fdw_*.grupo`, `fdw_*.inscripcion` | CRUD distribuido segun facultad. |
| Homologaciones | `reportes.vw_homologaciones_global` para lectura y `fdw_*.homologacion` para escritura | Solicitudes, evaluacion y cancelacion. |
| Financiera central | `financiero.tarifa_matricula`, `financiero.recibo` | CRUD de tarifas y recibos. |
| Matriculas | `reportes.vw_matriculas_detalle` para lectura y `fdw_*.matricula` para escritura | CRUD distribuido de matriculas. |
| Reportes | `reportes.*` | Consultas institucionales 1 a 20. |
| Auditoria | `auditoria.auditoria` | Trazabilidad minima de operaciones CRUD. |

Los modelos que consumen tablas/vistas externas se mantienen con
`managed = False`. Django no crea ni modifica el esquema distribuido.

## Mapeo FDW

La escritura distribuida no permite que el usuario escriba manualmente el
esquema. El esquema se deriva desde `id_facultad` y un mapeo interno:

| Facultad | Esquema FDW |
| --- | --- |
| `FING` | `fdw_ingenieria` |
| `FCE` | `fdw_ciencias_educacion` |
| `FTEC` | `fdw_tecnologica` |
| `FMA` | `fdw_medio_ambiente` |
| `FART` | `fdw_artes` |

## CRUD implementado

Academica:

- Estudiantes: crear, editar y desactivar.
- Grupos: crear, editar y cancelar.
- Inscripciones: crear, editar y cancelar.

Homologaciones:

- Crear, editar, asignar/evaluar y cancelar.
- La lectura global usa `reportes.vw_homologaciones_global`.
- Si la vista no trae nombres legibles, algunas pantallas muestran UUIDs.

Financiera:

- Tarifas: crear, editar y desactivar en `financiero.tarifa_matricula`.
- Recibos: crear, editar y anular en `financiero.recibo`.
- Matriculas: crear, editar y cancelar en `fdw_*.matricula`, con lectura desde
  `reportes.vw_matriculas_detalle`.

Auditoria:

- Las operaciones CRUD registran accion, usuario, fecha, tabla/esquema y
  descripcion en `auditoria.auditoria`.
- Si el registro de auditoria falla, la operacion principal no se bloquea.
- No se registran contrasenas, hashes ni datos sensibles.

## Comandos de preparacion local

Comandos usados o requeridos para preparar usuarios y roles demo:

```bash
uv run python backend/manage.py ensure_central_demo_user
uv run python backend/manage.py sync_legacy_users_to_central --apply
uv run python backend/manage.py reset_demo_users_passwords --password 'Demo12345*' --all-users --apply
uv run python backend/manage.py sync_central_roles --apply
```

Advertencia: estos comandos son para entorno local o academico. El comando de
reseteo de contrasenas no debe ejecutarse en produccion.

## Comandos de validacion

```bash
uv run python backend/manage.py check
uv run ruff check backend/apps backend/config
```

## Rutas funcionales principales

- `/login/`
- `/dashboard/`
- `/estructura/facultades/`
- `/estructura/programas/`
- `/estructura/periodos/`
- `/estructura/asignaturas/`
- `/academica/estudiantes/`
- `/academica/grupos/`
- `/academica/inscripciones/`
- `/homologaciones/`
- `/homologaciones/solicitudes/`
- `/homologaciones/pendientes/`
- `/financiera/tarifas/`
- `/financiera/recibos/`
- `/financiera/matriculas/`
- `/reportes/`
- `/reportes/consultas/`
- `/reportes/consultas/1/` a `/reportes/consultas/20/`
- `/auditoria/`
- `/auditoria/registros/`

## Limitaciones actuales

- No se usa `DatabaseRouter`.
- La escritura distribuida se hace via `fdw_*` desde `sga_central`.
- Django no toca bases fisicas de facultad directamente.
- Homologaciones puede mostrar UUIDs si la vista global no trae nombres
  legibles.
- `/admin/` no es obligatorio para la demo.
- No se modificaron scripts SQL.
- No se crearon migraciones.
