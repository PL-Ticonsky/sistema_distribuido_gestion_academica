# SGA distribuido físico - scripts limpios

Orden:
1. En postgres: 00_reset_entorno_opcional.sql si quieres limpiar.
2. En postgres: 01_create_databases.sql.
3. Crear conexiones en DBeaver para todas las bases.
4. En sga_central: 02_central_schema_tables.sql.
5. En cada base de facultad: scripts 03 a 07.
6. Inserts: 08 en central y 09 a 13 en cada base de facultad.
7. En sga_central: 14_fdw_connections.sql.
8. En sga_central: 15_views_globales.sql.
9. En sga_central: 16_roles_permissions.sql.
10. En sga_central: 17_consultas_requeridas.sql y 18_validation_queries.sql.

Los scripts de inserción usan únicamente INSERT directos, sin generate_series, DO, funciones auxiliares ni lógica procedimental.
Los datos fueron preparados para que las 20 consultas requeridas devuelvan resultados.
