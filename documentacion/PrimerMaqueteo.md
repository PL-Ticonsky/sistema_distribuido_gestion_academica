# Planteamiento del sistema de gestión académica

Se desea diseñar una base de datos normalizada para un sistema de gestión académica universitario. El sistema debe permitir gestionar usuarios, estudiantes, profesores, administrativos, facultades, programas académicos, asignaturas, periodos académicos, grupos, horarios, inscripciones, recibos de pago, notas, homologaciones y prerrequisitos de asignaturas.

---

## 1. Usuarios del sistema

El sistema contará con una entidad principal llamada **Usuario**, que representa a cualquier persona registrada en la plataforma.

### Atributos principales de Usuario

- Identificador del usuario.
- Tipo de documento.
- Número de documento.
- Nombre.
- Dirección.
- Correo electrónico.
- Contraseña.
- Fecha de creación.
- Teléfono.

### Observación

Un usuario puede tener más de un número telefónico. Por esta razón, el teléfono no debería almacenarse como un único atributo dentro de la entidad `Usuario`, sino en una entidad o tabla separada relacionada con el usuario.

---

## 2. Especialización de usuarios

Un usuario puede especializarse en tres tipos principales:

- Estudiante.
- Profesor.
- Administrativo.

Estas especializaciones representan los roles que puede tener una persona dentro del sistema académico.

### Regla de negocio importante

Un usuario puede ser **estudiante y profesor al mismo tiempo**.

Por ejemplo, una persona puede estar matriculada en un programa académico y, al mismo tiempo, dictar clases como profesor.

Por lo tanto, la especialización entre `Usuario`, `Estudiante`, `Profesor` y `Administrativo` no debe modelarse como totalmente excluyente, ya que al menos debe permitirse la combinación entre estudiante y profesor.

---

## 3. Profesores, coordinadores y decanos

La entidad **Profesor** representa a los usuarios que pueden dictar asignaturas o participar en procesos académicos.

### Atributos adicionales de Profesor

- Categoría.
- Tipo de vinculación.

Además, sobre la entidad `Profesor` existe una nueva especialización. Un profesor puede tener uno de los siguientes roles académicos adicionales:

- Profesor sin cargo académico-administrativo adicional.
- Coordinador de programa.
- Decano.

### Reglas de negocio

- Todo coordinador de programa debe ser profesor.
- Todo decano debe ser profesor.
- Un profesor puede no ser coordinador ni decano.
- Un profesor puede ser coordinador de programa o decano, pero no ambos al mismo tiempo.
- Un usuario puede ser profesor sin ser coordinador ni decano.
- Un usuario puede ser estudiante y profesor simultáneamente.
- Un estudiante no necesariamente es profesor.
- Un administrativo no necesariamente tiene atributos adicionales.

### Observación

Actualmente, ni el decano ni el coordinador de programa tienen atributos propios adicionales.

Por esta razón, se debe analizar si conviene representarlos como entidades independientes o si es suficiente modelarlos como roles o cargos asociados al profesor.

---

## 4. Administrativos

La especialización **Administrativo** representa a los usuarios que realizan funciones administrativas dentro del sistema.

Por el momento, los administrativos no tienen atributos adicionales distintos a los datos generales del usuario.

### Observación

Se debe evaluar si es necesario crear una entidad independiente para administrativos o si basta con registrar este rol mediante una relación o tabla de roles.

---

## 5. Facultades

La universidad está organizada en facultades.

### Atributos principales de Facultad

- Identificador de la facultad.
- Nombre de la facultad.
- Ubicación.
- Correo institucional.
- Teléfono.

### Observación

Una facultad también puede tener uno o varios teléfonos.

Por esta razón, el teléfono de una facultad debería modelarse en una tabla separada.

Se debe decidir si se usará una tabla general de teléfonos para diferentes entidades o si se crearán tablas separadas, por ejemplo:

- `TelefonoUsuario`
- `TelefonoFacultad`

---

## 6. Programas académicos

Una facultad puede tener muchos programas académicos, pero cada programa académico pertenece a una única facultad.

### Atributos principales de ProgramaAcademico

- Identificador del programa.
- Nombre del programa.
- Modalidad.
- Nivel de formación.
- Estado.

El estado del programa académico será **activo por defecto**, aunque también debe contemplarse la posibilidad de que un programa se encuentre **inactivo**.

### Reglas de negocio

