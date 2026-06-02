# Texto extraído completo del PDF original

> Este archivo conserva una extracción automática del PDF para consulta rápida. La documentación curada está distribuida en los demás archivos Markdown.


---

## Página 1


Universidad Distrital Francisco José de Caldas
Facultad de Ingeniería•Ingeniería de Sistemas
BASES DE DATOS
Sistema Distribuido de Gestión
Académica Universitaria
Primera entrega del proyecto
Planteamiento, modelo conceptual, modelo relacional y reglas de negocio
Modelo conceptual
Entidad–Relación
Modelo relacional
Tablas y claves
Reglas de negocio
Gestión académica
Autores
Nombre Código Correo institucional
Josue Urrego Lopez 20222020131jurregol@udistrital.edu.co
Alicia Pineda Quiroga 20222020047apinedaq@udistrital.edu.co
Jesus Mateo Munevar Mendez 20242020042jmmunevarm@udistrital.edu.co
TutorDaniel David Leal Lara
AsignaturaBases de Datos
TemaBase de datos distribuida para la gestión académica universitaria
Bogotá D.C., Colombia
21 de mayo de 2026



---

## Página 2


Sistema Distribuido de Gestión Académica 1
Índice
1. Introducción 3
2. Descripción general del sistema propuesto 3
2.1. Componentes principales . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 3
3. Alcance del documento 4
3.1. Elementos incluidos en esta entrega . . . . . . . . . . . . . . . . . . . . . . . 4
3.2. Elementos que se desarrollarán en etapas posteriores . . . . . . . . . . . . . 5
4. Reglas de negocio y vista general del sistema 5
4.1. Reglas sobre usuarios y especialización . . . . . . . . . . . . . . . . . . . . . 6
4.2. Reglas sobre administración de base de datos y permisos . . . . . . . . . . . 7
4.3. Reglas sobre facultades, programas y cargos académicos . . . . . . . . . . . . 7
4.4. Reglas sobre asignaturas y programas académicos . . . . . . . . . . . . . . . 8
4.5. Reglas sobre prerrequisitos . . . . . . . . . . . . . . . . . . . . . . . . . . . . 8
4.6. Reglas sobre grupos académicos . . . . . . . . . . . . . . . . . . . . . . . . . 8
4.7. Reglas sobre inscripción, notas e intentos . . . . . . . . . . . . . . . . . . . . 9
4.8. Reglas sobre matrícula y pagos . . . . . . . . . . . . . . . . . . . . . . . . . 9
4.9. Reglas sobre homologaciones . . . . . . . . . . . . . . . . . . . . . . . . . . . 10
4.10. Reglas sobre indicadores académicos derivados . . . . . . . . . . . . . . . . . 11
5. Diseño conceptual del modelo Entidad–Relación 11
5.1. Entidades conceptuales principales . . . . . . . . . . . . . . . . . . . . . . . 11
5.2. Descripción conceptual de relaciones principales . . . . . . . . . . . . . . . . 12
5.3. Diagrama conceptual . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 12
6. Modelo relacional 13



---

## Página 3


Sistema Distribuido de Gestión Académica 2
6.1. Estrategia de identificación de registros . . . . . . . . . . . . . . . . . . . . . 14
6.2. Diagrama relacional . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
6.3. Esquema de tablas . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
7. Diccionario de datos 20
8. Identificación de claves primarias y claves foráneas 24
8.1. Criterio de selección de claves primarias . . . . . . . . . . . . . . . . . . . . . 24
8.2. Resumen de claves primarias . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
9. Consideraciones preliminares sobre distribución 26
10.Conclusiones 27



---

## Página 4


Sistema Distribuido de Gestión Académica 3
1. Introducción
El presente documento expone la primera entrega del proyecto correspondiente al diseño
de una base de datos distribuida para un sistema de gestión académica universitaria. El
objetivo principal es plantear un modelo de datos que permita administrar usuarios, estu-
diantes, docentes, administrativos, facultades, programas académicos, asignaturas, grupos,
inscripciones, matrículas, pagos, homologaciones y procesos académicos asociados.
El sistema se concibe como una solución orientada a una arquitectura distribuida, en la cual
cada facultad conserva autonomía sobre la información académica que administra, pero al
mismo tiempo se mantiene la posibilidad de realizar consultas institucionales consolidadas.
Esta primera entrega no implementa todavía la distribución física, sino que deja construido
el planteamiento lógico y relacional necesario para etapas posteriores.
El documento incluye la descripción general del sistema, el alcance de la entrega, las reglas de
negocio principales, el diseño conceptual del modelo Entidad–Relación, el modelo relacional,
el esquema de tablas, la identificación de claves primarias y foráneas, y un diccionario de
datos preliminar.
2. Descripción general del sistema propuesto
El sistema propuesto corresponde a una plataforma universitaria para la gestión académica
y administrativa de una institución organizada por facultades. Cada facultad administra sus
programas académicos, docentes, estudiantes, grupos y procesos asociados, mientras que la
institución conserva información común necesaria para la operación general, como usuarios,
periodos académicos, auditoría, pagos, matrículas y reportes institucionales.
Propósito del sistema
El sistema busca integrar la gestión académica universitaria mediante una base de datos
que permita registrar, consultar y controlar información de estudiantes, profesores, admi-
nistrativos, programas académicos, asignaturas, grupos, inscripciones, notas, matrículas,
pagos y homologaciones.
2.1. Componentes principales
El sistema se estructura en los siguientes componentes:



