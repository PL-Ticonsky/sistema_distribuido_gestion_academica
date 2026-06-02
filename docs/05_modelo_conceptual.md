# Diseño conceptual del modelo Entidad-Relación

## 5. Diseño conceptual del modelo Entidad-Relación

El diseño conceptual identifica las entidades principales del sistema y sus relaciones desde una perspectiva de negocio.

Este modelo permite representar los objetos relevantes del dominio académico antes de transformarlos en tablas relacionales.

## 5.1. Entidades conceptuales principales

En lugar de listar únicamente las entidades, se presenta una clasificación funcional que permite entender el papel de cada una dentro del sistema.

| Grupo conceptual | Entidades asociadas |
|---|---|
| Personas y roles | Usuario, Estudiante, Profesor, Administrativo, Coordinador, Decano. |
| Estructura institucional | Facultad, Programa académico. |
| Estructura académica | Asignatura, Programa-asignatura, Prerrequisito, Periodo académico. |
| Oferta académica | Grupo, Inscripción. |
| Gestión financiera | Tarifa de matrícula, Recibo, Matrícula. |
| Procesos académicos especiales | Homologación. |
| Control institucional | Auditoría. |

## 5.2. Descripción conceptual de relaciones principales

| Relación conceptual | Descripción |
|---|---|
| Usuario-Estudiante | Un usuario puede especializarse como estudiante. |
| Usuario-Profesor | Un usuario puede especializarse como profesor. |
| Usuario-Administrativo | Un usuario puede especializarse como administrativo afiliado a una facultad. |
| Profesor-Coordinador | Un profesor puede ejercer como coordinador de un programa en un periodo. |
| Profesor-Decano | Un profesor puede ejercer como decano de una facultad en un periodo. |
| Facultad-Programa | Una facultad puede tener varios programas académicos. |
| Programa-Asignatura | Un programa puede tener muchas asignaturas y una asignatura puede pertenecer a muchos programas. |
| Programa-asignatura-Grupo | Un grupo oferta una asignatura específica de un programa en un periodo académico. |
| Grupo-Inscripción | Un estudiante se inscribe en un grupo mediante una inscripción. |
| Tarifa-Recibo-Matrícula | La tarifa define el valor base; el recibo registra el pago individual; la matrícula registra el estado académico-administrativo. |

## 5.3. Diagrama conceptual

El documento base indica que en esta sección se debe insertar el diagrama conceptual Entidad-Relación original del sistema.

Para la implementación del proyecto, este diagrama debe conservarse como referencia visual del diseño conceptual y debe estar alineado con el modelo relacional definitivo.
