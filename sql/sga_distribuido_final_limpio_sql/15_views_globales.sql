-- 15_views_globales.sql - Ejecutar conectado a sga_central.
create OR replace view reportes.vw_usuarios_global AS
SELECT
    p.id_usuario,
    p.nombre,
    p.tipo_de_documento,
    p.numero_de_documento,
    p.correo,
    p.direccion,
    c.last_login,
    c.is_superuser,
    c.is_staff,
    c.is_active,
    c.date_joined
FROM personas.usuario_dato_personal p
JOIN seguridad.usuario_credencial c ON c.id_usuario=p.id_usuario;

create OR replace view reportes.vw_estudiantes_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.estudiante
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.estudiante
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.estudiante
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.estudiante
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.estudiante;

create OR replace view reportes.vw_profesores_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.profesor
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.profesor
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.profesor
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.profesor
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.profesor;

create OR replace view reportes.vw_administrativos_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.administrativo
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.administrativo
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.administrativo
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.administrativo
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.administrativo;

create OR replace view reportes.vw_programa_asignatura_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.programa_asignatura
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.programa_asignatura
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.programa_asignatura
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.programa_asignatura
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.programa_asignatura;

create OR replace view reportes.vw_pre_requisitos_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.pre_requisito
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.pre_requisito
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.pre_requisito
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.pre_requisito
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.pre_requisito;

create OR replace view reportes.vw_grupos_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.grupo
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.grupo
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.grupo
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.grupo
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.grupo;

create OR replace view reportes.vw_matriculas_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.matricula
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.matricula
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.matricula
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.matricula
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.matricula;

create OR replace view reportes.vw_inscripciones_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.inscripcion
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.inscripcion
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.inscripcion
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.inscripcion
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.inscripcion;

create OR replace view reportes.vw_homologaciones_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.homologacion
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.homologacion
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.homologacion
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.homologacion
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.homologacion;

create OR replace view reportes.vw_decanos_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.decano
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.decano
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.decano
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.decano
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.decano;

create OR replace view reportes.vw_coordinadores_global AS
SELECT 'facultad_ingenieria' AS nodo_origen, *
FROM fdw_ingenieria.coordinador
UNION ALL SELECT 'facultad_ciencias_educacion' AS nodo_origen, *
FROM fdw_ciencias_educacion.coordinador
UNION ALL SELECT 'facultad_tecnologica' AS nodo_origen, *
FROM fdw_tecnologica.coordinador
UNION ALL SELECT 'facultad_medio_ambiente' AS nodo_origen, *
FROM fdw_medio_ambiente.coordinador
UNION ALL SELECT 'facultad_artes' AS nodo_origen, *
FROM fdw_artes.coordinador;

create OR replace view reportes.vw_estudiantes_detalle AS
SELECT
    e.nodo_origen,
    e.id_estudiante,
    e.id_usuario,
    e.id_facultad,
    f.nombre_facultad,
    e.id_programa_academico,
    pa.nombre_programa,
    u.nombre AS estudiante,
    u.correo,
    e.estado_estudiante,
    e.limite_matriculas
FROM reportes.vw_estudiantes_global e
JOIN reportes.vw_usuarios_global u ON u.id_usuario=e.id_usuario
JOIN institucional.programa_academico pa ON pa.id_programa_academico=e.id_programa_academico
JOIN institucional.facultad f ON f.id_facultad=e.id_facultad;

create OR replace view reportes.vw_profesores_detalle AS
SELECT
    p.nodo_origen,
    p.id_profesor,
    p.id_usuario,
    p.id_facultad,
    f.nombre_facultad,
    u.nombre AS profesor,
    u.correo,
    p.categoria,
    p.vinculacion
FROM reportes.vw_profesores_global p
JOIN reportes.vw_usuarios_global u ON u.id_usuario=p.id_usuario
JOIN institucional.facultad f ON f.id_facultad=p.id_facultad;

