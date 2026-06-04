# Matriz de acceso por roles

Esta matriz describe el control de acceso aplicado en backend para la version
distribuida sobre `sga_central`. Las listas y detalles sensibles se filtran por
queryset; un acceso directo por URL a objetos fuera del alcance retorna 404.

| Rol | Alcance | Modulos visibles | Acciones permitidas | Restricciones |
| --- | --- | --- | --- | --- |
| superadmin | Toda la universidad | Estructura, academica, financiera, homologaciones, reportes y auditoria | Crear, editar, cancelar, anular y auditar segun cada modulo | Ninguna restriccion funcional de alcance |
| estudiante | Sus propios registros academicos y financieros | Dashboard, plan de estudios, inscripciones, matriculas, recibos, homologaciones e indicadores propios | Consultar su informacion, solicitar inscripcion en grupos disponibles de su programa, cancelar inscripciones propias en curso y crear solicitudes de homologacion | No ve otros estudiantes, inscripciones, matriculas, recibos ni homologaciones ajenas; no edita notas, estado, intento ni evaluador |
| docente | Sus grupos asignados y estudiantes inscritos en esos grupos | Grupos, inscripciones/notas, homologaciones asignadas e indicadores docentes | Consultar sus grupos e inscripciones asociadas; evaluar homologaciones asignadas | No ve grupos ni inscripciones de otros docentes salvo que tenga otro rol adicional; no asigna evaluadores |
| coordinador | Programas academicos que coordina | Estudiantes, grupos, inscripciones, homologaciones, financiera y estructura de sus programas | Gestionar operaciones permitidas dentro del programa, asignar evaluadores y evaluar homologaciones | No ve programas distintos a los coordinados |
| decano | Facultades donde ejerce decanatura | Estudiantes, docentes, grupos, inscripciones, homologaciones, financiera y estructura de su facultad | Gestionar operaciones permitidas dentro de la facultad, asignar evaluadores y evaluar homologaciones | No ve facultades ajenas |
| administrativo | Facultad asignada en `reportes.vw_administrativos_global` | Financiera y consultas academicas/financieras de su facultad | Gestionar financiera dentro de su facultad | No ve informacion global salvo que tambien sea superadmin |

## Fuentes de alcance

- Usuario y grupos funcionales: `public.usuario`, `public.usuario_groups`.
- Estudiante propio: `reportes.vw_estudiantes_detalle`.
- Docente propio: `reportes.vw_profesores_detalle`.
- Administrativo: `reportes.vw_administrativos_global`.
- Coordinador: `reportes.vw_coordinadores_global`.
- Decano: `reportes.vw_decanos_global`.
- Datos academicos y financieros visibles: vistas `reportes.*` y tablas
  centrales/financieras ya usadas por la aplicacion.

## Helpers de filtrado

La aplicacion centraliza el alcance en `apps.accounts.access_context`:

- `filter_estudiantes_for_user`
- `filter_profesores_for_user`
- `filter_grupos_for_user`
- `filter_inscripciones_for_user`
- `filter_homologaciones_for_user`
- `filter_matriculas_for_user`
- `filter_recibos_for_user`
- `filter_tarifas_for_user`

## Reglas de interfaz y backend

- El plan de estudios y las asignaturas se filtran por los programas visibles
  del usuario; un estudiante ve solo asignaturas de su carrera/programa. La
  ruta academica `/academica/plan-estudios/` agrupa materias por
  `semestre_sugerido`.
- La ruta institucional `/estructura/asignaturas/` se conserva como catalogo
  global de estructura para roles de gestion; no es la vista principal del
  estudiante.
- Cada materia del plan enlaza a grupos ofertados del periodo activo mediante
  `/academica/plan-estudios/<id_programa_asignatura>/grupos/`.
- El formulario de inscripcion para estudiantes fija el estudiante actual,
  oculta notas, intento y estado, y muestra solo grupos disponibles de su
  programa. La edicion directa de una inscripcion por estudiante retorna 403.
- El backend bloquea inscripciones a asignaturas ya aprobadas, duplicados al
  mismo grupo y dos grupos de la misma asignatura en el mismo periodo activo.
- La cancelacion de inscripcion requiere confirmacion y solo se ofrece para
  inscripciones propias en estado `Cursando`.
- `/academica/inscripciones/` separa cursos actuales e historial para
  estudiantes; `/academica/mi-historial/` muestra solo historial academico.
- El detalle de grupo muestra datos del grupo e inscritos. La nota final se
  muestra a superadmin, docente del grupo, coordinador del programa, decano de
  la facultad y al estudiante solo para su propia fila.
- El formulario de homologacion para estudiantes no muestra evaluador ni estado;
  la solicitud entra como `Solicitada` y el backend toma un evaluador disponible
  de la facultad o bloquea si no existe.
- La asignacion de evaluador queda para coordinador, decano y superadmin; la
  evaluacion queda para docente, coordinador, decano y superadmin.
- Auditoria lista la accion realizada y enlaza cada fila a un detalle completo
  con usuario, fecha, esquema, tabla, descripcion e ID tecnico.
- Usuario de prueba docente puro: `docente.puro.fing@universidad.edu`, grupo
  funcional `docente` solamente, registro academico en FING.
