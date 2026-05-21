/*
================================================================================
DDL BASE DE DATOS - SISTEMA DISTRIBUIDO DE GESTION ACADEMICA
PostgreSQL / DBeaver
Version: 1.0 academica preparada para integracion con Django Auth
================================================================================

INSTRUCCIONES DE USO EN DBEAVER:
1. Crear manualmente una base de datos, por ejemplo: gestion_academica.
2. Conectarse a esa base desde DBeaver.
3. Abrir este archivo como SQL Script.
4. Ejecutarlo completo.

NOTA SOBRE DJANGO:
- Este DDL NO crea las tablas auth_user, auth_group, auth_permission ni django_session.
- Esas tablas las crea Django con: python manage.py migrate
- La tabla usuario queda preparada con id_auth_user integer UNIQUE.
- Cuando Django haya creado auth_user, ejecutar el bloque final llamado:
  BLOQUE OPCIONAL DE INTEGRACION CON DJANGO AUTH.
================================================================================
*/

BEGIN;

/* =============================================================================
   0. LIMPIEZA CONTROLADA DE OBJETOS ACADEMICOS
   No se eliminan tablas internas de Django.
============================================================================= */

DROP TABLE IF EXISTS
    decano,
    coordinador,
    homologacion,
    inscripcion,
    grupo,
    pre_requisitos,
    programa_asignatura,
    matricula,
    recibo,
    tarifa_matricula,
    administrativo,
    profesor,
    estudiante,
    auditoria,
    asignatura,
    programa_academico,
    periodo_academico,
    facultad,
    usuario
CASCADE;

DROP FUNCTION IF EXISTS fn_set_fecha_actualizacion() CASCADE;
DROP FUNCTION IF EXISTS fn_validar_pre_requisito_mismo_programa() CASCADE;
DROP FUNCTION IF EXISTS fn_validar_docente_grupo_facultad() CASCADE;
DROP FUNCTION IF EXISTS fn_validar_recibo_pago() CASCADE;
DROP FUNCTION IF EXISTS fn_validar_matricula_recibo_pagado() CASCADE;
DROP FUNCTION IF EXISTS fn_validar_inscripcion() CASCADE;
DROP FUNCTION IF EXISTS fn_validar_homologacion() CASCADE;

DROP TYPE IF EXISTS tipo_documento_enum CASCADE;
DROP TYPE IF EXISTS estado_estudiante_enum CASCADE;
DROP TYPE IF EXISTS categoria_profesor_enum CASCADE;
DROP TYPE IF EXISTS vinculacion_profesor_enum CASCADE;
DROP TYPE IF EXISTS estado_programa_enum CASCADE;
DROP TYPE IF EXISTS modalidad_programa_enum CASCADE;
DROP TYPE IF EXISTS nivel_formacion_enum CASCADE;
DROP TYPE IF EXISTS estado_periodo_enum CASCADE;
DROP TYPE IF EXISTS estado_tarifa_enum CASCADE;
DROP TYPE IF EXISTS metodo_pago_enum CASCADE;
DROP TYPE IF EXISTS estado_pago_enum CASCADE;
DROP TYPE IF EXISTS estado_matricula_enum CASCADE;
DROP TYPE IF EXISTS estado_asignatura_enum CASCADE;
DROP TYPE IF EXISTS tipo_asignatura_enum CASCADE;
DROP TYPE IF EXISTS estado_grupo_enum CASCADE;
DROP TYPE IF EXISTS estado_inscripcion_enum CASCADE;
DROP TYPE IF EXISTS estado_homologacion_enum CASCADE;

/* =============================================================================
   1. EXTENSIONES
============================================================================= */

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

/* =============================================================================
   2. TIPOS ENUMERADOS
============================================================================= */

CREATE TYPE tipo_documento_enum AS ENUM ('CC', 'TI', 'CE');

CREATE TYPE estado_estudiante_enum AS ENUM (
    'Activo',
    'Inactivo',
    'Suspendido',
    'Retirado',
    'Egresado'
);

CREATE TYPE categoria_profesor_enum AS ENUM (
    'Auxiliar',
    'Asistente',
    'Asociado',
    'Titular'
);

CREATE TYPE vinculacion_profesor_enum AS ENUM (
    'Planta',
    'Catedra',
    'Ocasional'
);

CREATE TYPE estado_programa_enum AS ENUM (
    'Activo',
    'Inactivo'
);

CREATE TYPE modalidad_programa_enum AS ENUM (
    'Presencial',
    'Virtual',
    'Hibrida'
);

CREATE TYPE nivel_formacion_enum AS ENUM (
    'Tecnico',
    'Tecnologico',
    'Pregrado',
    'Especializacion',
    'Maestria',
    'Doctorado'
);

CREATE TYPE estado_periodo_enum AS ENUM (
    'Planeado',
    'Activo',
    'Finalizado',
    'Cancelado'
);

CREATE TYPE estado_tarifa_enum AS ENUM (
    'Activa',
    'Inactiva'
);

CREATE TYPE metodo_pago_enum AS ENUM (
    'Efectivo',
    'Tarjeta',
    'PSE',
    'Transferencia',
    'Consignacion'
);

