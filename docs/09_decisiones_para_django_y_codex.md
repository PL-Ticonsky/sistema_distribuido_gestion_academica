# Decisiones iniciales para implementación local con Django y Codex

## Objetivo de este archivo

Este archivo documenta las decisiones técnicas iniciales para preparar el proyecto antes de programar con Codex.

La idea es que Codex tenga suficiente contexto del dominio académico, de la base de datos y de la futura estructura del aplicativo.

## Decisión principal

El sistema se desarrollará como una aplicación local usando:

- Django como framework web.
- PostgreSQL como motor de base de datos.
- Django Auth para autenticación y permisos funcionales.
- DBeaver como herramienta de administración y revisión de la base de datos.
- Codex como asistente de programación dentro de VS Code.

## Estado actual del modelo

El documento base contiene una tabla `usuario` propia, con un campo `hashed_password`.

Para trabajar correctamente con Django, esta tabla debe ajustarse en la siguiente fase, porque Django ya tiene su propio sistema de autenticación y espera una estructura compatible con su modelo de usuario.

## Decisión sobre usuarios

La tabla `usuario` del documento se convertirá en un modelo de usuario personalizado de Django.

Esto implica que el modelo final deberá conservar información académica propia del proyecto, como:

- Tipo de documento.
- Número de documento.
- Nombre.
- Correo.
- Dirección.

Pero también deberá incluir campos propios del sistema de autenticación de Django, como:

- `password`.
- `last_login`.
- `is_superuser`.
- `is_staff`.
- `is_active`.
- `date_joined`.

## Especializaciones de usuario

Las tablas `estudiante`, `profesor` y `administrativo` se mantendrán como especializaciones del usuario.

Cada una tendrá una relación uno a uno con `usuario`.

Esta decisión respeta la regla de negocio según la cual un usuario puede ser estudiante, docente o administrativo, e incluso puede ser estudiante y docente simultáneamente.

## Separación entre roles funcionales y roles de base de datos

### Roles funcionales en Django

Estos roles determinan qué puede hacer una persona dentro del sistema web.

- Estudiante.
- Docente.
- Coordinador.
- Decano.
- Administrativo.

Se recomienda manejarlos mediante grupos y permisos de Django.

### Roles técnicos en PostgreSQL

Estos roles determinan qué puede hacer una conexión directamente sobre la base de datos.

- Superusuario o administrador de PostgreSQL.
- Usuario de aplicación usado por Django.
- Usuario de solo lectura para consultas o evidencias, si se requiere.

## Apps propuestas en Django

| App | Responsabilidad | Tablas principales |
|---|---|---|
| accounts | Usuarios y roles académicos | usuario, estudiante, profesor, administrativo, coordinador, decano |
| estructura | Estructura institucional | facultad, programa_academico, periodo_academico |
| academica | Planes, grupos e inscripciones | asignatura, programa_asignatura, pre_requisitos, grupo, inscripcion |
| financiera | Matrícula y pagos | tarifa_matricula, recibo, matricula |
| homologaciones | Solicitudes y evaluación de homologaciones | homologacion |
| auditoria | Registro de acciones del sistema | auditoria |

## Orden recomendado de construcción

1. Documentación del proyecto.
2. Ajuste del modelo relacional para Django.
3. DDL definitivo.
4. Inserciones de prueba.
5. Proyecto Django base.
6. Modelo de usuario personalizado.
7. Modelos por app.
8. Login y permisos.
9. Pantallas por rol.
10. Consultas, vistas y reportes.
11. Evidencias de ejecución.
12. Manual técnico de instalación y uso local.

## Regla de trabajo con Codex

Codex no debe recibir instrucciones demasiado generales como “haz todo el proyecto”.

Se debe trabajar por tareas pequeñas, por ejemplo:

- Implementar solo la app `accounts`.
- Crear solo los modelos de `estructura`.
- Crear solo los formularios de inscripción.
- Crear solo las vistas de consulta para estudiantes.

Cada tarea debe indicar qué archivos puede modificar y qué archivos no debe tocar.

## Pendiente para la siguiente fase

Antes de escribir código definitivo se debe construir el archivo:

`06_modelo_relacional_ajustado_django.md`

Ese archivo deberá definir el modelo relacional corregido, con especial atención a:

- Tabla `usuario` compatible con Django.
- Nombres definitivos de campos.
- Tipos de datos definitivos.
- Restricciones `check`.
- Restricciones `unique`.
- Claves foráneas.
- Orden correcto de creación de tablas.
