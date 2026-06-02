-- Ejecutar conectado a sga_central.
CREATE ROLE rol_admin_institucional;

CREATE ROLE rol_seguridad_admin;

CREATE ROLE rol_facultad_ingenieria_rw;

CREATE ROLE rol_facultad_ciencias_rw;

CREATE ROLE rol_facultad_tecnologica_rw;

CREATE ROLE rol_facultad_medio_ambiente_rw;

CREATE ROLE rol_facultad_artes_rw;

CREATE ROLE rol_financiero_rw;

CREATE ROLE rol_auditoria_ro;

CREATE ROLE rol_rectoria_ro;

create user usr_admin_institucional WITH password 'Admin_Institucional_2026*';

create user usr_seguridad_admin WITH password 'Seguridad_2026*';

create user usr_operador_ingenieria WITH password 'Ingenieria_2026*';

create user usr_operador_ciencias WITH password 'Ciencias_2026*';

create user usr_operador_tecnologica WITH password 'Tecnologica_2026*';

create user usr_operador_medio_ambiente WITH password 'MedioAmbiente_2026*';

create user usr_operador_artes WITH password 'Artes_2026*';

create user usr_financiero WITH password 'Financiero_2026*';

create user usr_auditor WITH password 'Auditor_2026*';

create user usr_rectoria WITH password 'Rectoria_2026*';

GRANT rol_admin_institucional TO usr_admin_institucional;

GRANT rol_seguridad_admin TO usr_seguridad_admin;

GRANT rol_facultad_ingenieria_rw TO usr_operador_ingenieria;

GRANT rol_facultad_ciencias_rw TO usr_operador_ciencias;

GRANT rol_facultad_tecnologica_rw TO usr_operador_tecnologica;

GRANT rol_facultad_medio_ambiente_rw TO usr_operador_medio_ambiente;

GRANT rol_facultad_artes_rw TO usr_operador_artes;

GRANT rol_financiero_rw TO usr_financiero;

GRANT rol_auditoria_ro TO usr_auditor;

GRANT rol_rectoria_ro TO usr_rectoria;

GRANT usage ON schema personas,seguridad,institucional,financiero,auditoria,movilidad,reportes TO rol_admin_institucional;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema personas,seguridad,institucional,financiero,auditoria,movilidad TO rol_admin_institucional;

GRANT SELECT ON all tables IN schema reportes TO rol_admin_institucional;

GRANT usage ON schema seguridad,personas TO rol_seguridad_admin;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema seguridad TO rol_seguridad_admin;

GRANT SELECT ON personas.usuario_dato_personal TO rol_seguridad_admin;

GRANT usage ON schema financiero,institucional,reportes TO rol_financiero_rw;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema financiero TO rol_financiero_rw;

GRANT SELECT ON all tables IN schema institucional,reportes TO rol_financiero_rw;

GRANT usage ON schema auditoria,reportes TO rol_auditoria_ro;

GRANT SELECT ON all tables IN schema auditoria,reportes TO rol_auditoria_ro;

GRANT usage ON schema reportes,institucional TO rol_rectoria_ro;

GRANT SELECT ON all tables IN schema reportes,institucional TO rol_rectoria_ro;

GRANT usage ON schema fdw_ingenieria,reportes TO rol_facultad_ingenieria_rw;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema fdw_ingenieria TO rol_facultad_ingenieria_rw;

GRANT SELECT ON all tables IN schema reportes TO rol_facultad_ingenieria_rw;

GRANT usage ON schema fdw_ciencias_educacion,reportes TO rol_facultad_ciencias_rw;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema fdw_ciencias_educacion TO rol_facultad_ciencias_rw;

GRANT SELECT ON all tables IN schema reportes TO rol_facultad_ciencias_rw;

GRANT usage ON schema fdw_tecnologica,reportes TO rol_facultad_tecnologica_rw;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema fdw_tecnologica TO rol_facultad_tecnologica_rw;

GRANT SELECT ON all tables IN schema reportes TO rol_facultad_tecnologica_rw;

GRANT usage ON schema fdw_medio_ambiente,reportes TO rol_facultad_medio_ambiente_rw;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema fdw_medio_ambiente TO rol_facultad_medio_ambiente_rw;

GRANT SELECT ON all tables IN schema reportes TO rol_facultad_medio_ambiente_rw;

GRANT usage ON schema fdw_artes,reportes TO rol_facultad_artes_rw;

GRANT SELECT,insert,UPDATE,delete ON all tables IN schema fdw_artes TO rol_facultad_artes_rw;

GRANT SELECT ON all tables IN schema reportes TO rol_facultad_artes_rw;
