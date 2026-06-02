-- 02_central_schema_tables.sql - Ejecutar conectado a sga_central.
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SCHEMA personas;

CREATE SCHEMA seguridad;

CREATE SCHEMA institucional;

CREATE SCHEMA financiero;

CREATE SCHEMA auditoria;

CREATE SCHEMA movilidad;

CREATE SCHEMA reportes;

CREATE TABLE personas.usuario_dato_personal (
    id_usuario uuid PRIMARY KEY,
    nombre varchar(100) NOT NULL,
    tipo_de_documento varchar(2) NOT NULL,
    numero_de_documento varchar(20) NOT NULL,
    correo varchar(120) NOT NULL,
    direccion varchar(120),
    UNIQUE(tipo_de_documento,numero_de_documento),
    UNIQUE(correo),
    CHECK(tipo_de_documento IN ('CC','TI','CE'))
);

CREATE TABLE seguridad.usuario_credencial (
    id_usuario uuid PRIMARY KEY,
    password varchar(128) NOT NULL,
    last_login timestamptz,
    is_superuser boolean NOT NULL DEFAULT FALSE,
    is_staff boolean NOT NULL DEFAULT FALSE,
    is_active boolean NOT NULL DEFAULT TRUE,
    date_joined timestamptz NOT NULL DEFAULT NOW(),
    FOREIGN KEY(id_usuario) REFERENCES personas.usuario_dato_personal(id_usuario)
);

CREATE TABLE seguridad.rol (
    id_rol uuid PRIMARY KEY,
    nombre_rol varchar(60) NOT NULL UNIQUE,
    descripcion varchar(200)
);

CREATE TABLE seguridad.permiso (
    id_permiso uuid PRIMARY KEY,
    nombre_permiso varchar(80) NOT NULL UNIQUE,
    descripcion varchar(200)
);

CREATE TABLE seguridad.usuario_rol (
    id_usuario uuid NOT NULL,
    id_rol uuid NOT NULL,
    PRIMARY KEY(id_usuario,id_rol),
    FOREIGN KEY(id_usuario) REFERENCES personas.usuario_dato_personal(id_usuario),
    FOREIGN KEY(id_rol) REFERENCES seguridad.rol(id_rol)
);

CREATE TABLE seguridad.rol_permiso (
    id_rol uuid NOT NULL,
    id_permiso uuid NOT NULL,
    PRIMARY KEY(id_rol,id_permiso),
    FOREIGN KEY(id_rol) REFERENCES seguridad.rol(id_rol),
    FOREIGN KEY(id_permiso) REFERENCES seguridad.permiso(id_permiso)
);

CREATE TABLE institucional.facultad (
    id_facultad varchar(10) PRIMARY KEY,
    nombre_facultad varchar(100) NOT NULL,
    ubicacion varchar(100),
    correo_institucional varchar(120) UNIQUE
);

CREATE TABLE institucional.programa_academico (
    id_programa_academico varchar(20) PRIMARY KEY,
    id_facultad varchar(10) NOT NULL,
    nombre_programa varchar(120) NOT NULL,
    estado varchar(20) NOT NULL,
    modalidad varchar(20) NOT NULL,
    nivel_formacion varchar(30) NOT NULL,
    UNIQUE(id_programa_academico,id_facultad),
    FOREIGN KEY(id_facultad) REFERENCES institucional.facultad(id_facultad),
    CHECK(estado IN ('Activo','Inactivo')),
    CHECK(modalidad IN ('Presencial','Virtual','Hibrida')),
    CHECK(nivel_formacion IN ('Tecnico','Tecnologico','Pregrado','Especializacion','Maestria','Doctorado'))
);

CREATE TABLE institucional.periodo_academico (
    id_periodo_academico varchar(10) PRIMARY KEY,
    fecha_inicio date NOT NULL,
    fecha_final date NOT NULL,
    estado varchar(20) NOT NULL,
    CHECK(fecha_final>fecha_inicio),
    CHECK(estado IN ('Planeado','Activo','Finalizado','Cancelado'))
);

CREATE TABLE institucional.asignatura (
    cod_asignatura varchar(20) PRIMARY KEY,
    nombre_asignatura varchar(120) NOT NULL,
    creditos int NOT NULL,
    estado varchar(20) NOT NULL,
    horas_teoria int NOT NULL,
    horas_pract int NOT NULL,
    homologable boolean NOT NULL DEFAULT FALSE,
    CHECK(creditos>0),
    CHECK(horas_teoria>=0 AND horas_pract>=0),
    CHECK(estado IN ('Activa','Inactiva')),
    CHECK(homologable=FALSE OR horas_pract=0)
);

