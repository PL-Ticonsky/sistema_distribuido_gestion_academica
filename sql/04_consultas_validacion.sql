-- valida la cantidad de registros por tabla
select 'usuario' as tabla, count(*) as total_registros from usuario
union all
select 'facultad' as tabla, count(*) as total_registros from facultad
union all
select 'programa_academico' as tabla, count(*) as total_registros from programa_academico
union all
select 'periodo_academico' as tabla, count(*) as total_registros from periodo_academico
union all
select 'estudiante' as tabla, count(*) as total_registros from estudiante
union all
select 'profesor' as tabla, count(*) as total_registros from profesor
union all
select 'administrativo' as tabla, count(*) as total_registros from administrativo
union all
select 'asignatura' as tabla, count(*) as total_registros from asignatura
union all
select 'programa_asignatura' as tabla, count(*) as total_registros from programa_asignatura
union all
select 'pre_requisito' as tabla, count(*) as total_registros from pre_requisito
union all
select 'grupo' as tabla, count(*) as total_registros from grupo
union all
select 'tarifa_matricula' as tabla, count(*) as total_registros from tarifa_matricula
union all
select 'recibo' as tabla, count(*) as total_registros from recibo
union all
select 'matricula' as tabla, count(*) as total_registros from matricula
union all
select 'inscripcion' as tabla, count(*) as total_registros from inscripcion
union all
select 'homologacion' as tabla, count(*) as total_registros from homologacion
union all
select 'decano' as tabla, count(*) as total_registros from decano
union all
select 'coordinador' as tabla, count(*) as total_registros from coordinador
union all
select 'auditoria' as tabla, count(*) as total_registros from auditoria
order by tabla;

-- valida usuarios con sus roles funcionales
select
    u.nombre as usuario,
    u.correo,
    case when e.id_estudiante is not null then 'si' else 'no' end as estudiante,
    case when p.id_profesor is not null then 'si' else 'no' end as profesor,
    case when a.id_administrativo is not null then 'si' else 'no' end as administrativo,
    case
        when e.id_estudiante is not null and p.id_profesor is not null
            then 'estudiante-profesor'
        when e.id_estudiante is not null
            then 'estudiante'
        when p.id_profesor is not null
            then 'profesor'
        when a.id_administrativo is not null
            then 'administrativo'
        else 'sin rol especializado'
    end as rol_funcional
from usuario u
left join estudiante e on e.id_usuario = u.id_usuario
left join profesor p on p.id_usuario = u.id_usuario
left join administrativo a on a.id_usuario = u.id_usuario
order by rol_funcional, usuario;

-- valida estudiantes por programa academico y facultad
select
    f.nombre_facultad,
    pa.nombre_programa,
    u.nombre as estudiante,
    e.estado_estudiante
from estudiante e
join usuario u on u.id_usuario = e.id_usuario
join programa_academico pa on pa.id_programa_academico = e.id_programa_academico
join facultad f on f.id_facultad = pa.id_facultad
order by f.nombre_facultad, pa.nombre_programa, u.nombre;

-- valida cantidad de estudiantes por programa academico y facultad
select
    f.nombre_facultad,
    pa.nombre_programa,
    count(e.id_estudiante) as total_estudiantes
from programa_academico pa
join facultad f on f.id_facultad = pa.id_facultad
left join estudiante e on e.id_programa_academico = pa.id_programa_academico
group by f.nombre_facultad, pa.nombre_programa
order by f.nombre_facultad, pa.nombre_programa;

-- valida profesores por facultad
select
    f.nombre_facultad,
    u.nombre as profesor,
    p.categoria,
    p.vinculacion
from profesor p
join usuario u on u.id_usuario = p.id_usuario
join facultad f on f.id_facultad = p.id_facultad
order by f.nombre_facultad, u.nombre;

-- valida programas academicos por facultad
select
    f.nombre_facultad,
    pa.id_programa_academico,
    pa.nombre_programa,
    pa.estado,
    pa.modalidad,
    pa.nivel_formacion
from programa_academico pa
join facultad f on f.id_facultad = pa.id_facultad
order by f.nombre_facultad, pa.nombre_programa;

-- valida asignaturas por programa academico
select
    pa.nombre_programa,
    a.cod_asignatura,
    a.nombre_asignatura,
    pga.semestre_sugerido,
    pga.tipo_asignatura,
    pga.estado
