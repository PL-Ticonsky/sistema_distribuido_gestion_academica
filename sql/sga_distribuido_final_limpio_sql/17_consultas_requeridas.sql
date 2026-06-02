-- Ejecutar conectado a sga_central. Consultas mínimas requeridas.
-- 1
SELECT
    md.nombre_facultad,
    md.nombre_programa,
    ed.id_estudiante AS codigo_estudiante,
    ed.estudiante AS nombre_completo,
    idt.nombre_asignatura AS asignatura_inscrita,
    idt.codigo_grupo
FROM reportes.vw_matriculas_detalle md
JOIN reportes.vw_estudiantes_detalle ed ON ed.id_estudiante=md.id_estudiante AND ed.id_facultad=md.id_facultad
JOIN reportes.vw_inscripciones_detalle idt ON idt.id_estudiante=ed.id_estudiante AND idt.id_facultad=ed.id_facultad AND idt.id_periodo_academico=md.id_periodo_academico
WHERE md.id_periodo_academico='2026-1' AND md.estado_matricula='Activa' AND ed.estado_estudiante='Activo'
ORDER BY md.nombre_facultad,md.nombre_programa,ed.estudiante,idt.nombre_asignatura;

-- 2
SELECT
    gd.nombre_facultad,
    gd.profesor,
    count(distinct gd.id_grupo) AS grupos_asignados,
    count(distinct i.id_estudiante) AS total_estudiantes_matriculados,
    sum(distinct gd.creditos) AS creditos_asociados
FROM reportes.vw_grupos_detalle gd
LEFT JOIN reportes.vw_inscripciones_global i ON i.id_grupo=gd.id_grupo AND i.id_facultad=gd.id_facultad
WHERE gd.id_periodo_academico='2026-1' AND gd.id_profesor IS NOT NULL
GROUP BY gd.nombre_facultad,gd.profesor
ORDER BY total_estudiantes_matriculados DESC;

-- 3
SELECT
    nombre_facultad,
    nombre_programa,
    id_estudiante,
    estudiante,
    round(sum(nota_final*creditos)/nullif(sum(creditos),0),2) AS promedio_ponderado,
    sum(creditos) AS creditos_evaluados
FROM reportes.vw_inscripciones_detalle
WHERE nota_final IS NOT NULL
GROUP BY nombre_facultad,nombre_programa,id_estudiante,estudiante
ORDER BY nombre_facultad,nombre_programa,promedio_ponderado DESC;

-- 4
WITH promedio AS (SELECT id_estudiante,id_facultad,round(sum(nota_final*creditos)/nullif(sum(creditos),0),2) promedio_general
FROM reportes.vw_inscripciones_detalle
WHERE nota_final IS NOT NULL
GROUP BY id_estudiante,id_facultad), perdidas AS (SELECT id_estudiante,id_facultad,count(*) asignaturas_perdidas
FROM reportes.vw_inscripciones_detalle
WHERE nota_final<3.0
GROUP BY id_estudiante,id_facultad), intentos AS (SELECT id_estudiante,id_facultad,cod_asignatura,max(intento) max_intento
FROM reportes.vw_inscripciones_detalle
GROUP BY id_estudiante,id_facultad,cod_asignatura), pagos_pendientes AS (SELECT id_estudiante,id_facultad,count(*) pagos_pendientes
FROM reportes.vw_matriculas_detalle
WHERE estado_matricula='Activa' AND estado_pago<>'Pagado'
GROUP BY id_estudiante,id_facultad) SELECT ed.nombre_facultad,ed.nombre_programa,ed.id_estudiante,ed.estudiante,coalesce(p.promedio_general,0) promedio_general,coalesce(pe.asignaturas_perdidas,0) asignaturas_perdidas,max(coalesce(i.max_intento,1)) maximo_intento,coalesce(pp.pagos_pendientes,0) pagos_pendientes
FROM reportes.vw_estudiantes_detalle ed
LEFT JOIN promedio p ON p.id_estudiante=ed.id_estudiante AND p.id_facultad=ed.id_facultad
LEFT JOIN perdidas pe ON pe.id_estudiante=ed.id_estudiante AND pe.id_facultad=ed.id_facultad
LEFT JOIN intentos i ON i.id_estudiante=ed.id_estudiante AND i.id_facultad=ed.id_facultad
LEFT JOIN pagos_pendientes pp ON pp.id_estudiante=ed.id_estudiante AND pp.id_facultad=ed.id_facultad
GROUP BY ed.nombre_facultad,ed.nombre_programa,ed.id_estudiante,ed.estudiante,p.promedio_general,pe.asignaturas_perdidas,pp.pagos_pendientes
HAVING coalesce(p.promedio_general,5)<3.0 OR coalesce(pe.asignaturas_perdidas,0)>=3 OR max(coalesce(i.max_intento,1))>=2 OR coalesce(pp.pagos_pendientes,0)>0
ORDER BY ed.nombre_facultad,ed.estudiante;

