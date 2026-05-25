# 20. Análisis técnico del proyecto Django

## 1. Propósito del documento

Este documento consolida el análisis técnico del repositorio `sistema_distribuido_gestion_academica` a partir del código existente en `backend/apps/`, las rutas Django, los modelos, las vistas, los formularios, `backend/apps/accounts/roles.py` y el `README.md`.

El objetivo es documentar el alcance funcional, actores, arquitectura, requerimientos, casos de uso, trazabilidad y riesgos de mantenimiento sin modificar la lógica existente del sistema.

## 2. Alcance del sistema

El sistema es una aplicación web académica desarrollada con Django y PostgreSQL para soportar procesos universitarios en un ambiente local de validación académica.

### 2.1 Funcionalidades dentro del alcance

- Autenticación por correo mediante `accounts.CustomUser`.
- Dashboard adaptado a roles funcionales.
- Control de acceso por roles y alcance de datos.
- Consulta de estructura institucional: facultades, programas y periodos.
- Consulta de asignaturas, planes de estudio, prerrequisitos, docentes y grupos.
- Gestión controlada de inscripciones.
- Consulta y edición controlada de notas.
- Gestión financiera de tarifas, recibos y matrículas.
- Gestión de solicitudes de homologación.
- Cálculo de indicadores académicos.
- Consulta de auditoría para superadmin.
- Interfaz Django Templates con Bootstrap, CSS propio y sidebar colapsable.

### 2.2 Límites y exclusiones

- No se administra la estructura relacional principal mediante migraciones Django; los modelos académicos usan `managed = False`.
- No se modifica el DDL desde la aplicación.
- No se implementa despliegue cloud como parte del alcance actual.
- No se implementa una API REST pública.
- No se implementa frontend SPA con React, Vue u otros frameworks pesados.
- No se implementan roles técnicos de PostgreSQL desde Django.
- No se automatiza la ejecución de scripts SQL desde la aplicación.

## 3. Arquitectura Django

### 3.1 Vista general

```text
Usuario web
   ↓
Django URLs
   ↓
Vistas basadas en clases / funciones
   ↓
Mixins de autenticación y roles
   ↓
Forms / Services / Scope helpers
   ↓
ORM Django
   ↓
PostgreSQL con modelo relacional existente
```

### 3.2 Apps identificadas

| App | Responsabilidad principal | Archivos clave |
|---|---|---|
| `accounts` | Autenticación, usuario personalizado, roles, permisos, alcance y dashboard. | `models.py`, `roles.py`, `access.py`, `scope.py`, `views.py` |
| `estructura` | Consulta de facultades, programas y periodos. | `models.py`, `views.py`, `urls.py` |
| `academica` | Asignaturas, planes, docentes, grupos, inscripciones y notas. | `models.py`, `forms.py`, `views.py`, `urls.py` |
| `financiera` | Tarifas, recibos, matrículas y cambios de estado financiero. | `models.py`, `forms.py`, `views.py`, `urls.py` |
| `homologaciones` | Solicitudes, asignación de evaluador, evaluación y cancelación. | `models.py`, `forms.py`, `views.py`, `urls.py` |
| `indicadores` | Cálculo y consulta de indicadores académicos. | `views.py`, `services.py`, `urls.py` |
| `auditoria` | Consulta de trazabilidad operativa. | `models.py`, `views.py`, `urls.py` |

### 3.3 Organización de rutas

| Prefijo | App | Casos de uso principales |
|---|---|---|
| `/login/`, `/logout/`, `/dashboard/` | `accounts` | Autenticación, salida, dashboard por rol. |
| `/estructura/` | `estructura` | Consultar facultades, programas y periodos. |
| `/academica/` | `academica` | Consultar oferta académica, grupos, inscripciones y notas. |
| `/financiera/` | `financiera` | Gestionar tarifas, recibos y matrículas. |
| `/homologaciones/` | `homologaciones` | Crear, consultar, asignar, evaluar y cancelar homologaciones. |
| `/indicadores/` | `indicadores` | Consultar indicadores de estudiantes. |
| `/auditoria/` | `auditoria` | Consultar registros de auditoría. |
| `/admin/` | Django admin | Administración técnica por staff/superuser. |