---

## Página 5


Sistema Distribuido de Gestión Académica 4
Componente Descripción
Usuarios y roles Registra las personas del sistema y sus especializaciones como
estudiantes, docentes o administrativos.
Facultades y programas Representa la estructura académica institucional.
Asignaturas y planes Permite asociar asignaturas a programas académicos mediante planes
de estudio.
Grupos académicos Modela la oferta concreta de asignaturas por periodo académico.
Inscripciones y notas Registra las asignaturas cursadas por los estudiantes, sus notas,
intentos y estado académico.
Matrícula y pagos Gestiona tarifas, recibos individuales y estados de matrícula.
Homologaciones Permite solicitar y evaluar equivalencias de asignaturas cursadas en
otras instituciones.
Auditoría Registra acciones relevantes ejecutadas por usuarios del sistema.
Tabla 1: Componentes principales del sistema propuesto.
3. Alcance del documento
Esta primera entrega se enfoca en la definición estructural y lógica de la base de datos.
No corresponde todavía a la implementación completa del sistema en PostgreSQL ni a la
configuración física de esquemas distribuidos.
3.1. Elementos incluidos en esta entrega
Documento del proyecto.
Descripción general del sistema propuesto.
Diseño conceptual del modelo Entidad–Relación.
Modelo relacional.
Esquema de tablas.
Diccionario de datos preliminar.



---

## Página 6


Sistema Distribuido de Gestión Académica 5
Identificación de claves primarias y claves foráneas.
Reglas de negocio.
3.2. Elementos que se desarrollarán en etapas posteriores
Scripts SQL de creación de base de datos, esquemas y tablas.
Configuración de roles y permisos en PostgreSQL.
Creación de vistas institucionales.
Consultas SQL requeridas.
Inserción de datos de prueba.
Evidencias de ejecución.
Estrategia detallada de distribución física de la información.
Manual técnico de instalación y ejecución.
Nota sobre validaciones futuras
Algunas reglas de negocio, como el control de cupos, el cumplimiento de prerrequisitos, el
límite de matrículas y la consistencia entre estados de pago y matrícula, se dejan definidas
a nivel conceptual y relacional. Su implementación específica se abordará posteriormente
mediante restricciones, consultas, procedimientos o lógica de aplicación, según el alcance
final del proyecto.
4. Reglas de negocio y vista general del sistema
Las reglas de negocio definen el comportamiento esperado del sistema y justifican las prin-
cipales decisiones del modelo de datos. A partir de estas reglas se derivan las entidades,
relaciones, claves y restricciones que componen el modelo relacional.



---

## Página 7


Sistema Distribuido de Gestión Académica 6
4.1. Reglas sobre usuarios y especialización
Especialización de usuarios
Un usuario puede estar registrado en el sistema como estudiante, docente o administra-
tivo. Estas especializaciones no son totalmente excluyentes, ya que un usuario puede ser
estudiante y docente al mismo tiempo.
Las reglas definidas son:
1. Todo usuario debe tener un documento único y un correo único.
2. Un usuario puede ser estudiante, docente o administrativo.
3. Un usuario puede ser estudiante y docente simultáneamente.
4. Un usuario puede ser administrativo y estar afiliado a una facultad.
5. Un usuario docente puede ejercer funciones académicas adicionales como coordinador
de programa o decano.
6. Todo coordinador debe ser previamente un docente.
7. Todo decano debe ser previamente un docente.
8. Un coordinador tiene acceso y responsabilidad sobre un programa académico especí-
fico.
9. Un decano tiene acceso y responsabilidad sobre toda una facultad.
10. Un estudiante puede ser docente, pero no puede ser coordinador ni decano mientras
esté clasificado únicamente como estudiante-docente. En ese caso solo puede ejercer
el rol de profesor sin cargo académico-administrativo superior.
11. Para que un profesor pueda ejercer como coordinador o decano, debe estar registrado
como docente y tener asignación académica en el sistema.



---

## Página 8


Sistema Distribuido de Gestión Académica 7
4.2. Reglas sobre administración de base de datos y permisos
Administrador de PostgreSQL
El sistema contempla un usuario administrador o superusuario de PostgreSQL encargado
exclusivamente de modificar esquemas, crear objetos de base de datos, administrar permi-
sos y realizar configuraciones estructurales. Ningún otro tipo de usuario tendrá permisos
para modificar la estructura de la base de datos.
Las reglas definidas son:
1. El administrador o superusuario de PostgreSQL es el único usuario con permisos
para crear, modificar o eliminar esquemas, tablas, vistas, funciones, restricciones y
permisos.
2. Los coordinadores, docentes, estudiantes y administrativos acceden únicamente a la
información permitida por su rol.
3. Los usuarios funcionales del sistema no deben tener permisos directos para alterar la
estructura de la base de datos.
4. Las consultas institucionales se expondrán mediante vistas o mecanismos controlados,
evitando acceso directo innecesario a tablas base.
4.3. Reglas sobre facultades, programas y cargos académicos
1. Una facultad puede tener muchos programas académicos.
2. Un programa académico pertenece a una única facultad.
3. Una facultad puede tener muchos profesores.
4. Una facultad puede tener muchos administrativos.
5. Una facultad puede tener un único decano por periodo académico.
6. Un programa académico puede tener un único coordinador por periodo académico.
7. El coordinador se asocia a un programa académico y a un periodo académico.
8. El decano se asocia a una facultad y a un periodo académico.