CREATE TYPE estado_pago_enum AS ENUM (
    'Pendiente',
    'Pagado',
    'Vencido',
    'Anulado'
);

CREATE TYPE estado_matricula_enum AS ENUM (
    'Pendiente',
    'Activa',
    'Finalizada',
    'Cancelada',
    'Anulada'
);

CREATE TYPE estado_asignatura_enum AS ENUM (
    'Activa',
    'Inactiva'
);

CREATE TYPE tipo_asignatura_enum AS ENUM (
    'Obligatoria',
    'Electiva'
);

CREATE TYPE estado_grupo_enum AS ENUM (
    'Abierto',
    'En curso',
    'Finalizado',
    'Cancelado'
);

CREATE TYPE estado_inscripcion_enum AS ENUM (
    'Cursando',
    'Aprobada',
    'Reprobada',
    'Cancelada'
);

CREATE TYPE estado_homologacion_enum AS ENUM (
    'Solicitada',
    'En revision',
    'Aprobada',
    'Rechazada',
    'Cancelada'
);

/* =============================================================================
   3. TABLAS BASE E INSTITUCIONALES
============================================================================= */

CREATE TABLE usuario (
    id_usuario uuid PRIMARY KEY DEFAULT gen_random_uuid(),

    /*
       Campo preparado para conectar con Django Auth.
       Django crea auth_user posteriormente con sus migraciones.
       La FK se agrega después, usando el bloque opcional final.
    */
    id_auth_user integer UNIQUE,

    nombre varchar(120) NOT NULL,
    tipo_de_documento tipo_documento_enum NOT NULL,
    numero_de_documento varchar(20) NOT NULL,
    correo citext NOT NULL,
    direccion varchar(120),
    fecha_de_creacion timestamptz NOT NULL DEFAULT now(),
    fecha_actualizacion timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_usuario_documento
        UNIQUE (tipo_de_documento, numero_de_documento),

    CONSTRAINT uq_usuario_correo
        UNIQUE (correo),

    CONSTRAINT chk_usuario_numero_documento_no_vacio
        CHECK (length(trim(numero_de_documento)) > 0),

    CONSTRAINT chk_usuario_nombre_no_vacio
        CHECK (length(trim(nombre)) > 0)
);

CREATE TABLE facultad (
    id_facultad varchar(10) PRIMARY KEY,
    ubicacion varchar(80),
    nombre_facultad varchar(80) NOT NULL,
    correo_institucional citext UNIQUE,

    CONSTRAINT chk_facultad_nombre_no_vacio
        CHECK (length(trim(nombre_facultad)) > 0)
);

CREATE TABLE periodo_academico (
    id_periodo_academico varchar(10) PRIMARY KEY,
    fecha_inicio date NOT NULL,
    fecha_final date NOT NULL,
    estado estado_periodo_enum NOT NULL DEFAULT 'Planeado',

    CONSTRAINT chk_periodo_fechas
        CHECK (fecha_final > fecha_inicio)
);

