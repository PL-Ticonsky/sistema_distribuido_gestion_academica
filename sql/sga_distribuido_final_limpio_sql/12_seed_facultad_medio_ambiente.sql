-- Seed Facultad de Medio Ambiente y Recursos Naturales. Ejecutar conectado a sga_facultad_medio_ambiente. Solo INSERT directos.
INSERT INTO facultad_medio_ambiente.estudiante (
    id_estudiante,
    id_usuario,
    id_facultad,
    id_programa_academico,
    limite_matriculas,
    estado_estudiante
) VALUES
    ('b28c328b-9144-57c2-be55-328736917101', 'b273cefd-c446-5cdf-87bf-120927891b3f', 'FMA', 'IAM', 15, 'Activo'),
    ('d9a05974-9754-52a5-98a8-f8eeb4c9c3c6', '88f928dc-6340-5d9e-9547-a6b8919d6ee9', 'FMA', 'IAM', 15, 'Activo'),
    ('5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 'a48596aa-0cca-57bf-b29b-f2b5636f8940', 'FMA', 'IAM', 15, 'Activo'),
    ('dd26805b-261c-5021-98ea-00078a63fd54', 'a7a0621d-305a-595c-a4c8-c2cb7252cca6', 'FMA', 'IAM', 15, 'Inactivo'),
    ('7f5f609d-ef21-5d7f-851a-80d2b7194bf6', 'a797f8f8-6730-53dc-ae0b-177fe9877879', 'FMA', 'IAM', 15, 'Activo'),
    ('32e58bb1-0e4b-577d-ac15-9fbc33777dac', 'a3436d16-08e8-598e-9801-83ebecc740a8', 'FMA', 'IAM', 15, 'Activo');

INSERT INTO facultad_medio_ambiente.profesor (
    id_profesor,
    id_usuario,
    id_facultad,
    categoria,
    vinculacion
) VALUES
    ('864e1d8a-f73d-55c3-b415-fb7cc00d600e', '493527d7-c220-5738-a41a-d8aee46ad436', 'FMA', 'Asociado', 'Planta'),
    ('c7add78c-6f53-53da-b0cf-edbbcc41bf00', '92e97cdd-389b-5fd0-b86c-30caeaee8407', 'FMA', 'Asistente', 'Planta');

INSERT INTO facultad_medio_ambiente.administrativo (
    id_administrativo,
    id_usuario,
    id_facultad,
    detalles
) VALUES
    ('c751b149-e76e-590f-9b42-87ecef902f89', '90fa48dd-d5eb-5f3e-b691-9d8ac589d5dc', 'FMA', 'Secretaría académica');

INSERT INTO facultad_medio_ambiente.programa_asignatura (
    id_programa_asignatura,
    id_facultad,
    id_programa_academico,
    cod_asignatura,
    semestre_sugerido,
    tipo_asignatura,
    estado
) VALUES
    ('542147a8-620c-5088-a18f-74711691fb3f', 'FMA', 'IAM', 'AMB101', 1, 'Obligatoria', 'Activa'),
    ('9eb354ef-b2dd-5c8a-8c93-65aa3d8cc2cd', 'FMA', 'IAM', 'GIS101', 2, 'Obligatoria', 'Activa'),
    ('7ca51a5d-78cb-596d-b92e-2084682c2b62', 'FMA', 'IAM', 'BIO101', 3, 'Obligatoria', 'Activa'),
    ('ff487a42-d9b5-5430-bc3a-3a60ad832bb9', 'FMA', 'IAM', 'EST101', 4, 'Obligatoria', 'Activa');

INSERT INTO facultad_medio_ambiente.pre_requisito (
    id_pre_requisito,
    id_facultad,
    id_programa_academico,
    id_programa_asignatura,
    id_programa_asignatura_requisito
) VALUES
    ('110d8c83-bf41-5b6d-8f60-765e1e6ee998', 'FMA', 'IAM', '9eb354ef-b2dd-5c8a-8c93-65aa3d8cc2cd', '542147a8-620c-5088-a18f-74711691fb3f'),
    ('5c7c27c7-b711-5d01-91bb-c5353b5fb226', 'FMA', 'IAM', '7ca51a5d-78cb-596d-b92e-2084682c2b62', '9eb354ef-b2dd-5c8a-8c93-65aa3d8cc2cd');

INSERT INTO facultad_medio_ambiente.grupo (
    id_grupo,
    id_facultad,
    id_programa_asignatura,
    id_periodo_academico,
    id_profesor,
    codigo_grupo,
    cupo_maximo,
    estado_grupo
) VALUES
    ('eb91971d-733a-587f-b619-be37c90a5caa', 'FMA', '542147a8-620c-5088-a18f-74711691fb3f', '2026-1', '864e1d8a-f73d-55c3-b415-fb7cc00d600e', 'AMB101-01', 5, 'En curso'),
    ('83e8d009-3e6e-5f89-9f9f-ca5d3656c880', 'FMA', '9eb354ef-b2dd-5c8a-8c93-65aa3d8cc2cd', '2026-1', 'c7add78c-6f53-53da-b0cf-edbbcc41bf00', 'GIS101-01', 5, 'En curso'),
    ('c35fe9fa-f2e7-56b2-80a8-6ba8ba6a577d', 'FMA', '7ca51a5d-78cb-596d-b92e-2084682c2b62', '2026-1', null, 'BIO101-SD', 5, 'Abierto'),
    ('762e43d9-ed3a-5a45-bc7e-4ae4ea86c739', 'FMA', '542147a8-620c-5088-a18f-74711691fb3f', '2025-2', '864e1d8a-f73d-55c3-b415-fb7cc00d600e', 'AMB101-H1', 30, 'Finalizado'),
    ('42d07d17-65d5-51c1-b461-2f8a79588b06', 'FMA', '9eb354ef-b2dd-5c8a-8c93-65aa3d8cc2cd', '2025-2', 'c7add78c-6f53-53da-b0cf-edbbcc41bf00', 'GIS101-H1', 30, 'Finalizado'),
    ('9993eb3e-95a8-5d5f-a164-e80a9f077894', 'FMA', '7ca51a5d-78cb-596d-b92e-2084682c2b62', '2025-2', '864e1d8a-f73d-55c3-b415-fb7cc00d600e', 'BIO101-H1', 30, 'Finalizado'),
    ('4ea1bc86-49f2-560e-b837-f9ef6a4ba352', 'FMA', 'ff487a42-d9b5-5430-bc3a-3a60ad832bb9', '2025-2', 'c7add78c-6f53-53da-b0cf-edbbcc41bf00', 'EST101-H1', 30, 'Finalizado');

INSERT INTO facultad_medio_ambiente.matricula (
    id_matricula,
    id_facultad,
    id_estudiante,
    id_recibo,
    estado_matricula
) VALUES
    ('985fbfbb-76d2-5737-810b-6c3594415a34', 'FMA', 'b28c328b-9144-57c2-be55-328736917101', 'ae46e308-f482-5017-b9a9-9d935cc15d51', 'Activa'),
    ('cb2f2aa9-d239-5138-a8f4-561bc4f45588', 'FMA', 'd9a05974-9754-52a5-98a8-f8eeb4c9c3c6', '237cdc15-5fc9-590a-9c0f-b9810ad7c2fd', 'Activa'),
    ('fb92a74e-61cf-5831-99c4-f8e32b364c16', 'FMA', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', '962c699c-df1f-5bf1-964e-df8415c94122', 'Activa'),
    ('dea0d19b-bde6-580c-b8c8-398a4bc847fe', 'FMA', 'dd26805b-261c-5021-98ea-00078a63fd54', '68dee5f0-c556-5a12-a405-5de96d43c914', 'Activa'),
    ('62c629a4-5368-5ef1-b256-4d0efb42e6af', 'FMA', '7f5f609d-ef21-5d7f-851a-80d2b7194bf6', '1f1ae7e6-d41f-59ec-9630-e9027aa75185', 'Activa'),
    ('e645bb35-85c9-5167-baef-15f1f86c77b4', 'FMA', 'b28c328b-9144-57c2-be55-328736917101', '4d921e6b-c02c-53e3-be94-2f4fde24b7de', 'Finalizada'),
    ('e5a54a24-6111-5602-acc6-81c411218830', 'FMA', 'd9a05974-9754-52a5-98a8-f8eeb4c9c3c6', 'e36e801e-54d6-5c94-806b-45b31c5ff9e0', 'Finalizada'),
    ('c4cb62cc-a566-5de0-a83d-8897cb53b063', 'FMA', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 'd655afdd-a519-563f-ab93-c36dcca0f73c', 'Finalizada'),
    ('5630a7a0-3687-5806-bc47-af84c80fcb81', 'FMA', 'dd26805b-261c-5021-98ea-00078a63fd54', '35195a2f-ce57-5d2d-b6b0-066600eba212', 'Finalizada'),
    ('99272506-48a3-5fb5-8539-5eefff0cd29e', 'FMA', '7f5f609d-ef21-5d7f-851a-80d2b7194bf6', '099e0a07-fdc8-534f-a27a-c6af0c797cc5', 'Finalizada');

INSERT INTO facultad_medio_ambiente.inscripcion (
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
    ('482f107e-d3bd-520f-bfb7-4816ccc4ad56', 'FMA', 'eb91971d-733a-587f-b619-be37c90a5caa', 'b28c328b-9144-57c2-be55-328736917101', 3.6, null, null, null, 1, 'Cursando'),
    ('098850d6-461c-594f-b251-9bfcb28e8d7f', 'FMA', 'eb91971d-733a-587f-b619-be37c90a5caa', 'd9a05974-9754-52a5-98a8-f8eeb4c9c3c6', 3.6, null, null, null, 1, 'Cursando'),
    ('1bf19f52-42fe-5551-a874-e9203f3f8feb', 'FMA', 'eb91971d-733a-587f-b619-be37c90a5caa', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 3.6, null, null, null, 1, 'Cursando'),
    ('8d783518-b960-5b6e-83e0-430a59249456', 'FMA', 'eb91971d-733a-587f-b619-be37c90a5caa', 'dd26805b-261c-5021-98ea-00078a63fd54', 3.6, null, null, null, 1, 'Cursando'),
    ('002066ac-d177-5e07-b655-8a8918e106b8', 'FMA', 'eb91971d-733a-587f-b619-be37c90a5caa', '7f5f609d-ef21-5d7f-851a-80d2b7194bf6', 3.6, null, null, null, 1, 'Cursando'),
    ('80ae4111-2fcf-55f6-b109-2824c7365ddb', 'FMA', '83e8d009-3e6e-5f89-9f9f-ca5d3656c880', 'd9a05974-9754-52a5-98a8-f8eeb4c9c3c6', 3.1, null, null, null, 1, 'Cursando'),
    ('dc786c5a-22ca-5afe-b76a-59a85c642c98', 'FMA', '83e8d009-3e6e-5f89-9f9f-ca5d3656c880', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 3.1, null, null, null, 1, 'Cursando'),
    ('1d2a78a5-e93c-580b-a868-30f2155e1558', 'FMA', '83e8d009-3e6e-5f89-9f9f-ca5d3656c880', '7f5f609d-ef21-5d7f-851a-80d2b7194bf6', 3.1, null, null, null, 2, 'Cursando'),
    ('381bb8cc-8585-5c68-8c7f-590e2e14f4f0', 'FMA', '762e43d9-ed3a-5a45-bc7e-4ae4ea86c739', 'b28c328b-9144-57c2-be55-328736917101', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('c64e6ddb-5ccb-5cf6-bd24-6fa4984761a4', 'FMA', '42d07d17-65d5-51c1-b461-2f8a79588b06', 'b28c328b-9144-57c2-be55-328736917101', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('6f5ad9df-3a8a-5c0e-abbf-a7d95dbf37da', 'FMA', '9993eb3e-95a8-5d5f-a164-e80a9f077894', 'b28c328b-9144-57c2-be55-328736917101', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('df415710-2210-5e2e-bdfc-fea0a3f28790', 'FMA', '4ea1bc86-49f2-560e-b837-f9ef6a4ba352', 'b28c328b-9144-57c2-be55-328736917101', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('54c49b04-e422-5098-a9a7-836392c745af', 'FMA', '762e43d9-ed3a-5a45-bc7e-4ae4ea86c739', 'd9a05974-9754-52a5-98a8-f8eeb4c9c3c6', 2.1, 2.4, 2.7, 2.4, 1, 'Reprobada'),
    ('98c47065-0a9d-58c2-bfa8-96ccbbe4a6e8', 'FMA', '42d07d17-65d5-51c1-b461-2f8a79588b06', 'd9a05974-9754-52a5-98a8-f8eeb4c9c3c6', 3.1, 3.2, 3.4, 3.2, 1, 'Aprobada'),
    ('048713cf-26db-5f20-b891-c272d54e9b6b', 'FMA', '762e43d9-ed3a-5a45-bc7e-4ae4ea86c739', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 2.0, 2.4, 2.6, 2.2, 1, 'Reprobada'),
    ('be0f05e2-0502-588b-a917-c7e363c99118', 'FMA', '42d07d17-65d5-51c1-b461-2f8a79588b06', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 2.0, 2.4, 2.6, 2.5, 1, 'Reprobada'),
    ('428634e8-b6b0-55b3-b17d-d589a237abf5', 'FMA', '9993eb3e-95a8-5d5f-a164-e80a9f077894', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 2.0, 2.4, 2.6, 2.7, 1, 'Reprobada'),
    ('bccadc28-b59a-5424-9f4d-52cd01e5bfcf', 'FMA', '42d07d17-65d5-51c1-b461-2f8a79588b06', '7f5f609d-ef21-5d7f-851a-80d2b7194bf6', 2.1, 2.5, 2.7, 2.6, 1, 'Reprobada'),
    ('382cd96d-991a-5667-b78c-86bc2bf61fe0', 'FMA', '9993eb3e-95a8-5d5f-a164-e80a9f077894', 'dd26805b-261c-5021-98ea-00078a63fd54', 2.0, 2.2, 2.4, 2.2, 1, 'Reprobada');

INSERT INTO facultad_medio_ambiente.homologacion (
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
    ('05e3ff36-8e6b-5a7e-8dae-9954d09fc3d9', 'FMA', '864e1d8a-f73d-55c3-b415-fb7cc00d600e', '5b95a013-e2ad-53e8-83b7-7cade7cd8a04', 'Asignatura equivalente externa', 'Universidad Externa', 'ff487a42-d9b5-5430-bc3a-3a60ad832bb9', '2026-03-01', 'En revision', 'Pendiente de revisión documental', null, null),
    ('f374f48f-7170-5c0f-8f66-412db2f9e951', 'FMA', 'c7add78c-6f53-53da-b0cf-edbbcc41bf00', 'd9a05974-9754-52a5-98a8-f8eeb4c9c3c6', 'Curso equivalente', 'Institución Externa', 'ff487a42-d9b5-5430-bc3a-3a60ad832bb9', '2025-09-01', 'Aprobada', 'Homologación aprobada', '2025-09-15', 4.1);

INSERT INTO facultad_medio_ambiente.decano (
    id_decano,
    id_facultad,
    id_profesor,
    id_periodo_academico
) VALUES
    ('b8105480-0f41-5910-bd96-1a8afcd53c99', 'FMA', '864e1d8a-f73d-55c3-b415-fb7cc00d600e', '2026-1');

INSERT INTO facultad_medio_ambiente.coordinador (
    id_coordinador,
    id_facultad,
    id_profesor,
    id_periodo_academico,
    id_programa_academico
) VALUES
    ('b8eb819b-ef9b-5b48-8b78-1560eb7bc2cd', 'FMA', 'c7add78c-6f53-53da-b0cf-edbbcc41bf00', '2026-1', 'IAM');