---

## Página 9


Sistema Distribuido de Gestión Académica 8
4.4. Reglas sobre asignaturas y programas académicos
1. Una asignatura puede pertenecer a muchos programas académicos.
2. Un programa académico puede tener muchas asignaturas.
3. La relación entre programa académico y asignatura se modela mediante la tabla
programa_asignatura.
4. El semestre sugerido pertenece a la relación entre programa académico y asignatura.
5. El tipo de asignatura, obligatoria o electiva, pertenece a la relación entre programa
académico y asignatura.
6. Una asignatura homologable debe tener horas prácticas iguales a cero.
7. El hecho de que una asignatura tenga horas prácticas iguales a cero no implica auto-
máticamente que sea homologable.
4.5. Reglas sobre prerrequisitos
1. Una asignatura de un programa puede tener cero, uno o varios prerrequisitos.
2. Un prerrequisito corresponde a otra asignatura dentro del mismo plan de estudios.
3. Una asignatura no puede ser prerrequisito de sí misma.
4. No debe repetirse el mismo prerrequisito para una misma asignatura.
5. Se deben evitar ciclos de prerrequisitos.
6. Un estudiante no debe inscribir una asignatura si no ha aprobado previamente sus
prerrequisitos.
4.6. Reglas sobre grupos académicos
1. Un grupo representa la oferta concreta de una asignatura de un programa en un
periodo académico.
2. El identificador interno del grupo es técnico y no visible para el usuario.



---

## Página 10


Sistema Distribuido de Gestión Académica 9
3. El código del grupo es visible institucionalmente y puede repetirse en periodos aca-
démicos distintos.
4. No puede existir el mismo código de grupo para la misma asignatura-programa dentro
del mismo periodo.
5. El cupo máximo pertenece al histórico del grupo ofertado en un periodo académico.
6. Si una política institucional de cupos cambia, no se actualizan los grupos históricos;
el nuevo cupo aplica a los grupos creados posteriormente.
7. Un grupo puede existir sin docente asignado.
8. El sistema debe controlar que el número de estudiantes inscritos no supere el cupo
máximo.
4.7. Reglas sobre inscripción, notas e intentos
1. Una inscripción relaciona a un estudiante con un grupo.
2. Un estudiante no puede inscribirse dos veces al mismo grupo.
3. Un estudiante no debe inscribirse en dos grupos de la misma asignatura-programa en
el mismo periodo.
4. Un estudiante debe tener matrícula activa para poder inscribir asignaturas.
5. Las notas pertenecen a la inscripción.
6. La nota final se almacena en la inscripción.
7. El intento indica cuántas veces el estudiante ha cursado la asignatura.
8. Una inscripción aprobada o reprobada debe tener nota final.
9. Una inscripción en curso puede tener notas parciales o nulas.
4.8. Reglas sobre matrícula y pagos
1. Una tarifa de matrícula corresponde a un programa académico en un periodo acadé-
mico.



---

## Página 11


Sistema Distribuido de Gestión Académica 10
2. Un programa académico solo puede tener una tarifa por periodo.
3. El recibo es individual para cada estudiante.
4. El recibo representa el proceso financiero.
5. La matrícula representa el proceso académico-administrativo.
6. Una matrícula nace a partir de un recibo.
7. Un recibo pagado puede activar una matrícula.
8. El estado de pago y el estado de matrícula son diferentes.
9. Una matrícula activa o finalizada consume el límite de matrículas del estudiante.
10. Una matrícula pendiente, cancelada o anulada no consume el límite de matrículas.
11. Las matrículas restantes no se almacenan directamente; se calculan a partir de las
matrículas válidas.
4.9. Reglas sobre homologaciones
1. Una homologación pertenece a un estudiante.
2. Una homologación debe ser evaluada por un profesor.
3. La asignatura de origen se almacena como texto porque proviene de otra institución.
4. La institución de origen se almacena como texto.
5. La homologación se realiza contra una asignatura del programa académico del estu-
diante.
6. Solo se deben permitir homologaciones para asignaturas homologables.
7. Una homologación aprobada debe tener nota obtenida.
8. Un estudiante no debe tener más de una homologación aprobada para la misma
asignatura del programa.



---

## Página 12


