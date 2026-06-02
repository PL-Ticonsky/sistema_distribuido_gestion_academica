-- Ejecutar conectado a sga_facultad_artes. Crea el nodo físico Facultad de Artes ASAB.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA facultad_artes;

CREATE TABLE facultad_artes.estudiante (
    id_estudiante uuid PRIMARY KEY,
    id_usuario uuid NOT NULL UNIQUE,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_programa_academico varchar(20) NOT NULL,
    limite_matriculas int NOT NULL DEFAULT 15,
    estado_estudiante varchar(20) NOT NULL,
    CHECK(id_facultad='FART'),
    CHECK(limite_matriculas>0),
    CHECK(estado_estudiante IN ('Activo','Inactivo','Suspendido','Retirado','Egresado'))
);

CREATE TABLE facultad_artes.profesor (
    id_profesor uuid PRIMARY KEY,
    id_usuario uuid NOT NULL UNIQUE,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    categoria varchar(20),
    vinculacion varchar(20),
    CHECK(id_facultad='FART'),
    CHECK(categoria IS NULL OR categoria IN ('Auxiliar','Asistente','Asociado','Titular')),
    CHECK(vinculacion IS NULL OR vinculacion IN ('Planta','Catedra','Ocasional'))
);

CREATE TABLE facultad_artes.administrativo (
    id_administrativo uuid PRIMARY KEY,
    id_usuario uuid NOT NULL UNIQUE,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    detalles varchar(255),
    CHECK(id_facultad='FART')
);

CREATE TABLE facultad_artes.programa_asignatura (
    id_programa_asignatura uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_programa_academico varchar(20) NOT NULL,
    cod_asignatura varchar(20) NOT NULL,
    semestre_sugerido int NOT NULL,
    tipo_asignatura varchar(20) NOT NULL,
    estado varchar(20) NOT NULL,
    UNIQUE(id_programa_academico,cod_asignatura),
    UNIQUE(id_programa_asignatura,id_facultad),
    CHECK(id_facultad='FART'),
    CHECK(semestre_sugerido>0),
    CHECK(tipo_asignatura IN ('Obligatoria','Electiva')),
    CHECK(estado IN ('Activa','Inactiva'))
);

CREATE TABLE facultad_artes.pre_requisito (
    id_pre_requisito uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_programa_academico varchar(20) NOT NULL,
    id_programa_asignatura uuid NOT NULL,
    id_programa_asignatura_requisito uuid NOT NULL,
    UNIQUE(id_programa_asignatura,id_programa_asignatura_requisito),
    CHECK(id_facultad='FART'),
    CHECK(id_programa_asignatura<>id_programa_asignatura_requisito),
    FOREIGN KEY(id_programa_asignatura,id_facultad) REFERENCES facultad_artes.programa_asignatura(id_programa_asignatura,id_facultad),
    FOREIGN KEY(id_programa_asignatura_requisito,id_facultad) REFERENCES facultad_artes.programa_asignatura(id_programa_asignatura,id_facultad)
);

CREATE TABLE facultad_artes.grupo (
    id_grupo uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_programa_asignatura uuid NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    id_profesor uuid,
    codigo_grupo varchar(20) NOT NULL,
    cupo_maximo int NOT NULL,
    estado_grupo varchar(20) NOT NULL,
    UNIQUE(id_programa_asignatura,id_periodo_academico,codigo_grupo),
    UNIQUE(id_grupo,id_facultad),
    CHECK(id_facultad='FART'),
    CHECK(cupo_maximo>0),
    CHECK(estado_grupo IN ('Abierto','En curso','Finalizado','Cancelado')),
    FOREIGN KEY(id_programa_asignatura,id_facultad) REFERENCES facultad_artes.programa_asignatura(id_programa_asignatura,id_facultad),
    FOREIGN KEY(id_profesor) REFERENCES facultad_artes.profesor(id_profesor)
);

