# Alcance del documento

## 3. Alcance del documento

Esta primera entrega se enfoca en la definición estructural y lógica de la base de datos.

No corresponde todavía a la implementación completa del sistema en PostgreSQL ni a la configuración física de esquemas distribuidos.

## 3.1. Elementos incluidos en esta entrega

- Documento del proyecto.
- Descripción general del sistema propuesto.
- Diseño conceptual del modelo Entidad-Relación.
- Modelo relacional.
- Esquema de tablas.
- Diccionario de datos preliminar.
- Identificación de claves primarias y claves foráneas.
- Reglas de negocio.

## 3.2. Elementos que se desarrollarán en etapas posteriores

- Scripts SQL de creación de base de datos, esquemas y tablas.
- Configuración de roles y permisos en PostgreSQL.
- Creación de vistas institucionales.
- Consultas SQL requeridas.
- Inserción de datos de prueba.
- Evidencias de ejecución.
- Estrategia detallada de distribución física de la información.
- Manual técnico de instalación y ejecución.

## Nota sobre validaciones futuras

Algunas reglas de negocio se dejan definidas a nivel conceptual y relacional. Su implementación específica se abordará posteriormente mediante restricciones, consultas, procedimientos o lógica de aplicación, según el alcance final del proyecto.

Entre estas reglas se encuentran:

- Control de cupos.
- Cumplimiento de prerrequisitos.
- Límite de matrículas.
- Consistencia entre estados de pago y matrícula.

## Alcance operativo para la siguiente fase

Para el desarrollo local con Django y PostgreSQL, esta documentación servirá como base para construir:

- El DDL definitivo.
- Las migraciones o modelos equivalentes de Django.
- Los datos semilla.
- Las vistas institucionales.
- La lógica de permisos por rol.
- La documentación técnica que recibirá Codex antes de programar.