-- 5
SELECT
    nombre_facultad,
    cod_asignatura,
    nombre_asignatura,
    count(*) FILTER(WHERE nota_final IS NOT NULL) estudiantes_con_nota,
    count(*) FILTER(WHERE nota_final<3.0) estudiantes_reprobados,
    round(100.0*count(*) FILTER(WHERE nota_final<3.0)/nullif(count(*) FILTER(WHERE nota_final IS NOT NULL),0),2) porcentaje_perdida
FROM reportes.vw_inscripciones_detalle
WHERE id_periodo_academico='2025-2'
GROUP BY nombre_facultad,cod_asignatura,nombre_asignatura
HAVING count(*) FILTER(WHERE nota_final IS NOT NULL)>0
ORDER BY porcentaje_perdida DESC;

-- 6
SELECT
    gd.nombre_facultad,
    gd.nombre_asignatura,
    gd.codigo_grupo,
    gd.profesor,
    gd.cupo_maximo,
    count(i.id_inscripcion) estudiantes_matriculados,
    round(100.0*count(i.id_inscripcion)/nullif(gd.cupo_maximo,0),2) porcentaje_ocupacion
FROM reportes.vw_grupos_detalle gd
LEFT JOIN reportes.vw_inscripciones_global i ON i.id_grupo=gd.id_grupo AND i.id_facultad=gd.id_facultad
WHERE gd.id_periodo_academico='2026-1'
GROUP BY gd.nombre_facultad,gd.nombre_asignatura,gd.codigo_grupo,gd.profesor,gd.cupo_maximo
HAVING round(100.0*count(i.id_inscripcion)/nullif(gd.cupo_maximo,0),2)>=90
ORDER BY porcentaje_ocupacion DESC;

-- 7
SELECT
    fo.nombre_facultad facultad_origen,
    pa.nombre_programa programa_origen,
    u.nombre estudiante,
    fd.nombre_facultad facultad_destino,
    gd.nombre_asignatura,
    gd.codigo_grupo,
    m.id_periodo_academico,
    m.estado_inscripcion
FROM movilidad.inscripcion_interfacultad m
JOIN reportes.vw_usuarios_global u ON u.id_usuario=m.id_usuario
JOIN institucional.facultad fo ON fo.id_facultad=m.id_facultad_origen
JOIN institucional.facultad fd ON fd.id_facultad=m.id_facultad_destino
JOIN institucional.programa_academico pa ON pa.id_programa_academico=m.id_programa_academico_origen
JOIN reportes.vw_grupos_detalle gd ON gd.id_grupo=m.id_grupo AND gd.id_facultad=m.id_facultad_destino
ORDER BY facultad_origen,estudiante;

-- 8
SELECT
    estudiante,
    nombre_programa,
    nombre_asignatura,
    id_periodo_academico,
    nota_final,
    estado_inscripcion AS estado_aprobacion,
    intento,
    profesor
FROM reportes.vw_inscripciones_detalle
WHERE id_estudiante='73143e06-c8db-545b-a031-69ebf6b3948a'
ORDER BY id_periodo_academico,nombre_asignatura;

-- 9
SELECT
    f.nombre_facultad,
    pa.nombre_programa,
    u.nombre estudiante,
    h.asignatura_origen,
    h.institucion_origen,
    a.nombre_asignatura AS asignatura_a_homologar,
    h.fecha_solicitud,
    (CURRENT_DATE-h.fecha_solicitud) dias_transcurridos,
    h.estado_homologacion
