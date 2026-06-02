-- Ejecutar conectado a sga_central. Validación rápida.
SELECT 'facultades' objeto,count(*) total
FROM institucional.facultad
UNION ALL SELECT 'programas',count(*)
FROM institucional.programa_academico
UNION ALL SELECT 'usuarios',count(*)
FROM personas.usuario_dato_personal
UNION ALL SELECT 'estudiantes_global',count(*)
FROM reportes.vw_estudiantes_global
UNION ALL SELECT 'profesores_global',count(*)
FROM reportes.vw_profesores_global
UNION ALL SELECT 'grupos_global',count(*)
FROM reportes.vw_grupos_global
UNION ALL SELECT 'inscripciones_global',count(*)
FROM reportes.vw_inscripciones_global
UNION ALL SELECT 'matriculas_global',count(*)
FROM reportes.vw_matriculas_global
ORDER BY objeto;

SELECT id_facultad,count(*) estudiantes
FROM reportes.vw_estudiantes_global
GROUP BY id_facultad
ORDER BY id_facultad;

SELECT foreign_table_schema,foreign_table_name
FROM information_schema.foreign_tables
ORDER BY foreign_table_schema,foreign_table_name;
