# Documentación del Sistema Distribuido de Gestión Académica Universitaria

## Propósito de esta carpeta

Esta carpeta contiene la documentación del proyecto en formato Markdown, organizada para que pueda ser usada como contexto técnico antes de implementar la base de datos y el aplicativo web en Django.

La documentación se construyó a partir del documento base del proyecto: **Sistema Distribuido de Gestión Académica Universitaria - Primera entrega del proyecto**.

## Archivos incluidos

| Archivo | Contenido |
|---|---|
| `01_portada_y_datos_generales.md` | Información general del proyecto, autores, asignatura y tema. |
| `02_introduccion_y_descripcion.md` | Introducción, propósito del sistema y componentes principales. |
| `03_alcance_del_documento.md` | Alcance de la entrega actual y elementos para etapas posteriores. |
| `04_reglas_de_negocio.md` | Reglas funcionales del sistema por dominio. |
| `05_modelo_conceptual.md` | Entidades conceptuales y relaciones principales. |
| `06_modelo_relacional_original.md` | Modelo relacional tal como está planteado en el documento base. |
| `07_diccionario_de_datos.md` | Diccionario de datos preliminar del sistema. |
| `08_claves_y_distribucion.md` | Criterios de claves primarias y distribución preliminar. |
| `09_decisiones_para_django_y_codex.md` | Decisiones iniciales para preparar la futura implementación local en Django. |
| `10_prompt_base_para_codex.md` | Prompt base para entregar contexto a Codex antes de programar. |

## Nota de trabajo

El archivo `06_modelo_relacional_original.md` conserva el modelo del documento base. En la siguiente fase se debe construir el **modelo relacional ajustado para Django**, especialmente la tabla `usuario`, que debe integrarse con el sistema de autenticación de Django.
