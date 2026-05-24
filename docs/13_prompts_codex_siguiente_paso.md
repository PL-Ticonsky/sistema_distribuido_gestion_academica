# 13. Prompts para Codex: siguiente paso del proyecto

## 1. Objetivo

Este documento contiene prompts listos para usar en Codex después de terminar la documentación inicial del proyecto.

La idea es que Codex trabaje de forma controlada, por tareas pequeñas, sin modificar archivos que no correspondan.

## 2. Prompt 1: crear estructura inicial del proyecto

```text
Lee primero los archivos de documentación ubicados en la carpeta docs, especialmente:

- docs/00_readme_documentacion.md
- docs/11_decisiones_tecnicas.md
- docs/12_modelo_relacional_ajustado_django.md

Crea la estructura inicial del proyecto para una aplicación Django local llamada sistema_gestion_academica.

Condiciones obligatorias:
- No implementes todavía modelos de base de datos.
- No crees vistas funcionales.
- No crees formularios.
- No crees migraciones.
- No modifiques el contenido de los archivos markdown existentes.
- Solo crea carpetas y archivos base vacíos o mínimos.

Estructura requerida:

sistema_gestion_academica/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── docs/
├── sql/
│   ├── 01_ddl.sql
│   ├── 02_inserts_catalogos.sql
│   ├── 03_inserts_prueba.sql
│   ├── 04_vistas.sql
│   ├── 05_roles_permisos.sql
│   └── avanzado/
│       ├── 01_funciones_validacion.sql
│       ├── 02_triggers_auditoria.sql
│       ├── 03_triggers_cupos.sql
│       └── README.md
└── backend/
    ├── manage.py
    ├── config/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    ├── apps/
    │   ├── __init__.py
    │   ├── accounts/
    │   ├── estructura/
    │   ├── academica/
    │   ├── financiera/
    │   ├── homologaciones/
    │   └── auditoria/
    ├── templates/
    ├── static/
    └── media/

En cada app crea los archivos base:
- __init__.py
- admin.py
- apps.py
- models.py
- urls.py
- views.py
- tests.py

Al final, explica brevemente qué archivos creaste y no hagas más cambios.
```

## 3. Prompt 2: preparar configuración base de Django

```text
Lee:

- docs/11_decisiones_tecnicas.md
- docs/12_modelo_relacional_ajustado_django.md

Configura el proyecto Django para ejecución local con PostgreSQL.

Condiciones:
- No crees modelos todavía.
- No ejecutes migraciones.
- No modifiques el DDL.
- Usa variables de entorno desde .env.example.
- Configura INSTALLED_APPS con las apps del proyecto.
- Configura templates y static files.
- Configura idioma español y zona horaria de Colombia.

Resultado esperado:
- requirements.txt actualizado con dependencias necesarias.
- .env.example con variables para PostgreSQL local.
- settings.py configurado de forma básica.
- urls.py principal preparado.

No implementes login todavía.
```

## 4. Prompt 3: implementar usuario personalizado

```text
Lee:

- docs/11_decisiones_tecnicas.md
- docs/12_modelo_relacional_ajustado_django.md

Implementa únicamente la app accounts hasta el modelo CustomUser.

Condiciones:
- No implementes todavía estudiante, profesor ni administrativo.
- No implementes vistas.
- No implementes formularios.
- No implementes templates.
- No modifiques otras apps.

Requisitos del modelo:
- Debe extender AbstractUser o la opción más conveniente para integrarse correctamente con Django.
- Debe usar UUID como primary key en id_usuario.
- Debe eliminar username si se va a autenticar por correo.
- Debe usar correo como USERNAME_FIELD.
- Debe tener nombre, tipo_de_documento, numero_de_documento y direccion.
- Debe respetar db_table = 'usuario'.
- Debe incluir unique para correo.
- Debe incluir unique conjunto para tipo_de_documento y numero_de_documento.
- Debe incluir CustomUserManager.
- Debe registrar el modelo en admin.py.
- Debe configurar AUTH_USER_MODEL en settings.py.

Al final, explica qué archivos modificaste.
```

## 5. Prompt 4: crear DDL inicial solo con tablas

