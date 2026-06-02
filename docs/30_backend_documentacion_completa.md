# Documentación Completa - Backend Django

**Sistema Distribuido de Gestión Académica Universitaria**

Última actualización: Junio 2, 2026

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura General](#arquitectura-general)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Configuración del Proyecto](#configuración-del-proyecto)
5. [Aplicaciones y Módulos](#aplicaciones-y-módulos)
6. [Modelo de Datos](#modelo-de-datos)
7. [Sistema de Autenticación y Roles](#sistema-de-autenticación-y-roles)
8. [Control de Acceso y Alcance de Datos](#control-de-acceso-y-alcance-de-datos)
9. [Flujos de Negocio Principales](#flujos-de-negocio-principales)
10. [API de Vistas](#api-de-vistas)
11. [Formularios y Validaciones](#formularios-y-validaciones)
12. [Servicios y Utilidades](#servicios-y-utilidades)
13. [Base de Datos](#base-de-datos)
14. [Instrucciones de Setup](#instrucciones-de-setup)
15. [Desarrollo y Testing](#desarrollo-y-testing)
16. [Decisiones Arquitectónicas](#decisiones-arquitectónicas)

---

## Resumen Ejecutivo

### Propósito

Sistema web universitario que gestiona procesos académicos completos: estructura institucional, ofertas académicas, inscripciones, calificaciones, financiamiento, homologaciones, indicadores de desempeño e integración con auditoría.

### Características Principales

- **Autenticación por email** con contraseña hasheada
- **6 roles funcionales** con alcance de datos personalizado
- **7 aplicaciones modulares** independientes
- **Base de datos PostgreSQL existente** integrada con Django
- **Templates Django + Bootstrap 5** con interfaz institucional
- **Modelos non-managed** (`managed=False`) para respetar DDL existente
- **Validaciones de reglas de negocio** en formularios
- **Indicadores académicos** calculados dinámicamente
- **Auditoría completa** para superadmin

### Números Clave

| Métrica | Valor |
|---|---|
| Aplicaciones | 7 |
| Modelos | 27+ |
| Roles | 6 |
| Endpoints | 50+ |
| Tablas PostgreSQL | 18 |
| Vistas basadas en clases | 40+ |
| Formularios personalizados | 8+ |

---

## Arquitectura General

### Diagrama de Capas

```
┌─────────────────────────────────────────┐
│         Frontend (Django Templates)     │
│     HTML + Bootstrap 5 + CSS + JS      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      Django URL Router (URLs)            │
│    Enrutamiento a vistas por módulo     │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       Vistas (Class-Based & FBV)        │
│   • Autenticación                       │
│   • Autorización (Mixins)               │
│   • Filtrado de datos por alcance       │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│    Formularios (Forms personalizados)    │
│   • Validación de reglas                │
│   • Cálculo de intento                  │
│   • Restricciones de acceso             │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│  Servicios (business logic)             │
│   • calculate_student_indicators()      │
│   • Validaciones complejas              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│    Django ORM (Models non-managed)      │
│    • Queries optimizadas                │
│    • select_related, prefetch_related   │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      PostgreSQL (BD Existente)          │
│   • 18 tablas relacionales              │
│   • Constraints y tipos específicos      │
└─────────────────────────────────────────┘
```

### Patrón de Seguridad

```
Usuario NO Autenticado
        ↓
    /login/
        ↓
    Email + Contraseña
        ↓
    CustomUser autenticada
        ↓
    Obtiene grupos (roles)
        ↓
    LoginRequiredMixin en vistas
        ↓
    RoleRequiredMixin según endpoint
        ↓
    Filtra datos con scope.py
        ↓
    Renderiza solo datos permitidos
```

---

## Stack Tecnológico

### Versiones y Dependencias

```toml
[core]
- Python >= 3.12
- Django >= 5.0, < 6.0
- PostgreSQL (psycopg[binary] >= 3.1)

[frontend]
- Django Templates
- Bootstrap 5
- CSS personalizado (condor.css)
- JavaScript vanilla (condor.js)

[database]
- psycopg[binary] >= 3.1
- django-environ >= 0.11
- Pillow >= 10.0 (para imágenes)

[development]
- pytest >= 8.0
- pytest-django >= 4.8
- pytest-cov >= 5.0
- ruff >= 0.11
- django-debug-toolbar >= 5.0

[package-management]
- uv (gestor de dependencias)
```

### Lenguaje y Estándares

- **Lenguaje**: Python 3.12+
- **Linter**: Ruff (E, F, I, UP, B, DJ)
- **Formato**: Ruff formatter (comillas dobles, 88 chars)
- **Testing**: pytest con Django
- **Cobertura**: pytest-cov

---

## Configuración del Proyecto

### Estructura de Directorios

```
backend/
├── config/                          # Configuración global Django
│   ├── settings.py                 # Variables y configuración
│   ├── urls.py                     # Rutas raíz
│   ├── wsgi.py                     # Producción
│   └── asgi.py                     # Async
├── apps/                           # 7 aplicaciones modulares
│   ├── accounts/                   # Autenticación
│   ├── estructura/                 # Institucional
│   ├── academica/                  # Académico
│   ├── financiera/                 # Financiero
│   ├── homologaciones/             # Convalidaciones
│   ├── indicadores/                # Análisis
│   └── auditoria/                  # Trazabilidad
├── templates/                      # HTML Django Templates
│   ├── base.html                   # Layout base
│   ├── 403.html, 404.html          # Errores
│   └── [app_name]/                 # Templates por app
├── static/                         # CSS, JS, imágenes
│   ├── css/condor.css
│   └── js/condor.js
├── media/                          # Archivos cargados
├── tests/                          # Tests del proyecto
├── manage.py                       # CLI Django
└── pyproject.toml                  # Configuración uv
```

### Archivo settings.py (Configuración)

```python
# BASE_DIR → ruta raíz del proyecto
# SECRET_KEY → clave secreta (variable .env)
# DEBUG → modo debug (variable .env)
# ALLOWED_HOSTS → hosts permitidos (variable .env)

# INSTALLED_APPS → 7 apps Django
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.accounts',          # Autenticación
    'apps.estructura',        # Institucional
    'apps.academica',         # Académico
    'apps.financiera',        # Financiero
    'apps.homologaciones',    # Convalidaciones
    'apps.indicadores',       # Análisis
    'apps.auditoria',         # Trazabilidad
]

# DATABASES → configuración PostgreSQL
# AUTH_USER_MODEL = 'accounts.CustomUser'
# LOGIN_URL = 'accounts:login'
# LANGUAGE_CODE = 'es-co'
# TIME_ZONE = 'America/Bogota'
```

### Variables de Entorno (.env)

```bash
# Seguridad
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
POSTGRES_DB=gestion_academica_local
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_SSLMODE=prefer
```

---

## Aplicaciones y Módulos

### 1. App: `accounts` (Autenticación y Control de Acceso)

**Responsabilidad**: Gestionar usuarios, autenticación, roles funcionales y control de acceso.

#### Archivos Principales

| Archivo | Responsabilidad |
|---|---|
| `models.py` | `CustomUser` - Usuario personalizado con email como ID |
| `managers.py` | `CustomUserManager` - Crear usuarios y superusuarios |
| `forms.py` | `EmailAuthenticationForm` - Formulario de login por email |
| `roles.py` | Definiciones de roles, funciones para obtener roles y opciones dashboard |
| `scope.py` | Funciones para filtrar datos según alcance del usuario |
| `access.py` | Mixins de protección por rol (`RoleRequiredMixin`) |
| `views.py` | Vistas: Login, Logout, Dashboard |
| `urls.py` | Rutas: /login/, /logout/, /dashboard/ |

#### Modelo CustomUser

```python
class CustomUser(AbstractBaseUser, PermissionsMixin):
    id_usuario: UUID                          # Primary key
    correo: str (unique)                      # Email único
    nombre: str                               # Nombre completo
    tipo_de_documento: str (CC, TI, CE)      # Tipo doc
    numero_de_documento: str                  # Número doc
    direccion: str                            # Dirección opcional
    is_staff: bool                            # Admin site
    is_active: bool                           # Activo
    date_joined: datetime                     # Fecha registro
    
    # Relaciones Django
    groups: ManyToMany                        # Roles funcionales
    user_permissions: ManyToMany
    
    USERNAME_FIELD = 'correo'                 # Email es el ID
    REQUIRED_FIELDS = ['nombre', 'tipo_de_documento', 'numero_de_documento']
    
    db_table = 'usuario'
    managed = False
```

#### Roles Funcionales

```python
FUNCTIONAL_ROLES = (
    'estudiante',       # Estudiante
    'docente',          # Profesor
    'coordinador',      # Coordinador de programa
    'decano',           # Decano de facultad
    'administrativo',   # Staff administrativo
    'superadmin',       # Superadministrador
)

ROLE_LABELS = {
    'estudiante': 'Estudiante',
    'docente': 'Docente',
    'coordinador': 'Coordinador',
    'decano': 'Decano',
    'administrativo': 'Administrativo',
    'superadmin': 'Superadmin',
}
```

#### Funciones de Roles (roles.py)

```python
def get_user_roles(user) -> list[str]
    # Retorna roles del usuario

def user_has_role(user, role) -> bool
    # Verifica si usuario tiene un rol

def get_role_labels(user) -> list[str]
    # Retorna nombres amigables de roles

def get_dashboard_options(user) -> list[dict]
    # Retorna opciones del dashboard según rol
    # Estructura: { 'title', 'description', 'url', 'role' }
```

#### Dashboard por Rol

**Estudiante**:
- Mis inscripciones
- Mi plan de estudios
- Mis recibos
- Mis homologaciones
- Mis indicadores

**Docente**:
- Grupos asignados
- Perfil docente
- Indicadores de estudiantes

**Coordinador**:
- Agregar estudiante
- Gestión del programa
- Oferta académica
- Indicadores del programa

**Decano**:
- Gestión de facultad
- Docentes
- Indicadores de facultad

**Administrativo**:
- Procesos financieros

**Superadmin**:
- Agregar estudiante
- Administración general
- Auditoría

#### Vistas (views.py)

```python
class EmailLoginView(LoginView):
    # POST /login/
    # Autentica por email y contraseña
    # Redirige a /dashboard/ si es exitoso
    
class EmailLogoutView(LogoutView):
    # GET /logout/
    # Cierra sesión
    # Redirige a /login/

@login_required
def dashboard(request):
    # GET /dashboard/
    # Renderiza dashboard según rol del usuario
    # Context: dashboard_options, role_labels, roles
```

#### Control de Acceso (access.py)

```python
class RoleRequiredMixin(AccessMixin):
    """Protege vistas requeriendo ciertos roles"""
    allowed_roles = ()
    
    def dispatch(self, request, *args, **kwargs):
        # Verifica que usuario tenga uno de los allowed_roles
        # Si no, redirige a dashboard con mensaje de error

# Constantes de roles permitidos por módulo
STRUCTURE_ROLES = ('coordinador', 'decano', 'superadmin')
FINANCIAL_ROLES = ('estudiante', 'coordinador', 'decano', 'administrativo', 'superadmin')
STUDENT_ROLES = ('estudiante', 'coordinador', 'decano', 'superadmin')
TEACHING_ROLES = ('docente', 'coordinador', 'decano', 'superadmin')
HOMOLOGATION_ROLES = ('estudiante', 'docente', 'coordinador', 'decano', 'superadmin')
INDICATOR_ROLES = ('estudiante', 'docente', 'coordinador', 'decano', 'superadmin')
AUDIT_ROLES = ('superadmin',)
```

#### Alcance de Datos (scope.py)

Funciones para obtener IDs permitidos según rol:

```python
def is_superadmin(user) -> bool
    # True si es superadmin

def get_student_for_user(user) -> Estudiante
    # Retorna estudiante del usuario

def get_professor_for_user(user) -> Profesor
    # Retorna profesor del usuario

def get_coordinated_program_ids(user) -> list[UUID]
    # Programas que coordina

def get_dean_faculty_ids(user) -> list[str]
    # Facultades donde es decano

def get_administrative_faculty_ids(user) -> list[str]
    # Facultades donde administra

def get_visible_program_ids(user) -> list[UUID] | None
    # Programas visibles (None = todos)

def get_visible_faculty_ids(user) -> list[str] | None
    # Facultades visibles (None = todas)

def get_visible_student_ids(user) -> list[UUID] | None
    # Estudiantes visibles (None = todos)

def get_visible_group_ids(user) -> list[UUID] | None
    # Grupos visibles (None = todos)
```

---

### 2. App: `estructura` (Estructura Institucional)

**Responsabilidad**: Gestionar facultades, programas académicos y periodos.

#### Modelos

```python
class Facultad:
    id_facultad: str (PK)
    nombre_facultad: str
    ubicacion: str
    correo_institucional: str (unique)

class ProgramaAcademico:
    id_programa_academico: str (PK)
    facultad: FK → Facultad
    nombre_programa: str
    estado: Choice (Activo, Inactivo)
    modalidad: Choice (Presencial, Virtual, Hibrida)
    nivel_formacion: Choice (Tecnico, Tecnologico, Pregrado, 
                            Especializacion, Maestria, Doctorado)

class PeriodoAcademico:
    id_periodo_academico: str (PK)
    fecha_inicio: date
    fecha_final: date
    estado: Choice (Planeado, Activo, Finalizado, Cancelado)
```

#### Vistas

```python
class FacultadListView(ListView):
    # GET /estructura/facultades/
    # Roles: coordinador, decano, superadmin
    # Filtra por alcance del usuario

class FacultadDetailView(DetailView):
    # GET /estructura/facultades/<id_facultad>/
    # Muestra detalles y programas

class ProgramaListView(ListView):
    # GET /estructura/programas/
    # Lista programas según alcance

class PeriodoAcademicoListView(ListView):
    # GET /estructura/periodos/
    # Lista periodos académicos
```

---

### 3. App: `academica` (Gestión Académica)

**Responsabilidad**: Gestionar asignaturas, planes, docentes, grupos, inscripciones y notas.

#### Modelos

```python
class Asignatura:
    cod_asignatura: str (PK)
    nombre_asignatura: str
    creditos: int
    estado: Choice (Activa, Inactiva)
    horas_teoria: int
    horas_pract: int
    homologable: bool

class ProgramaAsignatura:
    id_programa_asignatura: UUID (PK)
    programa_academico: FK → ProgramaAcademico
    asignatura: FK → Asignatura
    semestre_sugerido: int
    tipo_asignatura: Choice (Obligatoria, Electiva)
    estado: Choice (Activa, Inactiva)

class PreRequisito:
    id_pre_requisito: UUID (PK)
    programa_academico: FK → ProgramaAcademico
    programa_asignatura: FK → ProgramaAsignatura (depende)
    programa_asignatura_requisito: FK → ProgramaAsignatura (requisito)

class Estudiante:
    id_estudiante: UUID (PK)
    usuario: FK → CustomUser
    programa_academico: FK → ProgramaAcademico
    limite_matriculas: int (máximo de matriculas)
    estado_estudiante: str (Activo, Inactivo, Suspendido, Retirado, Egresado)

class Profesor:
    id_profesor: UUID (PK)
    usuario: FK → CustomUser
    facultad: FK → Facultad
    categoria: str (Auxiliar, Asistente, Asociado, etc.)
    vinculacion: str (TC, MT, C, etc.)

class Decano:
    id_decano: UUID (PK)
    profesor: FK → Profesor
    periodo_academico: FK → PeriodoAcademico
    facultad: FK → Facultad

class Coordinador:
    id_coordinador: UUID (PK)
    profesor: FK → Profesor
    periodo_academico: FK → PeriodoAcademico
    programa_academico: FK → ProgramaAcademico

class Grupo:
    id_grupo: UUID (PK)
    programa_asignatura: FK → ProgramaAsignatura
    periodo_academico: FK → PeriodoAcademico
    profesor: FK → Profesor (nullable)
    codigo_grupo: str
    cupo_maximo: int
    estado_grupo: Choice (Abierto, En curso, Finalizado, Cancelado)

class Inscripcion:
    id_inscripcion: UUID (PK)
    grupo: FK → Grupo
    estudiante: FK → Estudiante
    nota1: Decimal (nullable)
    nota2: Decimal (nullable)
    nota3: Decimal (nullable)
    nota_final: Decimal (nullable)
    intento: int (número de intento)
    estado_inscripcion: Choice (Cursando, Aprobada, Reprobada, Cancelada)
```

#### Formularios

**EstudianteCreateForm**:
```python
# Campos
nombre, correo, tipo_de_documento, numero_de_documento
direccion, programa_academico, limite_matriculas, estado_estudiante

# Validaciones
- Correo único
- Documento tipo + número único
- Programa dentro del alcance del usuario
- Solo coordinador o superadmin puede crear

# Save
- Crea CustomUser con password 'Demo12345*'
- Agrega grupo 'estudiante'
- Crea Estudiante en BD
```

**InscripcionCreateForm**:
```python
# Campos
estudiante (optional si usuario es docente/coordinador)
grupo

# Validaciones
- Grupo abierto o en curso
- Sin inscripción duplicada en grupo
- Sin inscripción duplicada asignatura-periodo
- Cupo disponible
- Matrícula activa para estudiante
- Estudiante dentro del alcance del usuario

# Save
- Calcula intento (intento anterior + 1, o 1)
- Crea Inscripcion (estado='Cursando')
```

**NotaInscripcionForm**:
```python
# Campo
nota1, nota2, nota3, estado_inscripcion

# Validaciones
- Notas entre 0 y 5
- Usuario es docente del grupo o superadmin
- Inscripción no cancelada

# Save
- Actualiza notas
- Calcula nota_final = promedio(nota1, nota2, nota3)
- Actualiza estado
```

#### Vistas Principales

```python
class AsignaturaListView(ListView):
    # GET /academica/asignaturas/
    # Roles: estudiante, docente, coordinador, decano, superadmin
    # Filtra por programa del usuario

class AsignaturaDetailView(DetailView):
    # GET /academica/asignaturas/<cod_asignatura>/

class PlanEstudiosListView(ListView):
    # GET /academica/planes/
    # ProgramaAsignatura del programa del usuario

class PreRequisitoListView(ListView):
    # GET /academica/prerrequisitos/
    # Roles: coordinador, decano, superadmin

class ProfesorListView(ListView):
    # GET /academica/docentes/
    # Roles: docente, coordinador, decano, superadmin
    # Prefetch: decanaturas, coordinaciones, grupos

class ProfesorDetailView(DetailView):
    # GET /academica/docentes/<id_profesor>/
    # Detalle del profesor con sus cargos

class EstudianteCreateView(CreateView):
    # GET /academica/estudiantes/agregar/
    # POST con EstudianteCreateForm
    # Roles: coordinador, superadmin

class GrupoListView(ListView):
    # GET /academica/grupos/
    # Roles: docente, coordinador, decano, superadmin
    # Anota: total_inscritos, cupos_disponibles

class GrupoDetailView(DetailView):
    # GET /academica/grupos/<id_grupo>/
    # Prefetch: inscripciones

class InscripcionListView(ListView):
    # GET /academica/inscripciones/
    # Filtra según rol del usuario

class InscripcionCreateView(CreateView):
    # GET /academica/inscripciones/crear/
    # POST con InscripcionCreateForm
    # Roles: estudiante, coordinador, decano, superadmin

class InscripcionCancelView(View):
    # POST /academica/inscripciones/<id_inscripcion>/cancelar/
    # Cambia estado a Cancelada (solo superadmin o si es estudiante propio)

class NotaGrupoListView(ListView):
    # GET /academica/notas/
    # Grupos donde usuario es profesor o superadmin

class NotaGrupoDetailView(DetailView):
    # GET /academica/notas/grupos/<id_grupo>/
    # Inscripciones del grupo

class NotaInscripcionUpdateView(UpdateView):
    # GET /academica/notas/inscripciones/<id_inscripcion>/editar/
    # POST con NotaInscripcionForm
    # Roles: docente (si es profesor del grupo), superadmin
```

---

### 4. App: `financiera` (Gestión Financiera)

**Responsabilidad**: Gestionar tarifas, recibos y matrículas.

#### Modelos

```python
class TarifaMatricula:
    id_tarifa_matricula: UUID (PK)
    programa_academico: FK → ProgramaAcademico
    periodo_academico: FK → PeriodoAcademico
    valor_matricula: Decimal
    fecha_limite_ordinaria: date
    fecha_limite_extraordinaria: date
    estado: Choice (Activa, Inactiva)

class Recibo:
    id_recibo: UUID (PK)
    estudiante: FK → Estudiante
    tarifa_matricula: FK → TarifaMatricula
    fecha_pago: date (nullable)
    valor_pagado: Decimal (nullable)
    metodo_pago: Choice (Efectivo, Tarjeta, PSE, Transferencia, Consignacion)
    estado_pago: Choice (Pendiente, Pagado, Vencido, Anulado)
    extras: Decimal (default=0)

class Matricula:
    id_matricula: UUID (PK)
    recibo: OneToOne → Recibo
    estado_matricula: Choice (Pendiente, Activa, Finalizada, Cancelada, Anulada)
```

#### Formularios

**TarifaMatriculaForm**:
```python
# Campos
programa_academico, periodo_academico, valor_matricula
fecha_limite_ordinaria, fecha_limite_extraordinaria, estado

# Validaciones
- Valor no negativo
- Fecha extraordinaria >= ordinaria
- No duplicidad programa + periodo

# Restricción
- Solo administrativo o superadmin
```

**ReciboForm**:
```python
# Campos
estudiante, tarifa_matricula, fecha_pago
valor_pagado, metodo_pago, estado_pago, extras

# Validaciones
- Estudiante dentro del alcance del usuario
- Tarifa dentro del alcance del usuario
```

**MatriculaCreateForm**:
```python
# Campos
recibo

# Validaciones
- Estudiante no excede límite de matrículas
- Recibo existe y pertenece al estudiante
```

#### Vistas

```python
class TarifaMatriculaListView(ListView):
    # GET /financiera/tarifas/
    # Roles: estudiante, coordinador, decano, administrativo, superadmin

class TarifaMatriculaCreateView(CreateView):
    # GET /financiera/tarifas/crear/
    # POST con TarifaMatriculaForm
    # Roles: administrativo, superadmin

class TarifaMatriculaUpdateView(UpdateView):
    # GET /financiera/tarifas/<id>/editar/
    # POST

class TarifaMatriculaToggleEstadoView(View):
    # POST /financiera/tarifas/<id>/cambiar-estado/
    # Cambia entre Activa e Inactiva

class ReciboListView(ListView):
    # GET /financiera/recibos/
    # Filtra por estudiante según alcance

class ReciboDetailView(DetailView):
    # GET /financiera/recibos/<id>/

class ReciboCreateView(CreateView):
    # GET /financiera/recibos/crear/
    # POST con ReciboForm

class ReciboUpdateView(UpdateView):
    # GET /financiera/recibos/<id>/editar/

class ReciboAnularView(View):
    # POST /financiera/recibos/<id>/anular/
    # Cambia estado a Anulado

class MatriculaListView(ListView):
    # GET /financiera/matriculas/

class MatriculaCreateView(CreateView):
    # GET /financiera/matriculas/crear/
    # POST con MatriculaCreateForm

class MatriculaActivarView(View):
    # POST /financiera/matriculas/<id>/activar/
    # estado_matricula = Activa

class MatriculaFinalizarView(View):
    # POST /financiera/matriculas/<id>/finalizar/
    # estado_matricula = Finalizada

class MatriculaCancelarView(View):
    # POST /financiera/matriculas/<id>/cancelar/
    # estado_matricula = Cancelada

class MatriculaAnularView(View):
    # POST /financiera/matriculas/<id>/anular/
    # estado_matricula = Anulada
```

---

### 5. App: `homologaciones` (Convalidación de Asignaturas)

**Responsabilidad**: Gestionar solicitudes de homologación (convalidación).

#### Modelo

```python
class Homologacion:
    id_homologacion: UUID (PK)
    profesor_evaluador: FK → Profesor
    estudiante: FK → Estudiante
    asignatura_origen: str (nombre de origen)
    institucion_origen: str
    programa_asignatura: FK → ProgramaAsignatura
    fecha_solicitud: date
    estado_homologacion: Choice (Solicitada, En revision, Aprobada, Rechazada, Cancelada)
    observacion: str (nullable)
    fecha_respuesta: date (nullable)
    nota_obtenida: Decimal (nullable)
```

#### Formularios

**HomologacionSolicitudForm**:
```python
# Campos
asignatura_origen, institucion_origen, programa_asignatura, observacion

# Validaciones
- Usuario es estudiante
- ProgramaAsignatura es homologable
- ProgramaAsignatura es del programa del estudiante
```

**HomologacionAsignarEvaluadorForm**:
```python
# Campos
profesor_evaluador

# Validaciones
- Profesor es de la misma facultad/programa que la asignatura
- Estado es Solicitada o En revision
```

**HomologacionEvaluarForm**:
```python
# Campos
nota_obtenida, estado_homologacion, observacion

# Validaciones
- Usuario es el profesor evaluador
- Nota entre 0 y 5
- Estado es Aprobada o Rechazada
```

#### Vistas

```python
class HomologacionListView(ListView):
    # GET /homologaciones/
    # Filtra según rol del usuario

class HomologacionDetailView(DetailView):
    # GET /homologaciones/<id>/
    # Muestra opciones de acción según estado y rol

class HomologacionCreateView(CreateView):
    # GET /homologaciones/crear/
    # POST con HomologacionSolicitudForm
    # Solo estudiantes

class HomologacionAssignEvaluatorView(UpdateView):
    # GET /homologaciones/<id>/asignar-evaluador/
    # POST
    # Coordinador o superadmin

class HomologacionEvaluateView(UpdateView):
    # GET /homologaciones/<id>/evaluar/
    # POST
    # Docente evaluador o superadmin

class HomologacionCancelView(View):
    # POST /homologaciones/<id>/cancelar/
    # Solo estudiante si estado=Solicitada
```

---

### 6. App: `indicadores` (Indicadores Académicos)

**Responsabilidad**: Calcular y mostrar indicadores de desempeño estudiantil.

#### Servicios

```python
def calculate_student_indicators(student) -> dict:
    """
    Calcula indicadores de un estudiante:
    
    Retorna dict con:
    - student: Estudiante
    - total_subjects: int (asignaturas del programa)
    - approved_subjects: int (aprobadas)
    - missing_subjects: int (faltantes)
    - academic_progress: Decimal (0-100)
    - weighted_average: Decimal (0-5)
    - performance_percentage: Decimal (0-100)
    - failed_subjects: int (reprobadas)
    - has_high_attempt: bool (intento >= 3)
    - risk_score: int (0-100)
    - risk_label: str (Bajo, Medio, Alto)
    - has_enough_data: bool
    """
    # Lógica:
    # 1. Obtiene todas las asignaturas del programa
    # 2. Cuenta aprobadas (inscripciones + homologaciones)
    # 3. Calcula promedio ponderado por créditos
    # 4. Cuenta reprobadas
    # 5. Calcula riesgo según criterios
```

**Criterios de Riesgo**:
- Promedio < 3.2: +30 puntos
- Reprobadas >= 3: +25 puntos
- Avance < 40%: +20 puntos
- Estado (Inactivo, Suspendido, Retirado): +25 puntos
- Intento >= 3: +20 puntos
- **Total máximo**: 100 puntos

**Niveles de Riesgo**:
- Bajo: score <= 30
- Medio: score <= 60
- Alto: score > 60

#### Vistas

```python
class IndicadorListView(ListView):
    # GET /indicadores/
    # Roles: estudiante, docente, coordinador, decano, superadmin
    # Lista estudiantes con indicadores calculados

class MiIndicadorView(DetailView):
    # GET /indicadores/mis-indicadores/
    # Solo para estudiantes
    # Muestra sus propios indicadores

class IndicadorDetailView(DetailView):
    # GET /indicadores/estudiantes/<id_estudiante>/
    # Detalle del estudiante con indicadores
```

---

### 7. App: `auditoria` (Auditoría)

**Responsabilidad**: Registrar y consultar acciones del sistema.

#### Modelo

```python
class Auditoria:
    id_auditoria: UUID (PK)
    usuario: FK → CustomUser
    accion_realizada: str
    fecha_hora: datetime
    descripcion: str (nullable)
```

#### Vistas

```python
class AuditoriaListView(ListView):
    # GET /auditoria/
    # Solo superadmin
    # Lista registros ordenados por fecha

class AuditoriaDetailView(DetailView):
    # GET /auditoria/<id>/
    # Detalle de un registro
```

---

## Modelo de Datos

### Relaciones Principales

```
CustomUser (usuario)
    ├── Estudiante (1:1) → programa_academico → ProgramaAcademico
    ├── Profesor (1:1) → facultad → Facultad
    │   ├── Decano (1:N) → facultad, periodo_academico
    │   ├── Coordinador (1:N) → programa_academico, periodo_academico
    │   └── Grupo (1:N) → programa_asignatura, periodo_academico
    │       └── Inscripcion (1:N) → estudiante, grupo
    │           └── Nota (en Inscripcion)
    ├── Homologacion (evaluador)
    └── Auditoria (usuario_que_actúa)

ProgramaAcademico
    ├── Facultad (N:1)
    ├── ProgramaAsignatura (1:N)
    │   ├── Asignatura (N:1)
    │   ├── Grupo (1:N)
    │   │   └── Inscripcion (1:N)
    │   ├── PreRequisito (1:N) dependencias
    │   └── Homologacion (1:N)
    ├── TarifaMatricula (1:N)
    │   └── Recibo (1:N)
    │       └── Matricula (1:1)
    └── Coordinador (1:N) → profesor

PeriodoAcademico
    ├── Grupo (1:N)
    ├── TarifaMatricula (1:N)
    ├── Decano (1:N)
    └── Coordinador (1:N)
```

### Tabla de Entidades

| Entidad | Tabla | Registros | Relaciones Clave |
|---|---|---|---|
| Facultad | facultad | 5+ | ← ProgramaAcademico |
| ProgramaAcademico | programa_academico | 30+ | ← Estudiante, Grupo |
| PeriodoAcademico | periodo_academico | 10+ | ← Grupo, Inscripcion |
| Asignatura | asignatura | 100+ | ← ProgramaAsignatura |
| ProgramaAsignatura | programa_asignatura | 300+ | ← Grupo, PreRequisito |
| PreRequisito | pre_requisito | 200+ | → ProgramaAsignatura |
| CustomUser | usuario | 100+ | ← Estudiante, Profesor |
| Estudiante | estudiante | 50+ | → usuario, ProgramaAcademico |
| Profesor | profesor | 20+ | → usuario, Facultad |
| Coordinador | coordinador | 30+ | → Profesor, ProgramaAcademico |
| Decano | decano | 5+ | → Profesor, Facultad |
| Grupo | grupo | 150+ | → ProgramaAsignatura, Profesor |
| Inscripcion | inscripcion | 500+ | → Estudiante, Grupo |
| TarifaMatricula | tarifa_matricula | 30+ | → ProgramaAcademico |
| Recibo | recibo | 100+ | → Estudiante, TarifaMatricula |
| Matricula | matricula | 50+ | → Recibo |
| Homologacion | homologacion | 50+ | → Estudiante, Profesor |
| Auditoria | auditoria | 1000+ | → usuario |

---

## Sistema de Autenticación y Roles

### Flujo de Autenticación

```
1. Usuario abre /login/
   ↓
2. Completa email + contraseña
   ↓
3. Django autentica contra CustomUser
   ↓
4. Si es válido:
   - Crea sesión
   - Obtiene grupos (roles funcionales)
   - Redirige a /dashboard/
   ↓
5. Si no es válido:
   - Muestra error en /login/
```

### Estructura de Permisos

**Por roles funcionales (Django Groups)**:
- estudiante
- docente
- coordinador
- decano
- administrativo
- superadmin

**Sistema de Protección**:
1. `LoginRequiredMixin` - Usuario debe estar autenticado
2. `RoleRequiredMixin` - Usuario debe tener rol permitido
3. Filtros en `scope.py` - Datos filtrados por alcance

### Alcance de Datos por Rol

| Rol | Alcance | Vistas Permitidas |
|---|---|---|
| Estudiante | Su programa, sus inscripciones, sus recibos | Mi plan, Mis materias, Mis notas |
| Docente | Sus grupos y estudiantes | Mis grupos, Calificar, Evaluar homologación |
| Coordinador | Su programa | Programa, Inscripciones, Homologación |
| Decano | Su facultad | Facultad, Programas, Docentes, Indicadores |
| Administrativo | Su facultad | Tarifas, Recibos, Matrículas |
| Superadmin | Todo | Acceso total |

---

## Control de Acceso y Alcance de Datos

### Funciones de Alcance (scope.py)

Cada función retorna:
- `None` → acceso a todos los registros (superadmin)
- `list[ID]` → acceso solo a esos IDs
- Filtra automáticamente en querysets

```python
# Ejemplos de uso en vistas
def get_queryset(self):
    faculty_ids = get_visible_faculty_ids(self.request.user)
    queryset = Facultad.objects.all()
    if faculty_ids is None:
        return queryset  # Acceso total
    return queryset.filter(id_facultad__in=faculty_ids)  # Filtrado
```

### Patrón de Filtrado

```python
# En ListView o DetailView
queryset = Modelo.objects.all()
ids = get_visible_[type]_ids(user)  # Obtiene IDs permitidos
if ids is not None:
    queryset = queryset.filter(id__in=ids)  # Filtra
```

### Optimizaciones de Query

```python
# Usando select_related (1:1, N:1)
queryset = Profesor.objects.select_related('usuario', 'facultad')

# Usando prefetch_related (1:N, M:N)
queryset = Profesor.objects.prefetch_related(
    Prefetch('grupos', queryset=Grupo.objects.select_related(...))
)

# Usando annotate (agregaciones)
queryset = Grupo.objects.annotate(
    total_inscritos=Count('inscripciones'),
    cupos_disponibles=F('cupo_maximo') - F('total_inscritos')
)
```

---

## Flujos de Negocio Principales

### Flujo 1: Crear Inscripción

```
Estudiante/Coordinador abre /academica/inscripciones/crear/
        ↓
Completa formulario (grupo, estudiante opcional)
        ↓
InscripcionCreateForm.clean():
    - Verifica grupo activo (Abierto o En curso)
    - Verifica no duplicidad en grupo
    - Verifica no duplicidad asignatura-periodo
    - Verifica cupo disponible
    - Verifica matrícula activa del estudiante
        ↓
Si todo OK:
    - Calcula intento = max(intentos anteriores) + 1
    - Crea Inscripcion(estado='Cursando')
        ↓
Redirige a /academica/inscripciones/ con mensaje de éxito
```

### Flujo 2: Registrar Nota

```
Docente abre /academica/notas/grupos/<id_grupo>/
        ↓
Ve lista de inscripciones del grupo
        ↓
Docente hace clic en "Editar nota" de una inscripción
        ↓
Abre /academica/notas/inscripciones/<id>/editar/
        ↓
Completa formulario (nota1, nota2, nota3, estado)
        ↓
NotaInscripcionForm.clean():
    - Verifica que usuario es profesor del grupo
    - Verifica notas entre 0 y 5
    - Verifica inscripción no cancelada
        ↓
Si todo OK:
    - Calcula nota_final = (nota1 + nota2 + nota3) / 3
    - Si nota_final >= 3.0: estado = 'Aprobada'
    - Si nota_final < 3.0: estado = 'Reprobada'
    - Actualiza Inscripcion
        ↓
Redirige con mensaje de éxito
```

### Flujo 3: Crear Homologación

```
Estudiante abre /homologaciones/crear/
        ↓
Completa formulario (asignatura_origen, institucion, programa_asignatura)
        ↓
HomologacionSolicitudForm.clean():
    - Verifica usuario es estudiante
    - Verifica ProgramaAsignatura es homologable
    - Verifica es del programa del estudiante
        ↓
Si todo OK:
    - Selecciona profesor_evaluador (automático o manual)
    - Crea Homologacion(estado='Solicitada')
        ↓
Coordinador ve en listado
        ↓
Coordinador abre /homologaciones/<id>/asignar-evaluador/
        ↓
Cambia profesor_evaluador
    - Estado → 'En revision'
        ↓
Profesor evaluador ve en su listado
        ↓
Abre /homologaciones/<id>/evaluar/
        ↓
Registra nota_obtenida y observacion
    - Si nota >= 3.0: estado = 'Aprobada'
    - Si nota < 3.0: estado = 'Rechazada'
        ↓
Proceso finalizado
```

### Flujo 4: Calcular Indicadores

```
Usuario abre /indicadores/
        ↓
Sistema obtiene estudiantes en su alcance
        ↓
Para cada estudiante:
    - Obtiene asignaturas del programa
    - Cuenta aprobadas (inscripciones + homologaciones)
    - Calcula promedio ponderado
    - Cuenta reprobadas
    - Calcula risk_score según criterios
        ↓
Renderiza tabla con indicadores
```

---

## API de Vistas

### Vistas por App

#### accounts (3 vistas)
- `EmailLoginView` - POST /login/
- `EmailLogoutView` - GET /logout/
- `dashboard` - GET /dashboard/

#### estructura (4 vistas)
- `FacultadListView` - GET /estructura/facultades/
- `FacultadDetailView` - GET /estructura/facultades/<id>/
- `ProgramaListView` - GET /estructura/programas/
- `PeriodoAcademicoListView` - GET /estructura/periodos/

#### academica (14 vistas)
- `AsignaturaListView` - GET /academica/asignaturas/
- `AsignaturaDetailView` - GET /academica/asignaturas/<id>/
- `PlanEstudiosListView` - GET /academica/planes/
- `PreRequisitoListView` - GET /academica/prerrequisitos/
- `ProfesorListView` - GET /academica/docentes/
- `ProfesorDetailView` - GET /academica/docentes/<id>/
- `EstudianteCreateView` - GET/POST /academica/estudiantes/agregar/
- `GrupoListView` - GET /academica/grupos/
- `GrupoDetailView` - GET /academica/grupos/<id>/
- `InscripcionListView` - GET /academica/inscripciones/
- `InscripcionCreateView` - GET/POST /academica/inscripciones/crear/
- `InscripcionCancelView` - POST /academica/inscripciones/<id>/cancelar/
- `NotaGrupoListView` - GET /academica/notas/
- `NotaGrupoDetailView` - GET /academica/notas/grupos/<id>/
- `NotaInscripcionUpdateView` - GET/POST /academica/notas/inscripciones/<id>/editar/

#### financiera (13 vistas)
- `TarifaMatriculaListView` - GET /financiera/tarifas/
- `TarifaMatriculaCreateView` - GET/POST /financiera/tarifas/crear/
- `TarifaMatriculaUpdateView` - GET/POST /financiera/tarifas/<id>/editar/
- `TarifaMatriculaToggleEstadoView` - POST /financiera/tarifas/<id>/cambiar-estado/
- `ReciboListView` - GET /financiera/recibos/
- `ReciboDetailView` - GET /financiera/recibos/<id>/
- `ReciboCreateView` - GET/POST /financiera/recibos/crear/
- `ReciboUpdateView` - GET/POST /financiera/recibos/<id>/editar/
- `ReciboAnularView` - POST /financiera/recibos/<id>/anular/
- `MatriculaListView` - GET /financiera/matriculas/
- `MatriculaCreateView` - GET/POST /financiera/matriculas/crear/
- `MatriculaDetailView` - GET /financiera/matriculas/<id>/
- Cambios de estado: Activar, Finalizar, Cancelar, Anular

#### homologaciones (6 vistas)
- `HomologacionListView` - GET /homologaciones/
- `HomologacionDetailView` - GET /homologaciones/<id>/
- `HomologacionCreateView` - GET/POST /homologaciones/crear/
- `HomologacionAssignEvaluatorView` - GET/POST /homologaciones/<id>/asignar-evaluador/
- `HomologacionEvaluateView` - GET/POST /homologaciones/<id>/evaluar/
- `HomologacionCancelView` - POST /homologaciones/<id>/cancelar/

#### indicadores (3 vistas)
- `IndicadorListView` - GET /indicadores/
- `MiIndicadorView` - GET /indicadores/mis-indicadores/
- `IndicadorDetailView` - GET /indicadores/estudiantes/<id>/

#### auditoria (2 vistas)
- `AuditoriaListView` - GET /auditoria/
- `AuditoriaDetailView` - GET /auditoria/<id>/

**Total: 50+ vistas**

---

## Formularios y Validaciones

### Categorías de Formularios

#### Formularios de Usuario
- `EmailAuthenticationForm` - Login por email
- `EstudianteCreateForm` - Crear estudiante

#### Formularios Académicos
- `InscripcionCreateForm` - Crear inscripción
- `NotaInscripcionForm` - Registrar nota

#### Formularios Financieros
- `TarifaMatriculaForm` - Tarifa de matrícula
- `ReciboForm` - Recibo
- `MatriculaCreateForm` - Crear matrícula

#### Formularios de Homologación
- `HomologacionSolicitudForm` - Crear solicitud
- `HomologacionAsignarEvaluadorForm` - Asignar profesor
- `HomologacionEvaluarForm` - Evaluar solicitud

### Validaciones Comunes

```python
# Validación de alcance
if not user_can_create_students(user):
    raise ValidationError("No tienes permisos")

# Validación de duplicidad
if Model.objects.filter(field1=val1, field2=val2).exists():
    raise ValidationError("Ya existe un registro similar")

# Validación de rango
if value < 0 or value > 5:
    raise ValidationError("Valor fuera de rango")

# Validación de fechas
if fecha_fin < fecha_inicio:
    raise ValidationError("Fecha final debe ser posterior")
```

---

## Servicios y Utilidades

### Modulo: indicadores.services

```python
def _round_decimal(value, places=2) -> Decimal
    # Redondea decimal a N decimales

def _risk_label(score) -> str
    # Retorna 'Bajo', 'Medio', o 'Alto' según score

def calculate_student_indicators(student) -> dict
    # Calcula todos los indicadores del estudiante
```

### Modulo: accounts.scope

Funciones para obtener IDs permitidos:

```python
is_superadmin(user) -> bool
get_student_for_user(user) -> Estudiante | None
get_professor_for_user(user) -> Profesor | None
get_coordinated_program_ids(user) -> list[UUID]
get_dean_faculty_ids(user) -> list[str]
get_administrative_faculty_ids(user) -> list[str]
get_visible_program_ids(user, include_student, include_teacher) -> list[UUID] | None
get_visible_faculty_ids(user) -> list[str] | None
get_visible_student_ids(user) -> list[UUID] | None
get_visible_group_ids(user) -> list[UUID] | None
get_visible_professor_ids(user) -> list[UUID] | None
```

### Funciones de Validación

```python
# academica
def user_can_write_enrollments(user) -> bool
def user_can_create_students(user) -> bool

# financiera
def user_can_manage_financial(user) -> bool
def get_financial_program_ids(user) -> list[UUID] | None
def validate_matricula_limit(estudiante) -> None

# homologaciones
def _professors_for_program(program_id) -> QuerySet
def _default_evaluator_for_program_assignment(prog_asig) -> Profesor
```

---

## Base de Datos

### Configuración PostgreSQL

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
        'OPTIONS': {
            'sslmode': env('POSTGRES_SSLMODE'),
        },
    }
}
```

### Modelos Non-Managed

```python
class Meta:
    db_table = 'tabla_existente'
    managed = False  # Django no genera migraciones para esta tabla
```

**Ventajas**:
- Respeta estructura existente
- No modifica DDL
- Compatible con scripts SQL

**Desventajas**:
- No genera migraciones automáticas
- Cambios en BD requieren migraciones manuales

### Características de Indexed

- Primary keys (UUID)
- Foreign keys automáticamente indexados
- Ordenamientos en Meta.ordering
- Campos únicos (unique=True)

### Transacciones

```python
from django.db import transaction

@transaction.atomic
def save(self):
    # Operaciones múltiples atómicas
    user = CustomUser.objects.create(...)
    user.groups.add(...)
    return Estudiante.objects.create(...)
```

---

## Instrucciones de Setup

### Requisitos Previos

- Python 3.12+
- PostgreSQL 12+
- `uv` gestor de paquetes
- Git

### 1. Clonar Repositorio

```bash
cd /ruta/del/proyecto
git clone <repo-url>
```

### 2. Instalar Dependencias

```bash
# Con uv
uv sync

# O con pip tradicional
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Crear `.env` en raíz del proyecto:

```env
DJANGO_SECRET_KEY=change-me-in-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=gestion_academica_local
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_SSLMODE=prefer
```

### 4. Preparar Base de Datos

Ejecutar scripts SQL en orden:

```bash
# En DBeaver o psql
01_ddl.sql
02_inserts_catalogos.sql
03_inserts_operativos.sql
```

### 5. Migraciones Django

```bash
# Crear migraciones (si necesarias)
uv run python backend/manage.py makemigrations

# Aplicar migraciones
uv run python backend/manage.py migrate

# Crear tablas M2M de Django
# Ejecutar 09_auth_user_m2m_tables.sql

# Crear grupos funcionales
uv run python backend/manage.py setup_functional_groups

# Crear usuarios demo
uv run python backend/manage.py seed_demo_users
```

### 6. Ejecutar Servidor

```bash
uv run python backend/manage.py runserver
```

Acceder a `http://127.0.0.1:8000/login/`

### 7. Credenciales Demo

```
Contraseña: Demo12345*

Usuarios:
- claudia.benitez@universidad.edu (Superadmin)
- sofia.herrera@universidad.edu (Estudiante)
- carolina.vargas@universidad.edu (Docente)
- miguel.rojas@universidad.edu (Coordinador)
- laura.perez@universidad.edu (Decano)
- hector.suarez@universidad.edu (Administrativo)
```

---

## Desarrollo y Testing

### Comandos Útiles

```bash
# Verificar configuración
uv run python backend/manage.py check

# Ver migraciones
uv run python backend/manage.py showmigrations

# Crear superusuario
uv run python backend/manage.py createsuperuser

# Ejecutar tests
uv run pytest

# Ver cobertura
uv run pytest --cov=backend/apps

# Linting
uv run ruff check backend/apps backend/config

# Formatear código
uv run ruff format backend/apps backend/config

# Shell interactivo
uv run python backend/manage.py shell
```

### Estructura de Tests

```
backend/tests/
├── test_project_setup.py
└── (otros tests por app)
```

### Ejecutar Tests

```bash
# Todos los tests
uv run pytest

# Tests de una app
uv run pytest backend/apps/academica/

# Tests con patrón
uv run pytest -k "inscripcion"

# Con cobertura
uv run pytest --cov=backend/apps --cov-report=html
```

### Mejores Prácticas

1. **Usar fixtures**: Define datos reutilizables
2. **Test por caso de uso**: No solo por modelo
3. **Mocking externo**: BD simulada en tests
4. **Nombres descriptivos**: `test_user_cannot_create_students_without_role`

---

## Decisiones Arquitectónicas

### 1. Modelos Non-Managed (`managed=False`)

**Decisión**: Respetar BD existente en PostgreSQL.

**Razón**:
- BD ya existe con restricciones complejas
- Evita conflictos con migraciones
- Fácil rollback
- Documentación existente válida

**Trade-offs**:
- Las migraciones deben ser manuales
- Cambios en BD requieren sincronización

### 2. Autenticación por Email

**Decisión**: Usar email como USERNAME_FIELD en CustomUser.

**Razón**:
- Más amigable que ID numérico
- Integración con universidades (emails institucionales)
- Único por diseño

**Implementación**:
```python
USERNAME_FIELD = 'correo'
```

### 3. Roles mediante Django Groups

**Decisión**: Usar Groups de Django para roles funcionales.

**Razón**:
- Integración nativa con Django
- Gestión simplificada
- Escalable

**Roles**: 6 grupos funcionales (estudiante, docente, coordinador, decano, administrativo, superadmin)

### 4. Control de Acceso: Mixins + scope.py

**Decisión**: Combinar LoginRequiredMixin + RoleRequiredMixin + filtros en scope.py.

**Razón**:
- Separación de concerns
- Reutilizable
- Fácil de testear

**Capas**:
1. `LoginRequiredMixin` - Autenticación
2. `RoleRequiredMixin` - Autorización por rol
3. `scope.py` - Filtrado por alcance de datos

### 5. Vistas Basadas en Clases (CBV)

**Decisión**: Usar Class-Based Views sobre Function-Based Views.

**Razón**:
- Reutilización de código (Mixins)
- Menos código repetitivo
- Mejor para CRUD

**Complemento**: Usar FBV para lógica especial (dashboard).

### 6. Servicios Separados (services.py)

**Decisión**: Lógica compleja en services.py, no en vistas.

**Razón**:
- Vistas delgadas
- Lógica reutilizable
- Fácil de testear

**Ejemplo**: `calculate_student_indicators()` en indicadores.services

### 7. Validaciones en Formularios

**Decisión**: Validaciones de regla de negocio en formularios, no en modelos.

**Razón**:
- Feedback inmediato al usuario
- Mejor UX
- Menor carga en BD

**Cobertura**:
- clean_<field>() para validaciones simples
- clean() para validaciones cruzadas
- Alcance de datos verificado

### 8. Optimizaciones de Query

**Decisión**: Usar select_related(), prefetch_related() y annotate().

**Razón**:
- Reduce queries N+1
- Mejor performance
- Menos latencia BD

**Ejemplos**:
```python
# 1:1, N:1 → select_related
.select_related('usuario', 'facultad')

# 1:N, M:N → prefetch_related con Prefetch
.prefetch_related(Prefetch('grupos', queryset=...))

# Agregaciones → annotate
.annotate(total_inscritos=Count('inscripciones'))
```

### 9. Estructura: Apps Modulares

**Decisión**: 7 apps independientes por dominio.

**Razón**:
- Mantenibilidad
- Reusabilidad
- Equipos paralelos

**Apps**: accounts, estructura, academica, financiera, homologaciones, indicadores, auditoria

### 10. Frontend: Django Templates + Bootstrap

**Decisión**: No usar API REST ni SPA.

**Razón**:
- Simplicidad
- Rendimiento
- Mantenibilidad
- Django nativo

**Stack**: Django Templates + Bootstrap 5 + CSS personalizado

---

## Anexos

### A. Diagrama de Navegación

```
/login/ → /dashboard/
            ├─ /estructura/facultades/
            ├─ /academica/asignaturas/
            ├─ /academica/inscripciones/
            ├─ /academica/notas/
            ├─ /financiera/tarifas/
            ├─ /financiera/recibos/
            ├─ /homologaciones/
            ├─ /indicadores/
            └─ /auditoria/
```

### B. Checklist de Seguridad

- [ ] SECRET_KEY en variables de entorno
- [ ] DEBUG=False en producción
- [ ] ALLOWED_HOSTS configurado
- [ ] CSRF tokens en formularios
- [ ] SQL injection prevenido (ORM)
- [ ] XSS prevenido (auto-escape templates)
- [ ] Password hashing activado
- [ ] HTTPS en producción

### C. Comandos Frecuentes

```bash
# Desarrollo
uv run python backend/manage.py runserver

# Testing
uv run pytest backend/

# Linting
uv run ruff check backend/

# Formato
uv run ruff format backend/

# Base de datos
uv run python backend/manage.py dbshell

# Migrations
uv run python backend/manage.py makemigrations
uv run python backend/manage.py migrate

# Admin
uv run python backend/manage.py createsuperuser

# Custom commands
uv run python backend/manage.py setup_functional_groups
uv run python backend/manage.py seed_demo_users
```

### D. Recursos Útiles

- Django Documentation: https://docs.djangoproject.com/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- Bootstrap 5: https://getbootstrap.com/
- pytest-django: https://pytest-django.readthedocs.io/

---

## Conclusiones

Este proyecto implementa un **sistema académico universitario completo** con Django 5 y PostgreSQL, enfocado en:

✅ **Modularidad**: 7 apps independientes
✅ **Seguridad**: Autenticación, roles, alcance de datos
✅ **Escalabilidad**: Optimizaciones de BD, servicios separados
✅ **Mantenibilidad**: Código limpio, decisiones documentadas
✅ **UX**: Interface intuitiva con Bootstrap 5

El sistema está **listo para desarrollo local** y puede escalar a producción con ajustes mínimos.

---

**Documento generado**: Junio 2, 2026
**Versión**: 1.0
**Estado**: Completo y operativo