## 4. Actores y roles

Los roles funcionales provienen de `accounts.roles.FUNCTIONAL_ROLES`:

```text
estudiante, docente, coordinador, decano, administrativo, superadmin
```

### 4.1 Actores del sistema

| Actor | Rol Django | Intereses principales |
|---|---|---|
| Usuario autenticado | Cualquier rol | Ingresar, ver dashboard y navegar módulos permitidos. |
| Estudiante | `estudiante` | Ver plan, inscripciones, notas, recibos, homologaciones e indicadores propios. |
| Docente | `docente` | Ver grupos asignados, estudiantes, notas e indicadores de estudiantes relacionados. |
| Coordinador | `coordinador` | Consultar estructura y oferta de su programa; gestionar inscripciones y homologaciones dentro de alcance. |
| Decano | `decano` | Consultar información de facultad, programas, docentes, grupos e indicadores. |
| Administrativo | `administrativo` | Gestionar procesos financieros dentro de su facultad. |
| Superadmin | `superadmin` | Acceso general, auditoría y administración funcional amplia. |

### 4.2 Permisos por macrodominio

| Macrodominio | Roles con acceso |
|---|---|
| Estructura | `coordinador`, `decano`, `superadmin` |
| Financiera | `estudiante`, `coordinador`, `decano`, `administrativo`, `superadmin` |
| Académica estudiante | `estudiante`, `coordinador`, `decano`, `superadmin` |
| Académica docente | `docente`, `coordinador`, `decano`, `superadmin` |
| Homologaciones | `estudiante`, `docente`, `coordinador`, `decano`, `superadmin` |
| Indicadores | `estudiante`, `docente`, `coordinador`, `decano`, `superadmin` |
| Auditoría | `superadmin` |

## 5. Requerimientos funcionales

| ID | Requerimiento funcional | Evidencia en código |
|---|---|---|
| RF-01 | El sistema debe autenticar usuarios mediante correo y contraseña. | `EmailLoginView`, `EmailAuthenticationForm`, `CustomUser.USERNAME_FIELD = "correo"` |
| RF-02 | El sistema debe mostrar un dashboard con opciones según rol. | `accounts.views.dashboard`, `roles.get_dashboard_options` |
| RF-03 | El sistema debe proteger vistas mediante autenticación y roles. | `LoginRequiredMixin`, `RoleRequiredMixin` |
| RF-04 | El sistema debe filtrar datos según alcance académico, financiero o institucional. | `accounts.scope` |
| RF-05 | El sistema debe permitir consultar estructura institucional. | `estructura.views` |
| RF-06 | El sistema debe permitir consultar asignaturas, planes y prerrequisitos. | `academica.views.Asignatura*`, `PlanEstudiosListView`, `PreRequisitoListView` |
| RF-07 | El sistema debe permitir consultar docentes, grupos y estudiantes inscritos. | `Profesor*View`, `Grupo*View` |
| RF-08 | El sistema debe permitir crear inscripciones bajo reglas de negocio. | `InscripcionCreateView`, `InscripcionCreateForm` |
| RF-09 | El sistema debe permitir cancelar inscripciones autorizadas. | `InscripcionCancelView` |
| RF-10 | El sistema debe permitir consultar y editar notas según rol docente o superadmin. | `NotaGrupo*View`, `NotaInscripcionUpdateView` |
| RF-11 | El sistema debe gestionar tarifas de matrícula. | `TarifaMatricula*View`, `TarifaMatriculaForm` |
| RF-12 | El sistema debe gestionar recibos y estados de pago. | `Recibo*View`, `ReciboForm`, `ReciboAnularView` |
| RF-13 | El sistema debe crear y cambiar estados de matrículas. | `MatriculaCreateView`, `MatriculaEstadoView` |
| RF-14 | El sistema debe permitir crear solicitudes de homologación para estudiantes. | `HomologacionCreateView`, `HomologacionSolicitudForm` |
| RF-15 | El sistema debe permitir asignar profesor evaluador a homologaciones. | `HomologacionAssignEvaluatorView` |
| RF-16 | El sistema debe permitir evaluar homologaciones. | `HomologacionEvaluateView`, `HomologacionEvaluarForm` |
| RF-17 | El sistema debe permitir cancelar homologaciones solicitadas. | `HomologacionCancelView` |
| RF-18 | El sistema debe calcular indicadores académicos de estudiantes visibles. | `indicadores.services.calculate_student_indicators` |
| RF-19 | El sistema debe permitir consultar auditoría al superadmin. | `auditoria.views` |

