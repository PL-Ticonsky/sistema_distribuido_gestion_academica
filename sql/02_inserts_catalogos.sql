insert into facultad (
    id_facultad,
    nombre_facultad,
    ubicacion,
    correo_institucional
) values
    ('ing', 'Facultad de Ingenieria', 'Bloque A', 'ingenieria@universidad.edu'),
    ('cie', 'Facultad de Ciencias Basicas', 'Bloque B', 'ciencias@universidad.edu'),
    ('eco', 'Facultad de Ciencias Economicas', 'Bloque C', 'economicas@universidad.edu');

insert into programa_academico (
    id_programa_academico,
    id_facultad,
    nombre_programa,
    estado,
    modalidad,
    nivel_formacion
) values
    ('ing_sistemas', 'ing', 'Ingenieria de Sistemas', 'Activo', 'Presencial', 'Pregrado'),
    ('ing_industrial', 'ing', 'Ingenieria Industrial', 'Activo', 'Presencial', 'Pregrado'),
    ('matematicas', 'cie', 'Matematicas', 'Activo', 'Presencial', 'Pregrado'),
    ('administracion', 'eco', 'Administracion de Empresas', 'Activo', 'Hibrida', 'Pregrado'),
    ('contaduria', 'eco', 'Contaduria Publica', 'Activo', 'Presencial', 'Pregrado');

insert into periodo_academico (
    id_periodo_academico,
    fecha_inicio,
    fecha_final,
    estado
) values
    ('2025-2', '2025-08-01', '2025-12-15', 'Finalizado'),
    ('2026-1', '2026-02-01', '2026-06-15', 'Activo'),
    ('2026-2', '2026-08-01', '2026-12-15', 'Planeado');

insert into asignatura (
    cod_asignatura,
    nombre_asignatura,
    creditos,
    estado,
    horas_teoria,
    horas_pract,
    homologable
) values
    ('sis101', 'Introduccion a la Programacion', 3, 'Activa', 2, 2, false),
    ('sis102', 'Programacion Orientada a Objetos', 3, 'Activa', 2, 2, false),
    ('sis201', 'Estructuras de Datos', 3, 'Activa', 2, 2, false),
    ('sis202', 'Bases de Datos', 3, 'Activa', 2, 2, false),
    ('mat101', 'Matematicas I', 3, 'Activa', 3, 0, true),
    ('hum101', 'Comunicacion Academica', 2, 'Activa', 2, 0, true),
    ('ind101', 'Introduccion a la Ingenieria Industrial', 2, 'Activa', 2, 0, true),
    ('mat102', 'Calculo Diferencial', 4, 'Activa', 4, 0, true),
    ('est101', 'Estadistica Descriptiva', 3, 'Activa', 3, 0, true),
    ('ind201', 'Investigacion de Operaciones', 3, 'Activa', 2, 2, false),
    ('ind202', 'Gestion de Produccion', 3, 'Activa', 3, 0, true),
    ('ind301', 'Logistica', 3, 'Activa', 3, 0, true),
    ('mat110', 'Fundamentos de Matematicas', 3, 'Activa', 3, 0, true),
    ('mat111', 'Calculo I', 4, 'Activa', 4, 0, true),
    ('mat112', 'Algebra Lineal', 3, 'Activa', 3, 0, true),
    ('mat211', 'Calculo II', 4, 'Activa', 4, 0, true),
    ('mat212', 'Probabilidad', 3, 'Activa', 3, 0, true),
    ('mat311', 'Analisis Real', 4, 'Activa', 4, 0, true),
    ('adm101', 'Fundamentos de Administracion', 3, 'Activa', 3, 0, true),
    ('con101', 'Contabilidad General', 3, 'Activa', 3, 0, true),
    ('eco101', 'Microeconomia', 3, 'Activa', 3, 0, true),
    ('adm201', 'Mercadeo', 3, 'Activa', 3, 0, true),
    ('fin201', 'Finanzas Corporativas', 3, 'Activa', 3, 0, true),
    ('adm202', 'Gestion del Talento Humano', 3, 'Activa', 3, 0, true),
    ('con102', 'Derecho Empresarial', 2, 'Activa', 2, 0, true),
    ('con201', 'Contabilidad Financiera', 3, 'Activa', 3, 0, true),
    ('con202', 'Costos', 3, 'Activa', 3, 0, true),
    ('con301', 'Auditoria Financiera', 3, 'Activa', 3, 0, true);

