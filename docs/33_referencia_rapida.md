# Referencia Rápida - Backend Django

**Guía de bolsillo para desarrollo**

---

## Comandos Frecuentes

### Setup Inicial

```bash
# Clonar y configurar
git clone <repo>
cd sistema_distribuido_gestion_academica
uv sync

# Crear .env
cp .env.example .env

# Verificar
uv run python backend/manage.py check
```

### Base de Datos

```bash
# Preparar PostgreSQL (local)
createdb gestion_academica_local

# Cargar SQL scripts (en orden)
psql -U postgres -d gestion_academica_local -f sql/01_ddl.sql
psql -U postgres -d gestion_academica_local -f sql/02_inserts_catalogos.sql
psql -U postgres -d gestion_academica_local -f sql/03_inserts_operativos.sql

# Django migrations
uv run python backend/manage.py migrate
psql -U postgres -d gestion_academica_local -f sql/09_auth_user_m2m_tables.sql

# Setup grupos y usuarios
uv run python backend/manage.py setup_functional_groups
uv run python backend/manage.py seed_demo_users
```

### Ejecutar

```bash
# Desarrollo
uv run python backend/manage.py runserver

# Producción (local)
uv run python backend/manage.py runserver 0.0.0.0:8000
```

### Testing & Linting

```bash
# Tests
uv run pytest
uv run pytest backend/apps/academica/
uv run pytest -k "inscripcion" -v

# Cobertura
uv run pytest --cov=backend/apps --cov-report=html

# Linting
uv run ruff check backend/

# Formatear
uv run ruff format backend/

# Check Django
uv run python backend/manage.py check
```

### Migraciones

```bash
# Ver estado
uv run python backend/manage.py showmigrations

# Crear migración
uv run python backend/manage.py makemigrations academica

# Aplicar
uv run python backend/manage.py migrate

# Ver SQL
uv run python backend/manage.py sqlmigrate academica 0001

# Rollback
uv run python backend/manage.py migrate academica 0001
```

### Django Shell

```bash
# Interactivo
uv run python backend/manage.py shell

# Dentro:
>>> from apps.academica.models import Inscripcion
>>> Inscripcion.objects.all()
>>> obj = Inscripcion.objects.get(id=...)
>>> obj.nota1 = 4.5
>>> obj.save()
```

### Usuarios & Admin

```bash
# Crear superuser
uv run python backend/manage.py createsuperuser

# Admin site
# http://127.0.0.1:8000/admin/
```

### Utilities

```bash
# Limpiar BD (PELIGROSO!)
uv run python backend/manage.py flush

# Exportar datos
uv run python backend/manage.py dumpdata > backup.json

# Cargar datos
uv run python backend/manage.py loaddata backup.json

# Mostrar opciones view
uv run python backend/manage.py help runserver
```

---

## URLs Principales

