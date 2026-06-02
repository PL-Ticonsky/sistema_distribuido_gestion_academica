# Documentación del proyecto: Sistema Distribuido de Gestión Académica

Fecha: 2026-05-24

## Resumen general

Proyecto Django organizado bajo el directorio `backend/`. Objetivo: sistema de gestión académica universitario con PostgreSQL como BD. Contiene aplicaciones modulares para cuentas, estructura académica, académica (materias/programas), financiera, homologaciones y auditoría. Hay documentación en `docs/` y un DDL completo en `sql/01_ddl.sql`.

## Stack y dependencias principales
- Python >= 3.12
- Django >= 5.0, < 6.0
- PostgreSQL (psycopg[binary])
- Pillow (para manejo de imágenes)
- Dev: `pytest`, `pytest-django`, `ruff`

Las dependencias están declaradas en `pyproject.toml` y referenciadas en `requirements.txt` para compatibilidad.

## Estructura del repositorio (resumen)
- `backend/` : código Django (config, manage.py, apps)
  - `backend/config/` : configuración de Django (`settings.py`, `urls.py`, `wsgi.py`, `asgi.py`)
  - `backend/apps/` : aplicaciones específicas:
    - `apps.accounts` — autenticación, modelos de usuario extendido
    - `apps.estructura` — entidades de la estructura (facultad, programa, asignaturas)
    - `apps.academica` — lógica académica (grupos, inscripción, notas)
    - `apps.financiera` — matrículas, recibos, tarifas
    - `apps.homologaciones` — procesos de homologación
    - `apps.auditoria` — registros de auditoría
- `docs/` : documentación en formato Markdown (varios archivos)
- `sql/01_ddl.sql` : DDL SQL con el modelo relacional completo (usuarios, facultad, programas, periodo, estudiante, profesor, asignaturas, matrículas, homologaciones, auditoría, etc.)

## Estado actual por módulo (detección automática)
He inspeccionado `backend/apps/` y encontrado archivos clave para cada app; el estado es inferido por la presencia de ficheros `models.py`, `views.py`, `migrations/`:

- `apps.accounts`:
  - Archivos presentes: `apps.py`, `forms.py`, `managers.py`, `models.py`, `views.py`, `urls.py`, `migrations/`
  - Estado: Implementado a nivel de código (modelo de usuario extendido y managers). Migraciones presentes en `migrations/` (chequear si conteninen migraciones reales `0001_*.py`).

- `apps.estructura`:
  - Archivos presentes: `admin.py`, `apps.py`, `models.py`, `views.py`, `urls.py`, `migrations/`
  - Estado: Implementado (modelos y vistas). Revisar migraciones generadas.

- `apps.academica`:
  - Archivos presentes: `admin.py`, `apps.py`, `models.py`, `views.py`, `urls.py`, `migrations/`
  - Estado: Implementado.

- `apps.financiera`:
  - Archivos presentes: `admin.py`, `apps.py`, `models.py`, `views.py`, `urls.py`, `migrations/`
  - Estado: Implementado.

- `apps.homologaciones`:
  - Archivos presentes: `apps.py`, `migrations/` (no `models.py` detectado)
  - Estado: Parcial. La app existe pero no parece contener `models.py` en este listado — puede que las entidades estén en otra app o falte implementar modelos y vistas.

- `apps.auditoria`:
  - Archivos presentes: `apps.py`, `migrations/` (no `models.py` detectado en la lista)
  - Estado: Parcial. Existe la app, pero revisar si la lógica está implementada en ficheros aún no visibles.

Notas:
- La presencia de `migrations/` sugiere que se han ejecutado `makemigrations` o que hay migraciones iniciales; conviene abrir esas carpetas y revisar si contienen `0001_initial.py` u otras migraciones.
- No se encontró un directorio `tests/` a nivel raíz con tests de proyecto; `pyproject.toml` configura `pytest` para buscar tests en `backend`.

## Coherencia con DDL (`sql/01_ddl.sql`)
- Existe un DDL completo en `sql/01_ddl.sql` que define tablas y constraints para el modelo relacional. Recomendación: comparar los `models.py` de las apps con ese DDL para garantizar que las migraciones y el esquema SQL coincidan (nombres de campos, tipos, constraints, índices, checks, claves foráneas y unicidad).

## Pasos recomendados inmediatos (prioritarios)
1. Preparar entorno local reproducible:
   - Crear `.env` con variables necesarias: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `POSTGRES_*`.
   - Instalar dependencias (usar `pyproject.toml` o `requirements.txt`).
2. Verificar y aplicar migraciones:
   - Ejecutar `python backend/manage.py makemigrations --check` para detectar modelos sin migrar.
   - Ejecutar `python backend/manage.py migrate` y revisar errores.
3. Ejecutar tests con `pytest` y corregir fallos.
4. Comparar `models.py` vs `sql/01_ddl.sql` y documentar diferencias; si la fuente de verdad es el DDL, ajustar modelos o generar migraciones que repliquen el DDL.
5. Asegurar variables sensibles fuera del repo (`SECRET_KEY`, credenciales DB).

Comandos útiles:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt   # o usar el flujo con uv/pyproject
python backend/manage.py check
python backend/manage.py makemigrations
python backend/manage.py migrate
python backend/manage.py createsuperuser
pytest -q
ruff check backend
``` 

## Recomendaciones por área
- Calidad: integrar `ruff` en pre-commit y pipeline. Añadir `pytest-cov` y reglas mínimas de cobertura.
- CI: GitHub Actions para lint+tests+migrations (check-diff).
- Contenerización: añadir `Dockerfile` y `docker-compose.yml` con Postgres para desarrollo.
- Seguridad: añadir escaneo de dependencias y secrets, forzar `DEBUG=False` en producción y configurar `ALLOWED_HOSTS`.

## Tareas pendientes detectadas (alta prioridad)
- Revisar y/o crear migraciones para todas las apps (confirmar que `migrations/` contenga archivos relevantes).
- Implementar o revisar `models.py` en `apps.homologaciones` y `apps.auditoria` si falta lógica (el DDL sí define tablas homologacion y auditoria).
- Añadir tests para cubrir modelos y flujos críticos (matrícula, inscripciones, pagos, homologación).
- Completar `README.md` con pasos de setup y despliegue.

## Anexos y enlaces rápidos
- Archivo de configuración: `backend/config/settings.py` ([backend/config/settings.py](backend/config/settings.py#L1))
- DDL SQL: `sql/01_ddl.sql` ([sql/01_ddl.sql](sql/01_ddl.sql#L1))
- Dependencias / pyproject: `pyproject.toml` ([pyproject.toml](pyproject.toml#L1))

---
Generé este documento desde la inspección del árbol de fuentes. Si quieres, puedo:
- A: Abrir cada `migrations/` y listar sus archivos (recomendado para validar migraciones existentes).
- B: Comparar automáticamente `models.py` de cada app con el DDL y generar un informe de diferencias.
- C: Crear un `Dockerfile` y `docker-compose.yml` para desarrollo.
- D: Ejecutar `pytest` aquí y reportar resultados (necesita entorno y dependencias instaladas).

Indica la opción que prefieres para que continúe.