CREATE TABLE facultad_artes.matricula (
    id_matricula uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_estudiante uuid NOT NULL,
    id_recibo uuid NOT NULL UNIQUE,
    estado_matricula varchar(20) NOT NULL,
    CHECK(id_facultad='FART'),
    CHECK(estado_matricula IN ('Pendiente','Activa','Finalizada','Cancelada','Anulada')),
    FOREIGN KEY(id_estudiante) REFERENCES facultad_artes.estudiante(id_estudiante)
);

CREATE TABLE facultad_artes.inscripcion (
    id_inscripcion uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_grupo uuid NOT NULL,
    id_estudiante uuid NOT NULL,
    nota1 numeric(3,2),
    nota2 numeric(3,2),
    nota3 numeric(3,2),
    nota_final numeric(3,2),
    intento int NOT NULL,
    estado_inscripcion varchar(20) NOT NULL,
    UNIQUE(id_grupo,id_estudiante),
    CHECK(id_facultad='FART'),
    CHECK((nota1 IS NULL OR nota1 BETWEEN 0 AND 5) AND (nota2 IS NULL OR nota2 BETWEEN 0 AND 5) AND (nota3 IS NULL OR nota3 BETWEEN 0 AND 5) AND (nota_final IS NULL OR nota_final BETWEEN 0 AND 5)),
    CHECK(intento>0),
    CHECK(estado_inscripcion IN ('Cursando','Aprobada','Reprobada','Cancelada')),
    CHECK(estado_inscripcion IN ('Cursando','Cancelada') OR nota_final IS NOT NULL),
    FOREIGN KEY(id_grupo,id_facultad) REFERENCES facultad_artes.grupo(id_grupo,id_facultad),
    FOREIGN KEY(id_estudiante) REFERENCES facultad_artes.estudiante(id_estudiante)
);

CREATE TABLE facultad_artes.homologacion (
    id_homologacion uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_profesor_evaluador uuid NOT NULL,
    id_estudiante uuid NOT NULL,
    asignatura_origen varchar(100) NOT NULL,
    institucion_origen varchar(100) NOT NULL,
    id_programa_asignatura uuid NOT NULL,
    fecha_solicitud date NOT NULL,
    estado_homologacion varchar(20) NOT NULL,
    observacion varchar(255),
    fecha_respuesta date,
    nota_obtenida numeric(3,2),
    CHECK(id_facultad='FART'),
    CHECK(estado_homologacion IN ('Solicitada','En revision','Aprobada','Rechazada','Cancelada')),
    CHECK(nota_obtenida IS NULL OR nota_obtenida BETWEEN 0 AND 5),
    CHECK(estado_homologacion<>'Aprobada' OR nota_obtenida IS NOT NULL),
    CHECK(fecha_respuesta IS NULL OR fecha_respuesta>=fecha_solicitud),
    FOREIGN KEY(id_profesor_evaluador) REFERENCES facultad_artes.profesor(id_profesor),
    FOREIGN KEY(id_estudiante) REFERENCES facultad_artes.estudiante(id_estudiante),
    FOREIGN KEY(id_programa_asignatura,id_facultad) REFERENCES facultad_artes.programa_asignatura(id_programa_asignatura,id_facultad)
);

CREATE TABLE facultad_artes.decano (
    id_decano uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_profesor uuid NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    UNIQUE(id_facultad,id_periodo_academico),
    CHECK(id_facultad='FART'),
    FOREIGN KEY(id_profesor) REFERENCES facultad_artes.profesor(id_profesor)
);

CREATE TABLE facultad_artes.coordinador (
    id_coordinador uuid PRIMARY KEY,
    id_facultad varchar(10) NOT NULL DEFAULT 'FART',
    id_profesor uuid NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    id_programa_academico varchar(20) NOT NULL,
    UNIQUE(id_programa_academico,id_periodo_academico),
    CHECK(id_facultad='FART'),
    FOREIGN KEY(id_profesor) REFERENCES facultad_artes.profesor(id_profesor)
);
