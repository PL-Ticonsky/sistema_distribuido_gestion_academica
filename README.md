# Sistema Distribuido de Gestión Académica Universitaria

Aplicación web académica construida con Django y PostgreSQL para gestionar procesos universitarios como autenticación por roles, estructura institucional, oferta académica, inscripciones, notas, homologaciones, matrícula financiera, indicadores académicos y auditoría.

El proyecto conserva un modelo relacional existente en PostgreSQL y lo integra con Django mediante modelos no administrados (`managed = False`) para respetar la estructura de base de datos definida en los scripts SQL.

## Estado Del Proyecto

- Backend Django funcional con autenticación por correo.
- Roles funcionales implementados mediante grupos de Django.
- Permisos y alcance de datos por rol.
- Templates Django con interfaz institucional beige/café.
- Sidebar colapsable con persistencia en `localStorage`.
- Scripts SQL separados para DDL, catálogos, datos operativos y validaciones.
- Comandos locales para crear grupos funcionales y usuarios demo.

## Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ |
| Framework web | Django 5 |
| Base de datos | PostgreSQL |
| Conector PostgreSQL | psycopg |
| Configuración | django-environ |
| Frontend | Django Templates, Bootstrap 5, Bootstrap Icons, CSS propio |
| Calidad | Ruff, pytest, pytest-django |
| Gestión de entorno | uv |

## Módulos Funcionales

| App | Responsabilidad |
|---|---|
| `accounts` | Usuario personalizado, login/logout, dashboard, roles y alcance funcional. |
| `estructura` | Facultades, programas académicos y periodos. |
| `academica` | Asignaturas, planes, prerrequisitos, docentes, grupos, inscripciones y notas. |
| `financiera` | Tarifas, recibos y matrículas. |
| `homologaciones` | Solicitudes, asignación de evaluador, evaluación y cancelación. |
| `indicadores` | Avance académico, promedio, materias faltantes y riesgo. |
| `auditoria` | Consulta de trazabilidad operativa. |

## Roles Soportados

- Estudiante
- Docente
- Coordinador
- Decano
- Administrativo
- Superadmin / administrador funcional

La navegación, los listados y las acciones disponibles se filtran según el rol y el alcance del usuario autenticado.

## Estructura Del Repositorio