CREATE TABLE programa_academico (
    id_programa_academico varchar(20) PRIMARY KEY,
    id_facultad varchar(10) NOT NULL,
    nombre_programa varchar(80) NOT NULL,
    estado estado_programa_enum NOT NULL DEFAULT 'Activo',
    modalidad modalidad_programa_enum NOT NULL,
    nivel_formacion nivel_formacion_enum NOT NULL,

    CONSTRAINT fk_programa_facultad
        FOREIGN KEY (id_facultad)
        REFERENCES facultad(id_facultad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_programa_nombre_no_vacio
        CHECK (length(trim(nombre_programa)) > 0)
);

CREATE TABLE auditoria (
    id_auditoria uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario uuid,
    accion_realizada varchar(100) NOT NULL,
    tabla_afectada varchar(80),
    id_registro_afectado varchar(80),
    metodo_http varchar(10),
    ruta varchar(255),
    ip_origen varchar(45),
    user_agent varchar(255),
    fecha_hora timestamptz NOT NULL DEFAULT now(),
    descripcion varchar(255),

    CONSTRAINT fk_auditoria_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT chk_auditoria_accion_no_vacia
        CHECK (length(trim(accion_realizada)) > 0)
);

/* =============================================================================
   4. PERSONAS Y ESPECIALIZACIONES
============================================================================= */

CREATE TABLE estudiante (
    id_estudiante uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario uuid NOT NULL UNIQUE,
    id_programa_academico varchar(20) NOT NULL,
    limite_matriculas int NOT NULL DEFAULT 15,
    estado_estudiante estado_estudiante_enum NOT NULL DEFAULT 'Activo',

    CONSTRAINT fk_estudiante_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_estudiante_programa
        FOREIGN KEY (id_programa_academico)
        REFERENCES programa_academico(id_programa_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_estudiante_limite_matriculas
        CHECK (limite_matriculas > 0)
);

CREATE TABLE profesor (
    id_profesor uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario uuid NOT NULL UNIQUE,
    id_facultad varchar(10) NOT NULL,
    categoria categoria_profesor_enum,
    vinculacion vinculacion_profesor_enum,

    CONSTRAINT fk_profesor_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_profesor_facultad
        FOREIGN KEY (id_facultad)
        REFERENCES facultad(id_facultad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE administrativo (
    id_administrativo uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario uuid NOT NULL UNIQUE,
    id_facultad varchar(10) NOT NULL,
    cargo varchar(80),
    detalles varchar(255),

    CONSTRAINT fk_administrativo_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_administrativo_facultad
        FOREIGN KEY (id_facultad)
        REFERENCES facultad(id_facultad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

/* =============================================================================
   5. GESTION FINANCIERA Y MATRICULA
============================================================================= */

CREATE TABLE tarifa_matricula (
    id_tarifa_matricula uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_programa_academico varchar(20) NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    valor_matricula numeric(12,2) NOT NULL,
    fecha_limite_ordinaria date NOT NULL,
    fecha_limite_extraordinaria date NOT NULL,
    estado estado_tarifa_enum NOT NULL DEFAULT 'Activa',

    CONSTRAINT fk_tarifa_programa
        FOREIGN KEY (id_programa_academico)
        REFERENCES programa_academico(id_programa_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_tarifa_periodo
        FOREIGN KEY (id_periodo_academico)
        REFERENCES periodo_academico(id_periodo_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_tarifa_programa_periodo
        UNIQUE (id_programa_academico, id_periodo_academico),

    CONSTRAINT chk_tarifa_valor
        CHECK (valor_matricula >= 0),

    CONSTRAINT chk_tarifa_fechas
        CHECK (fecha_limite_extraordinaria >= fecha_limite_ordinaria)
);

CREATE TABLE recibo (
    id_recibo uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_estudiante uuid NOT NULL,
    id_tarifa_matricula uuid NOT NULL,
    fecha_pago date,
    valor_pagado numeric(12,2),
    metodo_pago metodo_pago_enum,
    estado_pago estado_pago_enum NOT NULL DEFAULT 'Pendiente',
    extras numeric(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT fk_recibo_estudiante
        FOREIGN KEY (id_estudiante)
        REFERENCES estudiante(id_estudiante)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_recibo_tarifa
        FOREIGN KEY (id_tarifa_matricula)
        REFERENCES tarifa_matricula(id_tarifa_matricula)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_recibo_estudiante_tarifa
        UNIQUE (id_estudiante, id_tarifa_matricula),

    CONSTRAINT chk_recibo_valor_pagado
        CHECK (valor_pagado IS NULL OR valor_pagado >= 0),

    CONSTRAINT chk_recibo_extras
        CHECK (extras >= 0)
);

CREATE TABLE matricula (
    id_matricula uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_recibo uuid NOT NULL UNIQUE,
    estado_matricula estado_matricula_enum NOT NULL DEFAULT 'Pendiente',
    fecha_creacion timestamptz NOT NULL DEFAULT now(),
    fecha_actualizacion timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT fk_matricula_recibo
        FOREIGN KEY (id_recibo)
        REFERENCES recibo(id_recibo)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

/* =============================================================================
   6. ESTRUCTURA ACADEMICA
============================================================================= */

CREATE TABLE asignatura (
    cod_asignatura varchar(20) PRIMARY KEY,
    nombre_asignatura varchar(80) NOT NULL,
    creditos int NOT NULL,
    estado estado_asignatura_enum NOT NULL DEFAULT 'Activa',
    horas_teoria int NOT NULL DEFAULT 0,
    horas_pract int NOT NULL DEFAULT 0,
    homologable boolean NOT NULL DEFAULT false,

    CONSTRAINT chk_asignatura_creditos
        CHECK (creditos > 0),

    CONSTRAINT chk_asignatura_horas_teoria
        CHECK (horas_teoria >= 0),

    CONSTRAINT chk_asignatura_horas_pract
        CHECK (horas_pract >= 0),

    CONSTRAINT chk_asignatura_homologable_sin_practica
        CHECK (homologable = false OR horas_pract = 0),

    CONSTRAINT chk_asignatura_nombre_no_vacio
        CHECK (length(trim(nombre_asignatura)) > 0)
);

CREATE TABLE programa_asignatura (
    id_programa_asignatura uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_programa_academico varchar(20) NOT NULL,
    cod_asignatura varchar(20) NOT NULL,
    semestre_sugerido int NOT NULL,
    tipo_asignatura tipo_asignatura_enum NOT NULL,
    estado estado_asignatura_enum NOT NULL DEFAULT 'Activa',

    CONSTRAINT fk_programa_asignatura_programa
        FOREIGN KEY (id_programa_academico)
        REFERENCES programa_academico(id_programa_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_programa_asignatura_asignatura
        FOREIGN KEY (cod_asignatura)
        REFERENCES asignatura(cod_asignatura)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_programa_asignatura
        UNIQUE (id_programa_academico, cod_asignatura),

    CONSTRAINT chk_programa_asignatura_semestre
        CHECK (semestre_sugerido > 0)
);

CREATE TABLE pre_requisitos (
    id_pre_requisito uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_programa_academico varchar(20) NOT NULL,
    id_programa_asignatura uuid NOT NULL,
    id_programa_asignatura_requisito uuid NOT NULL,

    CONSTRAINT fk_prereq_programa
        FOREIGN KEY (id_programa_academico)
        REFERENCES programa_academico(id_programa_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_prereq_programa_asignatura
        FOREIGN KEY (id_programa_asignatura)
        REFERENCES programa_asignatura(id_programa_asignatura)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_prereq_programa_asignatura_requisito
        FOREIGN KEY (id_programa_asignatura_requisito)
        REFERENCES programa_asignatura(id_programa_asignatura)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_prereq_asignatura_requisito
        UNIQUE (id_programa_asignatura, id_programa_asignatura_requisito),

    CONSTRAINT chk_prereq_no_mismo_registro
        CHECK (id_programa_asignatura <> id_programa_asignatura_requisito)
);

CREATE TABLE grupo (
    id_grupo uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_programa_asignatura uuid NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    id_docente uuid,
    codigo_grupo varchar(20) NOT NULL,
    cupo_maximo int NOT NULL,
    estado_grupo estado_grupo_enum NOT NULL DEFAULT 'Abierto',

    CONSTRAINT fk_grupo_programa_asignatura
        FOREIGN KEY (id_programa_asignatura)
        REFERENCES programa_asignatura(id_programa_asignatura)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_grupo_periodo
        FOREIGN KEY (id_periodo_academico)
        REFERENCES periodo_academico(id_periodo_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_grupo_docente
        FOREIGN KEY (id_docente)
        REFERENCES profesor(id_profesor)
        ON UPDATE CASCADE
        ON DELETE SET NULL,

    CONSTRAINT uq_grupo_codigo_periodo_asignatura
        UNIQUE (id_programa_asignatura, id_periodo_academico, codigo_grupo),

    CONSTRAINT chk_grupo_cupo_maximo
        CHECK (cupo_maximo > 0),

    CONSTRAINT chk_grupo_codigo_no_vacio
        CHECK (length(trim(codigo_grupo)) > 0)
);

CREATE TABLE inscripcion (
    id_inscripcion uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_grupo uuid NOT NULL,
    id_estudiante uuid NOT NULL,
    nota1 numeric(3,2),
    nota2 numeric(3,2),
    nota3 numeric(3,2),
    nota_final numeric(3,2),
    intento int NOT NULL,
    estado_inscripcion estado_inscripcion_enum NOT NULL DEFAULT 'Cursando',
    fecha_inscripcion timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT fk_inscripcion_grupo
        FOREIGN KEY (id_grupo)
        REFERENCES grupo(id_grupo)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_inscripcion_estudiante
        FOREIGN KEY (id_estudiante)
        REFERENCES estudiante(id_estudiante)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_inscripcion_grupo_estudiante
        UNIQUE (id_grupo, id_estudiante),

    CONSTRAINT chk_inscripcion_nota1
        CHECK (nota1 IS NULL OR nota1 BETWEEN 0 AND 5),

    CONSTRAINT chk_inscripcion_nota2
        CHECK (nota2 IS NULL OR nota2 BETWEEN 0 AND 5),

    CONSTRAINT chk_inscripcion_nota3
        CHECK (nota3 IS NULL OR nota3 BETWEEN 0 AND 5),

    CONSTRAINT chk_inscripcion_nota_final
        CHECK (nota_final IS NULL OR nota_final BETWEEN 0 AND 5),

    CONSTRAINT chk_inscripcion_intento
        CHECK (intento > 0),

    CONSTRAINT chk_inscripcion_estado_nota_final
        CHECK (
            (
                estado_inscripcion IN ('Aprobada', 'Reprobada')
                AND nota_final IS NOT NULL
            )
            OR estado_inscripcion IN ('Cursando', 'Cancelada')
        )
);

/* =============================================================================
   7. HOMOLOGACIONES Y CARGOS ACADEMICOS
============================================================================= */

CREATE TABLE homologacion (
    id_homologacion uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_profesor_evaluador uuid NOT NULL,
    id_estudiante uuid NOT NULL,
    asignatura_origen varchar(100) NOT NULL,
    institucion_origen varchar(100) NOT NULL,
    id_programa_asignatura uuid NOT NULL,
    fecha_solicitud date NOT NULL DEFAULT current_date,
    estado_homologacion estado_homologacion_enum NOT NULL DEFAULT 'Solicitada',
    observacion varchar(255),
    fecha_respuesta date,
    nota_obtenida numeric(3,2),

    CONSTRAINT fk_homologacion_profesor
        FOREIGN KEY (id_profesor_evaluador)
        REFERENCES profesor(id_profesor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_homologacion_estudiante
        FOREIGN KEY (id_estudiante)
        REFERENCES estudiante(id_estudiante)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_homologacion_programa_asignatura
        FOREIGN KEY (id_programa_asignatura)
        REFERENCES programa_asignatura(id_programa_asignatura)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT chk_homologacion_nota
        CHECK (nota_obtenida IS NULL OR nota_obtenida BETWEEN 0 AND 5),

    CONSTRAINT chk_homologacion_aprobada_con_nota
        CHECK (
            estado_homologacion <> 'Aprobada'
            OR nota_obtenida IS NOT NULL
        ),

    CONSTRAINT chk_homologacion_fecha_respuesta
        CHECK (
            fecha_respuesta IS NULL
            OR fecha_respuesta >= fecha_solicitud
        ),

    CONSTRAINT chk_homologacion_textos_no_vacios
        CHECK (
            length(trim(asignatura_origen)) > 0
            AND length(trim(institucion_origen)) > 0
        )
);

CREATE TABLE decano (
    id_decano uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_profesor uuid NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    id_facultad varchar(10) NOT NULL,

    CONSTRAINT fk_decano_profesor
        FOREIGN KEY (id_profesor)
        REFERENCES profesor(id_profesor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_decano_periodo
        FOREIGN KEY (id_periodo_academico)
        REFERENCES periodo_academico(id_periodo_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_decano_facultad
        FOREIGN KEY (id_facultad)
        REFERENCES facultad(id_facultad)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_decano_facultad_periodo
        UNIQUE (id_facultad, id_periodo_academico),

    CONSTRAINT uq_decano_profesor_periodo
        UNIQUE (id_profesor, id_periodo_academico)
);

CREATE TABLE coordinador (
    id_coordinador uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    id_profesor uuid NOT NULL,
    id_periodo_academico varchar(10) NOT NULL,
    id_programa_academico varchar(20) NOT NULL,

    CONSTRAINT fk_coordinador_profesor
        FOREIGN KEY (id_profesor)
        REFERENCES profesor(id_profesor)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_coordinador_periodo
        FOREIGN KEY (id_periodo_academico)
        REFERENCES periodo_academico(id_periodo_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT fk_coordinador_programa
        FOREIGN KEY (id_programa_academico)
        REFERENCES programa_academico(id_programa_academico)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    CONSTRAINT uq_coordinador_programa_periodo
        UNIQUE (id_programa_academico, id_periodo_academico),

    CONSTRAINT uq_coordinador_profesor_periodo
        UNIQUE (id_profesor, id_periodo_academico)
);

/* =============================================================================
   8. INDICES ADICIONALES
============================================================================= */

CREATE INDEX idx_usuario_id_auth_user ON usuario(id_auth_user);
CREATE INDEX idx_estudiante_programa ON estudiante(id_programa_academico);
CREATE INDEX idx_profesor_facultad ON profesor(id_facultad);
CREATE INDEX idx_administrativo_facultad ON administrativo(id_facultad);
CREATE INDEX idx_programa_facultad ON programa_academico(id_facultad);
CREATE INDEX idx_tarifa_programa_periodo ON tarifa_matricula(id_programa_academico, id_periodo_academico);
CREATE INDEX idx_recibo_estudiante ON recibo(id_estudiante);
CREATE INDEX idx_matricula_estado ON matricula(estado_matricula);
CREATE INDEX idx_programa_asignatura_programa ON programa_asignatura(id_programa_academico);
CREATE INDEX idx_grupo_periodo ON grupo(id_periodo_academico);
CREATE INDEX idx_grupo_docente ON grupo(id_docente);
CREATE INDEX idx_inscripcion_estudiante ON inscripcion(id_estudiante);
CREATE INDEX idx_inscripcion_grupo ON inscripcion(id_grupo);
CREATE INDEX idx_homologacion_estudiante ON homologacion(id_estudiante);
CREATE INDEX idx_auditoria_usuario_fecha ON auditoria(id_usuario, fecha_hora);

CREATE UNIQUE INDEX uq_homologacion_aprobada_estudiante_asignatura
ON homologacion (id_estudiante, id_programa_asignatura)
WHERE estado_homologacion = 'Aprobada';

/* =============================================================================
   9. FUNCIONES Y TRIGGERS DE VALIDACION
============================================================================= */

CREATE OR REPLACE FUNCTION fn_set_fecha_actualizacion()
RETURNS trigger AS $$
BEGIN
    NEW.fecha_actualizacion := now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuario_fecha_actualizacion
BEFORE UPDATE ON usuario
FOR EACH ROW
EXECUTE FUNCTION fn_set_fecha_actualizacion();

CREATE TRIGGER trg_matricula_fecha_actualizacion
BEFORE UPDATE ON matricula
FOR EACH ROW
EXECUTE FUNCTION fn_set_fecha_actualizacion();

/* -----------------------------------------------------------------------------
   Valida que los prerrequisitos pertenezcan al mismo programa académico.
----------------------------------------------------------------------------- */
CREATE OR REPLACE FUNCTION fn_validar_pre_requisito_mismo_programa()
RETURNS trigger AS $$
DECLARE
    v_programa_asignatura varchar(20);
    v_programa_requisito varchar(20);
BEGIN
    SELECT pa.id_programa_academico
    INTO v_programa_asignatura
    FROM programa_asignatura pa
    WHERE pa.id_programa_asignatura = NEW.id_programa_asignatura;

    SELECT pa.id_programa_academico
    INTO v_programa_requisito
    FROM programa_asignatura pa
    WHERE pa.id_programa_asignatura = NEW.id_programa_asignatura_requisito;

    IF v_programa_asignatura IS NULL OR v_programa_requisito IS NULL THEN
        RAISE EXCEPTION 'No fue posible validar el prerrequisito porque una asignatura del programa no existe.';
    END IF;

    IF v_programa_asignatura <> v_programa_requisito THEN
        RAISE EXCEPTION 'El prerrequisito debe pertenecer al mismo programa académico.';
    END IF;

    IF NEW.id_programa_academico <> v_programa_asignatura THEN
        RAISE EXCEPTION 'El id_programa_academico del prerrequisito no coincide con la asignatura del programa.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_pre_requisito_mismo_programa
BEFORE INSERT OR UPDATE ON pre_requisitos
FOR EACH ROW
EXECUTE FUNCTION fn_validar_pre_requisito_mismo_programa();

/* -----------------------------------------------------------------------------
   Valida que el docente asignado a un grupo pertenezca a la misma facultad del
   programa académico ofertado.
----------------------------------------------------------------------------- */
CREATE OR REPLACE FUNCTION fn_validar_docente_grupo_facultad()
RETURNS trigger AS $$
DECLARE
    v_facultad_programa varchar(10);
    v_facultad_docente varchar(10);
BEGIN
    IF NEW.id_docente IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT pr.id_facultad
    INTO v_facultad_programa
    FROM grupo g
    RIGHT JOIN programa_asignatura pa ON pa.id_programa_asignatura = NEW.id_programa_asignatura
    JOIN programa_academico pr ON pr.id_programa_academico = pa.id_programa_academico
    LIMIT 1;

    SELECT p.id_facultad
    INTO v_facultad_docente
    FROM profesor p
    WHERE p.id_profesor = NEW.id_docente;

    IF v_facultad_programa IS NULL OR v_facultad_docente IS NULL THEN
        RAISE EXCEPTION 'No fue posible validar la facultad del docente asignado al grupo.';
    END IF;

    IF v_facultad_programa <> v_facultad_docente THEN
        RAISE EXCEPTION 'El docente asignado debe pertenecer a la facultad del programa académico.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_docente_grupo_facultad
BEFORE INSERT OR UPDATE ON grupo
FOR EACH ROW
EXECUTE FUNCTION fn_validar_docente_grupo_facultad();

/* -----------------------------------------------------------------------------
   Valida consistencia de recibos pagados.
----------------------------------------------------------------------------- */
CREATE OR REPLACE FUNCTION fn_validar_recibo_pago()
RETURNS trigger AS $$
BEGIN
    IF NEW.estado_pago = 'Pagado' THEN
        IF NEW.fecha_pago IS NULL THEN
            RAISE EXCEPTION 'Un recibo pagado debe tener fecha de pago.';
        END IF;

        IF NEW.valor_pagado IS NULL OR NEW.valor_pagado <= 0 THEN
            RAISE EXCEPTION 'Un recibo pagado debe tener valor_pagado mayor que cero.';
        END IF;

        IF NEW.metodo_pago IS NULL THEN
            RAISE EXCEPTION 'Un recibo pagado debe tener método de pago.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_recibo_pago
BEFORE INSERT OR UPDATE ON recibo
FOR EACH ROW
EXECUTE FUNCTION fn_validar_recibo_pago();

/* -----------------------------------------------------------------------------
   Valida que una matrícula activa o finalizada tenga recibo pagado.
----------------------------------------------------------------------------- */
CREATE OR REPLACE FUNCTION fn_validar_matricula_recibo_pagado()
RETURNS trigger AS $$
DECLARE
    v_estado_pago estado_pago_enum;
BEGIN
    IF NEW.estado_matricula IN ('Activa', 'Finalizada') THEN
        SELECT r.estado_pago
        INTO v_estado_pago
        FROM recibo r
        WHERE r.id_recibo = NEW.id_recibo;

        IF v_estado_pago IS DISTINCT FROM 'Pagado' THEN
            RAISE EXCEPTION 'Una matrícula activa o finalizada requiere un recibo pagado.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_matricula_recibo_pagado
BEFORE INSERT OR UPDATE ON matricula
FOR EACH ROW
EXECUTE FUNCTION fn_validar_matricula_recibo_pagado();

/* -----------------------------------------------------------------------------
   Valida inscripción:
   - Grupo abierto o en curso.
   - Matrícula activa del estudiante para el periodo del grupo.
   - No superar cupo máximo.
   - No cursar dos grupos de la misma asignatura-programa en el mismo periodo.
----------------------------------------------------------------------------- */
CREATE OR REPLACE FUNCTION fn_validar_inscripcion()
RETURNS trigger AS $$
DECLARE
    v_id_periodo varchar(10);
    v_id_programa_asignatura uuid;
    v_estado_grupo estado_grupo_enum;
    v_cupo_maximo int;
    v_inscritos int;
    v_tiene_matricula_activa boolean;
    v_duplicado boolean;
BEGIN
    SELECT g.id_periodo_academico,
           g.id_programa_asignatura,
           g.estado_grupo,
           g.cupo_maximo
    INTO v_id_periodo,
         v_id_programa_asignatura,
         v_estado_grupo,
         v_cupo_maximo
    FROM grupo g
    WHERE g.id_grupo = NEW.id_grupo;

    IF v_id_periodo IS NULL THEN
        RAISE EXCEPTION 'El grupo indicado no existe.';
    END IF;

    IF NEW.estado_inscripcion <> 'Cancelada' AND v_estado_grupo NOT IN ('Abierto', 'En curso') THEN
        RAISE EXCEPTION 'Solo es posible inscribirse en grupos abiertos o en curso.';
    END IF;

    SELECT EXISTS (
        SELECT 1
        FROM matricula m
        JOIN recibo r ON r.id_recibo = m.id_recibo
        JOIN tarifa_matricula tm ON tm.id_tarifa_matricula = r.id_tarifa_matricula
        WHERE r.id_estudiante = NEW.id_estudiante
          AND tm.id_periodo_academico = v_id_periodo
          AND m.estado_matricula = 'Activa'
          AND r.estado_pago = 'Pagado'
    )
    INTO v_tiene_matricula_activa;

    IF NEW.estado_inscripcion <> 'Cancelada' AND NOT v_tiene_matricula_activa THEN
        RAISE EXCEPTION 'El estudiante debe tener matrícula activa y recibo pagado para inscribir asignaturas en este periodo.';
    END IF;

    SELECT COUNT(*)
    INTO v_inscritos
    FROM inscripcion i
    WHERE i.id_grupo = NEW.id_grupo
      AND i.estado_inscripcion <> 'Cancelada'
      AND (
          TG_OP = 'INSERT'
          OR i.id_inscripcion <> NEW.id_inscripcion
      );

    IF NEW.estado_inscripcion <> 'Cancelada' AND v_inscritos >= v_cupo_maximo THEN
        RAISE EXCEPTION 'El grupo ya alcanzó su cupo máximo.';
    END IF;

    SELECT EXISTS (
        SELECT 1
        FROM inscripcion i
        JOIN grupo g2 ON g2.id_grupo = i.id_grupo
        WHERE i.id_estudiante = NEW.id_estudiante
          AND i.estado_inscripcion <> 'Cancelada'
          AND g2.id_periodo_academico = v_id_periodo
          AND g2.id_programa_asignatura = v_id_programa_asignatura
          AND (
              TG_OP = 'INSERT'
              OR i.id_inscripcion <> NEW.id_inscripcion
          )
    )
    INTO v_duplicado;

    IF NEW.estado_inscripcion <> 'Cancelada' AND v_duplicado THEN
        RAISE EXCEPTION 'El estudiante no puede inscribir dos grupos de la misma asignatura-programa en el mismo periodo.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_inscripcion
BEFORE INSERT OR UPDATE ON inscripcion
FOR EACH ROW
EXECUTE FUNCTION fn_validar_inscripcion();

/* -----------------------------------------------------------------------------
   Valida homologación:
   - La asignatura objetivo debe pertenecer al programa del estudiante.
   - La asignatura objetivo debe ser homologable.
   - Si está aprobada debe tener nota y fecha de respuesta.
----------------------------------------------------------------------------- */
CREATE OR REPLACE FUNCTION fn_validar_homologacion()
RETURNS trigger AS $$
DECLARE
    v_programa_estudiante varchar(20);
    v_programa_asignatura varchar(20);
    v_homologable boolean;
BEGIN
    SELECT e.id_programa_academico
    INTO v_programa_estudiante
    FROM estudiante e
    WHERE e.id_estudiante = NEW.id_estudiante;

    SELECT pa.id_programa_academico,
           a.homologable
    INTO v_programa_asignatura,
         v_homologable
    FROM programa_asignatura pa
    JOIN asignatura a ON a.cod_asignatura = pa.cod_asignatura
    WHERE pa.id_programa_asignatura = NEW.id_programa_asignatura;

    IF v_programa_estudiante IS NULL OR v_programa_asignatura IS NULL THEN
        RAISE EXCEPTION 'No fue posible validar la homologación.';
    END IF;

    IF v_programa_estudiante <> v_programa_asignatura THEN
        RAISE EXCEPTION 'La homologación debe realizarse contra una asignatura del programa académico del estudiante.';
    END IF;

    IF NOT v_homologable THEN
        RAISE EXCEPTION 'La asignatura objetivo no está marcada como homologable.';
    END IF;

    IF NEW.estado_homologacion = 'Aprobada' THEN
        IF NEW.nota_obtenida IS NULL THEN
            RAISE EXCEPTION 'Una homologación aprobada debe tener nota obtenida.';
        END IF;

        IF NEW.fecha_respuesta IS NULL THEN
            RAISE EXCEPTION 'Una homologación aprobada debe tener fecha de respuesta.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validar_homologacion
BEFORE INSERT OR UPDATE ON homologacion
FOR EACH ROW
EXECUTE FUNCTION fn_validar_homologacion();

/* =============================================================================
   10. VISTAS BASICAS PARA LA APLICACION Y REPORTES
============================================================================= */

CREATE OR REPLACE VIEW vw_usuarios_roles AS
SELECT
    u.id_usuario,
    u.id_auth_user,
    u.nombre,
    u.tipo_de_documento,
    u.numero_de_documento,
    u.correo,
    CASE WHEN e.id_estudiante IS NOT NULL THEN true ELSE false END AS es_estudiante,
    CASE WHEN p.id_profesor IS NOT NULL THEN true ELSE false END AS es_profesor,
    CASE WHEN a.id_administrativo IS NOT NULL THEN true ELSE false END AS es_administrativo,
    CASE WHEN c.id_coordinador IS NOT NULL THEN true ELSE false END AS es_coordinador,
    CASE WHEN d.id_decano IS NOT NULL THEN true ELSE false END AS es_decano
FROM usuario u
LEFT JOIN estudiante e ON e.id_usuario = u.id_usuario
LEFT JOIN profesor p ON p.id_usuario = u.id_usuario
LEFT JOIN administrativo a ON a.id_usuario = u.id_usuario
LEFT JOIN coordinador c ON c.id_profesor = p.id_profesor
LEFT JOIN decano d ON d.id_profesor = p.id_profesor;

CREATE OR REPLACE VIEW vw_estudiantes_programa AS
SELECT
    e.id_estudiante,
    u.id_usuario,
    u.nombre,
    u.correo,
    e.estado_estudiante,
    e.limite_matriculas,
    pa.id_programa_academico,
    pa.nombre_programa,
    f.id_facultad,
    f.nombre_facultad
FROM estudiante e
JOIN usuario u ON u.id_usuario = e.id_usuario
JOIN programa_academico pa ON pa.id_programa_academico = e.id_programa_academico
JOIN facultad f ON f.id_facultad = pa.id_facultad;

CREATE OR REPLACE VIEW vw_grupos_detalle AS
SELECT
    g.id_grupo,
    g.codigo_grupo,
    g.cupo_maximo,
    g.estado_grupo,
    g.id_periodo_academico,
    pa.id_programa_asignatura,
    pr.id_programa_academico,
    pr.nombre_programa,
    a.cod_asignatura,
    a.nombre_asignatura,
    p.id_profesor,
    up.nombre AS nombre_docente,
    COUNT(i.id_inscripcion) FILTER (WHERE i.estado_inscripcion <> 'Cancelada') AS inscritos_activos
FROM grupo g
JOIN programa_asignatura pa ON pa.id_programa_asignatura = g.id_programa_asignatura
JOIN programa_academico pr ON pr.id_programa_academico = pa.id_programa_academico
JOIN asignatura a ON a.cod_asignatura = pa.cod_asignatura
LEFT JOIN profesor p ON p.id_profesor = g.id_docente
LEFT JOIN usuario up ON up.id_usuario = p.id_usuario
LEFT JOIN inscripcion i ON i.id_grupo = g.id_grupo
GROUP BY
    g.id_grupo,
    g.codigo_grupo,
    g.cupo_maximo,
    g.estado_grupo,
    g.id_periodo_academico,
    pa.id_programa_asignatura,
    pr.id_programa_academico,
    pr.nombre_programa,
    a.cod_asignatura,
    a.nombre_asignatura,
    p.id_profesor,
    up.nombre;

CREATE OR REPLACE VIEW vw_historial_academico AS
SELECT
    e.id_estudiante,
    u.nombre AS nombre_estudiante,
    pr.id_programa_academico,
    pr.nombre_programa,
    pe.id_periodo_academico,
    a.cod_asignatura,
    a.nombre_asignatura,
    g.codigo_grupo,
    i.nota1,
    i.nota2,
    i.nota3,
    i.nota_final,
    i.intento,
    i.estado_inscripcion
FROM inscripcion i
JOIN estudiante e ON e.id_estudiante = i.id_estudiante
JOIN usuario u ON u.id_usuario = e.id_usuario
JOIN grupo g ON g.id_grupo = i.id_grupo
JOIN periodo_academico pe ON pe.id_periodo_academico = g.id_periodo_academico
JOIN programa_asignatura pa ON pa.id_programa_asignatura = g.id_programa_asignatura
JOIN programa_academico pr ON pr.id_programa_academico = pa.id_programa_academico
JOIN asignatura a ON a.cod_asignatura = pa.cod_asignatura;

CREATE OR REPLACE VIEW vw_matriculas_detalle AS
SELECT
    m.id_matricula,
    m.estado_matricula,
    r.id_recibo,
    r.estado_pago,
    r.fecha_pago,
    r.valor_pagado,
    r.extras,
    tm.valor_matricula,
    tm.id_periodo_academico,
    e.id_estudiante,
    u.nombre AS nombre_estudiante,
    pr.id_programa_academico,
    pr.nombre_programa
FROM matricula m
JOIN recibo r ON r.id_recibo = m.id_recibo
JOIN tarifa_matricula tm ON tm.id_tarifa_matricula = r.id_tarifa_matricula
JOIN estudiante e ON e.id_estudiante = r.id_estudiante
JOIN usuario u ON u.id_usuario = e.id_usuario
JOIN programa_academico pr ON pr.id_programa_academico = tm.id_programa_academico;

COMMIT;

/* =============================================================================
   BLOQUE OPCIONAL DE INTEGRACION CON DJANGO AUTH
   Ejecutar SOLO después de crear el proyecto Django y correr:
   python manage.py migrate
=============================================================================

ALTER TABLE usuario
ADD CONSTRAINT fk_usuario_auth_user
FOREIGN KEY (id_auth_user)
REFERENCES auth_user(id)
ON UPDATE CASCADE
ON DELETE RESTRICT;

*/
