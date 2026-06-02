# Guía Técnica de Desarrollo - Backend Django

**Sistema Distribuido de Gestión Académica Universitaria**

---

## Índice Rápido

- [Primeros Pasos](#primeros-pasos)
- [Estructura de Carpetas](#estructura-de-carpetas)
- [Flujos de Desarrollo](#flujos-de-desarrollo)
- [Patrón MVC en Django](#patrón-mvc-en-django)
- [Cómo Agregar una Nueva Funcionalidad](#cómo-agregar-una-nueva-funcionalidad)
- [Debugging y Troubleshooting](#debugging-y-troubleshooting)

---

## Primeros Pasos

### 1. Configuración Inicial

```bash
# Clonar proyecto
git clone <repo-url>
cd sistema_distribuido_gestion_academica

# Instalar dependencias
uv sync

# Crear archivo .env
cat > .env << EOF
DJANGO_SECRET_KEY=dev-key-change-in-prod
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=gestion_academica_local
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_SSLMODE=prefer
EOF

# Verificar instalación
uv run python backend/manage.py check
```

### 2. Preparar Base de Datos

```bash
# Crear base de datos en PostgreSQL
createdb gestion_academica_local

# Ejecutar scripts SQL (en orden)
psql -U postgres -d gestion_academica_local -f sql/01_ddl.sql
psql -U postgres -d gestion_academica_local -f sql/02_inserts_catalogos.sql
psql -U postgres -d gestion_academica_local -f sql/03_inserts_operativos.sql

# Django migrations
uv run python backend/manage.py migrate

# Tablas M2M de Django
psql -U postgres -d gestion_academica_local -f sql/09_auth_user_m2m_tables.sql

# Crear grupos funcionales y usuarios demo
uv run python backend/manage.py setup_functional_groups
uv run python backend/manage.py seed_demo_users
```

### 3. Ejecutar Servidor

```bash
uv run python backend/manage.py runserver
# Acceder a http://127.0.0.1:8000/login/
```

---

## Estructura de Carpetas

### Carpeta: backend/config/

```
config/
├── settings.py          # Configuración Django (INSTALLED_APPS, DATABASES, etc.)
├── urls.py              # Rutas raíz (enrutamiento a apps)
├── wsgi.py              # Production entry point
└── asgi.py              # Async entry point
```

**settings.py** es el corazón:
- INSTALLED_APPS → apps registradas
- DATABASES → conexión PostgreSQL
- AUTH_USER_MODEL → CustomUser
- MIDDLEWARE → stack de procesos
- TEMPLATES → configuración de templates
- STATIC_URL, MEDIA_URL → archivos estáticos

**urls.py**:
```python
urlpatterns = [
    path("", include("apps.accounts.urls")),
    path("academica/", include("apps.academica.urls")),
    # ... otras apps
    path("admin/", admin.site.urls),
]
```

### Carpeta: backend/apps/

Estructura por app (e.g., academica/):

```
academica/
├── __init__.py
├── apps.py              # Configuración de la app
├── models.py            # Definición de modelos (ORM)
├── views.py             # Vistas (lógica de presentación)
├── forms.py             # Formularios y validaciones
├── urls.py              # Rutas de la app
├── admin.py             # Configuración admin site
├── migrations/          # Historial de cambios en BD
│   └── __init__.py
└── templates/academica/ # HTML templates de la app
    ├── asignatura_list.html
    ├── grupo_detail.html
    └── ...
```

**Cada archivo tiene responsabilidad clara**:
- **models.py**: Estructura de datos (ORM)
- **views.py**: Lógica, autenticación, renderizado
- **forms.py**: Validación de entrada
- **urls.py**: Mapeo URL → Vista
- **admin.py**: Interfaz admin site

### Carpeta: backend/templates/

```
templates/
├── base.html            # Layout base (herencia)
├── 403.html, 404.html   # Errores
├── accounts/
│   ├── login.html
│   └── dashboard.html
├── academica/
│   ├── asignatura_list.html
│   ├── grupo_list.html
│   └── ...
└── ... (otras apps)
```

**base.html** es la plantilla madre:
```html
<!DOCTYPE html>
<html>
<head>
    {% block title %}{% endblock %}
    <link rel="stylesheet" href="/static/css/condor.css">
</head>
<body>
    <nav>{% block navbar %}{% endblock %}</nav>
    <main>
        {% block content %}{% endblock %}
    </main>
    <script src="/static/js/condor.js"></script>
</body>
</html>
```

Los templates de cada view extienden base.html:
```html
{% extends "base.html" %}
{% block title %}Asignaturas{% endblock %}
{% block content %}
    <h1>Lista de Asignaturas</h1>
    {% for asignatura in asignaturas %}
        <div>{{ asignatura.nombre_asignatura }}</div>
    {% endfor %}
{% endblock %}
```

---

## Flujos de Desarrollo

### Flujo 1: Corregir Bug

```
1. Identificar el problema
   ↓
2. Abrir Django shell:
   uv run python backend/manage.py shell
   
   # Inspeccionar datos
   >>> from apps.academica.models import Inscripcion
   >>> inscripcion = Inscripcion.objects.get(id=...)
   >>> inscripcion.nota1  # Ver valor
   
   ↓
3. Revisar vista en views.py
   - ¿Qué datos envía?
   - ¿Qué filtros aplica?
   
   ↓
4. Revisar template HTML
   - ¿Cómo renderiza?
   - ¿Hay errores en variables?
   
   ↓
5. Revisar formulario en forms.py
   - ¿Qué valida?
   - ¿Hay clean() con lógica errónea?
   
   ↓
6. Crear test que reproduzca bug
   
   ↓
7. Hacer fix
   
   ↓
8. Ejecutar test nuevamente
   
   ↓
9. Commit y push
```

### Flujo 2: Agregar Nueva Funcionalidad

```
1. Especificación
   - ¿Qué modelo afecta?
   - ¿Qué vista necesita?
   - ¿Qué roles acceden?
   
   ↓
2. Actualizar modelo (si necesario)
   backend/apps/[app]/models.py
   
   ↓
3. Crear migración (si necesario)
   uv run python backend/manage.py makemigrations
   uv run python backend/manage.py migrate
   
   ↓
4. Crear/actualizar formulario
   backend/apps/[app]/forms.py
   - Agregar campos
   - Agregar validaciones en clean()
   
   ↓
5. Crear/actualizar vista
   backend/apps/[app]/views.py
   - Crear clase view
   - Especificar allowed_roles
   - Implementar get_queryset() con filtros
   
   ↓
6. Agregar URL
   backend/apps/[app]/urls.py
   path('ruta/', Vista.as_view(), name='nombre')
   
   ↓
7. Crear/actualizar template
   backend/templates/[app]/template.html
   
   ↓
8. Testear manualmente
   uv run python backend/manage.py runserver
   
   ↓
9. Escribir tests
   backend/tests/test_[feature].py
   
   ↓
10. Ejecutar tests
    uv run pytest
    
    ↓
11. Linting
    uv run ruff check backend/
    uv run ruff format backend/
    
    ↓
12. Commit y push
```

---

## Patrón MVC en Django

Django usa **MTV** (Model-Template-View), que es similar a MVC:

### Model (Modelo)

```python
# backend/apps/academica/models.py

class Grupo(models.Model):
    """Grupo académico (clase de una asignatura)"""
    
    id_grupo = models.UUIDField(primary_key=True)
    programa_asignatura = models.ForeignKey(
        ProgramaAsignatura,
        on_delete=models.DO_NOTHING,
        related_name='grupos'
    )
    profesor = models.ForeignKey(
        Profesor,
        on_delete=models.DO_NOTHING,
        null=True,
        related_name='grupos'
    )
    cupo_maximo = models.IntegerField()
    estado_grupo = models.CharField(
        max_length=20,
        choices=EstadoGrupo.choices
    )
    
    class Meta:
        db_table = 'grupo'
        managed = False  # No generar migraciones
        ordering = ['periodo_academico', 'programa_asignatura']
    
    def __str__(self):
        return f"{self.programa_asignatura.asignatura} - {self.codigo_grupo}"
```

**Responsabilidades del Model**:
- Define estructura de datos
- Relaciones entre tablas (FK, M2M)
- Opciones de campo (choices, max_length)
- Meta options (db_table, ordering, constraints)

### Template (Template)

```html
<!-- backend/templates/academica/grupo_list.html -->

{% extends "base.html" %}

{% block title %}Grupos Académicos{% endblock %}

{% block content %}
<div class="container">
    <h1>Grupos Académicos</h1>
    
    {% if grupos %}
        <table class="table">
            <thead>
                <tr>
                    <th>Asignatura</th>
                    <th>Código</th>
                    <th>Profesor</th>
                    <th>Cupo</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for grupo in grupos %}
                <tr>
                    <td>{{ grupo.programa_asignatura.asignatura.nombre_asignatura }}</td>
                    <td>{{ grupo.codigo_grupo }}</td>
                    <td>{{ grupo.profesor.usuario.nombre }}</td>
                    <td>{{ grupo.cupos_disponibles }} / {{ grupo.cupo_maximo }}</td>
                    <td>{{ grupo.estado_grupo }}</td>
                    <td>
                        <a href="{% url 'academica:grupo_detail' grupo.id_grupo %}">Ver</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p>No hay grupos disponibles.</p>
    {% endif %}
</div>
{% endblock %}
```

**Responsabilidades del Template**:
- Renderizar datos del view
- Formularios HTML
- Herencia de base.html
- Lógica de presentación (if, for, filters)

### View (Vista)

```python
# backend/apps/academica/views.py

from django.views.generic import ListView
from apps.academica.models import Grupo

class GrupoListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """Lista grupos académicos según alcance del usuario"""
    
    allowed_roles = ('docente', 'coordinador', 'decano', 'superadmin')
    model = Grupo
    template_name = 'academica/grupo_list.html'
    context_object_name = 'grupos'
    
    def get_queryset(self):
        """Obtiene grupos visibles para el usuario"""
        # Incluye optimizaciones de query
        queryset = Grupo.objects.select_related(
            'programa_asignatura__asignatura',
            'profesor__usuario',
            'periodo_academico'
        ).annotate(
            total_inscritos=Count('inscripciones'),
            cupos_disponibles=F('cupo_maximo') - F('total_inscritos')
        )
        
        # Filtra según alcance del usuario
        group_ids = get_visible_group_ids(self.request.user)
        if group_ids is not None:
            queryset = queryset.filter(id_grupo__in=group_ids)
        
        return queryset.order_by('periodo_academico', 'programa_asignatura')
    
    def get_context_data(self, **kwargs):
        """Agrega contexto adicional al template"""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Grupos Académicos'
        return context
```

**Responsabilidades de la View**:
- Obtener datos del modelo
- Aplicar filtros y seguridad
- Procesar entrada del usuario
- Renderizar template con contexto
- Redireccionar si es necesario

---

## Cómo Agregar una Nueva Funcionalidad

### Caso de Uso: Agregar "Nota de Participación" a Inscripción

#### Paso 1: Actualizar Modelo

```python
# backend/apps/academica/models.py

class Inscripcion(models.Model):
    # ... campos existentes ...
    
    # NUEVO
    nota_participacion = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Nota de participación (0-5)"
    )
    
    def calculate_weighted_average(self):
        """Calcula promedio ponderado incluyendo participación"""
        if all([self.nota1, self.nota2, self.nota3, self.nota_participacion]):
            # 70% de notas, 30% de participación
            return (
                (self.nota1 + self.nota2 + self.nota3) / 3 * 0.7 +
                self.nota_participacion * 0.3
            )
        return None
```

#### Paso 2: Crear Migración

```bash
uv run python backend/manage.py makemigrations academica
# Genera: 0XXX_add_nota_participacion.py

uv run python backend/manage.py migrate
```

#### Paso 3: Actualizar Formulario

```python
# backend/apps/academica/forms.py

class NotaInscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['nota1', 'nota2', 'nota3', 'nota_participacion', 'estado_inscripcion']
    
    def clean(self):
        cleaned_data = super().clean()
        # Validar nueva nota
        participacion = cleaned_data.get('nota_participacion')
        if participacion is not None:
            if participacion < 0 or participacion > 5:
                raise ValidationError("Nota de participación entre 0 y 5")
        return cleaned_data
```

#### Paso 4: Actualizar Vista

```python
# backend/apps/academica/views.py

class NotaInscripcionUpdateView(UpdateView):
    # ... configuración existente ...
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mostrar promedio ponderado
        context['promedio'] = self.object.calculate_weighted_average()
        return context
```

#### Paso 5: Actualizar Template

```html
<!-- backend/templates/academica/nota_form.html -->

{% extends "base.html" %}

{% block content %}
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    
    <!-- NUEVO: Mostrar promedio ponderado -->
    {% if promedio %}
    <div class="alert alert-info">
        Promedio ponderado: {{ promedio|floatformat:2 }}
    </div>
    {% endif %}
    
    <button type="submit">Guardar</button>
</form>
{% endblock %}
```

#### Paso 6: Crear Test

```python
# backend/tests/test_nota_participacion.py

import pytest
from apps.academica.models import Inscripcion

@pytest.mark.django_db
def test_calcula_promedio_con_participacion():
    """Verifica que el promedio ponderado incluye participación"""
    inscripcion = Inscripcion(
        nota1=4.0,
        nota2=4.0,
        nota3=4.0,
        nota_participacion=5.0
    )
    
    promedio = inscripcion.calculate_weighted_average()
    # (4+4+4)/3 * 0.7 + 5 * 0.3 = 4 * 0.7 + 5 * 0.3 = 4.3
    assert promedio == 4.3
```

#### Paso 7: Ejecutar y Validar

```bash
# Ejecutar servidor
uv run python backend/manage.py runserver

# Ejecutar tests
uv run pytest backend/tests/test_nota_participacion.py

# Linting
uv run ruff check backend/apps/academica/

# Formatear
uv run ruff format backend/apps/academica/
```

---

## Debugging y Troubleshooting

### 1. Error: "Grupo no tiene modelo Inscripcion"

**Problema**: En template intenta usar `grupo.inscripciones` pero no aparece.

**Solución**: En views.py, asegurate de usar `related_name`:

```python
# models.py
class Inscripcion(models.Model):
    grupo = models.ForeignKey(
        Grupo,
        related_name='inscripciones'  # ← Importante
    )

# views.py
context['inscripciones'] = grupo.inscripciones.all()  # Ahora funciona
```

### 2. Error: "N+1 queries"

**Problema**: Por cada Profesor, hace 1 query a Facultad (lento).

**Solución**: Usar select_related():

```python
# ANTES (lento)
profesores = Profesor.objects.all()
for p in profesores:
    print(p.facultad.nombre)  # Query por cada profesor

# DESPUÉS (rápido)
profesores = Profesor.objects.select_related('facultad')
for p in profesores:
    print(p.facultad.nombre)  # Solo 1 query
```

### 3. Error: "Usuario no tiene acceso"

**Problema**: Usuario autenticado pero vista redirige a dashboard.

**Solución**: Verificar roles en scope.py:

```python
# Debugging
user_roles = get_user_roles(request.user)
print(f"Roles: {user_roles}")  # Ver qué roles tiene

# Verificar alcance
student_ids = get_visible_student_ids(request.user)
print(f"Estudiantes visibles: {student_ids}")  # Ver si es None o lista
```

### 4. Error: "Validación de formulario falla sin razón"

**Problema**: Formulario no valida pero no ve el error.

**Solución**: En template, mostrar errores:

```html
{% if form.errors %}
    <div class="alert alert-danger">
        {% for field, errors in form.errors.items %}
            <strong>{{ field }}:</strong>
            {% for error in errors %}
                <div>{{ error }}</div>
            {% endfor %}
        {% endfor %}
    </div>
{% endif %}
```

### 5. Error: "POST 403 Forbidden"

**Problema**: CSRF token faltante en formulario.

**Solución**: En template, agregar token:

```html
<form method="post">
    {% csrf_token %}  <!-- ← Requerido -->
    {{ form.as_p }}
    <button type="submit">Enviar</button>
</form>
```

### 6. Debug en Django Shell

```bash
uv run python backend/manage.py shell

# Importar modelo
>>> from apps.academica.models import Inscripcion
>>> from apps.academica.models import Grupo

# Ver todos
>>> Inscripcion.objects.all()

# Filtrar
>>> Inscripcion.objects.filter(estado_inscripcion='Cursando')

# Actualizar
>>> inscripcion = Inscripcion.objects.get(id=...)
>>> inscripcion.nota1 = 4.5
>>> inscripcion.save()

# Queries SQL generadas
>>> from django.db import connection
>>> connection.queries[-1]
```

---

## Checklist para Nueva Feature

- [ ] Actualizar models.py
- [ ] Generar migración: `makemigrations`
- [ ] Aplicar migración: `migrate`
- [ ] Actualizar forms.py
- [ ] Actualizar views.py
- [ ] Agregar URL en urls.py
- [ ] Crear/actualizar template
- [ ] Escribir tests
- [ ] Ejecutar tests: `pytest`
- [ ] Linting: `ruff check`
- [ ] Formato: `ruff format`
- [ ] Testear manualmente
- [ ] Commit y push

---

## Recursos Rápidos

### Django Documentation
- Models: https://docs.djangoproject.com/en/5.0/topics/db/models/
- Views: https://docs.djangoproject.com/en/5.0/topics/class-based-views/
- Forms: https://docs.djangoproject.com/en/5.0/topics/forms/
- Queries: https://docs.djangoproject.com/en/5.0/topics/db/queries/

### Útiles Comandos
```bash
# Ver SQL de query
python manage.py sqlmigrate academica 0001

# Exportar datos
python manage.py dumpdata > backup.json

# Cargar datos
python manage.py loaddata backup.json

# Limpiar BD (cuidado!)
python manage.py flush

# Crear superuser
python manage.py createsuperuser
```

---

**Última actualización**: Junio 2, 2026