Sistema Distribuido de Gestión Académica 11
4.10. Reglas sobre indicadores académicos derivados
1. El rendimiento académico no se almacena directamente en la tabla estudiante.
2. Elporcentajedeavancedecarreranosealmacenadirectamenteenlatablaestudiante.
3. El riesgo de deserción no se almacena directamente en la tabla estudiante.
4. Estos indicadores se calculan mediante consultas, vistas o procesos analíticos poste-
riores.
5. Diseño conceptual del modelo Entidad–Relación
El diseño conceptual identifica las entidades principales del sistema y sus relaciones desde una
perspectiva de negocio. Este modelo permite representar los objetos relevantes del dominio
académico antes de transformarlos en tablas relacionales.
5.1. Entidades conceptuales principales
En lugar de listar únicamente las entidades, se presenta una clasificación funcional que per-
mite entender el papel de cada una dentro del sistema.
Grupo conceptual Entidades asociadas
Personas y roles Usuario, Estudiante, Profesor, Administrativo, Coordinador, Decano.
Estructura institucional Facultad, Programa académico.
Estructura académica Asignatura, Programa-asignatura, Prerrequisito, Periodo académico.
Oferta académica Grupo, Inscripción.
Gestión financiera Tarifa de matrícula, Recibo, Matrícula.
Procesos académicos
especiales
Homologación.
Control institucional Auditoría.
Tabla 2: Clasificación de entidades conceptuales principales.



---

## Página 13


Sistema Distribuido de Gestión Académica 12
5.2. Descripción conceptual de relaciones principales
Relación conceptual Descripción
Usuario–Estudiante Un usuario puede especializarse como estudiante.
Usuario–Profesor Un usuario puede especializarse como profesor.
Usuario–Administrativo Un usuario puede especializarse como administrativo afiliado a una
facultad.
Profesor–Coordinador Un profesor puede ejercer como coordinador de un programa en un
periodo.
Profesor–Decano Un profesor puede ejercer como decano de una facultad en un
periodo.
Facultad–Programa Una facultad puede tener varios programas académicos.
Programa–Asignatura Un programa puede tener muchas asignaturas y una asignatura
puede pertenecer a muchos programas.
Programa-asignatura–
Grupo
Un grupo oferta una asignatura específica de un programa en un
periodo académico.
Grupo–Inscripción Un estudiante se inscribe en un grupo mediante una inscripción.
Tarifa–Recibo–Matrícula La tarifa define el valor base; el recibo registra el pago individual;
la matrícula registra el estado académico-administrativo.
Tabla 3: Relaciones conceptuales principales del sistema.
5.3. Diagrama conceptual
EnestasecciónsedebeinsertareldiagramaconceptualEntidad–Relaciónoriginaldelsistema.



---

## Página 14


Sistema Distribuido de Gestión Académica 13
Figura 1: Diseño conceptual del modelo Entidad–Relación.
6. Modelo relacional
El modelo relacional corresponde a la transformación del diseño conceptual en un conjunto
de tablas, atributos, claves primarias, claves foráneas y restricciones. En esta etapa se define
cómo se representará la información dentro de la base de datos.



---

## Página 15


Sistema Distribuido de Gestión Académica 14
6.1. Estrategia de identificación de registros
Para la identificación de registros se adopta una estrategia mixta:
Se utilizan llaves internas de tipouuidpara tablas operativas, transaccionales y de
personas.
Se utilizan llaves de tipovarcharpara catálogos institucionales estables.
Los identificadoresuuidserán generados automáticamente por la base de datos mediante
gen_random_uuid(), evitando el uso de llaves autoincrementales y reduciendo la dependencia
de consecutivos globales.
6.2. Diagrama relacional
En esta sección se debe insertar el diagrama relacional final de la base de datos.
Figura 2: Modelo relacional del sistema de gestión académica.



---

## Página 16


Sistema Distribuido de Gestión Académica 15
6.3. Esquema de tablas
Para evitar problemas de desbordamiento visual, el esquema de tablas se presenta en bloques
compactos. Cada bloque contiene la definición resumida de atributos, claves y restricciones
principales.
usuario (
PK id_usuario uuid default gen_random_uuid(),
nombre varchar(50) not null,
tipo_de_documento enum(’CC’, ’TI’, ’CE’) not null,
numero_de_documento varchar(10) not null,
correo varchar(30) not null,
direccion varchar(30),
hashed_password varchar(255) not null,
fecha_de_creacion date not null,
unique(tipo_de_documento, numero_de_documento),
unique(correo)
)
estudiante (
PK id_estudiante uuid default gen_random_uuid(),
FK id_usuario(usuario.id_usuario) not null unique,
FK id_programa_academico(programa_academico.id_programa_academico) not null,
limite_matriculas int default 15 not null,
estado_estudiante enum(’Activo’, ’Inactivo’, ’Suspendido’, ’Retirado’, ’Egresado’)
not null
)
profesor (
PK id_profesor uuid default gen_random_uuid(),
FK id_usuario(usuario.id_usuario) not null unique,
FK id_facultad(facultad.id_facultad) not null,
categoria enum(’Auxiliar’, ’Asistente’, ’Asociado’, ’Titular’),
vinculacion enum(’Planta’, ’Catedra’, ’Ocasional’)
)
administrativo (
PK id_administrativo uuid default gen_random_uuid(),
FK id_usuario(usuario.id_usuario) not null unique,
FK id_facultad(facultad.id_facultad) not null,
detalles varchar(255)
)