from programa_asignatura pga
join programa_academico pa
    on pa.id_programa_academico = pga.id_programa_academico
join asignatura a on a.cod_asignatura = pga.cod_asignatura
order by pa.nombre_programa, pga.semestre_sugerido, a.nombre_asignatura;

-- valida prerrequisitos por asignatura
select
    pa.nombre_programa,
    a.nombre_asignatura as asignatura,
    ar.nombre_asignatura as prerrequisito
from pre_requisito pr
join programa_academico pa
    on pa.id_programa_academico = pr.id_programa_academico
join programa_asignatura pga
    on pga.id_programa_asignatura = pr.id_programa_asignatura
join asignatura a on a.cod_asignatura = pga.cod_asignatura
join programa_asignatura pgar
    on pgar.id_programa_asignatura = pr.id_programa_asignatura_requisito
join asignatura ar on ar.cod_asignatura = pgar.cod_asignatura
order by pa.nombre_programa, asignatura, prerrequisito;

-- valida grupos ofertados por periodo academico
select
    pe.id_periodo_academico,
    pa.nombre_programa,
    a.nombre_asignatura,
    g.codigo_grupo,
    g.estado_grupo,
    u.nombre as profesor
from grupo g
join periodo_academico pe
    on pe.id_periodo_academico = g.id_periodo_academico
join programa_asignatura pga
    on pga.id_programa_asignatura = g.id_programa_asignatura
join programa_academico pa
    on pa.id_programa_academico = pga.id_programa_academico
join asignatura a on a.cod_asignatura = pga.cod_asignatura
left join profesor p on p.id_profesor = g.id_profesor
left join usuario u on u.id_usuario = p.id_usuario
order by pe.id_periodo_academico, pa.nombre_programa, a.nombre_asignatura, g.codigo_grupo;

-- valida cupos por grupo
select
    pe.id_periodo_academico,
    pa.nombre_programa,
    a.nombre_asignatura,
    g.codigo_grupo,
    g.cupo_maximo,
    count(i.id_inscripcion) as cantidad_inscritos,
    g.cupo_maximo - count(i.id_inscripcion) as cupos_disponibles
from grupo g
join periodo_academico pe
    on pe.id_periodo_academico = g.id_periodo_academico
join programa_asignatura pga
    on pga.id_programa_asignatura = g.id_programa_asignatura
join programa_academico pa
    on pa.id_programa_academico = pga.id_programa_academico
join asignatura a on a.cod_asignatura = pga.cod_asignatura
left join inscripcion i on i.id_grupo = g.id_grupo
group by
    pe.id_periodo_academico,
    pa.nombre_programa,
    a.nombre_asignatura,
    g.codigo_grupo,
    g.cupo_maximo
order by pe.id_periodo_academico, pa.nombre_programa, a.nombre_asignatura, g.codigo_grupo;

-- valida inscripciones por estudiante
select
    ue.nombre as estudiante,
    pa.nombre_programa as programa,
    a.nombre_asignatura as asignatura,
    g.codigo_grupo as grupo,
    i.estado_inscripcion as estado,
    i.nota_final
from inscripcion i
join estudiante e on e.id_estudiante = i.id_estudiante
join usuario ue on ue.id_usuario = e.id_usuario
join programa_academico pa
    on pa.id_programa_academico = e.id_programa_academico
join grupo g on g.id_grupo = i.id_grupo
join programa_asignatura pga
    on pga.id_programa_asignatura = g.id_programa_asignatura
join asignatura a on a.cod_asignatura = pga.cod_asignatura
order by ue.nombre, a.nombre_asignatura, g.codigo_grupo;

-- valida promedio academico por estudiante calculado desde inscripcion
select
    ue.nombre as estudiante,
    pa.nombre_programa as programa,
    avg(i.nota_final) as promedio_nota_final,
    count(i.nota_final) as asignaturas_con_nota_final
from estudiante e
join usuario ue on ue.id_usuario = e.id_usuario
join programa_academico pa
    on pa.id_programa_academico = e.id_programa_academico
left join inscripcion i
    on i.id_estudiante = e.id_estudiante
   and i.nota_final is not null
group by ue.nombre, pa.nombre_programa
order by ue.nombre;

