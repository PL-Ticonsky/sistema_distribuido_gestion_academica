-- Seed Facultad de Ciencias y Educación. Ejecutar conectado a sga_facultad_ciencias_educacion. Solo INSERT directos.
INSERT INTO facultad_ciencias_educacion.estudiante (
    id_estudiante,
    id_usuario,
    id_facultad,
    id_programa_academico,
    limite_matriculas,
    estado_estudiante
) VALUES
    ('df7f052a-dfcd-5fb7-895d-3bda56da045b', 'cfd332a0-c9b4-51d6-89a6-1b5ee588b065', 'FCE', 'MAT', 15, 'Activo'),
    ('6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 'c24af39d-8525-5297-b6ef-838e91193bb1', 'FCE', 'MAT', 15, 'Activo'),
    ('1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', '7c364256-e621-5f11-a572-9fe95fd81f3b', 'FCE', 'MAT', 15, 'Activo'),
    ('a614426f-e47b-5639-82b7-6046f42b1a83', 'c268e153-c019-58ee-b9ae-ae736032da4e', 'FCE', 'MAT', 15, 'Inactivo'),
    ('310dd9ef-3c1c-5fba-98fc-dc85900cdb2d', '51a2b186-cfc6-5fd5-b8ae-1ea717f2ccca', 'FCE', 'MAT', 15, 'Activo'),
    ('22c9414d-bf7d-5973-90ab-1e4832f7edfd', '959256b4-6f6a-5df1-b05a-f6824178b839', 'FCE', 'MAT', 15, 'Activo');

INSERT INTO facultad_ciencias_educacion.profesor (
    id_profesor,
    id_usuario,
    id_facultad,
    categoria,
    vinculacion
) VALUES
    ('24642cea-35d2-53c4-bc69-d80647a4870b', 'e1d01086-df60-52a0-bc56-e4dd6f47fb0b', 'FCE', 'Asociado', 'Planta'),
    ('f000119e-5258-5867-842e-e3953ac45cd4', '8638898e-8d4b-5ed5-bfc0-99c811c7f704', 'FCE', 'Asistente', 'Planta');

INSERT INTO facultad_ciencias_educacion.administrativo (
    id_administrativo,
    id_usuario,
    id_facultad,
    detalles
) VALUES
    ('0dd91aee-1ace-57da-b3f3-e82b37e384b4', '91d2b790-a826-5c01-8423-0fce1df51178', 'FCE', 'Secretaría académica');

INSERT INTO facultad_ciencias_educacion.programa_asignatura (
    id_programa_asignatura,
    id_facultad,
    id_programa_academico,
    cod_asignatura,
    semestre_sugerido,
    tipo_asignatura,
    estado
) VALUES
    ('47c75390-3571-5d75-ab9b-4471615dae27', 'FCE', 'MAT', 'MAT101', 1, 'Obligatoria', 'Activa'),
    ('0a8dfd36-15b0-5c71-9fa2-f24407b562e5', 'FCE', 'MAT', 'ALG101', 2, 'Obligatoria', 'Activa'),
    ('3cd77b57-56b4-5d29-8a85-4976141952c0', 'FCE', 'MAT', 'PED101', 3, 'Obligatoria', 'Activa'),
    ('34dabb9e-089e-5725-b987-f32b10273401', 'FCE', 'MAT', 'BIO101', 4, 'Obligatoria', 'Activa');

INSERT INTO facultad_ciencias_educacion.pre_requisito (
    id_pre_requisito,
    id_facultad,
    id_programa_academico,
    id_programa_asignatura,
    id_programa_asignatura_requisito
) VALUES
    ('398cea1a-2956-5795-8844-97d7701a1021', 'FCE', 'MAT', '0a8dfd36-15b0-5c71-9fa2-f24407b562e5', '47c75390-3571-5d75-ab9b-4471615dae27'),
    ('357d8e19-4fca-5abf-8136-8aff8b6fe128', 'FCE', 'MAT', '3cd77b57-56b4-5d29-8a85-4976141952c0', '0a8dfd36-15b0-5c71-9fa2-f24407b562e5');

INSERT INTO facultad_ciencias_educacion.grupo (
    id_grupo,
    id_facultad,
    id_programa_asignatura,
    id_periodo_academico,
    id_profesor,
    codigo_grupo,
    cupo_maximo,
    estado_grupo
) VALUES
    ('0e198f9f-e780-5a78-835a-0f75d0a39c6b', 'FCE', '47c75390-3571-5d75-ab9b-4471615dae27', '2026-1', '24642cea-35d2-53c4-bc69-d80647a4870b', 'MAT101-01', 5, 'En curso'),
    ('89ccec81-88c6-5df6-8851-54c3ed21498f', 'FCE', '0a8dfd36-15b0-5c71-9fa2-f24407b562e5', '2026-1', 'f000119e-5258-5867-842e-e3953ac45cd4', 'ALG101-01', 5, 'En curso'),
    ('96315f34-0679-5958-b410-0c4f2ede72e8', 'FCE', '3cd77b57-56b4-5d29-8a85-4976141952c0', '2026-1', null, 'PED101-SD', 5, 'Abierto'),
    ('2e949ab5-e7d6-5a54-af57-82c8daa27a01', 'FCE', '47c75390-3571-5d75-ab9b-4471615dae27', '2025-2', '24642cea-35d2-53c4-bc69-d80647a4870b', 'MAT101-H1', 30, 'Finalizado'),
    ('d60c741d-fab4-546a-8259-400b1735e2be', 'FCE', '0a8dfd36-15b0-5c71-9fa2-f24407b562e5', '2025-2', 'f000119e-5258-5867-842e-e3953ac45cd4', 'ALG101-H1', 30, 'Finalizado'),
    ('c632fc99-88e6-5483-98d4-af266e3aa89b', 'FCE', '3cd77b57-56b4-5d29-8a85-4976141952c0', '2025-2', '24642cea-35d2-53c4-bc69-d80647a4870b', 'PED101-H1', 30, 'Finalizado'),
    ('745035ad-82fc-518d-a942-52320bb93d74', 'FCE', '34dabb9e-089e-5725-b987-f32b10273401', '2025-2', 'f000119e-5258-5867-842e-e3953ac45cd4', 'BIO101-H1', 30, 'Finalizado');

INSERT INTO facultad_ciencias_educacion.matricula (
    id_matricula,
    id_facultad,
    id_estudiante,
    id_recibo,
    estado_matricula
) VALUES
    ('aae3f3b3-0bab-5936-b3c0-ddd558fe526e', 'FCE', 'df7f052a-dfcd-5fb7-895d-3bda56da045b', '24eb28d4-e5da-5aea-ac06-8a8860ad35b2', 'Activa'),
    ('5a61fabb-e95c-5a0d-a57d-e85257a5bb93', 'FCE', '6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 'c854a262-45a6-503a-b3dc-294e8ecd6543', 'Activa'),
    ('826393ac-e933-5682-b27a-6f6d78948b8b', 'FCE', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', '6353a3dc-f57f-5c80-aac4-1c7d1b5f0ad0', 'Activa'),
    ('2529e5c0-1c12-5965-88db-07297d8b7590', 'FCE', 'a614426f-e47b-5639-82b7-6046f42b1a83', '895b87f6-af0a-509d-b9e1-39a0df1cda27', 'Activa'),
    ('2400c048-2e10-589c-b309-98abbbd6f834', 'FCE', '310dd9ef-3c1c-5fba-98fc-dc85900cdb2d', 'b0970dda-eab8-5d59-b61c-b74daaa6e0b5', 'Activa'),
    ('93cac53d-e686-5976-b43d-7da558726c2c', 'FCE', 'df7f052a-dfcd-5fb7-895d-3bda56da045b', '46e7b4ff-5434-5ecb-acb3-507f60ec9f0f', 'Finalizada'),
    ('c2e2a5b5-4c29-5f42-84f5-6ebb1bca87c9', 'FCE', '6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 'bbd57be9-3228-5d81-97fc-c7a70547cdcb', 'Finalizada'),
    ('59235d7b-e0f8-57ab-bd89-b6353ad70338', 'FCE', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', '7a3f80bb-274a-5020-8a40-4786c49c496f', 'Finalizada'),
    ('6c0db136-4266-5bf3-a410-83794acc0b7e', 'FCE', 'a614426f-e47b-5639-82b7-6046f42b1a83', '0ad5067a-8235-57aa-91f0-5111da270780', 'Finalizada'),
    ('70259939-1c82-54da-a3d8-8227e9a3737c', 'FCE', '310dd9ef-3c1c-5fba-98fc-dc85900cdb2d', '8883cdd5-e25a-539c-b95b-b3550dba34dc', 'Finalizada');

INSERT INTO facultad_ciencias_educacion.inscripcion (
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
    ('ad062e82-1e89-5b58-a9ed-8a6b0cabd418', 'FCE', '0e198f9f-e780-5a78-835a-0f75d0a39c6b', 'df7f052a-dfcd-5fb7-895d-3bda56da045b', 3.6, null, null, null, 1, 'Cursando'),
    ('85f6b7c3-7c23-5e8b-9a1f-b34f41e8e9a1', 'FCE', '0e198f9f-e780-5a78-835a-0f75d0a39c6b', '6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 3.6, null, null, null, 1, 'Cursando'),
    ('e9307814-1001-5883-ac6e-838e71a2cbf6', 'FCE', '0e198f9f-e780-5a78-835a-0f75d0a39c6b', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', 3.6, null, null, null, 1, 'Cursando'),
    ('a91d06a1-a865-53bd-b5f3-ba6f1b7bd3ac', 'FCE', '0e198f9f-e780-5a78-835a-0f75d0a39c6b', 'a614426f-e47b-5639-82b7-6046f42b1a83', 3.6, null, null, null, 1, 'Cursando'),
    ('c7f7d97c-cba9-5ffc-a793-f703c8a26ec9', 'FCE', '0e198f9f-e780-5a78-835a-0f75d0a39c6b', '310dd9ef-3c1c-5fba-98fc-dc85900cdb2d', 3.6, null, null, null, 1, 'Cursando'),
    ('e2ffe235-50c1-5c0f-9550-37f63befd0b3', 'FCE', '89ccec81-88c6-5df6-8851-54c3ed21498f', '6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 3.1, null, null, null, 1, 'Cursando'),
    ('d8b9b5b3-eb18-53ef-a9a1-9e597f86a285', 'FCE', '89ccec81-88c6-5df6-8851-54c3ed21498f', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', 3.1, null, null, null, 1, 'Cursando'),
    ('39e4c66a-df69-5371-b565-14aa31c83c16', 'FCE', '89ccec81-88c6-5df6-8851-54c3ed21498f', '310dd9ef-3c1c-5fba-98fc-dc85900cdb2d', 3.1, null, null, null, 2, 'Cursando'),
    ('c324c160-734b-59c9-b692-2c64956bc8da', 'FCE', '2e949ab5-e7d6-5a54-af57-82c8daa27a01', 'df7f052a-dfcd-5fb7-895d-3bda56da045b', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('e123e6c8-1fd5-577f-936c-81fef0d72236', 'FCE', 'd60c741d-fab4-546a-8259-400b1735e2be', 'df7f052a-dfcd-5fb7-895d-3bda56da045b', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('9019d477-0e00-54a4-ae1b-5c7c551689f8', 'FCE', 'c632fc99-88e6-5483-98d4-af266e3aa89b', 'df7f052a-dfcd-5fb7-895d-3bda56da045b', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('e1647919-9d32-5ea3-af4c-3feb59845842', 'FCE', '745035ad-82fc-518d-a942-52320bb93d74', 'df7f052a-dfcd-5fb7-895d-3bda56da045b', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('bcf8c7c3-9eb2-5a2d-b00f-66b10cce0149', 'FCE', '2e949ab5-e7d6-5a54-af57-82c8daa27a01', '6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 2.1, 2.4, 2.7, 2.4, 1, 'Reprobada'),
    ('f7ad3431-aa1c-5552-b4cf-910de0149c72', 'FCE', 'd60c741d-fab4-546a-8259-400b1735e2be', '6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 3.1, 3.2, 3.4, 3.2, 1, 'Aprobada'),
    ('7fe83410-4d4e-592c-a7ae-4daed00ccb24', 'FCE', '2e949ab5-e7d6-5a54-af57-82c8daa27a01', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', 2.0, 2.4, 2.6, 2.2, 1, 'Reprobada'),
    ('ffa1769d-5534-5e1a-8e83-fb57a0a03ec3', 'FCE', 'd60c741d-fab4-546a-8259-400b1735e2be', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', 2.0, 2.4, 2.6, 2.5, 1, 'Reprobada'),
    ('ef14da9b-481a-52a4-9900-d144c20bf2fc', 'FCE', 'c632fc99-88e6-5483-98d4-af266e3aa89b', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', 2.0, 2.4, 2.6, 2.7, 1, 'Reprobada'),
    ('fdb4450e-0095-5396-9654-be64ed4e8516', 'FCE', 'd60c741d-fab4-546a-8259-400b1735e2be', '310dd9ef-3c1c-5fba-98fc-dc85900cdb2d', 2.1, 2.5, 2.7, 2.6, 1, 'Reprobada'),
    ('08bb084a-7842-5756-b418-6edb20c11a61', 'FCE', 'c632fc99-88e6-5483-98d4-af266e3aa89b', 'a614426f-e47b-5639-82b7-6046f42b1a83', 2.0, 2.2, 2.4, 2.2, 1, 'Reprobada');

INSERT INTO facultad_ciencias_educacion.homologacion (
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
    ('74889735-1fa7-5571-9a8e-a43a94c23c87', 'FCE', '24642cea-35d2-53c4-bc69-d80647a4870b', '1ec5ec74-6c9e-570c-a250-ee8c65fbd9b8', 'Asignatura equivalente externa', 'Universidad Externa', '34dabb9e-089e-5725-b987-f32b10273401', '2026-03-01', 'En revision', 'Pendiente de revisión documental', null, null),
    ('7cb56f4e-5544-5f51-bcd5-8a6aacaf52db', 'FCE', 'f000119e-5258-5867-842e-e3953ac45cd4', '6d96f125-ef1d-5cd4-acea-9ffba5ff4a10', 'Curso equivalente', 'Institución Externa', '34dabb9e-089e-5725-b987-f32b10273401', '2025-09-01', 'Aprobada', 'Homologación aprobada', '2025-09-15', 4.1);

INSERT INTO facultad_ciencias_educacion.decano (
    id_decano,
    id_facultad,
    id_profesor,
    id_periodo_academico
) VALUES
    ('ddde2508-28d6-5294-a03c-7ce29b2bafd0', 'FCE', '24642cea-35d2-53c4-bc69-d80647a4870b', '2026-1');

INSERT INTO facultad_ciencias_educacion.coordinador (
    id_coordinador,
    id_facultad,
    id_profesor,
    id_periodo_academico,
    id_programa_academico
) VALUES
    ('3bc54060-16aa-517c-8014-d92efe9a673d', 'FCE', 'f000119e-5258-5867-842e-e3953ac45cd4', '2026-1', 'MAT');
