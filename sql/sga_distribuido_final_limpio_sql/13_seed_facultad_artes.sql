-- Seed Facultad de Artes ASAB. Ejecutar conectado a sga_facultad_artes. Solo INSERT directos.
INSERT INTO facultad_artes.estudiante (
    id_estudiante,
    id_usuario,
    id_facultad,
    id_programa_academico,
    limite_matriculas,
    estado_estudiante
) VALUES
    ('4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', '08de0956-8bec-53a3-8208-b80106f5cf81', 'FART', 'ARTM', 15, 'Activo'),
    ('2546ac8e-ac54-5eea-b55a-b27bb5efe64a', 'b99a3e60-fa7e-5dde-b27d-f740d2ebab00', 'FART', 'ARTM', 15, 'Activo'),
    ('1beeb244-a7cb-5372-900b-f8e1d8492267', 'bd6b096f-7b46-5485-9581-704939921590', 'FART', 'ARTM', 15, 'Activo'),
    ('91dab89e-f637-5be7-9af1-0bcf55822a48', '64ae17d0-cf42-54ac-abaf-36099512af83', 'FART', 'ARTM', 15, 'Inactivo'),
    ('377447cc-8696-5ca7-80e6-5a43000d897d', '26cf406d-e91b-5b5d-8d0a-e26037b52e50', 'FART', 'ARTM', 15, 'Activo'),
    ('4c43cf84-2506-5a81-866f-a5abeef00c77', 'e8425f49-40c0-57c4-92a1-5e9bcd884d4e', 'FART', 'ARTM', 15, 'Activo');

INSERT INTO facultad_artes.profesor (
    id_profesor,
    id_usuario,
    id_facultad,
    categoria,
    vinculacion
) VALUES
    ('d7297942-0401-5798-bacc-ba592f8adb05', 'c521afb3-bca2-547f-a51e-967f056e46db', 'FART', 'Asociado', 'Planta'),
    ('c90f040d-bef0-5125-afc0-1c72f14c01b3', '06d75246-2882-5b46-8e23-f35b7e94fab1', 'FART', 'Asistente', 'Planta');

INSERT INTO facultad_artes.administrativo (
    id_administrativo,
    id_usuario,
    id_facultad,
    detalles
) VALUES
    ('123923de-e251-540d-ab13-6fc1be330ce3', 'bbfed6cf-400a-5b42-b9b2-0111a203e3fa', 'FART', 'Secretaría académica');

INSERT INTO facultad_artes.programa_asignatura (
    id_programa_asignatura,
    id_facultad,
    id_programa_academico,
    cod_asignatura,
    semestre_sugerido,
    tipo_asignatura,
    estado
) VALUES
    ('cf2c6309-9d15-55c3-a67a-86bda2dbc52f', 'FART', 'ARTM', 'ART101', 1, 'Obligatoria', 'Activa'),
    ('cb95a78b-380d-56f6-8d5b-fd63f2cfa99d', 'FART', 'ARTM', 'MUS101', 2, 'Obligatoria', 'Activa'),
    ('46df919c-d8da-5dea-bdb7-85f9d51fea40', 'FART', 'ARTM', 'ETI101', 3, 'Obligatoria', 'Activa'),
    ('a722ab7a-923b-57df-94d7-4505db3f7923', 'FART', 'ARTM', 'INV101', 4, 'Obligatoria', 'Activa');

INSERT INTO facultad_artes.pre_requisito (
    id_pre_requisito,
    id_facultad,
    id_programa_academico,
    id_programa_asignatura,
    id_programa_asignatura_requisito
) VALUES
    ('ed8bdaad-c924-5571-bb54-f548be92493b', 'FART', 'ARTM', 'cb95a78b-380d-56f6-8d5b-fd63f2cfa99d', 'cf2c6309-9d15-55c3-a67a-86bda2dbc52f'),
    ('fc755a30-5d13-594f-a1ee-96b2c6f67f08', 'FART', 'ARTM', '46df919c-d8da-5dea-bdb7-85f9d51fea40', 'cb95a78b-380d-56f6-8d5b-fd63f2cfa99d');

