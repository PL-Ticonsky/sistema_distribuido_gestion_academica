-- 14_fdw_connections.sql - Ejecutar conectado a sga_central.
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

CREATE SCHEMA fdw_ingenieria;

DROP SERVER IF EXISTS srv_facultad_ingenieria CASCADE;

CREATE SERVER srv_facultad_ingenieria FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host 'localhost',
    dbname 'sga_facultad_ingenieria',
    port '5432'
);

CREATE USER MAPPING FOR CURRENT_USER SERVER srv_facultad_ingenieria OPTIONS (user 'postgres');

IMPORT FOREIGN SCHEMA facultad_ingenieria FROM SERVER srv_facultad_ingenieria INTO fdw_ingenieria;

CREATE SCHEMA fdw_ciencias_educacion;

DROP SERVER IF EXISTS srv_facultad_ciencias_educacion CASCADE;

CREATE SERVER srv_facultad_ciencias_educacion FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host 'localhost',
    dbname 'sga_facultad_ciencias_educacion',
    port '5432'
);

CREATE USER MAPPING FOR CURRENT_USER SERVER srv_facultad_ciencias_educacion OPTIONS (user 'postgres');

IMPORT FOREIGN SCHEMA facultad_ciencias_educacion FROM SERVER srv_facultad_ciencias_educacion INTO fdw_ciencias_educacion;

CREATE SCHEMA fdw_tecnologica;

DROP SERVER IF EXISTS srv_facultad_tecnologica CASCADE;

CREATE SERVER srv_facultad_tecnologica FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host 'localhost',
    dbname 'sga_facultad_tecnologica',
    port '5432'
);

CREATE USER MAPPING FOR CURRENT_USER SERVER srv_facultad_tecnologica OPTIONS (user 'postgres');

IMPORT FOREIGN SCHEMA facultad_tecnologica FROM SERVER srv_facultad_tecnologica INTO fdw_tecnologica;

CREATE SCHEMA fdw_medio_ambiente;

DROP SERVER IF EXISTS srv_facultad_medio_ambiente CASCADE;

CREATE SERVER srv_facultad_medio_ambiente FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host 'localhost',
    dbname 'sga_facultad_medio_ambiente',
    port '5432'
);

CREATE USER MAPPING FOR CURRENT_USER SERVER srv_facultad_medio_ambiente OPTIONS (user 'postgres');

IMPORT FOREIGN SCHEMA facultad_medio_ambiente FROM SERVER srv_facultad_medio_ambiente INTO fdw_medio_ambiente;

CREATE SCHEMA fdw_artes;

DROP SERVER IF EXISTS srv_facultad_artes CASCADE;

CREATE SERVER srv_facultad_artes FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host 'localhost',
    dbname 'sga_facultad_artes',
    port '5432'
);

CREATE USER MAPPING FOR CURRENT_USER SERVER srv_facultad_artes OPTIONS (user 'postgres');

IMPORT FOREIGN SCHEMA facultad_artes FROM SERVER srv_facultad_artes INTO fdw_artes;