## 6. Requerimientos no funcionales

| ID | Requerimiento no funcional | Evidencia o criterio |
|---|---|---|
| RNF-01 | Seguridad de acceso por autenticación y roles. | `LoginRequiredMixin`, `RoleRequiredMixin` |
| RNF-02 | Confidencialidad por alcance de datos. | Filtros en `accounts.scope` y querysets de vistas |
| RNF-03 | Integridad con base relacional existente. | Modelos `managed = False`; scripts SQL separados |
| RNF-04 | Mantenibilidad modular. | Apps Django separadas por dominio |
| RNF-05 | Trazabilidad documental. | `docs/`, `docs/diagrams/`, README |
| RNF-06 | Validación de reglas antes de escritura. | Forms en `academica`, `financiera`, `homologaciones` |
| RNF-07 | Usabilidad básica. | Templates, sidebar, dashboard por rol, mensajes |
| RNF-08 | Calidad estática. | Ruff y pytest configurados en `pyproject.toml` |
| RNF-09 | Configuración externa. | Variables `.env` con `django-environ` |
| RNF-10 | Rendimiento razonable en listados. | Uso de `select_related`, `prefetch_related`, `annotate` |

## 7. Catálogo de casos de uso

| ID | Caso de uso | Actor principal | Rutas principales |
|---|---|---|---|
| CU-01 | Iniciar sesión | Usuario no autenticado | `/login/` |
| CU-02 | Cerrar sesión | Usuario autenticado | `/logout/` |
| CU-03 | Consultar dashboard por rol | Usuario autenticado | `/dashboard/` |
| CU-04 | Consultar estructura institucional | Coordinador, Decano, Superadmin | `/estructura/facultades/`, `/estructura/programas/`, `/estructura/periodos/` |
| CU-05 | Consultar asignaturas y plan de estudios | Estudiante, Docente, Coordinador, Decano, Superadmin | `/academica/asignaturas/`, `/academica/planes/` |
| CU-06 | Consultar docentes y grupos | Docente, Coordinador, Decano, Superadmin | `/academica/docentes/`, `/academica/grupos/` |
| CU-07 | Crear inscripción | Estudiante, Coordinador, Decano, Superadmin | `/academica/inscripciones/crear/` |
| CU-08 | Cancelar inscripción | Estudiante, Coordinador, Decano, Superadmin | `/academica/inscripciones/<id>/cancelar/` |
| CU-09 | Consultar notas | Estudiante, Docente, Coordinador, Decano, Superadmin | `/academica/notas/` |
| CU-10 | Editar notas | Docente, Superadmin | `/academica/notas/inscripciones/<id>/editar/` |
| CU-11 | Consultar tarifas, recibos y matrículas | Roles financieros | `/financiera/tarifas/`, `/financiera/recibos/`, `/financiera/matriculas/` |
| CU-12 | Gestionar tarifas | Administrativo, Superadmin | `/financiera/tarifas/crear/`, `/editar/`, `/cambiar-estado/` |
| CU-13 | Gestionar recibos | Administrativo, Superadmin | `/financiera/recibos/crear/`, `/editar/`, `/anular/` |
| CU-14 | Gestionar matrículas | Administrativo, Superadmin | `/financiera/matriculas/crear/`, `/activar/`, `/finalizar/`, `/cancelar/`, `/anular/` |
| CU-15 | Crear solicitud de homologación | Estudiante | `/homologaciones/crear/` |
| CU-16 | Asignar evaluador de homologación | Coordinador, Superadmin | `/homologaciones/<id>/asignar-evaluador/` |
| CU-17 | Evaluar homologación | Docente, Superadmin | `/homologaciones/<id>/evaluar/` |
| CU-18 | Cancelar homologación | Estudiante, Superadmin | `/homologaciones/<id>/cancelar/` |
| CU-19 | Consultar indicadores académicos | Estudiante, Docente, Coordinador, Decano, Superadmin | `/indicadores/`, `/indicadores/mis-indicadores/` |
| CU-20 | Consultar auditoría | Superadmin | `/auditoria/` |

