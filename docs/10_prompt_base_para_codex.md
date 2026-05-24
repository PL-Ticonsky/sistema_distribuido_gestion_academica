# Prompt base para Codex

## Uso

Este prompt debe entregarse a Codex al iniciar el desarrollo del proyecto en VS Code.

La intención es darle contexto suficiente para que no improvise la arquitectura ni cambie decisiones centrales del proyecto.

## Prompt base

```text
Estoy desarrollando un sistema local de gestión académica universitaria usando Django y PostgreSQL.

El sistema NO se va a desplegar. Debe funcionar localmente.

El proyecto se basa en la documentación ubicada en la carpeta docs/.

Antes de programar, lee estos archivos:

- docs/00_readme_documentacion.md
- docs/02_introduccion_y_descripcion.md
- docs/03_alcance_del_documento.md
- docs/04_reglas_de_negocio.md
- docs/05_modelo_conceptual.md
- docs/06_modelo_relacional_original.md
- docs/09_decisiones_para_django_y_codex.md

Reglas de trabajo:

1. No hagas cambios masivos sin explicar qué vas a modificar.
2. No implementes todo el proyecto de una sola vez.
3. Trabaja por módulos pequeños.
4. Respeta la separación de apps propuesta:
   - accounts
   - estructura
   - academica
   - financiera
   - homologaciones
   - auditoria
5. La tabla usuario debe implementarse como modelo de usuario personalizado de Django.
6. Las especializaciones estudiante, profesor y administrativo deben relacionarse uno a uno con usuario.
7. No uses SQLite. El motor objetivo es PostgreSQL.
8. El proyecto debe ser claro, documentado y fácil de ejecutar localmente.
9. Antes de crear modelos, verifica que el modelo relacional ajustado para Django ya esté definido.
10. Cuando propongas cambios, indica archivos afectados y razón técnica.

Primera tarea:
Ayúdame a crear o revisar la estructura inicial del proyecto Django, pero no implementes todavía todos los modelos.
```

## Prompt para implementar una app específica

```text
Lee la documentación del proyecto en docs/.

Implementa únicamente la app indicada.
No modifiques otras apps salvo que sea estrictamente necesario.
Explica los archivos que vas a crear o modificar.
Respeta los nombres definidos en la documentación.

App a implementar: [NOMBRE_APP]
Objetivo de la tarea: [OBJETIVO]
Archivos permitidos: [LISTA]
Archivos que no debes tocar: [LISTA]
```

## Prompt para revisar código generado

```text
Revisa el código generado para esta app.
Verifica:

1. Coherencia con el modelo relacional.
2. Coherencia con las reglas de negocio.
3. Uso correcto de claves foráneas.
4. Uso correcto de relaciones uno a uno, uno a muchos y muchos a muchos.
5. Que no se haya roto la autenticación de Django.
6. Que los nombres sean consistentes con la documentación.

No hagas cambios todavía. Primero dame el diagnóstico.
```