---

## Página 17


Sistema Distribuido de Gestión Académica 16
auditoria (
PK id_auditoria uuid default gen_random_uuid(),
FK id_usuario(usuario.id_usuario) not null,
accion_realizada varchar(100) not null,
fecha_hora timestamp not null,
descripcion varchar(255)
)
facultad (
PK id_facultad varchar(10),
ubicacion varchar(80),
nombre_facultad varchar(80) not null,
correo_institucional varchar(80) unique
)
programa_academico (
PK id_programa_academico varchar(20),
FK id_facultad(facultad.id_facultad) not null,
nombre_programa varchar(80) not null,
estado enum(’Activo’, ’Inactivo’) not null,
modalidad enum(’Presencial’, ’Virtual’, ’Hibrida’) not null,
nivel_formacion enum(’Tecnico’, ’Tecnologico’, ’Pregrado’,
’Especializacion’, ’Maestria’, ’Doctorado’) not null
)
periodo_academico (
PK id_periodo_academico varchar(10),
fecha_inicio date not null,
fecha_final date not null,
estado enum(’Planeado’, ’Activo’, ’Finalizado’, ’Cancelado’) not null,
check(fecha_final > fecha_inicio)
)
tarifa_matricula (
PK id_tarifa_matricula uuid default gen_random_uuid(),
FK id_programa_academico(programa_academico.id_programa_academico) not null,
FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
valor_matricula numeric(12,2) not null,
fecha_limite_ordinaria date not null,



---

## Página 18


Sistema Distribuido de Gestión Académica 17
fecha_limite_extraordinaria date not null,
estado enum(’Activa’, ’Inactiva’) not null,
unique(id_programa_academico, id_periodo_academico),
check(valor_matricula >= 0),
check(fecha_limite_extraordinaria >= fecha_limite_ordinaria)
)
recibo (
PK id_recibo uuid default gen_random_uuid(),
FK id_estudiante(estudiante.id_estudiante) not null,
FK id_tarifa_matricula(tarifa_matricula.id_tarifa_matricula) not null,
fecha_pago date,
valor_pagado numeric(12,2),
metodo_pago enum(’Efectivo’, ’Tarjeta’, ’PSE’, ’Transferencia’, ’Consignacion’),
estado_pago enum(’Pendiente’, ’Pagado’, ’Vencido’, ’Anulado’) not null,
extras numeric(12,2) default 0,
unique(id_estudiante, id_tarifa_matricula),
check(valor_pagado >= 0),
check(extras >= 0)
)
matricula (
PK id_matricula uuid default gen_random_uuid(),
FK id_recibo(recibo.id_recibo) not null unique,
estado_matricula enum(’Pendiente’, ’Activa’, ’Finalizada’, ’Cancelada’, ’Anulada’)
not null
)
asignatura (
PK cod_asignatura varchar(20),
nombre_asignatura varchar(80) not null,
creditos int not null,
estado enum(’Activa’, ’Inactiva’) not null,
horas_teoria int not null,
horas_pract int not null,
homologable boolean not null,
check(creditos > 0),
check(horas_teoria >= 0),
check(horas_pract >= 0),
check(homologable = false or horas_pract = 0)
)



---

## Página 19


