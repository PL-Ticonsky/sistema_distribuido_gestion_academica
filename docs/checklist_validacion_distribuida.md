# Checklist de validacion distribuida

Estado general: OK.

Fecha de validacion: 2026-06-03.

Usuario usado: `admin.fing@universidad.edu`.

## Verificacion inicial

| Verificacion | Evidencia | Estado |
| --- | --- | --- |
| Rama activa | `feature/migracion-distribuida-completa` | OK |
| Arbol de trabajo inicial | Limpio antes de documentar | OK |
| Base default Django | `POSTGRES_DB` default `sga_central` | OK |
| Conexion activa | `current_database() = sga_central` | OK |
| SQL | Sin cambios en scripts SQL | OK |
| Migraciones | Sin migraciones nuevas y sin `makemigrations` | OK |
| Router | Sin `DatabaseRouter` | OK |

## Rutas probadas

| Ruta | Resultado | Estado |
| --- | --- | --- |
| `/login/` | `302` autenticado | OK |
| `/dashboard/` | `200` | OK |
| `/estructura/facultades/` | `200` | OK |
| `/estructura/programas/` | `200` | OK |
| `/estructura/periodos/` | `200` | OK |
| `/estructura/asignaturas/` | `200` | OK |
| `/academica/estudiantes/` | `200` | OK |
| `/academica/grupos/` | `200` | OK |
| `/academica/inscripciones/` | `200` | OK |
| `/homologaciones/` | `200` | OK |
| `/homologaciones/solicitudes/` | `200` | OK |
| `/homologaciones/pendientes/` | `200` | OK |
| `/financiera/tarifas/` | `200` | OK |
| `/financiera/recibos/` | `200` | OK |
| `/financiera/matriculas/` | `200` | OK |
| `/reportes/` | `200` | OK |
| `/reportes/consultas/` | `200` | OK |
| `/auditoria/` | `200` | OK |
| `/auditoria/registros/` | `200` | OK |

## Consultas institucionales

| Rango | Evidencia | Estado |
| --- | --- | --- |
| `/reportes/consultas/1/` a `/reportes/consultas/20/` | Todas respondieron `200` | OK |

## CRUD probado con rollback

Se ejecuto una transaccion de validacion con periodo temporal `TSTEND01` y
rollback final. No quedo data dummy.

| Flujo | Operaciones | Estado |
| --- | --- | --- |
| Estudiante | Crear, editar, desactivar | OK |
| Grupo | Crear, editar, cancelar | OK |
| Inscripcion | Crear, editar, cancelar | OK |
| Homologacion | Crear, editar, evaluar, cancelar | OK |
| Tarifa | Crear, editar, desactivar | OK |
| Recibo | Crear, editar, anular | OK |
| Matricula | Crear, editar, cancelar | OK |
| Auditoria | Registro `CREAR_MATRICULA` verificado | OK |

## Evidencia de rollback

| Objeto | Conteo posterior | Estado |
| --- | --- | --- |
| `institucional.periodo_academico` temporal | `0` | OK |
| `reportes.vw_estudiantes_detalle` temporal | `0` | OK |
| `reportes.vw_grupos_detalle` temporal | `0` | OK |
| `reportes.vw_inscripciones_detalle` temporal | `0` | OK |
| `reportes.vw_homologaciones_global` temporal | `0` | OK |
| `financiero.tarifa_matricula` temporal | `0` | OK |
| `financiero.recibo` temporal | `0` | OK |
| `reportes.vw_matriculas_detalle` temporal | `0` | OK |
| `auditoria.auditoria` temporal | `0` | OK |

## Comandos finales

| Comando | Resultado | Estado |
| --- | --- | --- |
| `uv run python backend/manage.py check` | `System check identified no issues (0 silenced).` | OK |
| `uv run ruff check backend/apps backend/config` | `All checks passed!` | OK |

## Observaciones

- No se ejecuto `makemigrations`.
- No se ejecuto `migrate`.
- No se modificaron scripts SQL.
- No se uso `gestion_academica_local`.
- No se tocaron bases fisicas directamente desde Django.
- La escritura distribuida se valido desde `sga_central` via `fdw_*`.
