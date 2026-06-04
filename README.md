<div align="center">

  <img src="backend/media/ChatGPT Image Jun 3, 2026, 06_11_27 PM (1).png" alt="Cóndor SGA" width="180"/>


  # Sistema Distribuido de Gestión Académica Universitaria

  **Aplicación web académica construida con Django y PostgreSQL para la gestión integral de procesos universitarios en una arquitectura orientada a distribución por facultades.**

  <br/>

  ![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)
  ![Django](https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white)
  ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
  ![uv](https://img.shields.io/badge/uv-package%20manager-261230?style=for-the-badge)
  ![Ruff](https://img.shields.io/badge/Ruff-linting-D7FF64?style=for-the-badge)
  ![pytest](https://img.shields.io/badge/pytest-testing-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)

</div>

---

## Descripción

Este repositorio contiene el desarrollo final de un **Sistema Distribuido de Gestión Académica Universitaria**, diseñado para administrar procesos académicos, financieros y administrativos dentro de una institución organizada por facultades.

El sistema permite gestionar:

- Autenticación institucional por correo.
- Usuarios y roles funcionales.
- Facultades y programas académicos.
- Asignaturas, planes de estudio y prerrequisitos.
- Grupos académicos por periodo.
- Inscripciones y notas.
- Matrículas, recibos y tarifas.
- Homologaciones académicas.
- Indicadores académicos.
- Auditoría operativa.
- Alcance de datos según rol.

El proyecto conserva un modelo relacional definido en PostgreSQL y lo integra con Django mediante modelos no administrados, respetando la estructura SQL construida durante el desarrollo académico.

---

## Identidad Visual

La interfaz adopta una identidad institucional basada en el concepto visual del **cóndor caído**, usado como elemento gráfico principal del sistema.

La línea visual del proyecto utiliza una paleta sobria en tonos:

- Beige.
- Arena.
- Crema.
- Café.
- Negro institucional.

El frontend fue construido con Django Templates, Bootstrap 5, Bootstrap Icons y estilos propios centralizados.

---

## Tabla de Contenido

- [Sistema Distribuido de Gestión Académica Universitaria](#sistema-distribuido-de-gestión-académica-universitaria)
  - [Descripción](#descripción)
  - [Identidad Visual](#identidad-visual)
  - [Tabla de Contenido](#tabla-de-contenido)
  - [Estado del Proyecto](#estado-del-proyecto)
  - [Características Principales](#características-principales)
    - [Gestión académica](#gestión-académica)
    - [Gestión financiera](#gestión-financiera)
    - [Homologaciones](#homologaciones)
    - [Indicadores](#indicadores)
    - [Auditoría](#auditoría)
  - [Arquitectura General](#arquitectura-general)
  - [Tecnologías](#tecnologías)
  - [Módulos Funcionales](#módulos-funcionales)
  - [Roles del Sistema](#roles-del-sistema)
  - [Estructura del Repositorio](#estructura-del-repositorio)
  - [Configuración Local](#configuración-local)
    - [1. Requisitos previos](#1-requisitos-previos)
    - [2. Clonar el repositorio](#2-clonar-el-repositorio)
    - [3. Instalar dependencias](#3-instalar-dependencias)
    - [4. Crear archivo `.env`](#4-crear-archivo-env)
  - [Base de Datos](#base-de-datos)
    - [Flujo recomendado para una base local limpia](#flujo-recomendado-para-una-base-local-limpia)
  - [Ejecución](#ejecución)
  - [Usuarios Demo](#usuarios-demo)
  - [Rutas Principales](#rutas-principales)
  - [Frontend](#frontend)
  - [Calidad y Validación](#calidad-y-validación)
  - [Decisiones Técnicas](#decisiones-técnicas)
    - [Modelo SQL-first](#modelo-sql-first)
    - [Modelos no administrados](#modelos-no-administrados)
    - [Autenticación personalizada](#autenticación-personalizada)
    - [Separación entre permisos y alcance](#separación-entre-permisos-y-alcance)
    - [Seguridad desde base de datos y aplicación](#seguridad-desde-base-de-datos-y-aplicación)
  - [Documentación](#documentación)
  - [Seguridad](#seguridad)
  - [Alcance Actual](#alcance-actual)
  - [Roadmap](#roadmap)
  - [Autores](#autores)

---

## Estado del Proyecto

El sistema se encuentra en una versión funcional de cierre académico.

Actualmente incluye:

- Backend Django operativo.
- Autenticación por correo electrónico.
- Usuario personalizado con integración al sistema de grupos de Django.
- Roles funcionales implementados.
- Alcance de datos por rol.
- Templates institucionales.
- Sidebar colapsable con persistencia en `localStorage`.
- Dashboard adaptado por usuario.
- Scripts SQL separados por propósito.
- Datos demo para validación.
- Comandos de carga inicial.
- Documentación técnica y académica.
- Validaciones con Ruff, pytest y comandos de Django.

---

## Características Principales

### Gestión académica

- Registro y consulta de facultades.
- Administración de programas académicos.
- Gestión de asignaturas.
- Planes de estudio por programa.
- Prerrequisitos.
- Grupos académicos por periodo.
- Inscripciones.
- Notas parciales y nota final.

### Gestión financiera

- Tarifas de matrícula.
- Recibos por estudiante.
- Estados de pago.
- Matrículas académicas.
- Separación entre proceso financiero y proceso académico-administrativo.

### Homologaciones

- Solicitud de homologaciones.
- Asignación de profesor evaluador.
- Evaluación académica.
- Registro de institución y asignatura de origen.
- Control de estado de solicitud.

### Indicadores

- Promedio académico.
- Avance de carrera.
- Materias aprobadas.
- Materias pendientes.
- Riesgo académico.
- Consultas derivadas sin almacenar métricas redundantes.

### Auditoría

- Registro de acciones relevantes.
- Consulta de trazabilidad operativa.
- Control institucional sobre operaciones del sistema.

---

## Arquitectura General

El sistema sigue una arquitectura web tradicional basada en Django, conectada a PostgreSQL como motor relacional principal.

```text
Usuario
  │
  ▼
Interfaz Web Django Templates
  │
  ▼
Vistas Django
  │
  ▼
Servicios de acceso y alcance por rol
  │
  ▼
Modelos Django no administrados
  │
  ▼
PostgreSQL
  │
  ├── Modelo académico
  ├── Modelo financiero
  ├── Modelo de homologaciones
  ├── Modelo de auditoría
  └── Tablas internas de autenticación Django
```

La arquitectura del proyecto fue pensada para evolucionar hacia un esquema distribuido por facultades, permitiendo que cada facultad administre su información académica local y que la institución mantenga consultas consolidadas.

---

## Tecnologías

| Componente | Tecnología |
|---|---|
| Lenguaje | Python 3.12+ |
| Framework web | Django 5.x |
| Base de datos | PostgreSQL |
| Driver PostgreSQL | psycopg |
| Variables de entorno | django-environ |
| Frontend | Django Templates |
| UI | Bootstrap 5 |
| Iconografía | Bootstrap Icons |
| Estilos | CSS propio |
| Testing | pytest, pytest-django |
| Linting y formato | Ruff |
| Gestión de dependencias | uv |
| Administración SQL | DBeaver / psql |

---

## Módulos Funcionales

| App | Responsabilidad |
|---|---|
| `accounts` | Usuario personalizado, login, logout, dashboard, roles y alcance funcional. |
| `estructura` | Facultades, programas académicos y periodos. |
| `academica` | Asignaturas, planes, prerrequisitos, docentes, grupos, inscripciones y notas. |
| `financiera` | Tarifas, recibos y matrículas. |
| `homologaciones` | Solicitudes, asignación de evaluador, evaluación y cancelación. |
| `indicadores` | Avance académico, promedio, materias faltantes y riesgo académico. |
| `auditoria` | Consulta de trazabilidad operativa. |

---

## Roles del Sistema

El sistema implementa navegación, permisos y alcance de información según el rol del usuario autenticado.

| Rol | Alcance funcional |
|---|---|
| Estudiante | Consulta de información académica propia, inscripciones, notas, matrícula e indicadores personales. |
| Docente | Consulta de grupos asignados y gestión académica asociada. |
| Coordinador | Gestión académica sobre un programa específico. |
| Decano | Consulta y supervisión sobre una facultad. |
| Administrativo | Apoyo a procesos financieros y administrativos. |
| Administrador funcional | Gestión general del sistema y datos institucionales. |

---

## Estructura del Repositorio

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
│   ├── media/
│   ├── static/
│   ├── templates/
│   ├── tests/
│   └── manage.py
├── backups/
├── docs/
├── sql/
├── .env.example
├── .gitignore
├── .python-version
├── pyproject.toml
├── requirements.txt
├── uv.lock
└── README.md
```

---

## Configuración Local

### 1. Requisitos previos

Antes de ejecutar el proyecto se requiere:

- Python 3.12 o superior.
- PostgreSQL instalado y activo.
- `uv` instalado.
- DBeaver, pgAdmin o `psql` para ejecutar scripts SQL.
- Git.

---

### 2. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd <nombre-del-repositorio>
```

---

### 3. Instalar dependencias

```bash
uv sync
```

También puede instalarse desde `requirements.txt` en entornos tradicionales:

```bash
pip install -r requirements.txt
```

Sin embargo, el flujo recomendado del proyecto es usar `uv`.

---

### 4. Crear archivo `.env`

Crear un archivo `.env` en la raíz del proyecto tomando como referencia `.env.example`.

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

> No se deben versionar credenciales reales. El archivo `.env` debe permanecer local.

---

## Base de Datos

El proyecto usa PostgreSQL como motor principal.

Los scripts SQL se encuentran en la carpeta `sql/`.

| Archivo | Propósito |
|---|---|
| `sql/01_ddl.sql` | Creación de tablas, claves, restricciones y estructura principal. |
| `sql/02_inserts_catalogos.sql` | Carga de catálogos institucionales. |
| `sql/03_inserts_operativos.sql` | Carga de datos operativos de prueba. |
| `sql/04_consultas_validacion.sql` | Consultas de validación del modelo. |
| `sql/09_auth_user_m2m_tables.sql` | Tablas M2M requeridas para grupos y permisos de Django con usuario personalizado. |

---

### Flujo recomendado para una base local limpia

Crear la base de datos:

```bash
createdb gestion_academica_local
```

Ejecutar los scripts SQL principales:

```bash
psql -d gestion_academica_local -f sql/01_ddl.sql
psql -d gestion_academica_local -f sql/02_inserts_catalogos.sql
psql -d gestion_academica_local -f sql/03_inserts_operativos.sql
```

Ejecutar migraciones internas de Django:

```bash
uv run python backend/manage.py migrate
```

Ejecutar tablas M2M de autenticación personalizada:

```bash
psql -d gestion_academica_local -f sql/09_auth_user_m2m_tables.sql
```

Crear grupos funcionales:

```bash
uv run python backend/manage.py setup_functional_groups
```

Crear usuarios demo:

```bash
uv run python backend/manage.py seed_demo_users
```

---

## Ejecución

Iniciar el servidor local:

```bash
uv run python backend/manage.py runserver
```

Abrir en el navegador:

```text
http://127.0.0.1:8000/login/
```

---

## Usuarios Demo

La contraseña demo para todos los usuarios es:

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

> Estas credenciales son ficticias y están destinadas exclusivamente a desarrollo local y validación académica.

---

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

Algunas rutas redirigen automáticamente cuando el usuario autenticado no tiene permisos suficientes.

---

## Frontend

La interfaz está construida con Django Templates y estilos propios.

Archivos principales:

```text
backend/templates/base.html
backend/static/css/condor.css
backend/static/js/condor.js
```

Características visuales:

- Login institucional personalizado.
- Sidebar izquierdo colapsable.
- Persistencia del estado del sidebar en `localStorage`.
- Navbar superior con usuario autenticado y roles activos.
- Dashboard con tarjetas y accesos rápidos.
- Tablas responsivas.
- Formularios estilizados.
- Badges y alertas consistentes.
- Paleta visual beige, café y crema.
- Uso de imágenes del cóndor como identidad del sistema.

---

## Calidad y Validación

Ejecutar validaciones de Django:

```bash
uv run python backend/manage.py check
```

Ejecutar linting:

```bash
uv run ruff check backend/apps backend/config
```

Verificar formato:

```bash
uv run ruff format --check backend/apps backend/config
```

Aplicar formato:

```bash
uv run ruff format backend/apps backend/config
```

Ejecutar pruebas:

```bash
uv run pytest
```

---

## Decisiones Técnicas

### Modelo SQL-first

El modelo de datos fue definido primero en PostgreSQL mediante scripts SQL. Django se integra sobre ese modelo sin reemplazarlo.

### Modelos no administrados

Las tablas académicas principales utilizan:

```python
managed = False
```

Esto evita que Django intente crear, modificar o eliminar tablas que ya están controladas por los scripts SQL del proyecto.

### Autenticación personalizada

El sistema utiliza un usuario personalizado basado en correo electrónico como identificador principal.

### Separación entre permisos y alcance

La lógica de acceso se divide en:

```text
apps.accounts.roles
apps.accounts.access
apps.accounts.scope
```

Esto permite diferenciar:

- Qué rol tiene el usuario.
- Qué acciones puede ejecutar.
- Qué subconjunto de datos puede consultar.

### Seguridad desde base de datos y aplicación

El diseño combina:

- Restricciones relacionales.
- Llaves primarias y foráneas.
- Validaciones SQL.
- Grupos de Django.
- Alcance funcional por rol.
- Separación entre datos propios, datos de programa y datos de facultad.

---

## Documentación

La carpeta `docs/` contiene la documentación técnica y académica del proyecto.

Incluye:

- Reglas de negocio.
- Modelo conceptual.
- Modelo relacional.
- Diccionario de datos.
- Decisiones técnicas.
- Guía de pantallas y flujos.
- Usuarios demo.
- Guía visual.
- Validaciones SQL.
- Manuales de ejecución.

Punto de entrada recomendado:

```text
docs/00_readme_documentacion.md
```

---

## Seguridad

Buenas prácticas aplicadas y recomendadas:

- No subir `.env` con credenciales reales.
- No hardcodear claves, tokens ni contraseñas.
- No publicar credenciales productivas.
- Usar usuarios demo únicamente en entorno local.
- Configurar `DJANGO_DEBUG=False` fuera de desarrollo.
- Definir explícitamente `DJANGO_ALLOWED_HOSTS` en ambientes no locales.
- Revisar permisos de PostgreSQL antes de publicar el sistema.
- Mantener separadas las credenciales locales y cloud.

---

## Alcance Actual

Esta versión corresponde a una entrega funcional académica con ejecución local y arquitectura preparada para evolución distribuida.

El sistema incluye:

- Modelo relacional completo.
- Scripts SQL.
- Backend Django.
- Roles funcionales.
- Interfaz web.
- Datos demo.
- Documentación.
- Validaciones.

La evolución hacia despliegue cloud completo queda preparada como fase posterior del proyecto.

---

## Roadmap

Próximas mejoras sugeridas:

- Despliegue completo en PostgreSQL administrado en la nube.
- Configuración formal de ambiente productivo.
- Automatización de carga inicial.
- Pipeline CI/CD.
- Pruebas de integración por módulo.
- Exportación de reportes académicos.
- Mejoras visuales sobre la identidad del cóndor.
- Dashboard institucional consolidado.
- Documentación de despliegue final.

---

## Autores

Proyecto académico desarrollado para la asignatura de Bases de Datos.

**Universidad Distrital Francisco José de Caldas**  
Facultad de Ingeniería  
Ingeniería de Sistemas

---

<div align="center">

  **Sistema Distribuido de Gestión Académica Universitaria**  
  _Diseño relacional, Django, PostgreSQL y arquitectura académica distribuida._

</div>