## 8. Casos de uso extendidos

### CU-01 Iniciar sesión y acceder al dashboard

**Actor principal:** Usuario no autenticado.

**Precondiciones:**

- El usuario existe en `usuario`.
- La contraseña está hasheada por Django.
- El usuario está activo.

**Flujo principal:**

1. El actor abre `/login/`.
2. El sistema muestra el formulario de correo y contraseña.
3. El actor envía credenciales.
4. Django autentica contra `CustomUser`.
5. El sistema crea sesión.
6. El sistema redirige a `/dashboard/`.
7. El dashboard invoca `get_dashboard_options()` y `get_role_labels()`.
8. El sistema muestra accesos disponibles por rol.

**Extensiones:**

- 4a. Si las credenciales son inválidas, se muestra error en login.
- 4b. Si el usuario no está activo, Django rechaza la autenticación.
- 7a. Si no tiene grupos funcionales, el dashboard informa que no hay roles asignados.

**Postcondiciones:**

- Existe sesión autenticada.
- El usuario visualiza opciones filtradas por rol.

### CU-07 Crear inscripción

**Actor principal:** Estudiante, Coordinador, Decano o Superadmin.

**Precondiciones:**

- El actor está autenticado.
- El actor tiene rol permitido.
- Existen estudiante, grupo, matrícula activa y cupo disponible.

**Flujo principal:**

1. El actor abre `/academica/inscripciones/crear/`.
2. El sistema construye `InscripcionCreateForm` con el usuario actual.
3. El sistema limita estudiantes y grupos según `scope.py`.
4. El actor selecciona grupo y, si aplica, estudiante.
5. El sistema valida reglas de negocio:
   - grupo abierto o en curso,
   - no duplicidad en el mismo grupo,
   - no duplicidad asignatura-periodo,
   - cupo disponible,
   - matrícula activa para el periodo.
6. El sistema calcula el intento.
7. El sistema crea la inscripción en estado `Cursando`.
8. El sistema redirige al listado de inscripciones.

**Extensiones:**

- 5a. Si el grupo no está activo, se rechaza la inscripción.
- 5b. Si no hay cupos, se muestra error de validación.
- 5c. Si el estudiante no tiene matrícula activa, se bloquea la operación.
- 5d. Si el usuario no tiene alcance sobre el estudiante o grupo, no aparecen en el formulario.

**Postcondiciones:**

- Se crea una inscripción con UUID, intento calculado y estado `Cursando`.

### CU-10 Editar notas de una inscripción

**Actor principal:** Docente o Superadmin.

**Precondiciones:**

- El actor está autenticado.
- El actor tiene rol `docente` o `superadmin`.
- Si es docente, debe ser profesor del grupo asociado a la inscripción.
- La inscripción no está cancelada.

**Flujo principal:**

1. El actor abre el detalle de notas del grupo.
2. El sistema muestra estudiantes inscritos y acciones permitidas.
3. El actor abre `/academica/notas/inscripciones/<id>/editar/`.
4. El sistema valida permiso sobre la inscripción.
5. El actor registra `nota1`, `nota2`, `nota3`.
6. El formulario valida que cada nota esté entre 0.0 y 5.0.
7. Si todas las notas existen, el sistema calcula `nota_final`.
8. Si `nota_final >= 3`, la inscripción pasa a `Aprobada`; si no, a `Reprobada`.
9. El sistema guarda cambios y redirige al detalle del grupo.

**Extensiones:**

- 4a. Si el docente no pertenece al grupo, el sistema redirige a notas.
- 6a. Si una nota está fuera de rango, se muestra error.
- 7a. Si faltan notas, la inscripción queda en `Cursando` y `nota_final` en `None`.
- 3a. Si la inscripción está cancelada, el formulario bloquea edición.

