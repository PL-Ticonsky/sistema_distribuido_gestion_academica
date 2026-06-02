# CONDOR 2 — Guía de Diseño UI/UX y Estándares Visuales

## Contexto General

CONDOR 2 es un sistema distribuido de gestión académica universitaria desarrollado con:

- Django
- PostgreSQL
- Templates Django
- Arquitectura modular por apps
- Base de datos relacional ya existente
- Modelos `managed = False`

Actualmente el sistema ya tiene implementadas todas las vistas en modo solo lectura para:

- accounts
- estructura
- academica
- financiera
- homologaciones
- auditoria

El objetivo de esta fase es transformar el sistema actual en una plataforma visualmente profesional, consistente y reutilizable antes de implementar CRUDs, permisos y lógica avanzada.

---

# Objetivo de la Fase 2

Implementar una capa visual moderna y consistente para todo el sistema CONDOR 2.

La prioridad NO es agregar lógica nueva todavía.

La prioridad es:

- mejorar experiencia visual
- unificar navegación
- crear layouts reutilizables
- estandarizar tablas
- mejorar accesibilidad y legibilidad
- preparar el sistema para CRUDs futuros

---

# Lineamientos Visuales

## Estilo General

El sistema debe tener apariencia:

- institucional
- académica
- profesional
- limpia
- moderna
- tipo ERP universitario

Debe evitar:

- estilos excesivamente coloridos
- diseño informal
- componentes recargados
- animaciones innecesarias

---

# Framework Visual

## Framework seleccionado

Bootstrap 5

### Razones

- integración rápida con Django Templates
- componentes reutilizables
- tablas responsivas
- navbar/sidebar simples
- formularios listos
- mantenimiento sencillo

No usar Tailwind por ahora.

---

# Tipografía Oficial

## Fuente principal

Inter

### Fallbacks

```css
font-family: 'Inter', sans-serif;
```

### Alternativas aceptables

- Roboto
- Source Sans 3
- Nunito Sans

---

# Paleta de Colores Oficial

## Colores principales

| Uso | Color |
|---|---|
| Principal | `#0F172A` |
| Secundario | `#1D4ED8` |
| Fondo general | `#F8FAFC` |
| Tarjetas | `#FFFFFF` |
| Texto principal | `#111827` |
| Texto secundario | `#6B7280` |
| Éxito | `#16A34A` |
| Advertencia | `#D97706` |
| Error | `#DC2626` |

---

# Arquitectura Visual

## Layout Global

Debe existir un layout base reutilizable para todo el sistema.

### Archivo esperado

```text
templates/base.html
```

### Este layout debe contener

- navbar superior
- sidebar lateral
- contenedor principal
- breadcrumbs
- footer simple
- espacio para mensajes
- bloques reutilizables

Todas las páginas deben extender `base.html`.

---

# Sidebar

El sidebar debe contener navegación agrupada por módulos.

## Módulos esperados

- Dashboard
- Estructura
- Académica
- Financiera
- Homologaciones
- Auditoría

Cada módulo debe tener:

- icono
- nombre
- enlaces organizados

---

# Navbar Superior

Debe contener:

- nombre CONDOR 2
- usuario autenticado
- botón logout
- breadcrumb simple

---

# Dashboard

## Objetivo

Convertir el dashboard actual en un panel administrativo profesional.

### Debe contener

- tarjetas por módulo
- accesos rápidos
- resumen institucional
- diseño limpio
- distribución responsive

---

# Tablas

Todas las tablas deben estandarizarse.

## Requisitos

Usar:

```html
table table-hover table-striped
```

### Las tablas deben incluir

- encabezados claros
- espaciado uniforme
- botones de detalle
- badges visuales
- mensaje vacío si no hay registros

---

# Estados Visuales

Todos los estados deben representarse visualmente mediante badges Bootstrap.

## Convenciones

| Estado | Badge |
|---|---|
| Activo | success |
| Inactivo | secondary |
| Pendiente | warning |
| Cancelado | danger |
| Aprobado | success |
| Reprobado | danger |
| En revisión | primary |
| Cursando | info |

---

# Navegación

Todas las vistas deben incluir:

- breadcrumbs
- botón volver
- títulos claros
- jerarquía visual consistente

---

# Paginación

Las vistas grandes deben implementar paginación.

## Aplicar en

- estudiantes
- profesores
- auditoría
- homologaciones
- inscripciones
- recibos

---

# Búsquedas

Agregar búsqueda básica en listados principales.

## Campos sugeridos

- nombre
- correo
- código
- documento
- programa
- estado

---

# Responsive Design

El sistema debe funcionar correctamente en:

- desktop
- laptop
- tablet

La prioridad principal es escritorio.

---

# Restricciones Técnicas

## No hacer todavía

- CRUDs
- escritura
- permisos por rol
- lógica compleja
- AJAX
- APIs
- React
- Tailwind
- migraciones
- modificación SQL

---

# Objetivo Final de la Fase 2

Al finalizar esta fase el sistema debe verse como un sistema institucional real y estar listo para:

- CRUDs
- permisos
- triggers
- validaciones
- despliegue

---

# Orden de Implementación Recomendado

## 1. Layout Global

Implementar:

- `base.html`
- sidebar
- navbar
- footer

---

## 2. Dashboard

Rediseñar dashboard principal.

---

## 3. Sistema de tablas

Estandarizar tablas y badges.

---

## 4. Navegación

Agregar breadcrumbs y botones volver.

---

## 5. Paginación

Implementar paginación reutilizable.

---

## 6. Búsquedas

Agregar filtros y buscadores básicos.

---

## 7. Refactor visual final

Uniformizar todo el sistema.

---

# Estado Actual del Proyecto

| Área | Estado |
|---|---|
| Modelo relacional | Completo |
| PostgreSQL | Muy avanzado |
| Vistas lectura | Completas |
| UI/UX | Pendiente |
| CRUD | Pendiente |
| Roles | Pendiente |
| Triggers | Pendiente |
| Distribución física | Pendiente |

---

# Filosofía del Proyecto

CONDOR 2 debe priorizar:

- claridad
- mantenibilidad
- escalabilidad
- separación modular
- consistencia visual
- facilidad de navegación

El sistema debe sentirse como una plataforma académica institucional seria.