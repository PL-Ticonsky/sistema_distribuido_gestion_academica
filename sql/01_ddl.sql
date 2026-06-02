create extension if not exists pgcrypto;

create table usuario (
    id_usuario uuid primary key default gen_random_uuid(),
    password varchar(128) not null,
    last_login timestamp with time zone,
    is_superuser boolean not null default false,
    is_staff boolean not null default false,
    is_active boolean not null default true,
    date_joined timestamp with time zone not null default now(),
    nombre varchar(80) not null,
    tipo_de_documento varchar(2) not null,
    numero_de_documento varchar(20) not null,
    correo varchar(254) not null unique,
    direccion varchar(120),
    unique (tipo_de_documento, numero_de_documento),
    check (tipo_de_documento in ('CC', 'TI', 'CE'))
);

create table facultad (
    id_facultad varchar(10) primary key,
    nombre_facultad varchar(80) not null,
    ubicacion varchar(80),
    correo_institucional varchar(120) unique
);

create table programa_academico (
    id_programa_academico varchar(20) primary key,
    id_facultad varchar(10) not null,
    nombre_programa varchar(100) not null,
    estado varchar(20) not null,
    modalidad varchar(20) not null,
    nivel_formacion varchar(30) not null,
    foreign key (id_facultad) references facultad (id_facultad),
    check (estado in ('Activo', 'Inactivo')),
    check (modalidad in ('Presencial', 'Virtual', 'Hibrida')),
    check (
        nivel_formacion in (
            'Tecnico',
            'Tecnologico',
            'Pregrado',
            'Especializacion',
            'Maestria',
            'Doctorado'
        )
    )
);

create table periodo_academico (
    id_periodo_academico varchar(10) primary key,
    fecha_inicio date not null,
    fecha_final date not null,
    estado varchar(20) not null,
    check (fecha_final > fecha_inicio),
    check (estado in ('Planeado', 'Activo', 'Finalizado', 'Cancelado'))
);

create table estudiante (
    id_estudiante uuid primary key default gen_random_uuid(),
    id_usuario uuid not null unique,
    id_programa_academico varchar(20) not null,
    limite_matriculas integer not null default 15,
    estado_estudiante varchar(20) not null,
    foreign key (id_usuario) references usuario (id_usuario),
    foreign key (id_programa_academico)
        references programa_academico (id_programa_academico),
    check (limite_matriculas > 0),
    check (
        estado_estudiante in (
            'Activo',
            'Inactivo',
            'Suspendido',
            'Retirado',
            'Egresado'
        )
    )
);

create table profesor (
    id_profesor uuid primary key default gen_random_uuid(),
    id_usuario uuid not null unique,
    id_facultad varchar(10) not null,
    categoria varchar(20),
    vinculacion varchar(20),
    foreign key (id_usuario) references usuario (id_usuario),
    foreign key (id_facultad) references facultad (id_facultad),
    check (
        categoria is null
        or categoria in ('Auxiliar', 'Asistente', 'Asociado', 'Titular')
    ),
    check (
        vinculacion is null
        or vinculacion in ('Planta', 'Catedra', 'Ocasional')
    )
);

create table administrativo (
    id_administrativo uuid primary key default gen_random_uuid(),
    id_usuario uuid not null unique,
    id_facultad varchar(10) not null,
    detalles varchar(255),
    foreign key (id_usuario) references usuario (id_usuario),
    foreign key (id_facultad) references facultad (id_facultad)
);

create table asignatura (
    cod_asignatura varchar(20) primary key,
    nombre_asignatura varchar(100) not null,
    creditos integer not null,
    estado varchar(20) not null,
    horas_teoria integer not null,
    horas_pract integer not null,
    homologable boolean not null default false,
    check (creditos > 0),
    check (horas_teoria >= 0),
    check (horas_pract >= 0),
    check (estado in ('Activa', 'Inactiva')),
    check (homologable = false or horas_pract = 0)
);

