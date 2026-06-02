-- Seed Facultad Tecnológica. Ejecutar conectado a sga_facultad_tecnologica. Solo INSERT directos.
INSERT INTO facultad_tecnologica.estudiante (
    id_estudiante,
    id_usuario,
    id_facultad,
    id_programa_academico,
    limite_matriculas,
    estado_estudiante
) VALUES
    ('77244e1c-0765-5f4c-90e5-6c81cdac7829', 'f0ca5e5f-976d-5199-9d19-0b927a096ee5', 'FTEC', 'TSD', 15, 'Activo'),
    ('599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', 'a0c5b631-74b4-57e9-afe7-2a984919eec3', 'FTEC', 'TSD', 15, 'Activo'),
    ('9334a155-cda0-5260-8be7-028b7e77c50e', 'cf066cb7-d143-5c21-9f82-a06157dabc36', 'FTEC', 'TSD', 15, 'Activo'),
    ('a7ccc807-79e1-509e-ac6d-71d1605b6d35', '2cf32ff8-0348-558a-9a25-53e55d9dec6e', 'FTEC', 'TSD', 15, 'Inactivo'),
    ('260e0ac9-f098-5848-ae43-f0822c2a4552', '864be4d8-d02f-56f9-ab61-9095a28478a3', 'FTEC', 'TSD', 15, 'Activo'),
    ('6b327c75-f5af-5e1a-b860-b36f9e628b6b', '746e6e39-36b0-5b7a-a691-664f96db8352', 'FTEC', 'TSD', 15, 'Activo');

INSERT INTO facultad_tecnologica.profesor (
    id_profesor,
    id_usuario,
    id_facultad,
    categoria,
    vinculacion
) VALUES
    ('76a339c7-9156-5995-840c-28f1f89bc80b', '01374452-6045-524b-a66c-9d18cccf1906', 'FTEC', 'Asociado', 'Planta'),
    ('759bf8ee-b398-588c-95ce-fd9e61c4276b', 'bba1e1dc-f11b-5fb3-b738-847f219af28d', 'FTEC', 'Asistente', 'Planta');

INSERT INTO facultad_tecnologica.administrativo (
    id_administrativo,
    id_usuario,
    id_facultad,
    detalles
) VALUES
    ('6fef61dd-98cf-5967-82e9-066da5e0e998', 'd5432768-b4bd-54b1-bf09-3be4a0dc6bfc', 'FTEC', 'Secretaría académica');

INSERT INTO facultad_tecnologica.programa_asignatura (
    id_programa_asignatura,
    id_facultad,
    id_programa_academico,
    cod_asignatura,
    semestre_sugerido,
    tipo_asignatura,
    estado
) VALUES
    ('651b360e-216b-5130-a6ad-20c19a0763ba', 'FTEC', 'TSD', 'TSD101', 1, 'Obligatoria', 'Activa'),
    ('16caa154-7f06-5c51-ad05-bbc7a2d41f3f', 'FTEC', 'TSD', 'BD101', 2, 'Obligatoria', 'Activa'),
    ('a648a5db-db30-5923-8adf-a48dcf97ad35', 'FTEC', 'TSD', 'IND101', 3, 'Obligatoria', 'Activa'),
    ('f844319a-1577-52c1-8731-dca62319e086', 'FTEC', 'TSD', 'EST101', 4, 'Obligatoria', 'Activa');

INSERT INTO facultad_tecnologica.pre_requisito (
    id_pre_requisito,
    id_facultad,
    id_programa_academico,
    id_programa_asignatura,
    id_programa_asignatura_requisito
) VALUES
    ('5d734d5f-be66-5800-8d3d-6cacffaf541e', 'FTEC', 'TSD', '16caa154-7f06-5c51-ad05-bbc7a2d41f3f', '651b360e-216b-5130-a6ad-20c19a0763ba'),
    ('e8c3edea-cd0d-5b91-afd2-1b36f55de485', 'FTEC', 'TSD', 'a648a5db-db30-5923-8adf-a48dcf97ad35', '16caa154-7f06-5c51-ad05-bbc7a2d41f3f');