FROM reportes.vw_homologaciones_global h
JOIN reportes.vw_estudiantes_global e ON e.id_estudiante=h.id_estudiante AND e.id_facultad=h.id_facultad
JOIN reportes.vw_usuarios_global u ON u.id_usuario=e.id_usuario
JOIN reportes.vw_programa_asignatura_global pga ON pga.id_programa_asignatura=h.id_programa_asignatura AND pga.id_facultad=h.id_facultad
JOIN institucional.asignatura a ON a.cod_asignatura=pga.cod_asignatura
JOIN institucional.programa_academico pa ON pa.id_programa_academico=e.id_programa_academico
JOIN institucional.facultad f ON f.id_facultad=h.id_facultad
WHERE h.estado_homologacion IN ('Solicitada','En revision')
ORDER BY dias_transcurridos DESC;

-- 10
SELECT
    nombre_facultad,
    nombre_programa,
    estudiante,
    id_periodo_academico,
    estado_matricula,
    estado_pago,
    valor_pagado,
    fecha_pago
FROM reportes.vw_matriculas_detalle
WHERE id_periodo_academico='2026-1' AND estado_matricula='Activa' AND estado_pago<>'Pagado'
ORDER BY nombre_facultad,nombre_programa,estudiante;

-- 11
SELECT
    nombre_facultad,
    profesor,
    count(*) estudiantes_reprobados
FROM reportes.vw_inscripciones_detalle
WHERE id_periodo_academico='2025-2' AND nota_final<3.0 AND profesor IS NOT NULL
GROUP BY nombre_facultad,profesor
ORDER BY estudiantes_reprobados DESC;

-- 12
WITH promedios AS (SELECT nombre_facultad,nombre_programa,id_estudiante,estudiante,round(sum(nota_final*creditos)/nullif(sum(creditos),0),2) promedio_ponderado
FROM reportes.vw_inscripciones_detalle
WHERE nota_final IS NOT NULL
GROUP BY nombre_facultad,nombre_programa,id_estudiante,estudiante) SELECT *,rank() OVER(PARTITION BY nombre_facultad,nombre_programa
ORDER BY promedio_ponderado DESC) ranking_programa
FROM promedios
ORDER BY nombre_facultad,nombre_programa,ranking_programa;

-- 13
SELECT
    nombre_facultad,
    nombre_programa,
    nombre_asignatura,
    codigo_grupo,
    estado_grupo
FROM reportes.vw_grupos_detalle
WHERE id_periodo_academico='2026-1' AND estado_grupo IN ('Abierto','En curso') AND id_profesor IS NULL
ORDER BY nombre_facultad,nombre_programa,nombre_asignatura;

-- 14
WITH plan AS (SELECT id_facultad,id_programa_academico,count(distinct cod_asignatura) total_asignaturas_plan
FROM reportes.vw_programa_asignatura_global
WHERE estado='Activa'
GROUP BY id_facultad,id_programa_academico), aprobadas AS (SELECT id_facultad,id_estudiante,count(distinct cod_asignatura) asignaturas_aprobadas
FROM reportes.vw_inscripciones_detalle
WHERE estado_inscripcion='Aprobada' AND nota_final>=3.0
GROUP BY id_facultad,id_estudiante), pagos_pendientes AS (SELECT id_facultad,id_estudiante,count(*) pendientes
FROM reportes.vw_matriculas_detalle
WHERE estado_pago<>'Pagado'
GROUP BY id_facultad,id_estudiante), homologaciones_pendientes AS (SELECT id_facultad,id_estudiante,count(*) pendientes
FROM reportes.vw_homologaciones_global
WHERE estado_homologacion IN ('Solicitada','En revision')
GROUP BY id_facultad,id_estudiante) SELECT ed.nombre_facultad,ed.nombre_programa,ed.id_estudiante,ed.estudiante,coalesce(a.asignaturas_aprobadas,0) asignaturas_aprobadas,p.total_asignaturas_plan
FROM reportes.vw_estudiantes_detalle ed
JOIN plan p ON p.id_facultad=ed.id_facultad AND p.id_programa_academico=ed.id_programa_academico
LEFT JOIN aprobadas a ON a.id_facultad=ed.id_facultad AND a.id_estudiante=ed.id_estudiante
LEFT JOIN pagos_pendientes pp ON pp.id_facultad=ed.id_facultad AND pp.id_estudiante=ed.id_estudiante
LEFT JOIN homologaciones_pendientes hp ON hp.id_facultad=ed.id_facultad AND hp.id_estudiante=ed.id_estudiante
WHERE coalesce(a.asignaturas_aprobadas,0)>=p.total_asignaturas_plan AND coalesce(pp.pendientes,0)=0 AND coalesce(hp.pendientes,0)=0
ORDER BY ed.nombre_facultad,ed.nombre_programa,ed.estudiante;