- Una facultad puede tener muchos programas académicos.
- Un programa académico pertenece a una sola facultad.
- Un programa académico puede estar activo o inactivo.

---

## 7. Asignaturas

Los programas académicos están compuestos por asignaturas.

Una asignatura puede pertenecer a más de un programa académico.

Por ejemplo, la asignatura **Cálculo I** puede pertenecer tanto al programa de Ingeniería de Sistemas como al programa de Matemáticas.

Por lo tanto, la relación entre `ProgramaAcademico` y `Asignatura` debe modelarse como una relación de muchos a muchos.

### Atributos principales de Asignatura

- Código de asignatura.
- Nombre de la asignatura.
- Horas teóricas.
- Horas prácticas.
- Créditos.
- Semestre sugerido.
- Indicador de si la asignatura es homologable o no.

### Observación sobre semestre sugerido

Debe revisarse si el atributo `semestre_sugerido` pertenece realmente a la entidad `Asignatura` o a la relación entre `ProgramaAcademico` y `Asignatura`.

Esto se debe a que una misma asignatura podría estar sugerida en semestres diferentes dependiendo del programa académico.

Por ejemplo:

- Cálculo I podría estar sugerida en primer semestre para Ingeniería de Sistemas.
- La misma asignatura podría estar sugerida en segundo semestre para otro programa.

Por esta razón, una alternativa más normalizada sería ubicar el semestre sugerido en la tabla intermedia entre `ProgramaAcademico` y `Asignatura`.

### Reglas de negocio

- Un programa académico puede tener muchas asignaturas.
- Una asignatura puede pertenecer a muchos programas académicos.
- Algunas asignaturas pueden ser homologables y otras no.
- El código de la asignatura no cambia entre periodos académicos.

---

## 8. Prerrequisitos de asignaturas

Algunas asignaturas pueden tener prerrequisitos.

Un prerrequisito es una asignatura que debe haber sido aprobada previamente para poder cursar otra asignatura.

Esta relación debe modelarse como una autorrelación sobre la entidad `Asignatura`, ya que una asignatura puede estar relacionada con otra asignatura de la misma entidad.

### Reglas de negocio

- Una asignatura puede tener cero, uno o varios prerrequisitos.
- Una asignatura puede ser prerrequisito de muchas otras asignaturas.
- Una asignatura no puede ser prerrequisito de sí misma.
- Se deben evitar ciclos entre prerrequisitos.

### Ejemplo de ciclo no permitido

No debería permitirse que:

- La asignatura A tenga como prerrequisito a B.
- La asignatura B tenga como prerrequisito a A.

### Solución propuesta

Una forma normalizada de resolver esto es mediante una tabla intermedia llamada, por ejemplo, `PrerequisitoAsignatura`, con los siguientes campos:

- Código de la asignatura.
- Código de la asignatura prerrequisito.

De esta forma, se puede representar que una asignatura tenga múltiples prerrequisitos.

---

## 9. Periodos académicos

El sistema debe manejar periodos académicos, los cuales representan los intervalos de tiempo en los que se ofertan asignaturas y se generan grupos.

### Atributos principales de PeriodoAcademico

- Identificador del periodo académico.
- Fecha de inicio.
- Fecha final.
- Estado.

### Estados posibles del periodo académico

- Iniciado.
- En curso.
- Finalizado.

### Observación

Se debe revisar si los estados `iniciado` y `en curso` representan situaciones diferentes o si podrían considerarse redundantes.

---

## 10. Grupos académicos

Cuando una asignatura se oferta en un periodo académico, se crean uno o varios grupos.

Es importante aclarar que el código de la asignatura no cambia entre periodos académicos.

Por ejemplo, si Cálculo I tiene código 101, dicho código será el mismo en 2024-1, 2024-2 y en cualquier otro periodo académico.

Lo que cambia de un periodo a otro no es la asignatura, sino los grupos ofertados para esa asignatura.

Un grupo representa la oferta concreta de una asignatura en un periodo académico determinado.

### Atributos principales de Grupo

- Identificador del grupo.
- Cupo máximo.
- Estado.

### Estados posibles del grupo

- En curso.
- Finalizado.
- Cancelado.

### Reglas de negocio

- Una asignatura puede tener muchos grupos.
- Un grupo pertenece a una sola asignatura.
- Un periodo académico puede tener muchos grupos.
- Un grupo pertenece a un solo periodo académico.
- Una misma asignatura puede tener varios grupos en el mismo periodo académico.
- El código de la asignatura se mantiene constante, aunque se creen nuevos grupos en distintos periodos.

