from dataclasses import dataclass

from django.db import connection


@dataclass(frozen=True)
class ConsultaInstitucional:
    numero: int
    titulo: str
    descripcion: str
    sql: str


def ejecutar_sql(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
    return columns, rows


CONSULTAS = {
    1: ConsultaInstitucional(
        1,
        "Estudiantes matriculados por facultad y programa",
        "Conteo de matriculas activas por facultad, programa y periodo.",
        """
        select
            nombre_facultad,
            nombre_programa,
            id_periodo_academico,
            count(distinct id_estudiante) as estudiantes_matriculados
        from reportes.vw_matriculas_detalle
        where estado_matricula = 'Activa'
        group by nombre_facultad, nombre_programa, id_periodo_academico
        order by nombre_facultad, nombre_programa, id_periodo_academico
        """,
    ),
    2: ConsultaInstitucional(
        2,
        "Carga academica docente",
        "Grupos, asignaturas y cupos asignados por docente.",
        """
        select
            nombre_facultad,
            profesor,
            id_periodo_academico,
            count(distinct id_grupo) as grupos,
            count(distinct cod_asignatura) as asignaturas,
            sum(coalesce(cupo_maximo, 0)) as cupo_total
        from reportes.vw_grupos_detalle
        where profesor is not null
        group by nombre_facultad, profesor, id_periodo_academico
        order by nombre_facultad, profesor, id_periodo_academico
        """,
    ),
    3: ConsultaInstitucional(
        3,
        "Promedio academico por estudiante",
        "Promedio de notas finales registradas por estudiante.",
        """
        select
            estudiante,
            nombre_programa,
            nombre_facultad,
            round(avg(nota_final)::numeric, 2) as promedio,
            count(*) as asignaturas_con_nota
        from reportes.vw_inscripciones_detalle
        where nota_final is not null
        group by estudiante, nombre_programa, nombre_facultad
        order by promedio desc nulls last, estudiante
        """,
    ),
    4: ConsultaInstitucional(
        4,
        "Estudiantes en riesgo academico",
        "Estudiantes con promedio menor a 3.0 o dos o mas reprobaciones.",
        """
        select
            estudiante,
            nombre_programa,
            nombre_facultad,
            round(avg(nota_final)::numeric, 2) as promedio,
            count(*) filter (where estado_inscripcion = 'Reprobada') as reprobadas
        from reportes.vw_inscripciones_detalle
        where nota_final is not null
        group by estudiante, nombre_programa, nombre_facultad
        having avg(nota_final) < 3.0
            or count(*) filter (where estado_inscripcion = 'Reprobada') >= 2
        order by reprobadas desc, promedio asc, estudiante
        """,
    ),
    5: ConsultaInstitucional(
        5,
        "Asignaturas con mayor indice de perdida",
        "Porcentaje de inscripciones reprobadas por asignatura.",
        """
        select
            nombre_asignatura,
            nombre_programa,
            count(*) as total_inscripciones,
            count(*) filter (where estado_inscripcion = 'Reprobada') as perdidas,
            round(
                100.0 * count(*) filter (where estado_inscripcion = 'Reprobada')
                / nullif(count(*), 0),
                2
            ) as porcentaje_perdida
        from reportes.vw_inscripciones_detalle
        group by nombre_asignatura, nombre_programa
        order by porcentaje_perdida desc nulls last, perdidas desc
        """,
    ),
    6: ConsultaInstitucional(
        6,
        "Grupos con sobrecupo o cercanos al limite",
        "Grupos con ocupacion mayor o igual al 90 por ciento del cupo.",
        """
        select
            g.nombre_facultad,
            g.nombre_programa,
            g.nombre_asignatura,
            g.codigo_grupo,
            g.cupo_maximo,
            count(i.id_inscripcion) as inscritos,
            round(100.0 * count(i.id_inscripcion) / nullif(g.cupo_maximo, 0), 2)
                as ocupacion
        from reportes.vw_grupos_detalle g
        left join reportes.vw_inscripciones_detalle i on i.id_grupo = g.id_grupo
        group by
            g.nombre_facultad,
            g.nombre_programa,
            g.nombre_asignatura,
            g.codigo_grupo,
            g.cupo_maximo
        having count(i.id_inscripcion) >= coalesce(g.cupo_maximo, 0) * 0.9
        order by ocupacion desc nulls last, inscritos desc
        """,
    ),
    7: ConsultaInstitucional(
        7,
        "Estudiantes que cursan asignaturas en otra facultad",
        (
            "Inscripciones donde el nodo/facultad de origen difiere de la "
            "facultad del programa reportado."
        ),
        """
        select
            estudiante,
            nombre_programa,
            nombre_facultad,
            nodo_origen,
            nombre_asignatura,
            codigo_grupo,
            estado_inscripcion
        from reportes.vw_inscripciones_detalle
        where nodo_origen is not null
          and nombre_facultad is not null
          and lower(nodo_origen) not like '%' || lower(id_facultad) || '%'
        order by estudiante, nombre_asignatura
        """,
    ),
    8: ConsultaInstitucional(
        8,
        "Historial academico completo",
        "Historial de inscripciones y notas por estudiante.",
        """
        select
            estudiante,
            nombre_programa,
            id_periodo_academico,
            nombre_asignatura,
            codigo_grupo,
            profesor,
            nota_final,
            intento,
            estado_inscripcion
        from reportes.vw_inscripciones_detalle
        order by estudiante, id_periodo_academico, nombre_asignatura
        """,
    ),
    9: ConsultaInstitucional(
        9,
        "Homologaciones pendientes",
        "Solicitudes de homologacion pendientes o en revision.",
        """
        select
            nodo_origen,
            id_facultad,
            id_estudiante,
            id_profesor_evaluador,
            asignatura_origen,
            institucion_origen,
            fecha_solicitud,
            estado_homologacion
        from reportes.vw_homologaciones_global
        where estado_homologacion in ('Solicitada', 'En revision')
        order by fecha_solicitud, id_facultad
        """,
    ),
    10: ConsultaInstitucional(
        10,
        "Pagos pendientes por periodo",
        "Matriculas con pago pendiente por facultad, programa y periodo.",
        """
        select
            nombre_facultad,
            nombre_programa,
            id_periodo_academico,
            count(*) as pagos_pendientes
        from reportes.vw_matriculas_detalle
        where estado_pago = 'Pendiente'
        group by nombre_facultad, nombre_programa, id_periodo_academico
        order by id_periodo_academico, nombre_facultad, nombre_programa
        """,
    ),
    11: ConsultaInstitucional(
        11,
        "Docentes con mayor numero de estudiantes reprobados",
        "Docentes ordenados por estudiantes reprobados en sus grupos.",
        """
        select
            profesor,
            nombre_facultad,
            count(distinct id_estudiante) as estudiantes_reprobados,
            count(*) as inscripciones_reprobadas
        from reportes.vw_inscripciones_detalle
        where estado_inscripcion = 'Reprobada'
        group by profesor, nombre_facultad
        order by estudiantes_reprobados desc, inscripciones_reprobadas desc
        """,
    ),
    12: ConsultaInstitucional(
        12,
        "Ranking de estudiantes por programa",
        "Ranking por promedio academico dentro de cada programa.",
        """
        select
            estudiante,
            nombre_programa,
            nombre_facultad,
            round(avg(nota_final)::numeric, 2) as promedio,
            rank() over (
                partition by nombre_programa
                order by avg(nota_final) desc nulls last
            ) as puesto_programa
        from reportes.vw_inscripciones_detalle
        where nota_final is not null
        group by estudiante, nombre_programa, nombre_facultad
        order by nombre_programa, puesto_programa, estudiante
        """,
    ),
    13: ConsultaInstitucional(
        13,
        "Asignaturas sin docente asignado",
        "Grupos activos sin profesor reportado.",
        """
        select
            nombre_facultad,
            nombre_programa,
            id_periodo_academico,
            nombre_asignatura,
            codigo_grupo,
            estado_grupo
        from reportes.vw_grupos_detalle
        where id_profesor is null or profesor is null
        order by nombre_facultad, nombre_programa, nombre_asignatura
        """,
    ),
    14: ConsultaInstitucional(
        14,
        "Estudiantes que cumplen requisitos para grado",
        (
            "Aproximacion: estudiantes activos sin reprobaciones registradas "
            "y sin pagos pendientes."
        ),
        """
        select
            e.estudiante,
            e.nombre_programa,
            e.nombre_facultad,
            count(i.id_inscripcion) filter (where i.estado_inscripcion = 'Aprobada')
                as asignaturas_aprobadas,
            count(i.id_inscripcion) filter (where i.estado_inscripcion = 'Reprobada')
                as asignaturas_reprobadas,
            count(m.id_matricula) filter (where m.estado_pago = 'Pendiente')
                as pagos_pendientes
        from reportes.vw_estudiantes_detalle e
        left join reportes.vw_inscripciones_detalle i
            on i.id_estudiante = e.id_estudiante
        left join reportes.vw_matriculas_detalle m
            on m.id_estudiante = e.id_estudiante
        where e.estado_estudiante = 'Activo'
        group by e.estudiante, e.nombre_programa, e.nombre_facultad
        having count(i.id_inscripcion) filter (
                where i.estado_inscripcion = 'Reprobada'
            ) = 0
           and count(m.id_matricula) filter (where m.estado_pago = 'Pendiente') = 0
        order by e.nombre_facultad, e.nombre_programa, e.estudiante
        """,
    ),
    15: ConsultaInstitucional(
        15,
        "Programas con mayor desercion o inactividad",
        "Programas ordenados por estudiantes inactivos.",
        """
        select
            nombre_facultad,
            nombre_programa,
            count(*) as estudiantes,
            count(*) filter (where estado_estudiante <> 'Activo') as inactivos,
            round(
                100.0 * count(*) filter (where estado_estudiante <> 'Activo')
                / nullif(count(*), 0),
                2
            ) as porcentaje_inactividad
        from reportes.vw_estudiantes_detalle
        group by nombre_facultad, nombre_programa
        order by porcentaje_inactividad desc nulls last, inactivos desc
        """,
    ),
    16: ConsultaInstitucional(
        16,
        "Prerrequisitos no cumplidos",
        "Cruce de prerrequisitos globales con asignaturas aprobadas por estudiante.",
        """
        with aprobadas as (
            select distinct
                id_estudiante,
                id_programa_academico,
                cod_asignatura
            from reportes.vw_inscripciones_detalle
            where estado_inscripcion = 'Aprobada'
        )
        select
            i.estudiante,
            i.nombre_programa,
            i.nombre_asignatura as asignatura_cursada,
            pa_req.cod_asignatura as prerequisito_pendiente,
            i.estado_inscripcion,
            i.nota_final
        from reportes.vw_inscripciones_detalle i
        join reportes.vw_programa_asignatura_global pa
            on pa.cod_asignatura = i.cod_asignatura
           and pa.id_programa_academico = i.id_programa_academico
        join reportes.vw_pre_requisitos_global pr
            on pr.id_programa_asignatura = pa.id_programa_asignatura
        join reportes.vw_programa_asignatura_global pa_req
            on pa_req.id_programa_asignatura =
                pr.id_programa_asignatura_requisito
        left join aprobadas a
            on a.id_estudiante = i.id_estudiante
           and a.id_programa_academico = i.id_programa_academico
           and a.cod_asignatura = pa_req.cod_asignatura
        where a.id_estudiante is null
        order by i.estudiante, i.nombre_asignatura
        """,
    ),
    17: ConsultaInstitucional(
        17,
        "Total personas universidad",
        "Total de usuarios centrales por estado de cuenta.",
        """
        select
            count(*) as total_personas,
            count(*) filter (where is_active) as activas,
            count(*) filter (where not is_active) as inactivas,
            count(*) filter (where is_staff) as staff,
            count(*) filter (where is_superuser) as superusuarios
        from reportes.vw_usuarios_global
        """,
    ),
    18: ConsultaInstitucional(
        18,
        "Estudiantes matriculados actualmente con perdidas previas",
        "Estudiantes con matricula activa y reprobaciones registradas.",
        """
        select distinct
            m.estudiante,
            m.nombre_programa,
            m.nombre_facultad,
            m.id_periodo_academico,
            count(i.id_inscripcion) filter (where i.estado_inscripcion = 'Reprobada')
                as perdidas_previas
        from reportes.vw_matriculas_detalle m
        join reportes.vw_inscripciones_detalle i
            on i.id_estudiante = m.id_estudiante
        where m.estado_matricula = 'Activa'
        group by
            m.estudiante,
            m.nombre_programa,
            m.nombre_facultad,
            m.id_periodo_academico
        having count(i.id_inscripcion) filter (
            where i.estado_inscripcion = 'Reprobada'
        ) > 0
        order by perdidas_previas desc, m.estudiante
        """,
    ),
    19: ConsultaInstitucional(
        19,
        "Estudiantes activos sin matricula actual",
        "Estudiantes activos sin matricula activa registrada.",
        """
        select
            e.estudiante,
            e.correo,
            e.nombre_programa,
            e.nombre_facultad,
            e.estado_estudiante
        from reportes.vw_estudiantes_detalle e
        where e.estado_estudiante = 'Activo'
          and not exists (
              select 1
              from reportes.vw_matriculas_detalle m
              where m.id_estudiante = e.id_estudiante
                and m.estado_matricula = 'Activa'
          )
        order by e.nombre_facultad, e.nombre_programa, e.estudiante
        """,
    ),
    20: ConsultaInstitucional(
        20,
        "Consulta institucional consolidada por facultad",
        (
            "Resumen de estudiantes, profesores, grupos, matriculas, pagos "
            "y homologaciones por facultad."
        ),
        """
        select
            f.nombre_facultad,
            count(distinct e.id_estudiante) as estudiantes,
            count(distinct p.id_profesor) as profesores,
            count(distinct g.id_grupo) as grupos,
            count(distinct m.id_matricula) as matriculas,
            count(distinct m.id_matricula) filter (where m.estado_pago = 'Pendiente')
                as pagos_pendientes,
            count(distinct h.id_homologacion) as homologaciones
        from institucional.facultad f
        left join reportes.vw_estudiantes_detalle e on e.id_facultad = f.id_facultad
        left join reportes.vw_profesores_detalle p on p.id_facultad = f.id_facultad
        left join reportes.vw_grupos_detalle g on g.id_facultad = f.id_facultad
        left join reportes.vw_matriculas_detalle m on m.id_facultad = f.id_facultad
        left join reportes.vw_homologaciones_global h on h.id_facultad = f.id_facultad
        group by f.nombre_facultad
        order by f.nombre_facultad
        """,
    ),
}


def listar_consultas():
    return [CONSULTAS[number] for number in sorted(CONSULTAS)]


def obtener_consulta(numero):
    return CONSULTAS.get(numero)


def ejecutar_consulta(numero):
    consulta = obtener_consulta(numero)
    if consulta is None:
        return None, [], []
    columns, rows = ejecutar_sql(consulta.sql)
    return consulta, columns, rows