Sistema Distribuido de Gestión Académica 18
programa_asignatura (
PK id_programa_asignatura uuid default gen_random_uuid(),
FK id_programa_academico(programa_academico.id_programa_academico) not null,
FK cod_asignatura(asignatura.cod_asignatura) not null,
semestre_sugerido int not null,
tipo_asignatura enum(’Obligatoria’, ’Electiva’) not null,
estado enum(’Activa’, ’Inactiva’) not null,
unique(id_programa_academico, cod_asignatura),
check(semestre_sugerido > 0)
)
pre_requisitos (
PK id_pre_requisito uuid default gen_random_uuid(),
FK id_programa_academico(programa_academico.id_programa_academico) not null,
FK id_programa_asignatura(programa_asignatura.id_programa_asignatura) not null,
FK id_programa_asignatura_requisito(programa_asignatura.id_programa_asignatura) not
null,
unique(id_programa_asignatura, id_programa_asignatura_requisito),
check(id_programa_asignatura <> id_programa_asignatura_requisito)
)
grupo (
PK id_grupo uuid default gen_random_uuid(),
FK id_programa_asignatura(programa_asignatura.id_programa_asignatura) not null,
FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
FK id_docente(profesor.id_profesor),
codigo_grupo varchar(20) not null,
cupo_maximo int not null,
estado_grupo enum(’Abierto’, ’En curso’, ’Finalizado’, ’Cancelado’) not null,
unique(id_programa_asignatura, id_periodo_academico, codigo_grupo),
check(cupo_maximo > 0)
)
inscripcion (
PK id_inscripcion uuid default gen_random_uuid(),
FK id_grupo(grupo.id_grupo) not null,
FK id_estudiante(estudiante.id_estudiante) not null,
nota1 numeric(3,2),
nota2 numeric(3,2),
nota3 numeric(3,2),
nota_final numeric(3,2),



---

## Página 20


Sistema Distribuido de Gestión Académica 19
intento int not null,
estado_inscripcion enum(’Cursando’, ’Aprobada’, ’Reprobada’, ’Cancelada’) not null,
unique(id_grupo, id_estudiante),
check(nota1 between 0 and 5),
check(nota2 between 0 and 5),
check(nota3 between 0 and 5),
check(nota_final between 0 and 5),
check(intento > 0)
)
homologacion (
PK id_homologacion uuid default gen_random_uuid(),
FK id_profesor_evaluador(profesor.id_profesor) not null,
FK id_estudiante(estudiante.id_estudiante) not null,
asignatura_origen varchar(100) not null,
institucion_origen varchar(100) not null,
FK id_programa_asignatura(programa_asignatura.id_programa_asignatura) not null,
fecha_solicitud date not null,
estado_homologacion enum(’Solicitada’, ’En revision’, ’Aprobada’,
’Rechazada’, ’Cancelada’) not null,
observacion varchar(255),
fecha_respuesta date,
nota_obtenida numeric(3,2),
check(nota_obtenida between 0 and 5)
)
decano (
PK id_decano uuid default gen_random_uuid(),
FK id_profesor(profesor.id_profesor) not null,
FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
FK id_facultad(facultad.id_facultad) not null,
unique(id_facultad, id_periodo_academico)
)
coordinador (
PK id_coordinador uuid default gen_random_uuid(),
FK id_profesor(profesor.id_profesor) not null,
FK id_periodo_academico(periodo_academico.id_periodo_academico) not null,
FK id_programa_academico(programa_academico.id_programa_academico) not null,
unique(id_programa_academico, id_periodo_academico)
)



---

## Página 21


Sistema Distribuido de Gestión Académica 20
7. Diccionario de datos
Eldiccionariodedatos describelos atributosprincipalesdelmodelorelacional. Paramantener
una presentación clara dentro del formato vertical del documento, la tabla se ajusta al ancho
de la página sin cambiar la orientación general del informe.
Tabla 4: Diccionario de datos preliminar del sistema.
Dato examinado Tabla de origen Tipo de dato ¿Nulo? ¿PK? Descripción
id_usuario usuario uuid No Sí Identificador interno único
del usuario.
nombre usuario varchar(50) No No Nombre completo del
usuario.
tipo_de_documento usuario enum No No Tipo de documento del
usuario.
numero_de_documento usuario varchar(10) No No Número de documento del
usuario.
correo usuario varchar(30) No No Correo electrónico del
usuario.
direccion usuario varchar(30) Sí No Dirección de residencia o
contacto del usuario.
hashed_password usuario varchar(255) No No Hash seguro de la
contraseña.
fecha_de_creacion usuario date No No Fecha de creación del
usuario en el sistema.
id_estudiante estudiante uuid No Sí Identificador interno del
estudiante.
id_usuario estudiante uuid No No Referencia al usuario
asociado al estudiante.
id_programa_academico estudiante varchar(20) No No Programa académico al que
pertenece el estudiante.
limite_matriculas estudiante int No No Número máximo de matrículas
permitidas.
estado_estudiante estudiante enum No No Estado
académico-administrativo
del estudiante.
id_profesor profesor uuid No Sí Identificador interno del
profesor.
id_usuario profesor uuid No No Referencia al usuario
asociado al profesor.
id_facultad profesor varchar(10) No No Facultad a la que pertenece
el profesor.
categoria profesor enum Sí No Categoría académica del
profesor.
vinculacion profesor enum Sí No Tipo de vinculación del
profesor.



---

## Página 22


Sistema Distribuido de Gestión Académica 21
Dato examinado Tabla de origen Tipo de dato ¿Nulo? ¿PK? Descripción
id_administrativo administrativo uuid No Sí Identificador interno del
administrativo.
id_usuario administrativo uuid No No Referencia al usuario
asociado al administrativo.
id_facultad administrativo varchar(10) No No Facultad a la que se
encuentra afiliado.
detalles administrativo varchar(255) Sí No Descripción del cargo, área
o funciones
administrativas.
id_facultad facultad varchar(10) No Sí Código institucional de la
facultad.
ubicacion facultad varchar(80) Sí No Ubicación física o sede de
la facultad.
nombre_facultad facultad varchar(80) No No Nombre oficial de la
facultad.
correo_institucional facultad varchar(80) Sí No Correo institucional de la
facultad.
id_programa_academico programa_
academico
varchar(20) No Sí Código institucional del
programa académico.
id_facultad programa_
academico
varchar(10) No No Facultad a la que pertenece
el programa.
nombre_programa programa_
academico
varchar(80) No No Nombre oficial del programa
académico.
estado programa_
academico
enum No No Estado del programa
académico.
modalidad programa_
academico
enum No No Modalidad de oferta del
programa.
nivel_formacion programa_
academico
enum No No Nivel académico del
programa.
id_periodo_academico periodo_academico varchar(10) No Sí Código del periodo
académico.
fecha_inicio periodo_academico date No No Fecha de inicio del periodo
académico.
fecha_final periodo_academico date No No Fecha de finalización del
periodo académico.
estado periodo_academico enum No No Estado del periodo
académico.
id_tarifa_matricula tarifa_matricula uuid No Sí Identificador interno de la
tarifa.
id_programa_academico tarifa_matricula varchar(20) No No Programa al que aplica la
tarifa.
id_periodo_academico tarifa_matricula varchar(10) No No Periodo al que aplica la
tarifa.
valor_matricula tarifa_matricula numeric(12,2) No No Valor base de matrícula del
programa en el periodo.
fecha_limite_ordinaria tarifa_matricula date No No Fecha límite de pago
ordinario.