create OR replace view reportes.vw_grupos_detalle AS
SELECT
    g.nodo_origen,
    g.id_grupo,
    g.id_facultad,
    f.nombre_facultad,
    g.id_periodo_academico,
    pa.id_programa_academico,
    pa.nombre_programa,
    pga.id_programa_asignatura,
    a.cod_asignatura,
    a.nombre_asignatura,
    a.creditos,
    g.codigo_grupo,
    g.estado_grupo,
    g.cupo_maximo,
    p.id_profesor,
    up.nombre AS profesor
FROM reportes.vw_grupos_global g
JOIN reportes.vw_programa_asignatura_global pga ON pga.id_programa_asignatura=g.id_programa_asignatura AND pga.id_facultad=g.id_facultad
JOIN institucional.programa_academico pa ON pa.id_programa_academico=pga.id_programa_academico
JOIN institucional.facultad f ON f.id_facultad=g.id_facultad
JOIN institucional.asignatura a ON a.cod_asignatura=pga.cod_asignatura
LEFT JOIN reportes.vw_profesores_global p ON p.id_profesor=g.id_profesor AND p.id_facultad=g.id_facultad
LEFT JOIN reportes.vw_usuarios_global up ON up.id_usuario=p.id_usuario;

create OR replace view reportes.vw_inscripciones_detalle AS
SELECT
    i.nodo_origen,
    i.id_inscripcion,
    i.id_facultad,
    f.nombre_facultad,
    e.id_estudiante,
    ue.nombre AS estudiante,
    e.id_programa_academico,
    pa.nombre_programa,
    g.id_periodo_academico,
    a.cod_asignatura,
    a.nombre_asignatura,
    a.creditos,
    g.id_grupo,
    g.codigo_grupo,
    g.id_profesor,
    up.nombre AS profesor,
    i.nota_final,
    i.intento,
    i.estado_inscripcion
FROM reportes.vw_inscripciones_global i
JOIN reportes.vw_estudiantes_global e ON e.id_estudiante=i.id_estudiante AND e.id_facultad=i.id_facultad
JOIN reportes.vw_usuarios_global ue ON ue.id_usuario=e.id_usuario
JOIN reportes.vw_grupos_global g ON g.id_grupo=i.id_grupo AND g.id_facultad=i.id_facultad
JOIN reportes.vw_programa_asignatura_global pga ON pga.id_programa_asignatura=g.id_programa_asignatura AND pga.id_facultad=g.id_facultad
JOIN institucional.programa_academico pa ON pa.id_programa_academico=e.id_programa_academico
JOIN institucional.facultad f ON f.id_facultad=i.id_facultad
JOIN institucional.asignatura a ON a.cod_asignatura=pga.cod_asignatura
LEFT JOIN reportes.vw_profesores_global p ON p.id_profesor=g.id_profesor AND p.id_facultad=g.id_facultad
LEFT JOIN reportes.vw_usuarios_global up ON up.id_usuario=p.id_usuario;

create OR replace view reportes.vw_matriculas_detalle AS
SELECT
    m.nodo_origen,
    m.id_matricula,
    m.id_facultad,
    f.nombre_facultad,
    e.id_estudiante,
    ue.nombre AS estudiante,
    e.id_programa_academico,
    pa.nombre_programa,
    pe.id_periodo_academico,
    m.estado_matricula,
    r.estado_pago,
    r.valor_pagado,
    r.fecha_pago,
    r.id_recibo
FROM reportes.vw_matriculas_global m
JOIN reportes.vw_estudiantes_global e ON e.id_estudiante=m.id_estudiante AND e.id_facultad=m.id_facultad
JOIN reportes.vw_usuarios_global ue ON ue.id_usuario=e.id_usuario
JOIN financiero.recibo r ON r.id_recibo=m.id_recibo AND r.id_facultad=m.id_facultad
JOIN financiero.tarifa_matricula tm ON tm.id_tarifa_matricula=r.id_tarifa_matricula
JOIN institucional.programa_academico pa ON pa.id_programa_academico=e.id_programa_academico
JOIN institucional.facultad f ON f.id_facultad=m.id_facultad
JOIN institucional.periodo_academico pe ON pe.id_periodo_academico=tm.id_periodo_academico;