---

## 11. Horarios de los grupos

Cada grupo debe tener asociado un horario.

El horario no debería almacenarse como un único atributo de texto dentro de la entidad `Grupo`, porque un grupo puede tener varias sesiones durante la semana.

### Ejemplo

Un grupo puede tener clase:

- Los lunes de 8:00 a. m. a 10:00 a. m.
- Los miércoles de 10:00 a. m. a 12:00 p. m.

Por esta razón, el horario debería modelarse mediante una entidad separada relacionada con el grupo.

### Atributos posibles de Horario

- Identificador del horario.
- Día de la semana.
- Hora de inicio.
- Hora de finalización.
- Aula o salón, si se desea incluir esta información.

### Reglas de negocio

- Un grupo puede tener uno o varios horarios.
- Cada horario pertenece a un único grupo.
- Se deben evitar horarios duplicados o inconsistentes para un mismo grupo.

---

## 12. Inscripción de estudiantes a grupos

Un estudiante puede inscribirse en varios grupos durante un periodo académico.

A su vez, un grupo puede tener varios estudiantes inscritos, dependiendo del cupo máximo permitido.

Por lo tanto, la relación entre `Estudiante` y `Grupo` es de muchos a muchos y debe resolverse mediante una tabla intermedia.

Esta tabla representa la inscripción académica del estudiante a una asignatura específica mediante un grupo determinado.

Además, en esta relación deben almacenarse las notas del estudiante, ya que las calificaciones no pertenecen directamente al estudiante ni directamente a la asignatura, sino a la inscripción del estudiante en un grupo.

### Atributos posibles de Inscripcion

- Identificador de la inscripción.
- Estudiante.
- Grupo.
- Nota 1.
- Nota 2.
- Nota 3.
- Nota final.
- Estado de la inscripción.

### Estados posibles de la inscripción

- Cursando.
- Aprobada.
- Reprobada.
- Cancelada.
- Finalizada.

### Reglas de negocio

- Un estudiante puede estar inscrito en muchos grupos.
- Un grupo puede tener muchos estudiantes inscritos.
- La cantidad de estudiantes inscritos no debe superar el cupo máximo del grupo.
- Las notas pertenecen a la inscripción del estudiante en el grupo.
- Un estudiante no debería inscribirse dos veces al mismo grupo.
- Se debe validar si un estudiante puede inscribirse en dos grupos diferentes de la misma asignatura durante el mismo periodo académico.

---

## 13. Relación entre estudiantes y periodos académicos

Un estudiante puede estar vinculado a muchos periodos académicos, y un periodo académico puede tener muchos estudiantes asociados.

Esta relación representa la matrícula financiera o administrativa del estudiante en un periodo académico.

De esta relación surge el recibo de pago.

### Diferencia importante

Se debe diferenciar entre:

- La matrícula financiera o administrativa del periodo.
- La inscripción académica a grupos o asignaturas.

### Matrícula financiera

La matrícula financiera indica si el estudiante pagó o no el recibo correspondiente al periodo académico.

### Inscripción académica

La inscripción académica indica qué asignaturas o grupos está cursando el estudiante en ese periodo.

---

## 14. Recibos de pago

El recibo de pago representa el cobro de matrícula de un estudiante para un periodo académico determinado.

### Atributos principales de ReciboPago

- Identificador del recibo.
- Estudiante.
- Periodo académico.
- Precio.
- Medio de pago.
- Estado de pago.
- Fecha de pago.
- Detalles.

### Estados posibles del pago

- Pendiente.
- Pagado.
- Vencido.
- Anulado.

### Reglas de negocio

- Un estudiante puede tener muchos recibos, normalmente uno por cada periodo académico.
- Un periodo académico puede tener muchos recibos asociados.
- Un recibo pertenece a un único estudiante.
- Un recibo pertenece a un único periodo académico.
- El recibo representa el pago del periodo académico, no la inscripción a una asignatura específica.

---

## 15. Homologaciones

El sistema debe permitir que un estudiante solicite la homologación de una asignatura.

### Atributos principales de Homologacion

- Identificador de la homologación.
- Estudiante solicitante.
- Asignatura solicitada para homologación.
- Nota obtenida.
- Fecha de solicitud.
- Fecha de respuesta.
- Institución de origen.
- Estado de la homologación.
- Docente evaluador.

