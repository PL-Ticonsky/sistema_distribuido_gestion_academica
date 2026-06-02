-- Ejecutar conectado a postgres. OPCIONAL: borra todo para iniciar limpio.
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname IN ('sga_central','sga_facultad_ingenieria','sga_facultad_ciencias_educacion','sga_facultad_tecnologica','sga_facultad_medio_ambiente','sga_facultad_artes') AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS sga_central;

DROP DATABASE IF EXISTS sga_facultad_ingenieria;

DROP DATABASE IF EXISTS sga_facultad_ciencias_educacion;

DROP DATABASE IF EXISTS sga_facultad_tecnologica;

DROP DATABASE IF EXISTS sga_facultad_medio_ambiente;

DROP DATABASE IF EXISTS sga_facultad_artes;

DROP ROLE IF EXISTS usr_admin_institucional;

DROP ROLE IF EXISTS usr_seguridad_admin;

DROP ROLE IF EXISTS usr_operador_ingenieria;

DROP ROLE IF EXISTS usr_operador_ciencias;

DROP ROLE IF EXISTS usr_operador_tecnologica;

DROP ROLE IF EXISTS usr_operador_medio_ambiente;

DROP ROLE IF EXISTS usr_operador_artes;

DROP ROLE IF EXISTS usr_financiero;

DROP ROLE IF EXISTS usr_auditor;

DROP ROLE IF EXISTS usr_rectoria;

DROP ROLE IF EXISTS rol_admin_institucional;

DROP ROLE IF EXISTS rol_seguridad_admin;

DROP ROLE IF EXISTS rol_facultad_ingenieria_rw;

DROP ROLE IF EXISTS rol_facultad_ciencias_rw;

DROP ROLE IF EXISTS rol_facultad_tecnologica_rw;

DROP ROLE IF EXISTS rol_facultad_medio_ambiente_rw;

DROP ROLE IF EXISTS rol_facultad_artes_rw;

DROP ROLE IF EXISTS rol_financiero_rw;

DROP ROLE IF EXISTS rol_auditoria_ro;

DROP ROLE IF EXISTS rol_rectoria_ro;
