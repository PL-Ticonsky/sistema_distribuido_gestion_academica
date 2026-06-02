# Diagramas Técnicos y Arquitectura - Backend Django

**Sistema Distribuido de Gestión Académica Universitaria**

---

## 1. Diagrama de Flujo: Autenticación y Dashboard

```
┌─────────────────┐
│ Usuario anónimo │
└────────┬────────┘
         │ GET /login/
         ↓
┌──────────────────────┐
│  LoginView           │
│ (EmailAuthenticationForm) │
└────────┬─────────────┘
         │ POST email + contraseña
         ↓
┌──────────────────────┐
│ CustomUserManager    │
│ .authenticate()      │
└────────┬─────────────┘
         │ ¿Válido?
    ┌────┴─────┐
    │ NO        │ SÍ
    ↓          ↓
   Error   ┌────────────────────┐
   Form    │ Crea sesión        │
           │ request.user = ...  │
           └────────┬───────────┘
                    │ Redirige
                    ↓
              ┌──────────────────┐
              │ get_dashboard()  │
              └────────┬─────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ↓             ↓             ↓
    get_user_roles()  get_role_labels()  get_dashboard_options()
         │             │             │
         └─────────────┼─────────────┘
                       ↓
              ┌──────────────────┐
              │ dashboard.html   │
              │ (renderiza opciones│
              │  según roles)    │
              └──────────────────┘
```

---

## 2. Diagrama de Flujo: Crear Inscripción

```
┌──────────────────────────────────┐
│ Usuario (Estudiante/Coordinador) │
└────────┬─────────────────────────┘
         │ GET /academica/inscripciones/crear/
         ↓
┌──────────────────────────────────┐
│ InscripcionCreateView            │
│ (LoginRequiredMixin +             │
│  RoleRequiredMixin)               │
└────────┬──────────────────────────┘
         │ ¿Rol permitido?
    ┌────┴──────┐
    │ NO        │ SÍ
    ↓          ↓
  Error    ┌─────────────────────────┐
  (403)    │ InscripcionCreateForm   │
           │ - estudiante/grupo      │
           │ - filtra por alcance    │
           └────────┬────────────────┘
                    │ POST (formulario completo)
                    ↓
           ┌─────────────────────────┐
           │ form.is_valid()         │
           └────────┬────────────────┘
                    │
            ┌───────┴────────┐
            │ NO             │ SÍ
            ↓                ↓
          Muestra      ┌────────────────────┐
          errores      │ form.clean():      │
                       │ - Verifica grupo   │
                       │   activo           │
                       │ - Verifica cupo    │
                       │ - Verifica         │
                       │   matrícula activa │
                       │ - Sin duplicidad   │
                       └────────┬───────────┘
                                │ ¿Válido?
                           ┌────┴────┐
                           │ NO      │ SÍ
                           ↓        ↓
                         Errores ┌──────────────────┐
                                 │ Calcula intento: │
                                 │ intento = max()  │
                                 │        + 1       │
                                 └────────┬─────────┘
                                          ↓
                                 ┌──────────────────┐
                                 │ Crea Inscripcion:│
                                 │ - estado =       │
                                 │   'Cursando'     │
                                 │ - intento = ...  │
                                 │ - save()         │
                                 └────────┬─────────┘
                                          ↓
                                 ┌──────────────────┐
                                 │ Redirige a list  │
                                 │ + mensaje éxito  │
                                 └──────────────────┘
```

---

## 3. Diagrama de Flujo: Calificar Estudiante

