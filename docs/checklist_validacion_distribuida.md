# Checklist de validacion distribuida

Estado general: OK con pendientes documentados.

Fecha de validacion: 2026-06-02.

## Verificacion inicial

| Verificacion | Evidencia esperada | Estado |
| --- | --- | --- |
| Rama activa | `feature/migracion-distribuida-completa` | OK |
| Base default Django | `sga_central` en `backend/config/settings.py` | OK |
| Conexion activa | `DB_CONNECTION_NAME sga_central` | OK |
| SQL | Sin cambios en scripts SQL | OK |
| Migraciones | Sin migraciones nuevas y sin `makemigrations` | OK |
| Escritura distribuida | No implementada | OK |

## Rutas probadas con login real

Usuario usado: `admin.fing@universidad.edu`.

| Ruta | Evidencia esperada | Estado |
| --- | --- | --- |
| `/login/` | `302` a `/dashboard/` si ya esta autenticado | OK |
| `/dashboard/` | `200` | OK |
| `/estructura/facultades/` | `200` | OK |
| `/estructura/programas/` | `200` | OK |
| `/estructura/periodos/` | `200` | OK |
| `/estructura/asignaturas/` | `200` | OK |
| `/academica/estudiantes/` | `200` | OK |
| `/academica/profesores/` | `200` | OK |
| `/academica/docentes/` | `200` | OK |
| `/academica/grupos/` | `200` | OK |
| `/academica/inscripciones/` | `200` | OK |
| `/financiera/tarifas/` | `200` | OK |
| `/financiera/recibos/` | `200` | OK |
| `/financiera/matriculas/` | `200` | OK |
| `/homologaciones/` | `200` | OK |
| `/homologaciones/solicitudes/` | `200` | OK |
| `/homologaciones/pendientes/` | `200` | OK |
| `/reportes/` | `200` | OK |
| `/reportes/consultas/` | `200` | OK |
| `/auditoria/` | `200` | OK |
| `/indicadores/` | `200` | OK |

## Consultas institucionales probadas

| Consulta | Ruta | Evidencia esperada | Estado |
| --- | --- | --- | --- |
| 1 | `/reportes/consultas/1/` | `200` | OK |
| 2 | `/reportes/consultas/2/` | `200` | OK |
| 3 | `/reportes/consultas/3/` | `200` | OK |
| 4 | `/reportes/consultas/4/` | `200` | OK |
| 5 | `/reportes/consultas/5/` | `200` | OK |
| 6 | `/reportes/consultas/6/` | `200` | OK |
| 7 | `/reportes/consultas/7/` | `200` | OK |
| 8 | `/reportes/consultas/8/` | `200` | OK |
| 9 | `/reportes/consultas/9/` | `200` | OK |
| 10 | `/reportes/consultas/10/` | `200` | OK |
| 11 | `/reportes/consultas/11/` | `200` | OK |
| 12 | `/reportes/consultas/12/` | `200` | OK |
| 13 | `/reportes/consultas/13/` | `200` | OK |
| 14 | `/reportes/consultas/14/` | `200` | OK |
| 15 | `/reportes/consultas/15/` | `200` | OK |
| 16 | `/reportes/consultas/16/` | `200` | OK |
| 17 | `/reportes/consultas/17/` | `200` | OK |
| 18 | `/reportes/consultas/18/` | `200` | OK |
| 19 | `/reportes/consultas/19/` | `200` | OK |
| 20 | `/reportes/consultas/20/` | `200` | OK |

## Apps pendientes

| App | Revision | Estado |
| --- | --- | --- |
| `backend/apps/auditoria` | Ajustada de `public.auditoria` implicita a `auditoria.auditoria` con `managed = False`. | OK |
| `backend/apps/indicadores` | Ajustada para calcular desde vistas `reportes.*` y catalogo `institucional.asignatura`, sin escritura. | OK |

## Comandos de validacion

| Comando | Evidencia esperada | Estado |
| --- | --- | --- |
| `uv run python backend/manage.py check` | `System check identified no issues (0 silenced).` | OK |
| `uv run ruff check backend/apps backend/config` | `All checks passed!` | OK |

## Observaciones

- No se ejecutaron `makemigrations` ni `migrate`.
- No se modificaron scripts SQL.
- No se tocaron bases fisicas de facultad desde Django.
- Los cambios de codigo fueron ajustes de mapeo/lectura en modelos, vistas y
  plantillas.
- `/indicadores/mis-indicadores/` con superadmin redirige a `/dashboard/` si el
  usuario no tiene registro de estudiante asociado.
