# Reglas de negocio y vista general del sistema

## 4. Reglas de negocio y vista general del sistema

Las reglas de negocio definen el comportamiento esperado del sistema y justifican las principales decisiones del modelo de datos.

A partir de estas reglas se derivan las entidades, relaciones, claves y restricciones que componen el modelo relacional.

## 4.1. Reglas sobre usuarios y especialización

Un usuario puede estar registrado en el sistema como estudiante, docente o administrativo.

Estas especializaciones no son totalmente excluyentes, ya que un usuario puede ser estudiante y docente al mismo tiempo.

Reglas definidas:

1. Todo usuario debe tener un documento único y un correo único.
2. Un usuario puede ser estudiante, docente o administrativo.
3. Un usuario puede ser estudiante y docente simultáneamente.
4. Un usuario puede ser administrativo y estar afiliado a una facultad.
5. Un usuario docente puede ejercer funciones académicas adicionales como coordinador de programa o decano.
6. Todo coordinador debe ser previamente un docente.
7. Todo decano debe ser previamente un docente.
8. Un coordinador tiene acceso y responsabilidad sobre un programa académico específico.
9. Un decano tiene acceso y responsabilidad sobre toda una facultad.
10. Un estudiante puede ser docente, pero no puede ser coordinador ni decano mientras esté clasificado únicamente como estudiante-docente. En ese caso solo puede ejercer el rol de profesor sin cargo académico-administrativo superior.
11. Para que un profesor pueda ejercer como coordinador o decano, debe estar registrado como docente y tener asignación académica en el sistema.

## 4.2. Reglas sobre administración de base de datos y permisos

El sistema contempla un usuario administrador o superusuario de PostgreSQL encargado exclusivamente de modificar esquemas, crear objetos de base de datos, administrar permisos y realizar configuraciones estructurales.

Ningún otro tipo de usuario tendrá permisos para modificar la estructura de la base de datos.

Reglas definidas:

1. El administrador o superusuario de PostgreSQL es el único usuario con permisos para crear, modificar o eliminar esquemas, tablas, vistas, funciones, restricciones y permisos.
2. Los coordinadores, docentes, estudiantes y administrativos acceden únicamente a la información permitida por su rol.
3. Los usuarios funcionales del sistema no deben tener permisos directos para alterar la estructura de la base de datos.
4. Las consultas institucionales se expondrán mediante vistas o mecanismos controlados, evitando acceso directo innecesario a tablas base.

## 4.3. Reglas sobre facultades, programas y cargos académicos

1. Una facultad puede tener muchos programas académicos.
2. Un programa académico pertenece a una única facultad.
3. Una facultad puede tener muchos profesores.
4. Una facultad puede tener muchos administrativos.
5. Una facultad puede tener un único decano por periodo académico.
6. Un programa académico puede tener un único coordinador por periodo académico.
7. El coordinador se asocia a un programa académico y a un periodo académico.
8. El decano se asocia a una facultad y a un periodo académico.

## 4.4. Reglas sobre asignaturas y programas académicos

1. Una asignatura puede pertenecer a muchos programas académicos.
2. Un programa académico puede tener muchas asignaturas.
3. La relación entre programa académico y asignatura se modela mediante la tabla `programa_asignatura`.
4. El semestre sugerido pertenece a la relación entre programa académico y asignatura.
5. El tipo de asignatura, obligatoria o electiva, pertenece a la relación entre programa académico y asignatura.
6. Una asignatura homologable debe tener horas prácticas iguales a cero.
7. El hecho de que una asignatura tenga horas prácticas iguales a cero no implica automáticamente que sea homologable.

## 4.5. Reglas sobre prerrequisitos

1. Una asignatura de un programa puede tener cero, uno o varios prerrequisitos.
2. Un prerrequisito corresponde a otra asignatura dentro del mismo plan de estudios.
3. Una asignatura no puede ser prerrequisito de sí misma.
4. No debe repetirse el mismo prerrequisito para una misma asignatura.
5. Se deben evitar ciclos de prerrequisitos.
6. Un estudiante no debe inscribir una asignatura si no ha aprobado previamente sus prerrequisitos.

## 4.6. Reglas sobre grupos académicos

1. Un grupo representa la oferta concreta de una asignatura de un programa en un periodo académico.
2. El identificador interno del grupo es técnico y no visible para el usuario.
3. El código del grupo es visible institucionalmente y puede repetirse en periodos académicos distintos.
4. No puede existir el mismo código de grupo para la misma asignatura-programa dentro del mismo periodo.
5. El cupo máximo pertenece al histórico del grupo ofertado en un periodo académico.
6. Si una política institucional de cupos cambia, no se actualizan los grupos históricos; el nuevo cupo aplica a los grupos creados posteriormente.
7. Un grupo puede existir sin docente asignado.
8. El sistema debe controlar que el número de estudiantes inscritos no supere el cupo máximo.

## 4.7. Reglas sobre inscripción, notas e intentos

1. Una inscripción relaciona a un estudiante con un grupo.
2. Un estudiante no puede inscribirse dos veces al mismo grupo.
3. Un estudiante no debe inscribirse en dos grupos de la misma asignatura-programa en el mismo periodo.
4. Un estudiante debe tener matrícula activa para poder inscribir asignaturas.
5. Las notas pertenecen a la inscripción.
6. La nota final se almacena en la inscripción.
7. El intento indica cuántas veces el estudiante ha cursado la asignatura.
8. Una inscripción aprobada o reprobada debe tener nota final.
9. Una inscripción en curso puede tener notas parciales o nulas.

## 4.8. Reglas sobre matrícula y pagos

1. Una tarifa de matrícula corresponde a un programa académico en un periodo académico.
2. Un programa académico solo puede tener una tarifa por periodo.
3. El recibo es individual para cada estudiante.
4. El recibo representa el proceso financiero.
5. La matrícula representa el proceso académico-administrativo.
6. Una matrícula nace a partir de un recibo.
7. Un recibo pagado puede activar una matrícula.
8. El estado de pago y el estado de matrícula son diferentes.
9. Una matrícula activa o finalizada consume el límite de matrículas del estudiante.
10. Una matrícula pendiente, cancelada o anulada no consume el límite de matrículas.
11. Las matrículas restantes no se almacenan directamente; se calculan a partir de las matrículas válidas.

## 4.9. Reglas sobre homologaciones

1. Una homologación pertenece a un estudiante.
2. Una homologación debe ser evaluada por un profesor.
3. La asignatura de origen se almacena como texto porque proviene de otra institución.
4. La institución de origen se almacena como texto.
5. La homologación se realiza contra una asignatura del programa académico del estudiante.
6. Solo se deben permitir homologaciones para asignaturas homologables.
7. Una homologación aprobada debe tener nota obtenida.
8. Un estudiante no debe tener más de una homologación aprobada para la misma asignatura del programa.

## 4.10. Reglas sobre indicadores académicos derivados

1. El rendimiento académico no se almacena directamente en la tabla `estudiante`.
2. El porcentaje de avance de carrera no se almacena directamente en la tabla `estudiante`.
3. El riesgo de deserción no se almacena directamente en la tabla `estudiante`.
4. Estos indicadores se calculan mediante consultas, vistas o procesos analíticos posteriores.
