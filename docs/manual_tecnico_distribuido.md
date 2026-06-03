# Manual tecnico distribuido

## Proposito

Este manual resume como esta conectada la version distribuida del sistema de
gestion academica en Django. El objetivo es reproducir la configuracion local,
entender las fuentes de datos y validar la version sin modificar SQL ni generar
migraciones.

## Base de datos

Django usa una unica conexion `default` hacia `sga_central`. El valor por
defecto esta en `backend/config/settings.py`:

```text
POSTGRES_DB=sga_central
```

No se usa `DatabaseRouter`. La separacion distribuida se resuelve con tablas,
vistas y esquemas disponibles dentro de `sga_central`.

## Fuentes por modulo

| Modulo | Lectura | Escritura |
| --- | --- | --- |
| Accounts | `public.usuario`, grupos Django y sesiones | `public.usuario` solo para operaciones propias de autenticacion/usuarios demo |
| Estructura | `institucional.facultad`, `institucional.programa_academico`, `institucional.periodo_academico`, `institucional.asignatura` | No aplica en la demo validada |
| Academica | `reportes.vw_estudiantes_detalle`, `reportes.vw_grupos_detalle`, `reportes.vw_inscripciones_detalle` | `fdw_*.estudiante`, `fdw_*.grupo`, `fdw_*.inscripcion` |
| Homologaciones | `reportes.vw_homologaciones_global` | `fdw_*.homologacion` |
| Financiera | `financiero.tarifa_matricula`, `financiero.recibo`, `reportes.vw_matriculas_detalle` | `financiero.tarifa_matricula`, `financiero.recibo`, `fdw_*.matricula` |
| Reportes | `reportes.*` | No aplica |
| Auditoria | `auditoria.auditoria` | `auditoria.auditoria` |

## Mapeo distribuido

Las funciones de escritura derivan el esquema desde `id_facultad`.

| Facultad | Esquema |
| --- | --- |
| `FING` | `fdw_ingenieria` |
| `FCE` | `fdw_ciencias_educacion` |
| `FTEC` | `fdw_tecnologica` |
| `FMA` | `fdw_medio_ambiente` |
| `FART` | `fdw_artes` |

El usuario no introduce el esquema FDW. La aplicacion lo selecciona desde el
mapeo interno y usa SQL parametrizado para los valores.

## Preparacion de usuarios demo

```bash
uv run python backend/manage.py ensure_central_demo_user
uv run python backend/manage.py sync_legacy_users_to_central --apply
uv run python backend/manage.py reset_demo_users_passwords --password 'Demo12345*' --all-users --apply
uv run python backend/manage.py sync_central_roles --apply
```

Estos comandos son para entorno local o academico. No deben ejecutarse en
produccion sin revision.

## Validacion funcional

Rutas principales:

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

CRUD validado:

- Estudiantes: crear, editar, desactivar.
- Grupos: crear, editar, cancelar.
- Inscripciones: crear, editar, cancelar.
- Homologaciones: crear, editar, evaluar, cancelar.
- Tarifas: crear, editar, desactivar.
- Recibos: crear, editar, anular.
- Matriculas: crear, editar, cancelar.

## Auditoria

Las operaciones CRUD registran en `auditoria.auditoria`:

- `id_auditoria`
- `id_usuario`
- `esquema_afectado`
- `tabla_afectada`
- `accion_realizada`
- `fecha_hora`
- `descripcion`

El helper de auditoria resuelve el usuario operativo de Django contra
`personas.usuario_dato_personal` cuando el UUID de login no coincide con la
llave foranea de auditoria. Si no puede registrar, captura el error y no bloquea
la operacion principal.

## Comandos de verificacion

```bash
uv run python backend/manage.py check
uv run ruff check backend/apps backend/config
```

## Limitaciones

- No se usa `DatabaseRouter`.
- La escritura distribuida se hace via `fdw_*` desde `sga_central`.
- No se modifican scripts SQL desde Django.
- No se generan migraciones para las tablas distribuidas.
- Homologaciones puede mostrar UUIDs si la vista no trae nombres legibles.
- `/admin/` no es obligatorio para la demo.