**Postcondiciones:**

- Las notas quedan persistidas.
- El estado académico de la inscripción se recalcula.

### CU-14 Gestionar matrícula

**Actor principal:** Administrativo o Superadmin.

**Precondiciones:**

- El actor está autenticado.
- El actor puede gestionar datos financieros.
- Existe recibo pagado sin matrícula asociada para crear matrícula.

**Flujo principal:**

1. El actor consulta `/financiera/matriculas/`.
2. El sistema filtra matrículas según estudiantes visibles.
3. El actor abre `/financiera/matriculas/crear/`.
4. El sistema muestra recibos pagados sin matrícula.
5. El actor crea matrícula en estado `Pendiente` o `Activa`.
6. Si se solicita estado `Activa`, el sistema valida límite de matrículas del estudiante.
7. El sistema guarda la matrícula.
8. El actor puede activar, finalizar, cancelar o anular desde el detalle.

**Extensiones:**

- 4a. Si el recibo no está pagado, no es elegible.
- 6a. Si el estudiante alcanzó límite de matrículas, se bloquea activación.
- 8a. Si la matrícula está anulada, no puede cambiarse.
- 8b. Si la matrícula está cancelada, no puede activarse.
- 8c. Si el recibo no está pagado, no puede activarse.

**Postcondiciones:**

- La matrícula queda creada o actualizada con estado válido.

### CU-15/CU-17 Gestionar homologación

**Actor principal:** Estudiante para solicitud; Coordinador para asignación; Docente para evaluación.

**Precondiciones:**

- El estudiante tiene registro asociado.
- La asignatura destino pertenece a su programa.
- La asignatura destino está activa y marcada como homologable.
- Existe un profesor evaluador disponible.

**Flujo principal:**

1. El estudiante abre `/homologaciones/crear/`.
2. El sistema muestra asignaturas homologables de su programa.
3. El estudiante registra asignatura de origen, institución y asignatura destino.
4. El sistema valida que no exista homologación aprobada previa para la asignatura.
5. El sistema asigna evaluador por defecto y crea solicitud en estado `Solicitada`.
6. El coordinador puede abrir la solicitud y reasignar evaluador.
7. El evaluador abre `/homologaciones/<id>/evaluar/`.
8. El docente aprueba con nota o rechaza con observación.
9. El sistema guarda estado, fecha de respuesta y nota si aplica.

**Extensiones:**

- 3a. Si el usuario no tiene registro de estudiante, se redirige al listado.
- 4a. Si ya existe homologación aprobada, se rechaza la solicitud.
- 5a. Si no hay profesor disponible, se bloquea la creación.
- 8a. Si se aprueba sin nota, se rechaza el formulario.
- 8b. Si se rechaza sin observación, se rechaza el formulario.
- 8c. Si el docente no es evaluador asignado, se rechaza la evaluación.
- 8d. Si la solicitud está cancelada o cerrada, no puede evaluarse.

**Postcondiciones:**

- La homologación queda en `Solicitada`, `En revision`, `Aprobada`, `Rechazada` o `Cancelada`.

## 9. Matriz de trazabilidad: requerimientos vs casos de uso

| Requerimiento | Casos de uso relacionados |
|---|---|
| RF-01 | CU-01 |
| RF-02 | CU-03 |
| RF-03 | CU-01 a CU-20 |
| RF-04 | CU-04 a CU-20 |
| RF-05 | CU-04 |
| RF-06 | CU-05 |
| RF-07 | CU-06, CU-09 |
| RF-08 | CU-07 |
| RF-09 | CU-08 |
| RF-10 | CU-09, CU-10 |
| RF-11 | CU-11, CU-12 |
| RF-12 | CU-11, CU-13 |
| RF-13 | CU-11, CU-14 |
| RF-14 | CU-15 |
| RF-15 | CU-16 |
| RF-16 | CU-17 |
| RF-17 | CU-18 |
| RF-18 | CU-19 |
| RF-19 | CU-20 |
| RNF-01 | CU-01 a CU-20 |
| RNF-02 | CU-04 a CU-20 |
| RNF-06 | CU-07, CU-10, CU-12, CU-13, CU-14, CU-15, CU-16, CU-17 |