### Observación sobre institución de origen

La institución de origen no se modelará como una entidad independiente.

En este caso, será un dato ingresado manualmente por el estudiante.

### Reglas de negocio

- Un estudiante puede solicitar muchas homologaciones.
- Una homologación pertenece a un único estudiante.
- Una homologación corresponde a una única asignatura.
- Una homologación debe ser evaluada por un único docente.
- Un docente puede evaluar muchas homologaciones.
- Solo se deberían permitir solicitudes de homologación para asignaturas marcadas como homologables.
- La fecha de respuesta puede estar vacía mientras la solicitud esté pendiente.
- La nota puede registrarse como parte del resultado de la homologación.
- Un estudiante no debería tener más de una homologación aprobada para la misma asignatura.

### Ajuste de regla de negocio

Debe ajustarse la regla que dice que:

> Una materia puede ser homologada por una única homologación, mas no por muchas.

La interpretación más adecuada sería:

> Una misma asignatura puede ser solicitada en homologación por muchos estudiantes diferentes, pero un mismo estudiante no debería tener más de una homologación aprobada para la misma asignatura.

Esto permite que varios estudiantes homologuen Cálculo I, por ejemplo, pero evita duplicidades para un mismo estudiante.

---

# 16. Observaciones generales del modelo

Antes de construir el modelo entidad-relación, se deben tener en cuenta las siguientes observaciones.

---

## 16.1. Especialización de usuarios

Como un usuario puede ser estudiante y profesor al mismo tiempo, la especialización de `Usuario` hacia `Estudiante`, `Profesor` y `Administrativo` no debería ser totalmente excluyente.

Una opción adecuada es modelar `Usuario` como entidad principal y crear tablas separadas para:

- `Estudiante`
- `Profesor`
- `Administrativo`

Cada una de estas tablas usaría el mismo identificador del usuario como clave primaria y clave foránea.

De esta forma, si un usuario es estudiante y profesor, puede existir tanto en la tabla `Estudiante` como en la tabla `Profesor`.

---

## 16.2. Coordinador y decano

Como `Coordinador` y `Decano` no tienen atributos adicionales, se debe evaluar si realmente necesitan entidades independientes.

### Opciones de modelado

#### Opción 1: Subtipos de Profesor

Modelarlos como subtipos de `Profesor`.

#### Opción 2: Cargo del profesor

Modelarlos mediante un campo o relación que represente el cargo del profesor.

Si se desea mantener la estructura conceptual de especialización/generalización, se pueden representar como subtipos de `Profesor`, indicando que son excluyentes entre sí.

---

## 16.3. Administrativo

Como `Administrativo` no tiene atributos adicionales, podría representarse mediante una tabla simple que indique qué usuarios tienen ese rol.

También podría manejarse mediante una tabla general de roles, si se quiere un diseño más flexible.

---

## 16.4. Teléfonos

Como tanto usuarios como facultades pueden tener teléfonos, se debe decidir si se usará una tabla general de teléfonos o tablas separadas.

Una solución clara para un modelo académico sería usar:

- `TelefonoUsuario`
- `TelefonoFacultad`

Esto evita relaciones polimórficas y mantiene el modelo más simple.

---

## 16.5. Semestre sugerido

El atributo `semestre_sugerido` probablemente no debería estar directamente en `Asignatura`, sino en la relación entre `ProgramaAcademico` y `Asignatura`.

Esto se debe a que una misma asignatura puede pertenecer a distintos programas y estar recomendada en semestres diferentes.

---

## 16.6. Grupo académico

El grupo debe entenderse como la oferta concreta de una asignatura en un periodo académico.

No se debe confundir el grupo con la asignatura.

La asignatura mantiene:

- Código.
- Nombre.
- Créditos.
- Horas.

El grupo cambia en cada periodo académico y representa una instancia específica en la que se dicta esa asignatura.

---

## 16.7. Recibo vs. inscripción

Se debe separar claramente el recibo de pago de la inscripción académica.

### Recibo

El recibo corresponde al pago del periodo académico.

### Inscripción

La inscripción corresponde a los grupos o asignaturas que el estudiante toma durante ese periodo.

---

## 16.8. Prerrequisitos

Los prerrequisitos se deben modelar mediante una relación de la entidad `Asignatura` consigo misma.

Esto se puede resolver mediante una tabla intermedia llamada `PrerequisitoAsignatura`, en la cual se almacena qué asignatura requiere previamente a otra.