---

## Página 23


Sistema Distribuido de Gestión Académica 22
Dato examinado Tabla de origen Tipo de dato ¿Nulo? ¿PK? Descripción
fecha_limite_
extraordinaria
tarifa_matricula date No No Fecha límite de pago
extraordinario.
estado tarifa_matricula enum No No Estado de la tarifa.
id_recibo recibo uuid No Sí Identificador interno del
recibo.
id_estudiante recibo uuid No No Estudiante al que pertenece
el recibo.
id_tarifa_matricula recibo uuid No No Tarifa asociada al recibo.
fecha_pago recibo date Sí No Fecha en la que se realizó
el pago.
valor_pagado recibo numeric(12,2) Sí No Valor efectivamente pagado
por el estudiante.
metodo_pago recibo enum Sí No Medio utilizado para
realizar el pago.
estado_pago recibo enum No No Estado financiero del
recibo.
extras recibo numeric(12,2) Sí No Valor adicional aplicado al
recibo.
id_matricula matricula uuid No Sí Identificador interno de la
matrícula.
id_recibo matricula uuid No No Recibo que origina la
matrícula.
estado_matricula matricula enum No No Estado
académico-administrativo de
la matrícula.
cod_asignatura asignatura varchar(20) No Sí Código institucional de la
asignatura.
nombre_asignatura asignatura varchar(80) No No Nombre oficial de la
asignatura.
creditos asignatura int No No Número de créditos
académicos.
estado asignatura enum No No Estado de la asignatura.
horas_teoria asignatura int No No Número de horas teóricas.
horas_pract asignatura int No No Número de horas prácticas.
homologable asignatura boolean No No Indica si la asignatura
puede ser homologada.
id_programa_asignatura programa_
asignatura
uuid No Sí Identificador interno de la
relación
programa-asignatura.
id_programa_academico programa_
asignatura
varchar(20) No No Programa académico
asociado.
cod_asignatura programa_
asignatura
varchar(20) No No Asignatura asociada.
semestre_sugerido programa_
asignatura
int No No Semestre sugerido dentro
del programa.
tipo_asignatura programa_
asignatura
enum No No Tipo de asignatura dentro
del programa.



---

## Página 24


Sistema Distribuido de Gestión Académica 23
Dato examinado Tabla de origen Tipo de dato ¿Nulo? ¿PK? Descripción
estado programa_
asignatura
enum No No Estado de la asignatura
dentro del programa.
id_pre_requisito pre_requisitos uuid No Sí Identificador interno del
prerrequisito.
id_programa_academico pre_requisitos varchar(20) No No Programa académico asociado
al prerrequisito.
id_programa_asignatura pre_requisitos uuid No No Asignatura que exige el
prerrequisito.
id_programa_
asignatura_requisito
pre_requisitos uuid No No Asignatura que debe
aprobarse previamente.
id_grupo grupo uuid No Sí Identificador interno del
grupo.
id_programa_asignatura grupo uuid No No Asignatura del programa que
se oferta.
id_periodo_academico grupo varchar(10) No No Periodo en el que se oferta
el grupo.
id_docente grupo uuid Sí No Profesor asignado al grupo.
codigo_grupo grupo varchar(20) No No Código visible
institucional del grupo.
cupo_maximo grupo int No No Cupo máximo autorizado para
el grupo.
estado_grupo grupo enum No No Estado del grupo.
id_inscripcion inscripcion uuid No Sí Identificador interno de la
inscripción.
id_grupo inscripcion uuid No No Grupo inscrito por el
estudiante.
id_estudiante inscripcion uuid No No Estudiante inscrito en el
grupo.
nota1 inscripcion numeric(3,2) Sí No Primera nota parcial.
nota2 inscripcion numeric(3,2) Sí No Segunda nota parcial.
nota3 inscripcion numeric(3,2) Sí No Tercera nota parcial.
nota_final inscripcion numeric(3,2) Sí No Nota final de la
inscripción.
intento inscripcion int No No Número de intento de la
asignatura.
estado_inscripcion inscripcion enum No No Estado académico de la
inscripción.
id_homologacion homologacion uuid No Sí Identificador interno de la
homologación.
id_profesor_evaluador homologacion uuid No No Profesor encargado de
evaluar la solicitud.
id_estudiante homologacion uuid No No Estudiante que solicita la
homologación.
asignatura_origen homologacion varchar(100) No No Asignatura cursada en otra
institución.
institucion_origen homologacion varchar(100) No No Institución de origen de la
asignatura.