```
LOGIN & DASHBOARD
/login/                             Inicio de sesión
/logout/                            Cerrar sesión
/dashboard/                         Dashboard por rol

ESTRUCTURA
/estructura/facultades/             Listar facultades
/estructura/facultades/<id>/        Detalle facultad
/estructura/programas/              Listar programas
/estructura/periodos/               Listar periodos

ACADÉMICA
/academica/asignaturas/             Listar asignaturas
/academica/asignaturas/<cod>/       Detalle asignatura
/academica/planes/                  Plan de estudios
/academica/prerrequisitos/          Prerrequisitos
/academica/docentes/                Listar docentes
/academica/docentes/<id>/           Detalle docente
/academica/grupos/                  Listar grupos
/academica/grupos/<id>/             Detalle grupo
/academica/estudiantes/agregar/     Crear estudiante
/academica/inscripciones/           Listar inscripciones
/academica/inscripciones/crear/     Crear inscripción
/academica/inscripciones/<id>/cancelar/ Cancelar inscripción
/academica/notas/                   Listar notas
/academica/notas/grupos/<id>/       Notas grupo
/academica/notas/inscripciones/<id>/editar/ Editar nota

FINANCIERA
/financiera/tarifas/                Listar tarifas
/financiera/tarifas/crear/          Crear tarifa
/financiera/tarifas/<id>/editar/    Editar tarifa
/financiera/tarifas/<id>/cambiar-estado/ Toggle tarifa
/financiera/recibos/                Listar recibos
/financiera/recibos/crear/          Crear recibo
/financiera/recibos/<id>/           Detalle recibo
/financiera/recibos/<id>/editar/    Editar recibo
/financiera/recibos/<id>/anular/    Anular recibo
/financiera/matriculas/             Listar matrículas
/financiera/matriculas/crear/       Crear matrícula
/financiera/matriculas/<id>/        Detalle matrícula
/financiera/matriculas/<id>/activar/ Activar matrícula
/financiera/matriculas/<id>/finalizar/ Finalizar matrícula
/financiera/matriculas/<id>/cancelar/ Cancelar matrícula
/financiera/matriculas/<id>/anular/ Anular matrícula

HOMOLOGACIONES
/homologaciones/                    Listar homologaciones
/homologaciones/crear/              Crear solicitud
/homologaciones/<id>/               Detalle homologación
/homologaciones/<id>/asignar-evaluador/ Asignar evaluador
/homologaciones/<id>/evaluar/       Evaluar
/homologaciones/<id>/cancelar/      Cancelar

INDICADORES
/indicadores/                       Listar estudiantes
/indicadores/mis-indicadores/       Mis indicadores
/indicadores/estudiantes/<id>/      Indicadores estudiante

AUDITORÍA
/auditoria/                         Listar registros
/auditoria/<id>/                    Detalle registro

ADMIN
/admin/                             Django admin site
```

---

## Estructura de Archivos Críticos

```
backend/
├── config/
│   ├── settings.py              ← CONFIGURACIÓN GLOBAL
│   ├── urls.py                  ← RUTAS RAÍZ
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── accounts/
│   │   ├── models.py            ← CustomUser
│   │   ├── views.py             ← Login, Dashboard
│   │   ├── forms.py             ← EmailAuthenticationForm
│   │   ├── roles.py             ← DEFINICIONES DE ROLES
│   │   ├── scope.py             ← FILTRADO POR ALCANCE
│   │   ├── access.py            ← RoleRequiredMixin
│   │   ├── urls.py
│   │   └── migrations/
│   ├── [app_name]/
│   │   ├── models.py            ← MODELOS
│   │   ├── views.py             ← VISTAS (CBV, FBV)
│   │   ├── forms.py             ← FORMULARIOS Y VALIDACIONES
│   │   ├── urls.py              ← RUTAS
│   │   ├── admin.py
│   │   ├── migrations/
│   │   └── templates/[app_name]/
│   │       ├── model_list.html
│   │       ├── model_detail.html
│   │       └── model_form.html
├── templates/
│   ├── base.html                ← LAYOUT BASE
│   ├── 403.html, 404.html
│   └── [app_name]/
├── static/
│   ├── css/condor.css
│   └── js/condor.js
├── media/                       ← Archivos cargados
├── tests/
│   ├── test_project_setup.py
│   └── (más tests)
└── manage.py

RAÍZ DEL PROYECTO
├── pyproject.toml               ← DEPENDENCIAS Y CONFIG
├── requirements.txt
├── .env                         ← VARIABLES (NO VERSIONAR)
└── README.md
```

---

## Estructura de Modelo Django

```python
# TEMPLATE BÁSICO

class MiModelo(models.Model):
    """Descripción del modelo"""
    
    # CAMPO PRIMARY KEY (implícito en Django, explícito aquí)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    
    # CAMPOS SIMPLES
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=20, choices=Estado.choices)
    
    # RELATIONSHIPS
    relacion_n_a_1 = models.ForeignKey(Otro, on_delete=models.DO_NOTHING)
    relacion_1_a_1 = models.OneToOneField(Otro, on_delete=models.DO_NOTHING)
    
    # TIMESTAMPS
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tabla_existente'
        managed = False  # Django no genera migraciones
        ordering = ['nombre']
        verbose_name = 'mi modelo'
        verbose_name_plural = 'mis modelos'
        constraints = [
            models.UniqueConstraint(fields=['campo1', 'campo2'])
        ]
    
    def __str__(self):
        return self.nombre
    
    def custom_method(self):
        """Método personalizado"""
        return self.nombre.upper()
```