## 10. Matriz de trazabilidad: casos de uso vs casos de uso

| Caso de uso base | Depende de | Relación |
|---|---|---|
| CU-03 Dashboard | CU-01 | Requiere sesión autenticada. |
| CU-04 Estructura | CU-01, CU-03 | Acceso desde navegación por rol. |
| CU-05 Plan/asignaturas | CU-01, CU-03 | Acceso filtrado por rol y programa. |
| CU-06 Docentes/grupos | CU-01, CU-03 | Requiere roles docentes o de gestión. |
| CU-07 Crear inscripción | CU-01, CU-05, CU-11, CU-14 | Requiere usuario, grupo, plan y matrícula activa. |
| CU-08 Cancelar inscripción | CU-07 | Opera sobre inscripción existente. |
| CU-09 Consultar notas | CU-01, CU-06, CU-07 | Requiere grupos e inscripciones. |
| CU-10 Editar notas | CU-09 | Opera sobre inscripción visible en grupo. |
| CU-11 Consultar financiera | CU-01 | Requiere rol financiero. |
| CU-12 Gestionar tarifas | CU-04, CU-11 | Requiere programas y periodos. |
| CU-13 Gestionar recibos | CU-11, CU-12 | Requiere tarifa y estudiante. |
| CU-14 Gestionar matrículas | CU-11, CU-13 | Requiere recibo pagado. |
| CU-15 Crear homologación | CU-01, CU-05 | Requiere estudiante y asignatura homologable. |
| CU-16 Asignar evaluador | CU-15 | Opera sobre solicitud abierta. |
| CU-17 Evaluar homologación | CU-15, CU-16 | Requiere solicitud y evaluador. |
| CU-18 Cancelar homologación | CU-15 | Opera sobre solicitud propia en estado `Solicitada`. |
| CU-19 Indicadores | CU-07, CU-10, CU-17 | Calcula avance con inscripciones y homologaciones aprobadas. |
| CU-20 Auditoría | CU-01 | Requiere superadmin. |

## 11. Análisis de actores tipo Pressman

Según el enfoque de Pressman, los actores se analizan por metas, frecuencia, nivel de experiencia, interacción y valor para el negocio.

| Actor | Meta primaria | Frecuencia esperada | Experiencia técnica | Valor del actor | Riesgos de interacción |
|---|---|---:|---|---|---|
| Estudiante | Consultar y gestionar su trayectoria académica básica. | Alta | Baja-media | Alto: consumidor principal de servicios. | Confusión si no entiende restricciones de inscripción o homologación. |
| Docente | Consultar grupos y registrar notas. | Media-alta | Media | Alto: fuente de datos académicos. | Edición incorrecta de notas; requiere validaciones claras. |
| Coordinador | Supervisar programa, inscripciones y homologaciones. | Media | Media | Alto: gestión académica por programa. | Alcance mal configurado puede exponer o ocultar datos. |
| Decano | Consultar facultad, docentes e indicadores. | Media | Media | Medio-alto: visión gerencial. | Necesita datos agregados claros; exceso de detalle puede afectar utilidad. |
| Administrativo | Gestionar recibos, tarifas y matrículas. | Alta en periodos de matrícula | Media | Alto: operación financiera. | Estados financieros incorrectos impactan matrícula. |
| Superadmin | Administrar y auditar el sistema. | Baja-media | Alta | Alto: control global. | Acceso amplio exige cuidado operativo. |
| Sistema PostgreSQL | Persistir modelo relacional existente. | Permanente | N/A | Crítico: fuente de verdad. | Inconsistencias si se altera DDL fuera de control. |

### Observaciones Pressman