INSERT INTO facultad_artes.grupo (
    id_grupo,
    id_facultad,
    id_programa_asignatura,
    id_periodo_academico,
    id_profesor,
    codigo_grupo,
    cupo_maximo,
    estado_grupo
) VALUES
    ('d5046e74-582e-5532-9db5-a58d97ec3860', 'FART', 'cf2c6309-9d15-55c3-a67a-86bda2dbc52f', '2026-1', 'd7297942-0401-5798-bacc-ba592f8adb05', 'ART101-01', 5, 'En curso'),
    ('4a645070-14ff-5d26-b44c-f41e33a25cc2', 'FART', 'cb95a78b-380d-56f6-8d5b-fd63f2cfa99d', '2026-1', 'c90f040d-bef0-5125-afc0-1c72f14c01b3', 'MUS101-01', 5, 'En curso'),
    ('f24ce792-98ae-5e2c-99be-d463ba169fb6', 'FART', '46df919c-d8da-5dea-bdb7-85f9d51fea40', '2026-1', null, 'ETI101-SD', 5, 'Abierto'),
    ('47f4bdb6-88dc-58b6-be98-db12c88836fd', 'FART', 'cf2c6309-9d15-55c3-a67a-86bda2dbc52f', '2025-2', 'd7297942-0401-5798-bacc-ba592f8adb05', 'ART101-H1', 30, 'Finalizado'),
    ('e3b347c8-4ba1-560b-98cb-26eac76c05ff', 'FART', 'cb95a78b-380d-56f6-8d5b-fd63f2cfa99d', '2025-2', 'c90f040d-bef0-5125-afc0-1c72f14c01b3', 'MUS101-H1', 30, 'Finalizado'),
    ('357136dc-db3a-5ae1-823c-7d04b00ddfc3', 'FART', '46df919c-d8da-5dea-bdb7-85f9d51fea40', '2025-2', 'd7297942-0401-5798-bacc-ba592f8adb05', 'ETI101-H1', 30, 'Finalizado'),
    ('2cccc2f2-f8a5-53f7-bbd2-b5a73066d4c5', 'FART', 'a722ab7a-923b-57df-94d7-4505db3f7923', '2025-2', 'c90f040d-bef0-5125-afc0-1c72f14c01b3', 'INV101-H1', 30, 'Finalizado');

INSERT INTO facultad_artes.matricula (
    id_matricula,
    id_facultad,
    id_estudiante,
    id_recibo,
    estado_matricula
) VALUES
    ('29de8aee-42fa-5764-83e6-0a3eb5530379', 'FART', '4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', 'ee8f5dcb-35d4-551a-9906-61be0b1094b9', 'Activa'),
    ('955c7acd-1231-59dd-97fb-947fd478948e', 'FART', '2546ac8e-ac54-5eea-b55a-b27bb5efe64a', '4d02676a-a791-5d05-a4b8-0afd1d90995f', 'Activa'),
    ('72332765-49f3-5037-86d5-a1597f1b7662', 'FART', '1beeb244-a7cb-5372-900b-f8e1d8492267', 'ddee4c34-2421-59a4-9f58-afc58e1550ba', 'Activa'),
    ('2eb89b23-d6a1-52a4-b56d-0aab8fe8e87b', 'FART', '91dab89e-f637-5be7-9af1-0bcf55822a48', '8b81eaab-86c9-550b-8d63-67aafc5018e8', 'Activa'),
    ('21b21a1f-bdcf-5b2c-9029-5c3ba2a150aa', 'FART', '377447cc-8696-5ca7-80e6-5a43000d897d', '2b62aca0-69d8-552d-8430-50456649dfc3', 'Activa'),
    ('ee60c745-12c3-5674-bc2d-ddfe186e9595', 'FART', '4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', '73795e36-c3c3-5da1-ac10-61208765b1b2', 'Finalizada'),
    ('3067e7dd-c9f5-5323-bd10-bd7fa982a1fb', 'FART', '2546ac8e-ac54-5eea-b55a-b27bb5efe64a', 'c73d2941-10a0-56a1-839b-8b51961e2a4f', 'Finalizada'),
    ('cc6ddb61-04d6-57db-89a9-150a54ee9038', 'FART', '1beeb244-a7cb-5372-900b-f8e1d8492267', '6e690535-356b-54aa-ae41-167a83b5fd04', 'Finalizada'),
    ('6a65e093-0df1-5dfa-bff9-c2f0a2aebfe6', 'FART', '91dab89e-f637-5be7-9af1-0bcf55822a48', 'eb77862b-2031-5dc4-ad57-5dcf9ea95bce', 'Finalizada'),
    ('ec2f5a2f-2c61-58cb-a2b7-fcb3121f0947', 'FART', '377447cc-8696-5ca7-80e6-5a43000d897d', 'a517bccb-5c9b-59a0-93eb-e51c1938e964', 'Finalizada');