-- 15
SELECT
    nombre_facultad,
    nombre_programa,
    count(*) total_estudiantes,
    count(*) FILTER(WHERE estado_estudiante IN ('Inactivo','Retirado','Suspendido')) estudiantes_inactivos_retirados_suspendidos,
    round(100.0*count(*) FILTER(WHERE estado_estudiante IN ('Inactivo','Retirado','Suspendido'))/nullif(count(*),0),2) porcentaje_desercion_inactividad
FROM reportes.vw_estudiantes_detalle
GROUP BY nombre_facultad,nombre_programa
ORDER BY porcentaje_desercion_inactividad DESC;

-- 16
WITH prerequisitos AS (SELECT pr.id_facultad,pr.id_programa_academico,pa.cod_asignatura asignatura_actual,req.cod_asignatura asignatura_requisito
FROM reportes.vw_pre_requisitos_global pr
JOIN reportes.vw_programa_asignatura_global pa ON pa.id_programa_asignatura=pr.id_programa_asignatura AND pa.id_facultad=pr.id_facultad
JOIN reportes.vw_programa_asignatura_global req ON req.id_programa_asignatura=pr.id_programa_asignatura_requisito AND req.id_facultad=pr.id_facultad), aprobadas AS (SELECT id_estudiante,id_facultad,cod_asignatura
FROM reportes.vw_inscripciones_detalle
WHERE estado_inscripcion='Aprobada' AND nota_final>=3.0) SELECT c.nombre_facultad,c.nombre_programa,c.estudiante,c.nombre_asignatura AS asignatura_matriculada,p.asignatura_requisito,c.id_periodo_academico
FROM reportes.vw_inscripciones_detalle c
JOIN prerequisitos p ON p.id_facultad=c.id_facultad AND p.id_programa_academico=c.id_programa_academico AND p.asignatura_actual=c.cod_asignatura
LEFT JOIN aprobadas a ON a.id_estudiante=c.id_estudiante AND a.id_facultad=c.id_facultad AND a.cod_asignatura=p.asignatura_requisito
WHERE c.estado_inscripcion IN ('Cursando','Aprobada','Reprobada') AND a.cod_asignatura IS NULL
ORDER BY c.nombre_facultad,c.estudiante;

-- 17
SELECT
    u.numero_de_documento identificacion,
    u.nombre nombre_completo,
    u.correo,
    'Estudiante' tipo_vinculacion,
    ed.nombre_programa facultad_o_programa_asociado
FROM reportes.vw_estudiantes_detalle ed
JOIN reportes.vw_usuarios_global u ON u.id_usuario=ed.id_usuario
UNION ALL SELECT u.numero_de_documento,u.nombre,u.correo,'Docente',pd.nombre_facultad
FROM reportes.vw_profesores_detalle pd
JOIN reportes.vw_usuarios_global u ON u.id_usuario=pd.id_usuario
ORDER BY tipo_vinculacion,nombre_completo;