---

## Página 25


Sistema Distribuido de Gestión Académica 24
Dato examinado Tabla de origen Tipo de dato ¿Nulo? ¿PK? Descripción
id_programa_asignatura homologacion uuid No No Asignatura del programa que
se desea homologar.
fecha_solicitud homologacion date No No Fecha de solicitud de
homologación.
estado_homologacion homologacion enum No No Estado del proceso de
homologación.
observacion homologacion varchar(255) Sí No Comentarios del proceso de
homologación.
fecha_respuesta homologacion date Sí No Fecha de respuesta de la
solicitud.
nota_obtenida homologacion numeric(3,2) Sí No Nota reconocida en caso de
aprobación.
id_decano decano uuid No Sí Identificador interno de la
asignación del decano.
id_profesor decano uuid No No Profesor que ejerce como
decano.
id_periodo_academico decano varchar(10) No No Periodo de asignación del
decano.
id_facultad decano varchar(10) No No Facultad dirigida por el
decano.
id_coordinador coordinador uuid No Sí Identificador interno de la
asignación del coordinador.
id_profesor coordinador uuid No No Profesor que ejerce como
coordinador.
id_periodo_academico coordinador varchar(10) No No Periodo de asignación del
coordinador.
id_programa_academico coordinador varchar(20) No No Programa académico
coordinado.
id_auditoria auditoria uuid No Sí Identificador interno del
registro de auditoría.
id_usuario auditoria uuid No No Usuario que realizó la
acción.
accion_realizada auditoria varchar(100) No No Acción registrada por el
sistema.
fecha_hora auditoria timestamp No No Fecha y hora de la acción.
descripcion auditoria varchar(255) Sí No Descripción adicional de la
acción.
8. Identificación de claves primarias y claves foráneas
8.1. Criterio de selección de claves primarias
Las claves primarias se definieron mediante una estrategia mixta. Las tablas operativas, tran-
saccionales o de personas utilizan identificadoresuuid. Las tablas de catálogo institucional



---

## Página 26


Sistema Distribuido de Gestión Académica 25
estable utilizan identificadores de tipovarchar.
Tipo de tabla Tipo de clave Justificación
Tablas operativas uuid Evita consecutivos globales,
permite generación automática
y no expone información
institucional.
Catálogos institucionales varchar Permite usar códigos oficiales,
pequeños, estables y
entendibles dentro del contexto
académico.
Tabla 5: Criterio de selección de claves primarias.



---

## Página 27


Sistema Distribuido de Gestión Académica 26
8.2. Resumen de claves primarias
Tabla Clave primaria Tipo de dato
usuario id_usuario uuid
estudiante id_estudiante uuid
profesor id_profesor uuid
administrativo id_administrativo uuid
facultad id_facultad varchar(10)
programa_academico id_programa_academico varchar(20)
periodo_academico id_periodo_academico varchar(10)
asignatura cod_asignatura varchar(20)
tarifa_matricula id_tarifa_matricula uuid
recibo id_recibo uuid
matricula id_matricula uuid
programa_asignatura id_programa_asignatura uuid
pre_requisitos id_pre_requisito uuid
grupo id_grupo uuid
inscripcion id_inscripcion uuid
homologacion id_homologacion uuid
decano id_decano uuid
coordinador id_coordinador uuid
auditoria id_auditoria uuid
Tabla 6: Identificación de claves primarias.
9. Consideraciones preliminares sobre distribución
La estrategia de distribución se desarrollará en una etapa posterior del proyecto. Sin embar-
go, el modelo fue planteado de forma que permita distribuir la información por facultad o
programa académico.
De manera preliminar, la distribución podría considerar:



---

## Página 28


Sistema Distribuido de Gestión Académica 27
Fragmentación horizontal de estudiantes por facultad o programa.
Fragmentación horizontal de grupos por facultad y periodo académico.
Fragmentación horizontal de inscripciones a partir de los grupos.
Centralización de usuarios, auditoría, periodos académicos, pagos y matrículas.
Construcción de vistas institucionales para integrar datos entre facultades.
10. Conclusiones
El modelo propuesto permite representar los principales procesos académicos, administrati-
vos y financieros de una universidad organizada por facultades. La separación entre usuarios,
roles, facultades, programas, asignaturas, grupos, inscripciones, pagos, matrículas y homolo-
gaciones permite mantener un diseño coherente y extensible.
El diseño relacional permite controlar reglas fundamentales como la unicidad de documentos,
la asignación de programas a facultades, la relación muchos a muchos entre programas y
asignaturas, los prerrequisitos, el control de cupos, los estados de matrícula, los pagos de
matrícula y los procesos de homologación.
Asimismo,laestrategiamixtadellavesprimariaspermiteevitaridentificadoresautoincremen-
tales en las tablas operativas, manteniendo códigos institucionales únicamente en catálogos
estables. Esta decisión favorece una futura implementación distribuida y reduce problemas
asociados a consecutivos globales o claves primarias excesivamente descriptivas.