```
┌──────────────┐
│ Profesor     │
└────┬─────────┘
     │ GET /academica/notas/grupos/<id>/
     ↓
┌──────────────────────────┐
│ NotaGrupoDetailView      │
│ (verifica profesor)      │
└────┬───────────────────┘
     │ ¿Es profesor del grupo?
┌────┴────┐
│ NO      │ SÍ
↓        ↓
Error   ┌────────────────────────┐
        │ Ve inscripciones       │
        │ del grupo              │
        └────────┬───────────────┘
                 │ Hace clic en "Editar nota"
                 ↓
        ┌────────────────────────┐
        │ NotaInscripcionUpdateView
        │ GET /academica/notas/  │
        │ inscripciones/<id>/... │
        └────────┬───────────────┘
                 │
                 ↓ Renderiza formulario
        ┌────────────────────────┐
        │ nota_form.html         │
        │ - Campos: nota1, nota2,│
        │   nota3, estado        │
        └────────┬───────────────┘
                 │ POST (notas completadas)
                 ↓
        ┌────────────────────────┐
        │ NotaInscripcionForm    │
        │ .clean():              │
        │ - Verifica rango 0-5   │
        │ - Verifica profesor    │
        │ - No cancelada         │
        └────────┬───────────────┘
                 │ ¿Válido?
            ┌────┴────┐
            │ NO      │ SÍ
            ↓        ↓
          Error   ┌────────────────────┐
                  │ Calcula nota_final:│
                  │ = (n1+n2+n3)/3     │
                  └────────┬───────────┘
                           ↓
                  ┌────────────────────┐
                  │ Determina estado:  │
                  │ Si nota >= 3.0:    │
                  │   estado = Aprobada
                  │ Si nota < 3.0:     │
                  │   estado = Reprobada
                  └────────┬───────────┘
                           ↓
                  ┌────────────────────┐
                  │ Actualiza          │
                  │ Inscripcion.save() │
                  └────────┬───────────┘
                           ↓
                  ┌────────────────────┐
                  │ Redirige + éxito   │
                  └────────────────────┘
```

---

## 4. Diagrama de Datos: Modelo Relacional (Simplificado)

```
                    ┌─────────────────┐
                    │  PeriodoAcademico│
                    │  (periodo_id, PK)│
                    └────────┬─────────┘
                             │
           ┌─────────────────┼─────────────────┐
           │                 │                 │
           ↓                 ↓                 ↓
    ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
    │    Grupo    │  │  Decano      │  │  Coordinador│
    │ (grupo_id)  │  │ (decano_id)  │  │ (coord_id)  │
    └──────┬──────┘  │              │  │             │
           │         │ profesor ─┐  │  │ profesor ─┐ │
           │         │ facultad  │  │  │ programa  │ │
           │         └──────┬────┘  │  └─────┬─────┘ │
           │ programa      │       │        │        │
           │ asignatura    └────┬──┴────────┘        │
           │ profesor           │                    │
           │                    ↓                    ↓
    ┌──────┴──────────┐  ┌─────────────┐  ┌──────────────┐
    │ ProgramaAsignaura  │  Profesor   │  ProgramaAcademico
    │ (pa_id)        │  │ (prof_id)   │  │ (prog_id)    │
    │ programa ───┬─┘  │ usuario  ──┐│  │ facultad ────→
    │ asignatura ─┘    │ facultad  ─┤│  │              │
    └────┬─────────────┘            ││  └──────────────┘
         │                          ││        │
         │                          ││        ↓
         │ Inscripcion              │└────→ ┌──────────────┐
         │                          │      │  Facultad    │
         ↓                          │      │ (faculty_id) │
┌──────────────────┐              │      └──────────────┘
│  Inscripcion     │              │
│ (inscripcion_id) │              │
│ grupo ───────────┘              │
│ estudiante  ┬──────────────────┘
└──────────────────┘  ↓
                   CustomUser
                   (user_id)
                      │
           ┌──────────┼──────────┐
           │          │          │
           ↓          ↓          ↓
       Estudiante  Profesor   (otros)
```

---

## 5. Diagrama de Control de Acceso

```
                        ┌─────────────────┐
                        │  Usuario Login  │
                        └────────┬────────┘
                                 │
                      ┌──────────┴──────────┐
                      │ Obtiene grupos     │
                      │ (roles funcionales)│
                      └──────────┬─────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
     (Si es docente)        (Si es coordinador)      (Si es superadmin)
        │                        │                        │
        ↓                        ↓                        ↓
    get_professor_        get_coordinated_         is_superadmin()
    for_user()            program_ids()            = True
        │                        │                        │
        ↓                        ↓                        ↓
   get_visible_            get_visible_           Todas las
   group_ids()             program_ids()          vistas
        │                        │                  │
        ↓                        ↓                  ↓
┌──────────────┐          ┌──────────────┐    ┌──────────┐
│Grupo.objects │          │Programa...   │    │ Acceso   │
│.filter(      │          │.filter(      │    │ total    │
│id__in=[ids]) │          │id__in=[ids]) │    │          │
└──────────────┘          └──────────────┘    └──────────┘
```