```text
Lee:

- docs/11_decisiones_tecnicas.md
- docs/12_modelo_relacional_ajustado_django.md

Crea el archivo sql/01_ddl.sql con el DDL inicial del proyecto.

Condiciones obligatorias:
- El DDL solo debe tener tablas y restricciones simples.
- No crees triggers.
- No crees funciones.
- No crees vistas.
- No crees roles.
- No incluyas inserts.
- Todas las palabras reservadas de SQL deben ir en minúscula.
- Usa PostgreSQL.
- Usa create extension if not exists pgcrypto; al inicio.
- Usa uuid con default gen_random_uuid() en tablas operativas.
- Usa varchar para catálogos institucionales.
- Usa varchar + check en lugar de enum nativo de PostgreSQL.
- Respeta el orden de creación de tablas definido en docs/12_modelo_relacional_ajustado_django.md.

Tablas requeridas:
- usuario
- facultad
- programa_academico
- periodo_academico
- estudiante
- profesor
- administrativo
- asignatura
- programa_asignatura
- pre_requisito
- grupo
- tarifa_matricula
- recibo
- matricula
- inscripcion
- homologacion
- decano
- coordinador
- auditoria

Al final, revisa mentalmente las dependencias de foreign keys y corrige el orden si es necesario.
```

## 6. Prompt 5: revisar DDL sin modificar otras partes

```text
Revisa únicamente el archivo sql/01_ddl.sql.

Verifica:
- Que no existan triggers.
- Que no existan funciones.
- Que no existan vistas.
- Que no existan inserts.
- Que las tablas estén en orden correcto según dependencias.
- Que las foreign keys apunten a tablas ya creadas.
- Que usuario esté ajustado para Django.
- Que no se use hashed_password.
- Que se use password.
- Que se usen check constraints en lugar de enums nativos.
- Que todas las palabras reservadas de SQL estén en minúscula.

Si encuentras errores, corrige solo sql/01_ddl.sql.
Al final, muestra un resumen de los cambios realizados.
```

## 7. Prompt 6: crear inserts de catálogos

```text
Lee:

- docs/12_modelo_relacional_ajustado_django.md
- sql/01_ddl.sql

Crea el archivo sql/02_inserts_catalogos.sql.

Condiciones:
- Solo incluye inserts de catálogos o datos institucionales relativamente estables.
- No incluyas usuarios todavía.
- No incluyas estudiantes todavía.
- No incluyas profesores todavía.
- No incluyas inscripciones todavía.
- No incluyas matrículas todavía.
- No uses lógica procedural.
- No uses triggers.
- No uses funciones.
- Solo usa insert into ... values.

Incluye datos para:
- facultad
- programa_academico
- periodo_academico
- asignatura
- programa_asignatura
- pre_requisito

Los datos deben ser coherentes con una universidad organizada por facultades y programas.
```

## 8. Prompt 7: crear inserts de prueba operativa

```text
Lee:

- docs/12_modelo_relacional_ajustado_django.md
- sql/01_ddl.sql
- sql/02_inserts_catalogos.sql

Crea el archivo sql/03_inserts_prueba.sql.

Condiciones:
- Solo usa insert into ... values.
- No uses lógica procedural.
- No uses triggers.
- No uses funciones.
- Los datos deben respetar las foreign keys.
- Los datos deben permitir probar login, estudiantes, profesores, grupos, pagos, matrículas, inscripciones y homologaciones.

Incluye datos para:
- usuario
- estudiante
- profesor
- administrativo
- tarifa_matricula
- recibo
- matricula
- grupo
- inscripcion
- homologacion
- decano
- coordinador
- auditoria

Importante:
Para usuarios de prueba, deja claro que las contraseñas no deben insertarse manualmente en producción porque Django maneja el hash. Si vas a poner password de prueba, indícalo como valor temporal no válido para login real hasta crear usuarios desde Django.
```

## 9. Recomendación de uso

No ejecutes todos los prompts seguidos sin revisar.

Orden recomendado:

```text
1. Ejecutar prompt 1.
2. Revisar estructura creada.
3. Hacer commit.
4. Ejecutar prompt 2.
5. Revisar configuración.
6. Hacer commit.
7. Ejecutar prompt 3.
8. Revisar CustomUser antes de migrar.
9. Hacer commit.
10. Ejecutar prompt 4 para DDL.
11. Revisar con prompt 5.
12. Hacer commit.
```