insert into programa_asignatura (
    id_programa_asignatura,
    id_programa_academico,
    cod_asignatura,
    semestre_sugerido,
    tipo_asignatura,
    estado
) values
    ('10000000-0000-0000-0000-000000000101', 'ing_sistemas', 'sis101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000102', 'ing_sistemas', 'mat101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000103', 'ing_sistemas', 'hum101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000104', 'ing_sistemas', 'sis102', 2, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000105', 'ing_sistemas', 'sis201', 3, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000106', 'ing_sistemas', 'sis202', 4, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000201', 'ing_industrial', 'ind101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000202', 'ing_industrial', 'mat102', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000203', 'ing_industrial', 'est101', 2, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000204', 'ing_industrial', 'ind201', 4, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000205', 'ing_industrial', 'ind202', 5, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000206', 'ing_industrial', 'ind301', 6, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000301', 'matematicas', 'mat110', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000302', 'matematicas', 'mat111', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000303', 'matematicas', 'mat112', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000304', 'matematicas', 'mat211', 2, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000305', 'matematicas', 'mat212', 3, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000306', 'matematicas', 'mat311', 5, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000401', 'administracion', 'adm101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000402', 'administracion', 'con101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000403', 'administracion', 'eco101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000404', 'administracion', 'adm201', 3, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000405', 'administracion', 'fin201', 4, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000406', 'administracion', 'adm202', 4, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000501', 'contaduria', 'con101', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000502', 'contaduria', 'con102', 1, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000503', 'contaduria', 'con201', 2, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000504', 'contaduria', 'con202', 3, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000505', 'contaduria', 'fin201', 4, 'Obligatoria', 'Activa'),
    ('10000000-0000-0000-0000-000000000506', 'contaduria', 'con301', 5, 'Obligatoria', 'Activa');

insert into pre_requisito (
    id_pre_requisito,
    id_programa_academico,
    id_programa_asignatura,
    id_programa_asignatura_requisito
) values
    ('20000000-0000-0000-0000-000000000001', 'ing_sistemas', '10000000-0000-0000-0000-000000000104', '10000000-0000-0000-0000-000000000101'),
    ('20000000-0000-0000-0000-000000000002', 'ing_sistemas', '10000000-0000-0000-0000-000000000105', '10000000-0000-0000-0000-000000000104'),
    ('20000000-0000-0000-0000-000000000003', 'ing_sistemas', '10000000-0000-0000-0000-000000000106', '10000000-0000-0000-0000-000000000105'),
    ('20000000-0000-0000-0000-000000000004', 'ing_industrial', '10000000-0000-0000-0000-000000000203', '10000000-0000-0000-0000-000000000202'),
    ('20000000-0000-0000-0000-000000000005', 'ing_industrial', '10000000-0000-0000-0000-000000000204', '10000000-0000-0000-0000-000000000203'),
    ('20000000-0000-0000-0000-000000000006', 'ing_industrial', '10000000-0000-0000-0000-000000000205', '10000000-0000-0000-0000-000000000204'),
    ('20000000-0000-0000-0000-000000000007', 'ing_industrial', '10000000-0000-0000-0000-000000000206', '10000000-0000-0000-0000-000000000205'),
    ('20000000-0000-0000-0000-000000000008', 'matematicas', '10000000-0000-0000-0000-000000000304', '10000000-0000-0000-0000-000000000302'),
    ('20000000-0000-0000-0000-000000000009', 'matematicas', '10000000-0000-0000-0000-000000000305', '10000000-0000-0000-0000-000000000302'),
    ('20000000-0000-0000-0000-000000000010', 'matematicas', '10000000-0000-0000-0000-000000000306', '10000000-0000-0000-0000-000000000304'),
    ('20000000-0000-0000-0000-000000000011', 'administracion', '10000000-0000-0000-0000-000000000404', '10000000-0000-0000-0000-000000000401'),
    ('20000000-0000-0000-0000-000000000012', 'administracion', '10000000-0000-0000-0000-000000000405', '10000000-0000-0000-0000-000000000402'),
    ('20000000-0000-0000-0000-000000000013', 'administracion', '10000000-0000-0000-0000-000000000406', '10000000-0000-0000-0000-000000000401'),
    ('20000000-0000-0000-0000-000000000014', 'contaduria', '10000000-0000-0000-0000-000000000503', '10000000-0000-0000-0000-000000000501'),
    ('20000000-0000-0000-0000-000000000015', 'contaduria', '10000000-0000-0000-0000-000000000504', '10000000-0000-0000-0000-000000000503'),
    ('20000000-0000-0000-0000-000000000016', 'contaduria', '10000000-0000-0000-0000-000000000505', '10000000-0000-0000-0000-000000000503'),
    ('20000000-0000-0000-0000-000000000017', 'contaduria', '10000000-0000-0000-0000-000000000506', '10000000-0000-0000-0000-000000000504');