---

## 6. Diagrama de Indicadores Académicos

```
┌─────────────────────────┐
│ calculate_student_       │
│ indicators(student)      │
└────────┬────────────────┘
         │
         ├─→ total_subjects = ProgramaAsignatura.count()
         │
         ├─→ APROBADAS:
         │   ├─ inscripciones: Inscripcion(estado=Aprobada)
         │   ├─ homologaciones: Homologacion(estado=Aprobada)
         │   └─ aprobadas_count = len(approved_subjects)
         │
         ├─→ PROMEDIO:
         │   ├─ suma = Σ(nota * créditos)
         │   ├─ pesos = Σ(créditos)
         │   └─ promedio = suma / pesos
         │
         ├─→ REPROBADAS:
         │   └─ reprobadas_count = Inscripcion(estado=Reprobada).count()
         │
         ├─→ RIESGO:
         │   ├─ Si promedio < 3.2: +30 pts
         │   ├─ Si reprobadas >= 3: +25 pts
         │   ├─ Si avance < 40%: +20 pts
         │   ├─ Si estado = Inactivo|Suspendido|Retirado: +25 pts
         │   ├─ Si intento >= 3: +20 pts
         │   └─ risk_score = min(total, 100)
         │
         ├─→ LABEL:
         │   ├─ Si score <= 30: "Bajo"
         │   ├─ Si score <= 60: "Medio"
         │   └─ Si score > 60: "Alto"
         │
         └─→ Retorna dict con:
             {
                 'student': Estudiante,
                 'total_subjects': int,
                 'approved_subjects': int,
                 'missing_subjects': int,
                 'academic_progress': Decimal,
                 'weighted_average': Decimal,
                 'performance_percentage': Decimal,
                 'failed_subjects': int,
                 'risk_score': int,
                 'risk_label': str,
                 'has_enough_data': bool
             }
```

---

## 7. Diagrama de Stack de Middlewares

```
┌─────────────────────────────────────────┐
│ Solicitud HTTP entrante                │
└────────┬────────────────────────────────┘
         │
    ┌────┴──────────────────────────────────┐
    │ MIDDLEWARE (order matters)             │
    ├────────────────────────────────────────┤
    │ 1. SecurityMiddleware                  │
    │    (headers de seguridad)              │
    ├────────────────────────────────────────┤
    │ 2. SessionMiddleware                   │
    │    (carga/crea sesión)                 │
    ├────────────────────────────────────────┤
    │ 3. CommonMiddleware                    │
    │    (URLs, APPEND_SLASH)                │
    ├────────────────────────────────────────┤
    │ 4. CsrfViewMiddleware                  │
    │    (valida CSRF tokens)                │
    ├────────────────────────────────────────┤
    │ 5. AuthenticationMiddleware            │
    │    (request.user = usuario actual)     │
    ├────────────────────────────────────────┤
    │ 6. MessageMiddleware                   │
    │    (almacena mensajes)                 │
    ├────────────────────────────────────────┤
    │ 7. XFrameOptionsMiddleware             │
    │    (previene clickjacking)             │
    └────┬──────────────────────────────────┘
         ↓
    ┌─────────────────────────────┐
    │ URL Router (urls.py)        │
    │ ↓ encuentra vista            │
    └────┬────────────────────────┘
         ↓
    ┌─────────────────────────────┐
    │ Mixins (order matters)       │
    │ 1. LoginRequiredMixin        │
    │ 2. RoleRequiredMixin         │
    │ ↓ checks passed              │
    └────┬────────────────────────┘
         ↓
    ┌─────────────────────────────┐
    │ Vista (get_queryset etc.)    │
    └────┬────────────────────────┘
         ↓
    ┌─────────────────────────────┐
    │ Renderiza template           │
    └────┬────────────────────────┘
         │
    ┌────┴──────────────────────────┐
    │ MIDDLEWARE REVERSA (orden inv.)│
    │ (procesamiento de respuesta)   │
    └────┬──────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│ Respuesta HTTP                          │
└─────────────────────────────────────────┘
```