create table programa_asignatura (
    id_programa_asignatura uuid primary key default gen_random_uuid(),
    id_programa_academico varchar(20) not null,
    cod_asignatura varchar(20) not null,
    semestre_sugerido integer not null,
    tipo_asignatura varchar(20) not null,
    estado varchar(20) not null,
    foreign key (id_programa_academico)
        references programa_academico (id_programa_academico),
    foreign key (cod_asignatura) references asignatura (cod_asignatura),
    unique (id_programa_academico, cod_asignatura),
    check (semestre_sugerido > 0),
    check (tipo_asignatura in ('Obligatoria', 'Electiva')),
    check (estado in ('Activa', 'Inactiva'))
);

create table pre_requisito (
    id_pre_requisito uuid primary key default gen_random_uuid(),
    id_programa_academico varchar(20) not null,
    id_programa_asignatura uuid not null,
    id_programa_asignatura_requisito uuid not null,
    foreign key (id_programa_academico)
        references programa_academico (id_programa_academico),
    foreign key (id_programa_asignatura)
        references programa_asignatura (id_programa_asignatura),
    foreign key (id_programa_asignatura_requisito)
        references programa_asignatura (id_programa_asignatura),
    unique (id_programa_asignatura, id_programa_asignatura_requisito),
    check (id_programa_asignatura <> id_programa_asignatura_requisito)
);

create table grupo (
    id_grupo uuid primary key default gen_random_uuid(),
    id_programa_asignatura uuid not null,
    id_periodo_academico varchar(10) not null,
    id_profesor uuid,
    codigo_grupo varchar(20) not null,
    cupo_maximo integer not null,
    estado_grupo varchar(20) not null,
    foreign key (id_programa_asignatura)
        references programa_asignatura (id_programa_asignatura),
    foreign key (id_periodo_academico)
        references periodo_academico (id_periodo_academico),
    foreign key (id_profesor) references profesor (id_profesor),
    unique (id_programa_asignatura, id_periodo_academico, codigo_grupo),
    check (cupo_maximo > 0),
    check (estado_grupo in ('Abierto', 'En curso', 'Finalizado', 'Cancelado'))
);

create table tarifa_matricula (
    id_tarifa_matricula uuid primary key default gen_random_uuid(),
    id_programa_academico varchar(20) not null,
    id_periodo_academico varchar(10) not null,
    valor_matricula numeric(12, 2) not null,
    fecha_limite_ordinaria date not null,
    fecha_limite_extraordinaria date not null,
    estado varchar(20) not null,
    foreign key (id_programa_academico)
        references programa_academico (id_programa_academico),
    foreign key (id_periodo_academico)
        references periodo_academico (id_periodo_academico),
    unique (id_programa_academico, id_periodo_academico),
    check (valor_matricula >= 0),
    check (fecha_limite_extraordinaria >= fecha_limite_ordinaria),
    check (estado in ('Activa', 'Inactiva'))
);

create table recibo (
    id_recibo uuid primary key default gen_random_uuid(),
    id_estudiante uuid not null,
    id_tarifa_matricula uuid not null,
    fecha_pago date,
    valor_pagado numeric(12, 2),
    metodo_pago varchar(20),
    estado_pago varchar(20) not null,
    extras numeric(12, 2) not null default 0,
    foreign key (id_estudiante) references estudiante (id_estudiante),
    foreign key (id_tarifa_matricula)
        references tarifa_matricula (id_tarifa_matricula),
    unique (id_estudiante, id_tarifa_matricula),
    check (valor_pagado is null or valor_pagado >= 0),
    check (extras >= 0),
    check (
        metodo_pago is null
        or metodo_pago in (
            'Efectivo',
            'Tarjeta',
            'PSE',
            'Transferencia',
            'Consignacion'
        )
    ),
    check (estado_pago in ('Pendiente', 'Pagado', 'Vencido', 'Anulado')),
    check (
        estado_pago <> 'Pagado'
        or (fecha_pago is not null and valor_pagado is not null)
    )
);