INSERT INTO facultad_artes.inscripcion (
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
    ('9a5af85a-7e76-5070-8e9e-472e9d588f56', 'FART', 'd5046e74-582e-5532-9db5-a58d97ec3860', '4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', 3.6, null, null, null, 1, 'Cursando'),
    ('b21f4aa9-0a15-59f3-8c56-ee4abc419cd4', 'FART', 'd5046e74-582e-5532-9db5-a58d97ec3860', '2546ac8e-ac54-5eea-b55a-b27bb5efe64a', 3.6, null, null, null, 1, 'Cursando'),
    ('1c9b272c-f44c-5317-b215-9c81321a7c5e', 'FART', 'd5046e74-582e-5532-9db5-a58d97ec3860', '1beeb244-a7cb-5372-900b-f8e1d8492267', 3.6, null, null, null, 1, 'Cursando'),
    ('de2a52d5-895b-54d4-8c92-52016c6422ca', 'FART', 'd5046e74-582e-5532-9db5-a58d97ec3860', '91dab89e-f637-5be7-9af1-0bcf55822a48', 3.6, null, null, null, 1, 'Cursando'),
    ('8c18f875-25b0-571c-ac65-5aaa6de24e80', 'FART', 'd5046e74-582e-5532-9db5-a58d97ec3860', '377447cc-8696-5ca7-80e6-5a43000d897d', 3.6, null, null, null, 1, 'Cursando'),
    ('6702c7eb-364b-5510-84e2-78fc43499bc1', 'FART', '4a645070-14ff-5d26-b44c-f41e33a25cc2', '2546ac8e-ac54-5eea-b55a-b27bb5efe64a', 3.1, null, null, null, 1, 'Cursando'),
    ('b7fcb21b-b6d9-59f8-af8a-680a2bc90022', 'FART', '4a645070-14ff-5d26-b44c-f41e33a25cc2', '1beeb244-a7cb-5372-900b-f8e1d8492267', 3.1, null, null, null, 1, 'Cursando'),
    ('99345491-c429-59e5-9999-12c14040de58', 'FART', '4a645070-14ff-5d26-b44c-f41e33a25cc2', '377447cc-8696-5ca7-80e6-5a43000d897d', 3.1, null, null, null, 2, 'Cursando'),
    ('747f4577-f523-5f06-85cb-018f360e08d5', 'FART', '47f4bdb6-88dc-58b6-be98-db12c88836fd', '4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('dac59a40-516b-551d-8309-59edb48c763f', 'FART', 'e3b347c8-4ba1-560b-98cb-26eac76c05ff', '4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('73153ede-3c10-550e-beb7-f6b0ec0a9cb5', 'FART', '357136dc-db3a-5ae1-823c-7d04b00ddfc3', '4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('190b191b-353f-5eb8-a6f7-f92b706e744b', 'FART', '2cccc2f2-f8a5-53f7-bbd2-b5a73066d4c5', '4a2ff7c3-dbc8-5010-a865-cae7320ce9d0', 4.0, 4.2, 4.5, 4.3, 1, 'Aprobada'),
    ('af212fac-521b-5dce-9f96-792fa023459d', 'FART', '47f4bdb6-88dc-58b6-be98-db12c88836fd', '2546ac8e-ac54-5eea-b55a-b27bb5efe64a', 2.1, 2.4, 2.7, 2.4, 1, 'Reprobada'),
    ('fa0b6538-21d0-5213-a8de-cc880aa1a187', 'FART', 'e3b347c8-4ba1-560b-98cb-26eac76c05ff', '2546ac8e-ac54-5eea-b55a-b27bb5efe64a', 3.1, 3.2, 3.4, 3.2, 1, 'Aprobada'),
    ('301cd655-55ce-5fa5-8d35-c01639bbb79c', 'FART', '47f4bdb6-88dc-58b6-be98-db12c88836fd', '1beeb244-a7cb-5372-900b-f8e1d8492267', 2.0, 2.4, 2.6, 2.2, 1, 'Reprobada'),
    ('017b630d-539d-5fea-aa8c-1c8ce6a81b0c', 'FART', 'e3b347c8-4ba1-560b-98cb-26eac76c05ff', '1beeb244-a7cb-5372-900b-f8e1d8492267', 2.0, 2.4, 2.6, 2.5, 1, 'Reprobada'),
    ('5135d7d4-0a30-53c2-8083-94dab00533af', 'FART', '357136dc-db3a-5ae1-823c-7d04b00ddfc3', '1beeb244-a7cb-5372-900b-f8e1d8492267', 2.0, 2.4, 2.6, 2.7, 1, 'Reprobada'),
    ('8e812e1a-7b68-54e4-9671-6c32c07fd852', 'FART', 'e3b347c8-4ba1-560b-98cb-26eac76c05ff', '377447cc-8696-5ca7-80e6-5a43000d897d', 2.1, 2.5, 2.7, 2.6, 1, 'Reprobada'),
    ('eadc7391-1372-53dd-8386-5fcc1572f4a7', 'FART', '357136dc-db3a-5ae1-823c-7d04b00ddfc3', '91dab89e-f637-5be7-9af1-0bcf55822a48', 2.0, 2.2, 2.4, 2.2, 1, 'Reprobada');

INSERT INTO facultad_artes.homologacion (
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
    ('de5c283f-3c4d-5a3d-80b0-d9ddbefc780c', 'FART', 'd7297942-0401-5798-bacc-ba592f8adb05', '1beeb244-a7cb-5372-900b-f8e1d8492267', 'Asignatura equivalente externa', 'Universidad Externa', 'a722ab7a-923b-57df-94d7-4505db3f7923', '2026-03-01', 'En revision', 'Pendiente de revisión documental', null, null),
    ('b4a531f5-9f5a-5701-80d5-5c92a7903c23', 'FART', 'c90f040d-bef0-5125-afc0-1c72f14c01b3', '2546ac8e-ac54-5eea-b55a-b27bb5efe64a', 'Curso equivalente', 'Institución Externa', 'a722ab7a-923b-57df-94d7-4505db3f7923', '2025-09-01', 'Aprobada', 'Homologación aprobada', '2025-09-15', 4.1);

INSERT INTO facultad_artes.decano (
    id_decano,
    id_facultad,
    id_profesor,
    id_periodo_academico
) VALUES
    ('ae99ff5b-bef8-5b35-96b5-afdf88349ae3', 'FART', 'd7297942-0401-5798-bacc-ba592f8adb05', '2026-1');

INSERT INTO facultad_artes.coordinador (
    id_coordinador,
    id_facultad,
    id_profesor,
    id_periodo_academico,
    id_programa_academico
) VALUES
    ('ca2dabc8-39d3-5138-8293-7269d53d97d8', 'FART', 'c90f040d-bef0-5125-afc0-1c72f14c01b3', '2026-1', 'ARTM');