---

## 8. Diagrama: QuerySet Optimization

```
┌────────────────────────────────────────┐
│ GrupoListView.get_queryset()           │
└────────┬───────────────────────────────┘
         │
         ↓ INICIO: Sin optimizar
    ┌────────────────────────────────────┐
    │ Grupo.objects.all()                │
    │ → 1 query: SELECT * FROM grupo     │
    └────────┬───────────────────────────┘
             │
             ↓ POR CADA GRUPO EN TEMPLATE:
        ┌────────────────────────────────┐
        │ {{ grupo.profesor.usuario }}    │
        │ → N queries adicionales:        │
        │   - 1 por profesor             │
        │   - 1 por usuario              │
        │ TOTAL: 1 + (2 * N grupos)      │
        └────────────────────────────────┘
         │
         └─────────────────────────────────┐
                                           │
         ┌─────────────────────────────────┘
         │
         ↓ CON select_related()
    ┌────────────────────────────────────┐
    │ Grupo.objects.select_related(      │
    │   'profesor__usuario',             │
    │   'programa_asignatura'            │
    │ )                                  │
    │ → 1 query con JOINS                │
    │   SELECT * FROM grupo              │
    │   JOIN profesor ...                │
    │   JOIN usuario ...                 │
    │   TOTAL: 1 query solamente         │
    └────────┬───────────────────────────┘
             │
             ↓ RESULTADO
        Reducción: N+1 → 1 query
```

---

## 9. Ciclo de Vida de una Solicitud

```
Solicitud: GET /academica/inscripciones/

┌──────────────────────────────────────┐
│ 1. Django Router                     │
│ Busca en urls.py                     │
│ → encuentra InscripcionListView      │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 2. Instancia la vista                │
│ InscripcionListView()                │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 3. dispatch() - Enrutamiento         │
│ → GET → get()                        │
│ → POST → post()                      │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 4. Mixins (check en orden)           │
│ - LoginRequiredMixin.dispatch()      │
│   ¿Usuario autenticado?              │
│ - RoleRequiredMixin.dispatch()       │
│   ¿Usuario tiene rol?                │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 5. get() de ListView                 │
│ Llama get_queryset()                 │
│ Llama get_context_data()             │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 6. get_queryset()                    │
│ Obtiene modelo                       │
│ Filtra por scope (alcance)           │
│ Optim. (select_related, etc.)        │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 7. get_context_data()                │
│ Agrega objetos a contexto            │
│ {'inscripciones': [...]}             │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 8. render_to_response()              │
│ Encuentra template                   │
│ Renderiza HTML                       │
└────────┬─────────────────────────────┘
         ↓
┌──────────────────────────────────────┐
│ 9. HttpResponse                      │
│ HTML renderizado                     │
│ → Browser                            │
└──────────────────────────────────────┘
```

---

## 10. Diagrama: Filtrado por Alcance

```
┌─────────────────────────────────────────┐
│ Usuario: "sofia.herrera@..." (Estudiante)
└────────┬────────────────────────────────┘
         │
         ↓ get_visible_student_ids(user)
    ┌──────────────────────────────────────┐
    │ 1. ¿Es superadmin?                   │
    │    NO → continúa                     │
    └────────┬─────────────────────────────┘
             │
             ↓ 2. ¿Es estudiante?
        ┌────────────────────────────────┐
        │ SÍ → obtiene su estudiante     │
        │ Estudiante.objects.filter(     │
        │   usuario=sofia               │
        │ ).first()                      │
        │ → id_estudiante = "abc123"    │
        └────────┬───────────────────────┘
                 │
                 ↓ 3. ¿Es coordinador?
            ┌──────────────────────────┐
            │ NO → salta               │
            └──────────────────────────┘
                 │
                 ↓ 4. ¿Es decano?
            ┌──────────────────────────┐
            │ NO → salta               │
            └──────────────────────────┘
                 │
                 ↓ 5. ¿Es administrativo?
            ┌──────────────────────────┐
            │ NO → salta               │
            └──────────────────────────┘
                 │
                 ↓ RESULTADO
        ┌────────────────────────────────┐
        │ visible_student_ids =          │
        │ ["abc123"]  ← solo el suyo    │
        └────────────────────────────────┘

                 ↓

┌─────────────────────────────────────────┐
│ En vista: ListView.get_queryset()       │
│                                         │
│ Inscripcion.objects.all()              │
│ .filter(id_estudiante__in=[            │
│   "abc123"                              │
│ ])                                      │
│                                         │
│ ↓ Solo ve sus propias inscripciones    │
└─────────────────────────────────────────┘
```