create table matricula (
    id_matricula uuid primary key default gen_random_uuid(),
    id_recibo uuid not null unique,
    estado_matricula varchar(20) not null,
    foreign key (id_recibo) references recibo (id_recibo),
    check (
        estado_matricula in (
            'Pendiente',
            'Activa',
            'Finalizada',
            'Cancelada',
            'Anulada'
        )
    )
);

create table inscripcion (
    id_inscripcion uuid primary key default gen_random_uuid(),
    id_grupo uuid not null,
    id_estudiante uuid not null,
    nota1 numeric(3, 2),
    nota2 numeric(3, 2),
    nota3 numeric(3, 2),
    nota_final numeric(3, 2),
    intento integer not null,
    estado_inscripcion varchar(20) not null,
    foreign key (id_grupo) references grupo (id_grupo),
    foreign key (id_estudiante) references estudiante (id_estudiante),
    unique (id_grupo, id_estudiante),
    check (nota1 is null or nota1 between 0 and 5),
    check (nota2 is null or nota2 between 0 and 5),
    check (nota3 is null or nota3 between 0 and 5),
    check (nota_final is null or nota_final between 0 and 5),
    check (intento > 0),
    check (
        estado_inscripcion in (
            'Cursando',
            'Aprobada',
            'Reprobada',
            'Cancelada'
        )
    ),
    check (
        estado_inscripcion in ('Cursando', 'Cancelada')
        or nota_final is not null
    )
);

create table homologacion (
    id_homologacion uuid primary key default gen_random_uuid(),
    id_profesor_evaluador uuid not null,
    id_estudiante uuid not null,
    asignatura_origen varchar(100) not null,
    institucion_origen varchar(100) not null,
    id_programa_asignatura uuid not null,
    fecha_solicitud date not null,
    estado_homologacion varchar(20) not null,
    observacion varchar(255),
    fecha_respuesta date,
    nota_obtenida numeric(3, 2),
    foreign key (id_profesor_evaluador) references profesor (id_profesor),
    foreign key (id_estudiante) references estudiante (id_estudiante),
    foreign key (id_programa_asignatura)
        references programa_asignatura (id_programa_asignatura),
    check (
        estado_homologacion in (
            'Solicitada',
            'En revision',
            'Aprobada',
            'Rechazada',
            'Cancelada'
        )
    ),
    check (nota_obtenida is null or nota_obtenida between 0 and 5),
    check (estado_homologacion <> 'Aprobada' or nota_obtenida is not null),
    check (fecha_respuesta is null or fecha_respuesta >= fecha_solicitud)
);

create table decano (
    id_decano uuid primary key default gen_random_uuid(),
    id_profesor uuid not null,
    id_periodo_academico varchar(10) not null,
    id_facultad varchar(10) not null,
    foreign key (id_profesor) references profesor (id_profesor),
    foreign key (id_periodo_academico)
        references periodo_academico (id_periodo_academico),
    foreign key (id_facultad) references facultad (id_facultad),
    unique (id_facultad, id_periodo_academico)
);

create table coordinador (
    id_coordinador uuid primary key default gen_random_uuid(),
    id_profesor uuid not null,
    id_periodo_academico varchar(10) not null,
    id_programa_academico varchar(20) not null,
    foreign key (id_profesor) references profesor (id_profesor),
    foreign key (id_periodo_academico)
        references periodo_academico (id_periodo_academico),
    foreign key (id_programa_academico)
        references programa_academico (id_programa_academico),
    unique (id_programa_academico, id_periodo_academico)
);

create table auditoria (
    id_auditoria uuid primary key default gen_random_uuid(),
    id_usuario uuid not null,
    accion_realizada varchar(100) not null,
    fecha_hora timestamp with time zone not null default now(),
    descripcion varchar(255),
    foreign key (id_usuario) references usuario (id_usuario)
);