-- 18
WITH actual AS (SELECT distinct id_estudiante,id_facultad
FROM reportes.vw_matriculas_detalle
WHERE id_periodo_academico='2026-1' AND estado_matricula='Activa'), perdidas_anteriores AS (SELECT distinct id_estudiante,id_facultad
FROM reportes.vw_inscripciones_detalle
WHERE id_periodo_academico<'2026-1' AND nota_final<3.0) SELECT ed.nombre_facultad,ed.nombre_programa,ed.id_estudiante,ed.estudiante
FROM actual a
JOIN perdidas_anteriores p ON p.id_estudiante=a.id_estudiante AND p.id_facultad=a.id_facultad
JOIN reportes.vw_estudiantes_detalle ed ON ed.id_estudiante=a.id_estudiante AND ed.id_facultad=a.id_facultad
ORDER BY ed.nombre_facultad,ed.nombre_programa,ed.estudiante;

-- 19
SELECT
    ed.nombre_facultad,
    ed.nombre_programa,
    ed.id_estudiante,
    ed.estudiante
FROM reportes.vw_estudiantes_detalle ed
LEFT JOIN reportes.vw_matriculas_detalle md ON md.id_estudiante=ed.id_estudiante AND md.id_facultad=ed.id_facultad AND md.id_periodo_academico='2026-1'
WHERE ed.estado_estudiante='Activo' AND md.id_matricula IS NULL
ORDER BY ed.nombre_facultad,ed.nombre_programa,ed.estudiante;

-- 20
WITH programas AS (SELECT id_facultad,count(*) programas_activos
FROM institucional.programa_academico
WHERE estado='Activo'
GROUP BY id_facultad), estudiantes AS (SELECT id_facultad,count(*) estudiantes_activos
FROM reportes.vw_estudiantes_global
WHERE estado_estudiante='Activo'
GROUP BY id_facultad), docentes AS (SELECT id_facultad,count(*) docentes_activos
FROM reportes.vw_profesores_global
GROUP BY id_facultad), asignaturas AS (SELECT id_facultad,count(distinct cod_asignatura) asignaturas_activas
FROM reportes.vw_programa_asignatura_global
WHERE estado='Activa'
GROUP BY id_facultad), grupos AS (SELECT id_facultad,count(*) grupos_ofertados
FROM reportes.vw_grupos_global
WHERE id_periodo_academico='2026-1'
GROUP BY id_facultad), promedios AS (SELECT id_facultad,round(sum(nota_final*creditos)/nullif(sum(creditos),0),2) promedio_academico_general,round(100.0*count(*) FILTER(WHERE nota_final<3.0)/nullif(count(*) FILTER(WHERE nota_final IS NOT NULL),0),2) porcentaje_perdida_academica
FROM reportes.vw_inscripciones_detalle
WHERE nota_final IS NOT NULL
GROUP BY id_facultad), pagos AS (SELECT id_facultad,count(*) FILTER(WHERE estado_pago='Pagado') total_pagos_aprobados,count(*) FILTER(WHERE estado_pago<>'Pagado') total_pagos_pendientes
FROM reportes.vw_matriculas_detalle
WHERE id_periodo_academico='2026-1'
GROUP BY id_facultad) SELECT f.nombre_facultad,coalesce(pr.programas_activos,0) programas_activos,coalesce(es.estudiantes_activos,0) estudiantes_activos,coalesce(doce.docentes_activos,0) docentes_activos,coalesce(asig.asignaturas_activas,0) asignaturas_activas,coalesce(gr.grupos_ofertados,0) grupos_ofertados,coalesce(prom.promedio_academico_general,0) promedio_academico_general,coalesce(prom.porcentaje_perdida_academica,0) porcentaje_perdida_academica,coalesce(pa.total_pagos_aprobados,0) total_pagos_aprobados,coalesce(pa.total_pagos_pendientes,0) total_pagos_pendientes
FROM institucional.facultad f
LEFT JOIN programas pr ON pr.id_facultad=f.id_facultad
LEFT JOIN estudiantes es ON es.id_facultad=f.id_facultad
LEFT JOIN docentes doce ON doce.id_facultad=f.id_facultad
LEFT JOIN asignaturas asig ON asig.id_facultad=f.id_facultad
LEFT JOIN grupos gr ON gr.id_facultad=f.id_facultad
LEFT JOIN promedios prom ON prom.id_facultad=f.id_facultad
LEFT JOIN pagos pa ON pa.id_facultad=f.id_facultad
ORDER BY f.nombre_facultad;