---

## 11. Estadísticas del Proyecto

```
CODEBASE METRICS
════════════════════════════════════════════

Aplicaciones:              7
├─ accounts
├─ estructura
├─ academica
├─ financiera
├─ homologaciones
├─ indicadores
└─ auditoria

Modelos:                   27
├─ CustomUser, Facultad, ProgramaAcademico
├─ Asignatura, ProgramaAsignatura, PreRequisito
├─ Estudiante, Profesor, Grupo, Inscripcion
├─ TarifaMatricula, Recibo, Matricula
├─ Homologacion, Auditoria
└─ Coordinador, Decano

Vistas (CBV):              45+
├─ ListView, DetailView
├─ CreateView, UpdateView
├─ FormView, View

Formularios:               8+
├─ EmailAuthenticationForm
├─ EstudianteCreateForm
├─ InscripcionCreateForm
└─ (Formularios por app)

URLs:                      50+
├─ /accounts/ (3)
├─ /estructura/ (4)
├─ /academica/ (14)
├─ /financiera/ (13)
├─ /homologaciones/ (6)
├─ /indicadores/ (3)
└─ /auditoria/ (2)

Templates:                 25+
├─ base.html
├─ Listados (list.html)
├─ Detalles (detail.html)
├─ Formularios (form.html)
└─ (Por cada vista)

Tests:                     TBD
├─ test_project_setup.py
└─ (A expandir)

Database Tables:           18
├─ usuario, facultad, programa_academico
├─ periodo_academico, asignatura
├─ programa_asignatura, pre_requisito
├─ estudiante, profesor, decano, coordinador
├─ grupo, inscripcion
├─ tarifa_matricula, recibo, matricula
├─ homologacion, auditoria
└─ Django: auth_user, auth_group, etc.

Total Lines of Code:       ~5,000+
├─ models.py: ~500
├─ views.py: ~1,500+
├─ forms.py: ~800
├─ templates: ~1,500+
└─ config: ~200

Languages:
├─ Python: 80%
├─ HTML/Django: 15%
├─ CSS/JS: 5%

Technologies:
├─ Backend: Django 5.0+
├─ Database: PostgreSQL
├─ Frontend: Bootstrap 5
├─ Testing: pytest
├─ Linting: ruff
└─ Package Mgmt: uv

Configuration Files:
├─ pyproject.toml
├─ requirements.txt
├─ .env (local)
├─ settings.py
├─ urls.py
└─ pytest.ini
```

---

## 12. Matrix de Permiso por Rol