CREATE TABLE financiero.tarifa_matricula (
    id_tarifa_matricula uuid PRIMARY KEY,
    id_programa_academico varchar(20) NOT NULL,
    id_facultad varchar(10) NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    valor_matricula numeric(12,2) NOT NULL,
    fecha_limite_ordinaria date NOT NULL,
    fecha_limite_extraordinaria date NOT NULL,
    estado varchar(20) NOT NULL,
    UNIQUE(id_programa_academico,id_periodo_academico),
    UNIQUE(id_tarifa_matricula,id_facultad),
    FOREIGN KEY(id_programa_academico,id_facultad) REFERENCES institucional.programa_academico(id_programa_academico,id_facultad),
    FOREIGN KEY(id_periodo_academico) REFERENCES institucional.periodo_academico(id_periodo_academico),
    CHECK(valor_matricula>=0),
    CHECK(fecha_limite_extraordinaria>=fecha_limite_ordinaria),
    CHECK(estado IN ('Activa','Inactiva'))
);

CREATE TABLE financiero.recibo (
    id_recibo uuid PRIMARY KEY,
    id_estudiante uuid NOT NULL,
    id_facultad varchar(10) NOT NULL,
    id_tarifa_matricula uuid NOT NULL,
    fecha_pago date,
    valor_pagado numeric(12,2),
    metodo_pago varchar(20),
    estado_pago varchar(20) NOT NULL,
    extras numeric(12,2) NOT NULL DEFAULT 0,
    UNIQUE(id_estudiante,id_tarifa_matricula),
    UNIQUE(id_recibo,id_facultad),
    FOREIGN KEY(id_tarifa_matricula,id_facultad) REFERENCES financiero.tarifa_matricula(id_tarifa_matricula,id_facultad),
    CHECK((valor_pagado IS NULL OR valor_pagado>=0) AND extras>=0),
    CHECK(metodo_pago IS NULL OR metodo_pago IN ('Efectivo','Tarjeta','PSE','Transferencia','Consignacion')),
    CHECK(estado_pago IN ('Pendiente','Pagado','Vencido','Anulado')),
    CHECK(estado_pago<>'Pagado' OR (fecha_pago IS NOT NULL AND valor_pagado IS NOT NULL))
);

CREATE TABLE movilidad.inscripcion_interfacultad (
    id_inscripcion_interfacultad uuid PRIMARY KEY,
    id_estudiante uuid NOT NULL,
    id_usuario uuid NOT NULL,
    id_facultad_origen varchar(10) NOT NULL,
    id_programa_academico_origen varchar(20) NOT NULL,
    id_grupo uuid NOT NULL,
    id_facultad_destino varchar(10) NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    estado_inscripcion varchar(20) NOT NULL,
    nota_final numeric(3,2),
    intento int NOT NULL DEFAULT 1,
    FOREIGN KEY(id_usuario) REFERENCES personas.usuario_dato_personal(id_usuario),
    FOREIGN KEY(id_facultad_origen) REFERENCES institucional.facultad(id_facultad),
    FOREIGN KEY(id_facultad_destino) REFERENCES institucional.facultad(id_facultad),
    FOREIGN KEY(id_programa_academico_origen) REFERENCES institucional.programa_academico(id_programa_academico),
    FOREIGN KEY(id_periodo_academico) REFERENCES institucional.periodo_academico(id_periodo_academico),
    CHECK(estado_inscripcion IN ('Cursando','Aprobada','Reprobada','Cancelada')),
    CHECK(nota_final IS NULL OR nota_final BETWEEN 0 AND 5),
    CHECK(intento>0),
    CHECK(id_facultad_origen<>id_facultad_destino)
);

CREATE TABLE auditoria.auditoria (
    id_auditoria uuid PRIMARY KEY,
    id_usuario uuid NOT NULL,
    esquema_afectado varchar(80),
    tabla_afectada varchar(80),
    accion_realizada varchar(100) NOT NULL,
    fecha_hora timestamptz NOT NULL DEFAULT NOW(),
    descripcion varchar(255),
    FOREIGN KEY(id_usuario) REFERENCES personas.usuario_dato_personal(id_usuario)
);