-- valida asignaturas aprobadas y reprobadas por estudiante
select
    ue.nombre as estudiante,
    pa.nombre_programa as programa,
    sum(case when i.estado_inscripcion = 'Aprobada' then 1 else 0 end) as aprobadas,
    sum(case when i.estado_inscripcion = 'Reprobada' then 1 else 0 end) as reprobadas,
    sum(case when i.estado_inscripcion = 'Cursando' then 1 else 0 end) as cursando,
    sum(case when i.estado_inscripcion = 'Cancelada' then 1 else 0 end) as canceladas
from estudiante e
join usuario ue on ue.id_usuario = e.id_usuario
join programa_academico pa
    on pa.id_programa_academico = e.id_programa_academico
left join inscripcion i on i.id_estudiante = e.id_estudiante
group by ue.nombre, pa.nombre_programa
order by ue.nombre;

-- valida recibos por estudiante
select
    ue.nombre as estudiante,
    pa.nombre_programa as programa,
    pe.id_periodo_academico,
    r.estado_pago,
    r.valor_pagado,
    r.fecha_pago,
    r.metodo_pago,
    r.extras
from recibo r
join estudiante e on e.id_estudiante = r.id_estudiante
join usuario ue on ue.id_usuario = e.id_usuario
join tarifa_matricula tm
    on tm.id_tarifa_matricula = r.id_tarifa_matricula
join programa_academico pa
    on pa.id_programa_academico = tm.id_programa_academico
join periodo_academico pe
    on pe.id_periodo_academico = tm.id_periodo_academico
order by ue.nombre, pe.id_periodo_academico;

-- valida matriculas por estudiante
select
    ue.nombre as estudiante,
    pa.nombre_programa as programa,
    pe.id_periodo_academico,
    m.estado_matricula,
    r.estado_pago
from matricula m
join recibo r on r.id_recibo = m.id_recibo
join estudiante e on e.id_estudiante = r.id_estudiante
join usuario ue on ue.id_usuario = e.id_usuario
join tarifa_matricula tm
    on tm.id_tarifa_matricula = r.id_tarifa_matricula
join programa_academico pa
    on pa.id_programa_academico = tm.id_programa_academico
join periodo_academico pe
    on pe.id_periodo_academico = tm.id_periodo_academico
order by ue.nombre, pe.id_periodo_academico;

-- valida homologaciones por estudiante
select
    ue.nombre as estudiante,
    pa.nombre_programa as programa,
    h.asignatura_origen,
    h.institucion_origen,
    a.nombre_asignatura as asignatura_homologada,
    h.estado_homologacion as estado,
    h.nota_obtenida
from homologacion h
join estudiante e on e.id_estudiante = h.id_estudiante
join usuario ue on ue.id_usuario = e.id_usuario
join programa_asignatura pga
    on pga.id_programa_asignatura = h.id_programa_asignatura
join programa_academico pa
    on pa.id_programa_academico = pga.id_programa_academico
join asignatura a on a.cod_asignatura = pga.cod_asignatura
order by ue.nombre, h.fecha_solicitud, a.nombre_asignatura;

-- valida decanos por facultad y periodo
select
    f.nombre_facultad,
    pe.id_periodo_academico,
    u.nombre as decano,
    p.categoria,
    p.vinculacion
from decano d
join facultad f on f.id_facultad = d.id_facultad
join periodo_academico pe
    on pe.id_periodo_academico = d.id_periodo_academico
join profesor p on p.id_profesor = d.id_profesor
join usuario u on u.id_usuario = p.id_usuario
order by pe.id_periodo_academico, f.nombre_facultad;

-- valida coordinadores por programa y periodo
select
    pa.nombre_programa,
    f.nombre_facultad,
    pe.id_periodo_academico,
    u.nombre as coordinador,
    p.categoria,
    p.vinculacion
from coordinador c
join programa_academico pa
    on pa.id_programa_academico = c.id_programa_academico
join facultad f on f.id_facultad = pa.id_facultad
join periodo_academico pe
    on pe.id_periodo_academico = c.id_periodo_academico
join profesor p on p.id_profesor = c.id_profesor
join usuario u on u.id_usuario = p.id_usuario
order by pe.id_periodo_academico, pa.nombre_programa;

-- valida auditoria por usuario
select
    u.nombre as usuario,
    u.correo,
    a.accion_realizada,
    a.fecha_hora,
    a.descripcion
from auditoria a
join usuario u on u.id_usuario = a.id_usuario
order by a.fecha_hora, u.nombre;