INSERT INTO facultad_tecnologica.grupo (
    id_grupo,
    id_facultad,
    id_programa_asignatura,
    id_periodo_academico,
    id_profesor,
    codigo_grupo,
    cupo_maximo,
    estado_grupo
) VALUES
    ('96cefb34-69ce-5ae2-98ea-0e16728d9eec', 'FTEC', '651b360e-216b-5130-a6ad-20c19a0763ba', '2026-1', '76a339c7-9156-5995-840c-28f1f89bc80b', 'TSD101-01', 5, 'En curso'),
    ('31f89435-32f5-5daa-a7a3-a51952f3801d', 'FTEC', '16caa154-7f06-5c51-ad05-bbc7a2d41f3f', '2026-1', '759bf8ee-b398-588c-95ce-fd9e61c4276b', 'BD101-01', 5, 'En curso'),
    ('18eda460-e142-5124-9679-e1321fd8e4a4', 'FTEC', 'a648a5db-db30-5923-8adf-a48dcf97ad35', '2026-1', null, 'IND101-SD', 5, 'Abierto'),
    ('03cc2852-42ce-527d-b165-4d3cdf5bff9a', 'FTEC', '651b360e-216b-5130-a6ad-20c19a0763ba', '2025-2', '76a339c7-9156-5995-840c-28f1f89bc80b', 'TSD101-H1', 30, 'Finalizado'),
    ('e97ec875-f54f-540f-b578-4201d3097c91', 'FTEC', '16caa154-7f06-5c51-ad05-bbc7a2d41f3f', '2025-2', '759bf8ee-b398-588c-95ce-fd9e61c4276b', 'BD101-H1', 30, 'Finalizado'),
    ('1873a4ea-2678-5678-a6b9-0a2b509963ab', 'FTEC', 'a648a5db-db30-5923-8adf-a48dcf97ad35', '2025-2', '76a339c7-9156-5995-840c-28f1f89bc80b', 'IND101-H1', 30, 'Finalizado'),
    ('20a10956-cffc-5d2d-8500-d1bcbabdf987', 'FTEC', 'f844319a-1577-52c1-8731-dca62319e086', '2025-2', '759bf8ee-b398-588c-95ce-fd9e61c4276b', 'EST101-H1', 30, 'Finalizado');

INSERT INTO facultad_tecnologica.matricula (
    id_matricula,
    id_facultad,
    id_estudiante,
    id_recibo,
    estado_matricula
) VALUES
    ('94c90290-2e5d-5428-8457-ccd1f1c5cc12', 'FTEC', '77244e1c-0765-5f4c-90e5-6c81cdac7829', '82907dee-fc8d-5b3e-9a2a-ad168809033c', 'Activa'),
    ('ba3f244e-0ac0-5b57-b3ee-1014fe5aabed', 'FTEC', '599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', '7495a12b-db03-5f3b-971d-f7d58453deaa', 'Activa'),
    ('e85a594c-3b44-57b2-b0ba-0b7a5b957a4c', 'FTEC', '9334a155-cda0-5260-8be7-028b7e77c50e', '8c2dc216-da3d-5c32-aa44-398093ba26c2', 'Activa'),
    ('36810949-7333-515b-aced-899e47318cdd', 'FTEC', 'a7ccc807-79e1-509e-ac6d-71d1605b6d35', 'af812f1f-2f79-50d6-aabc-f134588a6397', 'Activa'),
    ('5cd14724-f4f2-5092-a5c8-a0d962947ebc', 'FTEC', '260e0ac9-f098-5848-ae43-f0822c2a4552', '96bbe0c2-53c7-5e7a-94b7-9686c4d61f83', 'Activa'),
    ('a6e3b21f-48df-5378-8d00-df1b6384f159', 'FTEC', '77244e1c-0765-5f4c-90e5-6c81cdac7829', '186f9ade-9ccc-5969-a3cc-9923efae0ea9', 'Finalizada'),
    ('3f7c1f0a-b974-5658-ba19-cdaa7cd52934', 'FTEC', '599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', '70b82fdf-39fd-5f38-bc25-083258fcf762', 'Finalizada'),
    ('c71648b0-529a-50e0-8573-55516a910b02', 'FTEC', '9334a155-cda0-5260-8be7-028b7e77c50e', '56604a1e-cd12-5fd6-8390-e9937e5fe9d1', 'Finalizada'),
    ('f4f1b4d3-b61d-5baa-809e-5979055072e7', 'FTEC', 'a7ccc807-79e1-509e-ac6d-71d1605b6d35', 'af4e40c2-52c6-56d5-8597-cb1e3ce8815e', 'Finalizada'),
    ('209e52ed-8811-5ac3-91c7-0a2364dc3a8e', 'FTEC', '260e0ac9-f098-5848-ae43-f0822c2a4552', '1cc3992c-4a56-5e5e-87d9-d41e61ff815a', 'Finalizada');