- Los actores humanos tienen metas distintas, por lo que la navegación por rol reduce complejidad accidental.
- Los actores con más privilegios (`administrativo`, `superadmin`) tienen mayor impacto sobre integridad de datos.
- Los estudiantes son actores de alta frecuencia y baja tolerancia a mensajes técnicos; las validaciones deben comunicarse de forma clara.
- El sistema debe tratar a PostgreSQL como actor externo pasivo pero crítico, porque la aplicación depende de un esquema preexistente.

## 12. Riesgos técnicos

| Riesgo | Impacto | Probabilidad | Mitigación recomendada |
|---|---|---:|---|
| Cambios manuales en SQL rompen modelos `managed = False`. | Alto | Media | Mantener scripts versionados, revisar modelos tras cambios de DDL. |
| Roles o grupos mal asignados exponen datos. | Alto | Media | Probar usuarios demo por rol y crear tests de autorización. |
| Querysets de alcance incompletos ocultan datos válidos. | Medio-alto | Media | Añadir pruebas por rol para `scope.py`. |
| Estados financieros inconsistentes. | Alto | Media | Tests de transición de `Recibo` y `Matricula`. |
| Cálculo de indicadores costoso en muchos estudiantes. | Medio | Media | Cachear o precomputar si el volumen crece. |
| Ausencia de auditoría automática completa. | Medio | Media | Definir eventos críticos y registrar cambios de escritura. |
| Dependencias de diagramas no instaladas. | Bajo | Alta | Documentar instalación y usar `uv --with` para regeneración puntual. |
| Falta de despliegue cloud documentado. | Medio | Media | Crear guía específica cuando el proyecto salga del entorno local. |

## 13. Recomendaciones de mantenimiento

- Mantener separación entre lógica de negocio en formularios/servicios y presentación en templates.
- Centralizar nuevas reglas de alcance en `accounts.scope` para evitar duplicidad.
- Agregar tests para cada rol funcional y cada módulo crítico.
- Documentar cualquier cambio SQL junto con cambios en modelos Django.
- No cambiar `managed = False` sin una decisión técnica explícita.
- Mantener `README.md`, `docs/diagrams/` y este documento sincronizados con rutas y modelos.
- Usar fixtures o comandos de seed controlados para datos demo.
- Revisar periódicamente que `RoleRequiredMixin` cubra nuevas vistas.

## 14. Validación de dependencias

### 14.1 Dependencias del proyecto

El proyecto declara dependencias en `pyproject.toml`, entre ellas:

- Django
- django-environ
- psycopg
- Pillow
- pytest
- pytest-django
- Ruff

### 14.2 Dependencias documentales y de diagramas

Para diagramas se recomiendan:

- `django-extensions`
- `pylint`
- `graphviz`
- `plantuml`

Estas dependencias pueden instalarse como dev dependencies o usarse transitoriamente con `uv --with`, según la política del equipo.

### 14.3 Comandos mínimos de validación

```bash
uv run python backend/manage.py check
uv run ruff check backend/apps backend/config
uv run ruff format --check backend/apps backend/config
uv run pytest
```

### 14.4 Validaciones recomendadas por rol

- Login y dashboard con usuario estudiante.
- Login y dashboard con usuario docente.
- Login y dashboard con usuario coordinador.
- Login y dashboard con usuario decano.
- Login y dashboard con usuario administrativo.
- Login y dashboard con usuario superadmin.
- Intentos de acceso no autorizado a módulos restringidos.
- Creación/cancelación de inscripción.
- Edición de notas.
- Creación/anulación de recibo.
- Activación/cancelación/anulación de matrícula.
- Creación/asignación/evaluación/cancelación de homologación.
- Cálculo de indicadores con estudiantes sin datos, con datos parciales y con datos completos.

## 15. Conclusión

El proyecto presenta una arquitectura Django modular, alineada con dominios académicos y financieros claros. La decisión de preservar el esquema PostgreSQL mediante modelos `managed = False` reduce el riesgo de alterar la base relacional original, pero exige disciplina documental y pruebas de regresión cuando cambien tablas, relaciones o reglas.

La mayor fortaleza técnica actual es la separación explícita de roles, alcance y vistas por dominio. Los principales puntos de atención son la cobertura de pruebas por rol, la validación de transiciones de estado y la sincronización entre SQL, modelos Django y documentación.