---

## Estructura de Vista Django

```python
# TEMPLATE BÁSICO

from django.views.generic import ListView, DetailView, CreateView
from apps.myapp.models import Modelo
from apps.myapp.forms import MiForm
from apps.accounts.access import RoleRequiredMixin

class MiListView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """Lista objetos filtrando por alcance"""
    
    allowed_roles = ('rol1', 'rol2')  # Roles permitidos
    model = Modelo
    template_name = 'myapp/modelo_list.html'
    context_object_name = 'objetos'
    paginate_by = 20  # Paginación
    
    def get_queryset(self):
        """Filtra según usuario"""
        queryset = Modelo.objects.select_related('relacion')
        
        # Filtrar por alcance
        ids = get_visible_ids(self.request.user)
        if ids is not None:
            queryset = queryset.filter(id__in=ids)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Agrega contexto adicional"""
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Mis Objetos'
        return context

class MiCreateView(LoginRequiredMixin, RoleRequiredMixin, CreateView):
    """Crea nuevo objeto"""
    
    allowed_roles = ('rol1',)
    model = Modelo
    form_class = MiForm
    template_name = 'myapp/modelo_form.html'
    success_url = reverse_lazy('myapp:modelo_list')
    
    def form_valid(self, form):
        """Procesa formulario válido"""
        messages.success(self.request, 'Creado exitosamente')
        return super().form_valid(form)
```

---

## Estructura de Formulario Django

```python
# TEMPLATE BÁSICO

class MiForm(forms.ModelForm):
    """Formulario para modelo"""
    
    class Meta:
        model = Modelo
        fields = ['campo1', 'campo2', 'campo3']
        labels = {
            'campo1': 'Etiqueta personalizada',
        }
        widgets = {
            'campo1': forms.TextInput(attrs={'class': 'form-control'}),
            'campo2': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        """Inicializa formulario con datos dinámicos"""
        super().__init__(*args, **kwargs)
        self.user = user
        
        # Filtrar queryset según alcance
        self.fields['relacion'].queryset = Relacion.objects.filter(
            activo=True
        )
        
        # Agregar CSS a todos los campos
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
    
    def clean_campo1(self):
        """Validación simple de campo"""
        valor = self.cleaned_data.get('campo1')
        if valor and len(valor) < 3:
            raise ValidationError('Mínimo 3 caracteres')
        return valor
    
    def clean(self):
        """Validación cruzada"""
        cleaned_data = super().clean()
        campo1 = cleaned_data.get('campo1')
        campo2 = cleaned_data.get('campo2')
        
        # Validación de negocio
        if campo1 and campo2 and campo2 < campo1:
            raise ValidationError('Campo2 debe ser mayor que campo1')
        
        # Validación de alcance
        if not user_can_edit(self.user):
            raise ValidationError('No tienes permiso')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Personalizar guardado"""
        instance = super().save(commit=False)
        instance.user_id = self.user.id
        if commit:
            instance.save()
        return instance
```

---

## Patrón: Protección de Vistas

```python
# MIXIN ORDER MATTERS!

class ProtectedView(
    LoginRequiredMixin,          # 1. ¿Autenticado?
    RoleRequiredMixin,           # 2. ¿Rol permitido?
    ListView                     # 3. Lógica
):
    allowed_roles = ('rol1', 'rol2')
    
    def get_queryset(self):
        # 4. Filtra por alcance
        queryset = super().get_queryset()
        ids = get_visible_ids(self.request.user)
        if ids is not None:
            queryset = queryset.filter(id__in=ids)
        return queryset

# FLUJO DE EJECUCIÓN:
# 1. LoginRequiredMixin.dispatch() → ¿user.is_authenticated?
# 2. RoleRequiredMixin.dispatch() → ¿user.roles in allowed_roles?
# 3. Si OK → ListView.get()
# 4. get_queryset() con filtros
# 5. render_to_response() template
```

---

## Patrón: Validación de Negocio