INSERT INTO facultad_tecnologica.inscripcion (
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
    ('081e7ece-91d9-521e-916a-57b6762487c5', 'FTEC', '96cefb34-69ce-5ae2-98ea-0e16728d9eec', '77244e1c-0765-5f4c-90e5-6c81cdac7829', 3.6, null, null, null, 1, 'Cursando'),
    ('133f414d-11ed-5353-91b7-e1a47ff1a8c5', 'FTEC', '96cefb34-69ce-5ae2-98ea-0e16728d9eec', '599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', 3.6, null, null, null, 1, 'Cursando'),
    ('91277173-665d-5990-ba82-46d9fa8c9347', 'FTEC', '96cefb34-69ce-5ae2-98ea-0e16728d9eec', '9334a155-cda0-5260-8be7-028b7e77c50e', 3.6, null, null, null, 1, 'Cursando'),
    ('8d133c34-9035-5a3e-9b2d-9c5105e159c2', 'FTEC', '96cefb34-69ce-5ae2-98ea-0e16728d9eec', 'a7ccc807-79e1-509e-ac6d-71d1605b6d35', 3.6, null, null, null, 1, 'Cursando'),
    ('a90bdefb-748a-55ef-8d7a-a7e4600220f0', 'FTEC', '96cefb34-69ce-5ae2-98ea-0e16728d9eec', '260e0ac9-f098-5848-ae43-f0822c2a4552', 3.6, null, null, null, 1, 'Cursando'),
    ('82959b11-7f06-5fc5-84d1-89d32945aece', 'FTEC', '31f89435-32f5-5daa-a7a3-a51952f3801d', '599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', 3.1, null, null, null, 1, 'Cursando'),
    ('229fe006-9cc2-5fd1-996c-dc59f84a7791', 'FTEC', '31f89435-32f5-5daa-a7a3-a51952f3801d', '9334a155-cda0-5260-8be7-028b7e77c50e', 3.1, null, null, null, 1, 'Cursando'),
    ('66d69b9a-c89a-5220-b779-2ee3617a8694', 'FTEC', '31f89435-32f5-5daa-a7a3-a51952f3801d', '260e0ac9-f098-5848-ae43-f0822c2a4552', 3.1, null, null, null, 2, 'Cursando'),
    ('d1debde2-5300-5337-8863-fa9e750870c3', 'FTEC', '03cc2852-42ce-527d-b165-4d3cdf5bff9a', '77244e1c-0765-5f4c-90e5-6c81cdac7829', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('75baf89b-0f34-55bf-b04e-66a8398a821d', 'FTEC', 'e97ec875-f54f-540f-b578-4201d3097c91', '77244e1c-0765-5f4c-90e5-6c81cdac7829', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('ccc09776-1104-5341-a443-fcf3c1c4fcec', 'FTEC', '1873a4ea-2678-5678-a6b9-0a2b509963ab', '77244e1c-0765-5f4c-90e5-6c81cdac7829', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('e1c0c9de-6d20-5ec9-a9e7-4353c4dd3c2c', 'FTEC', '20a10956-cffc-5d2d-8500-d1bcbabdf987', '77244e1c-0765-5f4c-90e5-6c81cdac7829', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('11c8b2e4-3b2c-5cfa-bf15-88ef78c0955f', 'FTEC', '03cc2852-42ce-527d-b165-4d3cdf5bff9a', '599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', 2.1, 2.4, 2.7, 2.4, 1, 'Reprobada'),
    ('d1de7eee-821b-5ca3-9a68-61519bee1d9c', 'FTEC', 'e97ec875-f54f-540f-b578-4201d3097c91', '599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', 3.1, 3.2, 3.4, 3.2, 1, 'Aprobada'),
    ('60ccff26-44bb-5b13-88fe-33392531af19', 'FTEC', '03cc2852-42ce-527d-b165-4d3cdf5bff9a', '9334a155-cda0-5260-8be7-028b7e77c50e', 2.0, 2.4, 2.6, 2.2, 1, 'Reprobada'),
    ('267587bd-4fe1-5a84-8b86-4d0c7838799d', 'FTEC', 'e97ec875-f54f-540f-b578-4201d3097c91', '9334a155-cda0-5260-8be7-028b7e77c50e', 2.0, 2.4, 2.6, 2.5, 1, 'Reprobada'),
    ('fea6861d-5368-5b55-b5ab-61fbe92d4525', 'FTEC', '1873a4ea-2678-5678-a6b9-0a2b509963ab', '9334a155-cda0-5260-8be7-028b7e77c50e', 2.0, 2.4, 2.6, 2.7, 1, 'Reprobada'),
    ('d76ff8b1-a8a6-5a4e-b538-8f2aed75741c', 'FTEC', 'e97ec875-f54f-540f-b578-4201d3097c91', '260e0ac9-f098-5848-ae43-f0822c2a4552', 2.1, 2.5, 2.7, 2.6, 1, 'Reprobada'),
    ('bba87196-8182-5d25-97d9-9611b9c3d915', 'FTEC', '1873a4ea-2678-5678-a6b9-0a2b509963ab', 'a7ccc807-79e1-509e-ac6d-71d1605b6d35', 2.0, 2.2, 2.4, 2.2, 1, 'Reprobada');

INSERT INTO facultad_tecnologica.homologacion (
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
    ('dc3bfee2-4912-5f09-ab4f-1aaa422333dc', 'FTEC', '76a339c7-9156-5995-840c-28f1f89bc80b', '9334a155-cda0-5260-8be7-028b7e77c50e', 'Asignatura equivalente externa', 'Universidad Externa', 'f844319a-1577-52c1-8731-dca62319e086', '2026-03-01', 'En revision', 'Pendiente de revisión documental', null, null),
    ('2f0cbd9b-e9a1-5369-ba3e-5dd1e10975a1', 'FTEC', '759bf8ee-b398-588c-95ce-fd9e61c4276b', '599cfd88-d1b9-527c-8125-0f3ebcc1d6cd', 'Curso equivalente', 'Institución Externa', 'f844319a-1577-52c1-8731-dca62319e086', '2025-09-01', 'Aprobada', 'Homologación aprobada', '2025-09-15', 4.1);

INSERT INTO facultad_tecnologica.decano (
    id_decano,
    id_facultad,
    id_profesor,
    id_periodo_academico
) VALUES
    ('1523a2a7-87c5-53c5-b44f-d8a6c2567ccd', 'FTEC', '76a339c7-9156-5995-840c-28f1f89bc80b', '2026-1');

INSERT INTO facultad_tecnologica.coordinador (
    id_coordinador,
    id_facultad,
    id_profesor,
    id_periodo_academico,
    id_programa_academico
) VALUES
    ('eaef6cdb-5b0a-5b3d-863f-df0e9754cccb', 'FTEC', '759bf8ee-b398-588c-95ce-fd9e61c4276b', '2026-1', 'TSD');