```text
.
├── backend/
│   ├── apps/
│   │   ├── academica/
│   │   ├── accounts/
│   │   ├── auditoria/
│   │   ├── estructura/
│   │   ├── financiera/
│   │   ├── homologaciones/
│   │   └── indicadores/
│   ├── config/
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   ├── templates/
│   └── manage.py
├── docs/
├── sql/
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

## Configuración Local

### 1. Requisitos

- Python 3.12 o superior
- PostgreSQL instalado y en ejecución
- `uv` instalado
- DBeaver u otra herramienta SQL para ejecutar scripts manuales

### 2. Instalar Dependencias

```bash
uv sync
```

### 3. Crear Archivo `.env`

Crear un archivo `.env` en la raíz del proyecto:

```env
DJANGO_SECRET_KEY=change-me-local
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=gestion_academica_local
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_SSLMODE=prefer
```

No versionar credenciales reales. El archivo `.env` debe ser local.

## Base De Datos

Los scripts SQL están en `sql/` y se deben ejecutar en orden según el ambiente local:

| Archivo | Propósito |
|---|---|
| `sql/01_ddl.sql` | Crea tablas y restricciones principales. |
| `sql/02_inserts_catalogos.sql` | Carga catálogos base. |
| `sql/03_inserts_operativos.sql` | Carga datos operativos de prueba. |
| `sql/04_consultas_validacion.sql` | Consultas para validar datos y reglas. |
| `sql/09_auth_user_m2m_tables.sql` | Tablas M2M requeridas por grupos/permisos de Django para el usuario personalizado. |

Flujo recomendado para una base local limpia:

```text
sql/01_ddl.sql
sql/02_inserts_catalogos.sql
sql/03_inserts_operativos.sql
```

Luego crear las tablas internas de Django:

```bash
uv run python backend/manage.py migrate
```

Después ejecutar en PostgreSQL:

```text
sql/09_auth_user_m2m_tables.sql
```

Finalmente crear grupos y usuarios demo:

```bash
uv run python backend/manage.py setup_functional_groups
uv run python backend/manage.py seed_demo_users
```

> Nota: el orden exacto puede depender del estado de la base local. La documentación técnica en `docs/` contiene las validaciones detalladas del DDL e inserts.

## Ejecutar La Aplicación

```bash
uv run python backend/manage.py runserver
```

Abrir:

```text
http://127.0.0.1:8000/login/
```

## Usuarios Demo

Contraseña demo para todos:

```text
Demo12345*
```

| Rol | Correo |
|---|---|
| Administrador funcional | `claudia.benitez@universidad.edu` |
| Estudiante | `sofia.herrera@universidad.edu` |
| Docente | `carolina.vargas@universidad.edu` |
| Coordinador | `miguel.rojas@universidad.edu` |
| Decano | `laura.perez@universidad.edu` |
| Administrativo | `hector.suarez@universidad.edu` |

Estas credenciales son ficticias y solo sirven para desarrollo local.

## Rutas Principales

| Ruta | Descripción |
|---|---|
| `/login/` | Inicio de sesión. |
| `/logout/` | Cierre de sesión. |
| `/dashboard/` | Dashboard según rol. |
| `/estructura/facultades/` | Facultades. |
| `/estructura/programas/` | Programas académicos. |
| `/estructura/periodos/` | Periodos académicos. |
| `/academica/asignaturas/` | Asignaturas. |
| `/academica/planes/` | Planes de estudio. |
| `/academica/grupos/` | Grupos académicos. |
| `/academica/inscripciones/` | Inscripciones. |
| `/academica/notas/` | Gestión de notas. |
| `/financiera/tarifas/` | Tarifas de matrícula. |
| `/financiera/recibos/` | Recibos. |
| `/financiera/matriculas/` | Matrículas. |
| `/homologaciones/` | Homologaciones. |
| `/indicadores/` | Indicadores académicos. |
| `/auditoria/` | Auditoría. |

Algunas rutas redirigen si el usuario no tiene el rol requerido.

## Frontend

La interfaz usa Django Templates y CSS centralizado:

```text
backend/templates/base.html
backend/static/css/condor.css
backend/static/js/condor.js
```

Características:

- Identidad visual institucional en tonos beige, crema, arena y café.
- Sidebar izquierdo colapsable.
- Persistencia del estado del sidebar en `localStorage`.
- Navbar superior con usuario y roles activos.
- Login rediseñado.
- Dashboard visual con cards y accesos rápidos.
- Tablas responsivas con hover y encabezados estilizados.
- Formularios y detalles con superficies tipo card.
- Alertas y badges consistentes con la paleta.

## Comandos De Validación

```bash
uv run python backend/manage.py check
uv run ruff check backend/apps backend/config
uv run ruff format --check backend/apps backend/config
uv run pytest
```

Para formatear:

```bash
uv run ruff format backend/apps backend/config
```

## Decisiones Importantes

- No se debe modificar SQL sin revisar la documentación y el modelo relacional.
- No se deben crear migraciones para tablas existentes del modelo académico.
- Los modelos asociados a tablas existentes usan `managed = False`.
- La lógica de permisos vive en `apps.accounts.access`, `apps.accounts.roles` y `apps.accounts.scope`.
- Los querysets de cada módulo aplican filtros según rol y alcance.
- La autenticación usa `accounts.CustomUser` con correo como identificador.
- Las contraseñas se gestionan con el sistema de hashing de Django.

## Documentación

La carpeta `docs/` contiene el contexto académico y técnico:

- Reglas de negocio
- Modelo conceptual y relacional
- Diccionario de datos
- Decisiones técnicas para Django
- Pantallas y flujos
- Usuarios demo
- Guía visual
- Validaciones SQL

Punto de entrada recomendado:

```text
docs/00_readme_documentacion.md
```

## Seguridad

- No subir `.env` con credenciales reales.
- No documentar contraseñas productivas.
- No hardcodear claves de PostgreSQL, Azure, tokens ni `SECRET_KEY`.
- Usar credenciales demo únicamente en ambiente local.
- Configurar `DJANGO_DEBUG=False` y `DJANGO_ALLOWED_HOSTS` explícito fuera de desarrollo.

## Alcance Actual

El sistema está orientado a una fase local de desarrollo y validación académica. La arquitectura documental contempla una evolución posterior hacia PostgreSQL administrado en la nube, pero el despliegue cloud no forma parte del alcance actual del repositorio.