```python
# FORM VALIDATION

class MiForm(forms.Form):
    campo = forms.IntegerField()
    
    def clean_campo(self):
        """Validación simple - por campo"""
        valor = self.cleaned_data['campo']
        if valor < 0:
            raise ValidationError('No puede ser negativo')
        return valor
    
    def clean(self):
        """Validación cruzada - múltiples campos"""
        cleaned = super().clean()
        
        # Validar relación entre campos
        if cleaned.get('fecha_inicio') > cleaned.get('fecha_fin'):
            raise ValidationError('Fecha inicio > fecha fin')
        
        # Validar regla de negocio
        if not regla_negocio_valida(cleaned):
            raise ValidationError('Violación de regla de negocio')
        
        return cleaned

# EN VISTA:
form = MiForm(data=request.POST)
if form.is_valid():
    # cleaned_data validado y limpio
    valor = form.cleaned_data['campo']
else:
    # form.errors dict con errores
    for field, errors in form.errors.items():
        print(f"{field}: {errors}")
```

---

## Patrón: Optimización de Queries

```python
# ANTES (N+1 problem)
grupos = Grupo.objects.all()
for grupo in grupos:
    print(grupo.profesor.usuario.nombre)  # Query por cada grupo!

# DESPUÉS (Optimizado)
grupos = Grupo.objects.select_related(
    'profesor',      # N:1
    'profesor__usuario'  # 1:1
)
for grupo in grupos:
    print(grupo.profesor.usuario.nombre)  # Sin queries adicionales

# ANOTACIONES
from django.db.models import Count, F

grupos = Grupo.objects.annotate(
    total_inscritos=Count('inscripciones'),
    cupos_restantes=F('cupo_maximo') - Count('inscripciones')
)
for grupo in grupos:
    print(f"{grupo.total_inscritos} inscritos")  # Dato en memory
```

---

## Checklist: Nuevo Endpoint

- [ ] Modelo: ¿Necesita nuevo modelo o actualizar existente?
- [ ] Migración: `makemigrations`, `migrate`
- [ ] Formulario: Crear forms.py con clean()
- [ ] Vista: Crear en views.py
  - [ ] Hereda de LoginRequiredMixin
  - [ ] Hereda de RoleRequiredMixin (si aplica)
  - [ ] Define allowed_roles
  - [ ] Implementa get_queryset() con filtros de alcance
- [ ] URL: Agregar en urls.py
- [ ] Template: Crear HTML en templates/
- [ ] Test: Escribir en tests/
- [ ] Lint: `ruff check`
- [ ] Format: `ruff format`
- [ ] Manual: Testear en navegador
- [ ] Commit: `git commit -m "Feat: ..."`

---

## Troubleshooting Rápido

| Problema | Solución |
|---|---|
| ImportError: No module | Verificar `settings.INSTALLED_APPS` |
| 403 Forbidden | Verificar CSRF token, roles, scope |
| N+1 queries | Agregar `select_related()`, `prefetch_related()` |
| Template error | Verificar context_object_name en vista |
| Form not valid | Ver `form.errors` en template |
| User not found | Verificar `USERNAME_FIELD = 'correo'` |
| Query slow | Usar `django-debug-toolbar` o `.query` |
| Migration conflict | Rebase o merge .py manualmente |
| BD connection | Verificar .env, PostgreSQL running |

---

## Recursos

```
Django Docs: https://docs.djangoproject.com/
PostgreSQL:   https://www.postgresql.org/docs/
Bootstrap:    https://getbootstrap.com/
pytest-django: https://pytest-django.readthedocs.io/

REPL COMMANDS:
>>> from django.core import management
>>> management.call_command('shell')
>>> from django.test.utils import setup_test_environment
>>> setup_test_environment()
```

---

## Roles y Acceso

```
ROLES:
- estudiante (mi programa)
- docente (mis grupos)
- coordinador (mi programa)
- decano (mi facultad)
- administrativo (mi facultad)
- superadmin (todo)

FUNCIONES CLAVE:
get_user_roles(user) → ['rol1', 'rol2', ...]
is_superadmin(user) → bool
get_visible_[type]_ids(user) → list | None

Si None → acceso total (superadmin)
Si list → filtrar por esos IDs
```

---

**Referencia rápida v1.0 - Junio 2, 2026**