```
┌─────────────────┬──────────┬───────┬───────────┬──────┬───────────┬──────────┐
│ Acción/Recurso  │Estudiante│Docente│Coordinador│Decano│Admin.     │Superadmin│
├─────────────────┼──────────┼───────┼───────────┼──────┼───────────┼──────────┤
│ Ver Facultades  │    ✗     │   ✓   │     ✓     │  ✓   │    ✗      │    ✓     │
│ Ver Programas   │    ✓*    │   ✓   │     ✓     │  ✓   │    ✗      │    ✓     │
│ Ver Asignaturas │    ✓     │   ✓   │     ✓     │  ✓   │    ✗      │    ✓     │
│ Ver Grupos      │    ✓*    │   ✓   │     ✓     │  ✓   │    ✗      │    ✓     │
│ Crear Grupo     │    ✗     │   ✗   │     ✗     │  ✗   │    ✗      │    ✓     │
│ Ver Docentes    │    ✗     │   ✓   │     ✓     │  ✓   │    ✗      │    ✓     │
│ Agregar Est.    │    ✗     │   ✗   │     ✓*    │  ✗   │    ✗      │    ✓     │
│ Ver Inscrip.    │    ✓*    │   ✓*  │     ✓*    │  ✓*  │    ✗      │    ✓     │
│ Crear Inscrip.  │    ✓*    │   ✗   │     ✓*    │  ✓*  │    ✗      │    ✓     │
│ Cancelar Inscrip│    ✓*    │   ✗   │     ✓*    │  ✓*  │    ✗      │    ✓     │
│ Ver Notas       │    ✓*    │   ✓*  │     ✓*    │  ✓*  │    ✗      │    ✓     │
│ Editar Notas    │    ✗     │   ✓*  │     ✗     │  ✗   │    ✗      │    ✓     │
│ Ver Tarifas     │    ✓     │   ✗   │     ✓     │  ✓   │    ✓      │    ✓     │
│ Crear Tarifa    │    ✗     │   ✗   │     ✗     │  ✗   │    ✓      │    ✓     │
│ Ver Recibos     │    ✓*    │   ✗   │     ✓     │  ✓   │    ✓      │    ✓     │
│ Crear Recibo    │    ✗     │   ✗   │     ✗     │  ✗   │    ✓      │    ✓     │
│ Ver Matrículas  │    ✓*    │   ✗   │     ✓     │  ✓   │    ✓      │    ✓     │
│ Crear Matrícula │    ✗     │   ✗   │     ✗     │  ✗   │    ✓      │    ✓     │
│ Crear Homolog.  │    ✓*    │   ✗   │     ✗     │  ✗   │    ✗      │    ✓     │
│ Evaluar Homolog.│    ✗     │   ✓*  │     ✗     │  ✗   │    ✗      │    ✓     │
│ Ver Indicadores │    ✓*    │   ✓*  │     ✓*    │  ✓*  │    ✗      │    ✓     │
│ Ver Auditoría   │    ✗     │   ✗   │     ✗     │  ✗   │    ✗      │    ✓     │
└─────────────────┴──────────┴───────┴───────────┴──────┴───────────┴──────────┘

LEYENDA:
✓  = Acceso total
✓* = Acceso limitado a su alcance
✗  = Sin acceso

ALCANCE LIMITADO (*):
- Estudiante: Solo sus datos
- Docente: Solo sus grupos y estudiantes
- Coordinador: Su programa académico
- Decano: Su facultad
- Administrativo: Su facultad
```

---

## 13. Resumen Visual del Flujo Completo

```
USER REQUEST
    ↓
┌─────────────────────────────────────┐
│ URL Router (urls.py)                │
│ ↓ coincide con pattern              │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ View Class Selected                 │
│ (e.g., InscripcionListView)         │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Mixins Execution (orden)            │
│ 1. LoginRequiredMixin               │
│    → request.user autenticado?      │
│ 2. RoleRequiredMixin                │
│    → usuario.roles en allowed_roles?│
└─────────────────────────────────────┘
    ↓ PASS
┌─────────────────────────────────────┐
│ View.get() or post()                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ get_queryset()                      │
│ ├─ Obtiene modelo base              │
│ ├─ Aplica filtros por alcance       │
│ │  (scope.py functions)             │
│ ├─ Optimiza queries                 │
│ │  (select_related, prefetch_related)
│ └─ Retorna QuerySet filtrado        │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ get_context_data()                  │
│ ├─ Obtiene objeto(s) del queryset   │
│ ├─ Agrega contexto adicional        │
│ └─ Retorna dict context             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ render_to_response()                │
│ ├─ Busca template_name              │
│ ├─ Renderiza HTML con contexto      │
│ └─ Retorna HttpResponse             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ HttpResponse(html_content)          │
└─────────────────────────────────────┘
    ↓
RENDERED HTML → BROWSER
```

---

**Documento generado**: Junio 2, 2026
**Versión**: 1.0
**Status**: Completo
