-- Seed Facultad de Ingeniería. Ejecutar conectado a sga_facultad_ingenieria. Solo INSERT directos.
INSERT INTO facultad_ingenieria.estudiante (
    id_estudiante,
    id_usuario,
    id_facultad,
    id_programa_academico,
    limite_matriculas,
    estado_estudiante
) VALUES
    ('73143e06-c8db-545b-a031-69ebf6b3948a', '4a8dba6a-1e73-517b-b124-1163461703e0', 'FING', 'SIS', 15, 'Activo'),
    ('4995613a-8969-5199-b641-b6635b307578', '90c39787-9720-52ed-8f29-83ce8b875686', 'FING', 'SIS', 15, 'Activo'),
    ('57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 'f3decbae-32c0-5621-8e55-68f028ab11a6', 'FING', 'SIS', 15, 'Activo'),
    ('4c4c9c8b-4528-5958-a7be-aeecfb2c6714', 'b81b8302-8d39-5e03-adc0-4f4f156ef09c', 'FING', 'SIS', 15, 'Inactivo'),
    ('a5f72a23-4676-50a2-8071-42e8f96f4120', '0cd0a9ce-5047-5778-a99b-990ba734f397', 'FING', 'SIS', 15, 'Activo'),
    ('a4b66279-9dab-53f1-aefa-f76ce8bc67e1', 'f212413e-ee06-583d-8858-2ea4e0861cc8', 'FING', 'SIS', 15, 'Activo');

INSERT INTO facultad_ingenieria.profesor (
    id_profesor,
    id_usuario,
    id_facultad,
    categoria,
    vinculacion
) VALUES
    ('6109c6b6-6a0b-5528-a929-3e9faa39404e', '1d6b1836-c456-53e1-8cc1-86149f9d72a1', 'FING', 'Asociado', 'Planta'),
    ('ddd36ebe-661e-5fcc-91f8-ccd8d6b6d03d', '8aeca420-4cbf-5e82-89ed-30c1fd876819', 'FING', 'Asistente', 'Planta');

INSERT INTO facultad_ingenieria.administrativo (
    id_administrativo,
    id_usuario,
    id_facultad,
    detalles
) VALUES
    ('8e8f4a25-f474-56e5-a501-a4c07d5c5580', '968b0299-304b-5179-83c1-e9baf5a9bb4d', 'FING', 'Secretaría académica');

INSERT INTO facultad_ingenieria.programa_asignatura (
    id_programa_asignatura,
    id_facultad,
    id_programa_academico,
    cod_asignatura,
    semestre_sugerido,
    tipo_asignatura,
    estado
) VALUES
    ('089ffaea-5af3-5471-bcb1-c228c6a7f8ce', 'FING', 'SIS', 'PROG101', 1, 'Obligatoria', 'Activa'),
    ('9e3c2f7f-2438-501e-85c1-410502738bea', 'FING', 'SIS', 'BD101', 2, 'Obligatoria', 'Activa'),
    ('1c98bb3a-c6cc-5b18-b843-09a2098b82a9', 'FING', 'SIS', 'RED201', 3, 'Obligatoria', 'Activa'),
    ('c84a22b7-607e-542e-8362-36c919fca2e7', 'FING', 'SIS', 'MAT101', 4, 'Obligatoria', 'Activa');

INSERT INTO facultad_ingenieria.pre_requisito (
    id_pre_requisito,
    id_facultad,
    id_programa_academico,
    id_programa_asignatura,
    id_programa_asignatura_requisito
) VALUES
    ('88dde13e-13a2-553e-a209-979ccc2a00e5', 'FING', 'SIS', '9e3c2f7f-2438-501e-85c1-410502738bea', '089ffaea-5af3-5471-bcb1-c228c6a7f8ce'),
    ('2d0e7411-628a-5a12-abc7-39e1bb8fdacb', 'FING', 'SIS', '1c98bb3a-c6cc-5b18-b843-09a2098b82a9', '9e3c2f7f-2438-501e-85c1-410502738bea');

INSERT INTO facultad_ingenieria.grupo (
    id_grupo,
    id_facultad,
    id_programa_asignatura,
    id_periodo_academico,
    id_profesor,
    codigo_grupo,
    cupo_maximo,
    estado_grupo
) VALUES
    ('5ecf39bd-3d27-570c-b9c5-3437e050d7a8', 'FING', '089ffaea-5af3-5471-bcb1-c228c6a7f8ce', '2026-1', '6109c6b6-6a0b-5528-a929-3e9faa39404e', 'PROG101-01', 5, 'En curso'),
    ('30694d25-a1be-512b-9de8-cc02294fbdd5', 'FING', '9e3c2f7f-2438-501e-85c1-410502738bea', '2026-1', 'ddd36ebe-661e-5fcc-91f8-ccd8d6b6d03d', 'BD101-01', 5, 'En curso'),
    ('67f55304-f2bd-5fb5-990f-7bca876e44ea', 'FING', '1c98bb3a-c6cc-5b18-b843-09a2098b82a9', '2026-1', null, 'RED201-SD', 5, 'Abierto'),
    ('94a20444-2235-57f5-a6da-c2f042410b08', 'FING', '089ffaea-5af3-5471-bcb1-c228c6a7f8ce', '2025-2', '6109c6b6-6a0b-5528-a929-3e9faa39404e', 'PROG101-H1', 30, 'Finalizado'),
    ('eba18abc-2d8b-5321-8b0d-7366ea755798', 'FING', '9e3c2f7f-2438-501e-85c1-410502738bea', '2025-2', 'ddd36ebe-661e-5fcc-91f8-ccd8d6b6d03d', 'BD101-H1', 30, 'Finalizado'),
    ('1efed4d5-4063-5c75-8da6-cbf7983f979f', 'FING', '1c98bb3a-c6cc-5b18-b843-09a2098b82a9', '2025-2', '6109c6b6-6a0b-5528-a929-3e9faa39404e', 'RED201-H1', 30, 'Finalizado'),
    ('9e5ab8e9-8054-5ebd-9554-7fc92f10c416', 'FING', 'c84a22b7-607e-542e-8362-36c919fca2e7', '2025-2', 'ddd36ebe-661e-5fcc-91f8-ccd8d6b6d03d', 'MAT101-H1', 30, 'Finalizado');

INSERT INTO facultad_ingenieria.matricula (
    id_matricula,
    id_facultad,
    id_estudiante,
    id_recibo,
    estado_matricula
) VALUES
    ('9ea074ff-d6d4-530f-b449-9021ef4ea03d', 'FING', '73143e06-c8db-545b-a031-69ebf6b3948a', 'faa7563d-a8c4-5f2f-b790-24a4f718840e', 'Activa'),
    ('e16f5da5-aaf8-5f63-8f92-9aeed54a2936', 'FING', '4995613a-8969-5199-b641-b6635b307578', 'd61e4d04-b931-5659-bb76-1a3685e491fe', 'Activa'),
    ('18c531a2-5a12-5cbf-9143-75337e08077d', 'FING', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 'e2b8b44f-6946-58fa-93bf-d6f3d2ff8530', 'Activa'),
    ('f3ac87e3-49b6-5a33-b21c-0b36e84a0a4f', 'FING', '4c4c9c8b-4528-5958-a7be-aeecfb2c6714', '545e437d-a93b-503f-bcf3-80e124f584d1', 'Activa'),
    ('8f62fa50-1a4f-5fae-bf58-22ea3c60fdf0', 'FING', 'a5f72a23-4676-50a2-8071-42e8f96f4120', '29b4bd75-fce7-5db0-858b-9ed10c051854', 'Activa'),
    ('521a8d6b-d1e0-500b-af79-bb530bba9839', 'FING', '73143e06-c8db-545b-a031-69ebf6b3948a', '200dd214-863e-5ac0-ab1e-1ccd58a4abca', 'Finalizada'),
    ('ec64a391-79e5-57dc-8cd7-a7400964c84c', 'FING', '4995613a-8969-5199-b641-b6635b307578', '241a9be7-0f1a-5121-967b-07ac5034c499', 'Finalizada'),
    ('1c528b21-b24e-5e86-a400-49200c10acb4', 'FING', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', '1bfb4a06-79fe-5435-883b-f733fd622452', 'Finalizada'),
    ('63fe80ce-f2f7-519c-b1df-4305a90cb14e', 'FING', '4c4c9c8b-4528-5958-a7be-aeecfb2c6714', 'fcf2afdc-d5bf-5348-9ac8-72d6a5b6ab97', 'Finalizada'),
    ('a32152f0-3609-596f-96f3-0bdb4d667ea6', 'FING', 'a5f72a23-4676-50a2-8071-42e8f96f4120', '4f7fa7cd-1554-5469-a786-c964e6fd9310', 'Finalizada');

INSERT INTO facultad_ingenieria.inscripcion (
    id_inscripcion,
    id_facultad,
    id_grupo,
    id_estudiante,
    nota1,
    nota2,
    nota3,
    nota_final,
    intento,
    estado_inscripcion
) VALUES
    ('e1cf89bc-99fb-5391-ae63-5a1fc4212044', 'FING', '5ecf39bd-3d27-570c-b9c5-3437e050d7a8', '73143e06-c8db-545b-a031-69ebf6b3948a', 3.6, null, null, null, 1, 'Cursando'),
    ('532b8735-da34-5faa-976b-290914560664', 'FING', '5ecf39bd-3d27-570c-b9c5-3437e050d7a8', '4995613a-8969-5199-b641-b6635b307578', 3.6, null, null, null, 1, 'Cursando'),
    ('97c77412-7a6a-561b-a04d-3ac958392827', 'FING', '5ecf39bd-3d27-570c-b9c5-3437e050d7a8', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 3.6, null, null, null, 1, 'Cursando'),
    ('3e75449f-3739-54db-8344-6ea3e864537f', 'FING', '5ecf39bd-3d27-570c-b9c5-3437e050d7a8', '4c4c9c8b-4528-5958-a7be-aeecfb2c6714', 3.6, null, null, null, 1, 'Cursando'),
    ('3a818548-97d7-5345-88c6-f90b8ec0aa5e', 'FING', '5ecf39bd-3d27-570c-b9c5-3437e050d7a8', 'a5f72a23-4676-50a2-8071-42e8f96f4120', 3.6, null, null, null, 1, 'Cursando'),
    ('72741f02-4098-5f7e-994b-4f3d394bc6cb', 'FING', '30694d25-a1be-512b-9de8-cc02294fbdd5', '4995613a-8969-5199-b641-b6635b307578', 3.1, null, null, null, 1, 'Cursando'),
    ('0f35ec74-8289-5b60-aa12-2dc7aa9af03b', 'FING', '30694d25-a1be-512b-9de8-cc02294fbdd5', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 3.1, null, null, null, 1, 'Cursando'),
    ('5f7a4835-dc8c-506b-a4e3-00d86ef23990', 'FING', '30694d25-a1be-512b-9de8-cc02294fbdd5', 'a5f72a23-4676-50a2-8071-42e8f96f4120', 3.1, null, null, null, 2, 'Cursando'),
    ('5dde0873-4a18-5ee8-b38d-780ffbfa339a', 'FING', '94a20444-2235-57f5-a6da-c2f042410b08', '73143e06-c8db-545b-a031-69ebf6b3948a', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('ac5ca2f0-007d-5b14-bad3-3090f6a14bff', 'FING', 'eba18abc-2d8b-5321-8b0d-7366ea755798', '73143e06-c8db-545b-a031-69ebf6b3948a', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('72c58996-749e-5b3b-aaa5-b43433b19533', 'FING', '1efed4d5-4063-5c75-8da6-cbf7983f979f', '73143e06-c8db-545b-a031-69ebf6b3948a', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('851b0f28-d152-5cc0-8a09-e55030f997b7', 'FING', '9e5ab8e9-8054-5ebd-9554-7fc92f10c416', '73143e06-c8db-545b-a031-69ebf6b3948a', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('9a3dee0e-42e1-5517-a741-110573f0b1d0', 'FING', '94a20444-2235-57f5-a6da-c2f042410b08', '4995613a-8969-5199-b641-b6635b307578', 2.1, 2.4, 2.7, 2.4, 1, 'Reprobada'),
    ('fde67b11-0139-5a89-9744-0b5b995a89d9', 'FING', 'eba18abc-2d8b-5321-8b0d-7366ea755798', '4995613a-8969-5199-b641-b6635b307578', 3.1, 3.2, 3.4, 3.2, 1, 'Aprobada'),
    ('ff3e68e2-9fbf-5ae4-a771-42079502791d', 'FING', '94a20444-2235-57f5-a6da-c2f042410b08', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 2.0, 2.4, 2.6, 2.2, 1, 'Reprobada'),
    ('0b202b13-f0fa-5e03-b395-bb1bf8de054f', 'FING', 'eba18abc-2d8b-5321-8b0d-7366ea755798', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 2.0, 2.4, 2.6, 2.5, 1, 'Reprobada'),
    ('f4dd4e28-990b-5fdc-8303-9528cd6d640f', 'FING', '1efed4d5-4063-5c75-8da6-cbf7983f979f', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 2.0, 2.4, 2.6, 2.7, 1, 'Reprobada'),
    ('84fe106e-79f4-5720-a391-fd96455d255a', 'FING', 'eba18abc-2d8b-5321-8b0d-7366ea755798', 'a5f72a23-4676-50a2-8071-42e8f96f4120', 2.1, 2.5, 2.7, 2.6, 1, 'Reprobada'),
    ('321bb8e8-4ce6-58d7-b96b-85750b6393ef', 'FING', '1efed4d5-4063-5c75-8da6-cbf7983f979f', '4c4c9c8b-4528-5958-a7be-aeecfb2c6714', 2.0, 2.2, 2.4, 2.2, 1, 'Reprobada');

INSERT INTO facultad_ingenieria.homologacion (
    id_homologacion,
    id_facultad,
    id_profesor_evaluador,
    id_estudiante,
    asignatura_origen,
    institucion_origen,
    id_programa_asignatura,
    fecha_solicitud,
    estado_homologacion,
    observacion,
    fecha_respuesta,
    nota_obtenida
) VALUES
    ('d9bb3a4e-b919-5911-9564-bba88a8153e1', 'FING', '6109c6b6-6a0b-5528-a929-3e9faa39404e', '57184116-5c6e-58d9-b7c1-1eea9e5cbdc4', 'Asignatura equivalente externa', 'Universidad Externa', 'c84a22b7-607e-542e-8362-36c919fca2e7', '2026-03-01', 'En revision', 'Pendiente de revisión documental', null, null),
    ('0b3dc5a7-d026-5362-8981-174d93a820cf', 'FING', 'ddd36ebe-661e-5fcc-91f8-ccd8d6b6d03d', '4995613a-8969-5199-b641-b6635b307578', 'Curso equivalente', 'Institución Externa', 'c84a22b7-607e-542e-8362-36c919fca2e7', '2025-09-01', 'Aprobada', 'Homologación aprobada', '2025-09-15', 4.1);

INSERT INTO facultad_ingenieria.decano (
    id_decano,
    id_facultad,
    id_profesor,
    id_periodo_academico
) VALUES
    ('7801e35f-deb3-5b5e-b28b-81a5ee34a8ef', 'FING', '6109c6b6-6a0b-5528-a929-3e9faa39404e', '2026-1');

INSERT INTO facultad_ingenieria.coordinador (
    id_coordinador,
    id_facultad,
    id_profesor,
    id_periodo_academico,
    id_programa_academico
) VALUES
    ('67938924-7697-5a1b-bb9f-a1cf5904dbc5', 'FING', 'ddd36ebe-661e-5fcc-91f8-ccd8d6b6d03d', '2026-1', 'SIS');
