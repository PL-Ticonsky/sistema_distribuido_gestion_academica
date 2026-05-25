# Diagramas UML

Esta carpeta contiene diagramas derivados del código Django actual y del dominio académico del proyecto.

## Archivos Generados

| Archivo | Tipo | Origen |
|---|---|---|
| `django_models.puml` | Diagrama de clases UML de modelos Django | `backend/apps/*/models.py` |
| `django_models_graphviz.dot` | Diagrama DOT generado con `django-extensions graph_models` | Modelos Django cargados con settings en memoria |
| `classes_sistema_distribuido_gestion_academica.puml` | Diagrama de clases Python | `pyreverse` |
| `packages_sistema_distribuido_gestion_academica.puml` | Diagrama de paquetes/componentes Python | `pyreverse` |
| `component_dependencies.puml` | Componentes y dependencias principales | Apps Django, vistas, servicios y modelos |
| `sequence_login_dashboard.puml` | Secuencia de login y dashboard | `accounts.views`, `roles.py`, `context_processors.py` |
| `sequence_inscripciones_notas.puml` | Secuencia de inscripciones y notas | `academica.views` |
| `sequence_homologaciones.puml` | Secuencia de homologaciones | `homologaciones.views` |
| `state_domain_entities.puml` | Estados del dominio | `TextChoices`, campos de estado y acciones de vistas |

Cada archivo `.puml` tiene un `.png` acompañante con el mismo nombre. En este entorno no estaban disponibles los binarios `plantuml` ni `dot`; por eso los PNG incluidos funcionan como previsualizaciones locales. Para obtener renders UML nativos, ejecutar PlantUML con las instrucciones de abajo.

## Dependencias Para Regenerar

Instalación recomendada con `uv`:

```bash
uv add --dev django-extensions pylint graphviz
```

Dependencias del sistema:

```bash
# Debian/Ubuntu
sudo apt-get install graphviz plantuml

# Arch Linux
sudo pacman -S graphviz plantuml

# macOS con Homebrew
brew install graphviz plantuml
```

Si no se quieren modificar dependencias del proyecto, también se pueden usar dependencias transitorias:

```bash
uv run --with django-extensions --with pylint --with graphviz python -c "import django_extensions, pylint, graphviz"
```

## Regenerar Diagrama De Modelos Con Django Extensions

`graph_models` requiere que `django_extensions` esté en `INSTALLED_APPS`. Para no modificar `backend/config/settings.py`, se puede ejecutar con settings ajustados solo en memoria:

```bash
uv run --with django-extensions python -c "import os,sys; sys.path.insert(0,'backend'); os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings'); from django.conf import settings; settings.INSTALLED_APPS=list(settings.INSTALLED_APPS)+['django_extensions']; import django; django.setup(); from django.core.management import call_command; call_command('graph_models','accounts','estructura','academica','financiera','homologaciones','auditoria',dot=True,group_models=True,hide_relations_from_fields=True,output='docs/diagrams/django_models_graphviz.dot')"
```

Comando equivalente si `django_extensions` ya está instalado y habilitado en settings locales:

```bash
python backend/manage.py graph_models accounts estructura academica financiera homologaciones auditoria --dot --group-models --hide-relations-from-fields --output docs/diagrams/django_models_graphviz.dot
```

Para exportar desde DOT a PNG con Graphviz:

```bash
dot -Tpng docs/diagrams/django_models_graphviz.dot -o docs/diagrams/django_models_graphviz.png
```

## Regenerar Diagramas Con Pyreverse

```bash
uv run --with pylint pyreverse \
  -o puml \
  -p sistema_distribuido_gestion_academica \
  -d docs/diagrams \
  --source-roots backend \
  backend/apps backend/config
```

Esto genera:

```text
docs/diagrams/classes_sistema_distribuido_gestion_academica.puml
docs/diagrams/packages_sistema_distribuido_gestion_academica.puml
```

## Renderizar PlantUML A PNG

Con PlantUML instalado:

```bash
plantuml -tpng docs/diagrams/*.puml
```

Con Java y un jar local de PlantUML:

```bash
java -jar plantuml.jar -tpng docs/diagrams/*.puml
```

## Mantener Sincronizados

Regenerar estos diagramas cuando cambien:

- Modelos en `backend/apps/*/models.py`
- Relaciones entre apps
- Vistas o flujos principales
- Estados de dominio
- Permisos o alcance funcional por rol

Los diagramas no deben cambiar la lógica de la aplicación. Son documentación derivada del código fuente.
