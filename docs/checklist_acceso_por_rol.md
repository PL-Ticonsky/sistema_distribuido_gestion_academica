# Checklist de validacion de acceso por rol

Password demo usada en todos los casos: `Demo12345*`.

| Usuario probado | Rol observado | Ruta/caso | Resultado esperado | Resultado obtenido |
| --- | --- | --- | --- | --- |
| `estudiante1.fing@universidad.edu` | estudiante | `/dashboard/` | 200 | 200 |
| `estudiante1.fing@universidad.edu` | estudiante | `/academica/inscripciones/` | Solo inscripciones propias | 5 inscripciones propias |
| `estudiante1.fing@universidad.edu` | estudiante | `/financiera/matriculas/` | Solo matriculas propias | 2 matriculas propias |
| `estudiante1.fing@universidad.edu` | estudiante | `/homologaciones/` | Solo homologaciones propias | 0 homologaciones propias en los datos actuales |
| `estudiante1.fing@universidad.edu` | estudiante | Detalle de inscripcion ajena | 403 o 404 | 404 |
| `estudiante1.fing@universidad.edu` | estudiante | `/academica/planes/` | Solo asignaturas del programa propio | 200 |
| `estudiante1.fing@universidad.edu` | estudiante | `/academica/inscripciones/crear/` | Estudiante fijo, sin notas ni estado manual | 200; campos sensibles ocultos |
| `estudiante1.fing@universidad.edu` | estudiante | Edicion directa de inscripcion propia | 403 o 404 | 403 |
| `estudiante1.fing@universidad.edu` | estudiante | `/homologaciones/crear/` | Sin selector de evaluador | 200; evaluador oculto |
| `docente.puro.fing@universidad.edu` | docente | Login demo | Autenticacion correcta y grupo docente unico | OK; grupos `docente` |
| `docente.puro.fing@universidad.edu` | docente | `reportes.vw_profesores_detalle` | Registro academico en FING | 1 registro |
| `docente.puro.fing@universidad.edu` | docente | `/academica/grupos/`, `/academica/inscripciones/`, `/homologaciones/` | Acceso docente sin roles extra | 200 |
| `docente2.fing@universidad.edu` | docente, coordinador | `/academica/grupos/` | Grupos de su alcance | 8 grupos del programa/alcance |
| `docente2.fing@universidad.edu` | docente, coordinador | Grupo fuera de alcance | 403 o 404 | 404 |
| `docente2.fart@universidad.edu` | docente, coordinador | Estudiantes por programa | Solo `ARTM` | Solo `ARTM` |
| `docente1.fart@universidad.edu` | docente, decano | Estudiantes por facultad | Solo `FART` | Solo `FART` |
| `docente1.fart@universidad.edu` | docente, decano | Estudiante de otra facultad | 403 o 404 | 404 |
| `admin.fart@universidad.edu` | administrativo | `/financiera/matriculas/` y `/financiera/recibos/` | Solo `FART` | Solo `FART` |
| `admin.fing@universidad.edu` | administrativo, superadmin | Estudiantes y matriculas | Vista global | 30 estudiantes y 50 matriculas |

## Rutas protegidas con filtros de backend

- `/academica/estudiantes/`
- `/academica/grupos/`
- `/academica/inscripciones/`
- `/homologaciones/`
- `/financiera/tarifas/`
- `/financiera/recibos/`
- `/financiera/matriculas/`
- `/estructura/facultades/`
- `/estructura/programas/`
- reportes sensibles de estudiantes, profesores, grupos, inscripciones,
  matriculas y homologaciones.

## Validaciones finales ejecutadas

- `uv run python backend/manage.py check`
- `uv run ruff check backend/apps backend/config`
- `uv run python backend/manage.py ensure_student_login_users --dry-run`
- `uv run python backend/manage.py ensure_student_login_users --apply --reset-password`
- `uv run python backend/manage.py ensure_pure_teacher_demo_user --dry-run`
- `uv run python backend/manage.py ensure_pure_teacher_demo_user --apply --reset-password`
