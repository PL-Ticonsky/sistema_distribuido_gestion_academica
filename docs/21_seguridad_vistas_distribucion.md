# 21. Seguridad, vistas y distribución de la base de datos

## Seguridad y control de acceso

La seguridad del Sistema Distribuido de Gestión Académica Universitaria se estructura a partir de un modelo de autenticación centralizada, autorización basada en roles funcionales y segmentación del acceso según el alcance académico, administrativo o institucional de cada usuario. Esta estrategia permite que el sistema controle no solo quién puede ingresar, sino también qué información puede consultar y qué operaciones puede ejecutar dentro de los módulos académicos, financieros, de homologación, indicadores y auditoría.

El diseño de seguridad se apoya en los mecanismos nativos de Django para autenticación, sesiones y almacenamiento seguro de contraseñas, complementados por reglas propias de negocio y filtros de datos implementados desde el backend. De esta manera, la aplicación evita que la seguridad dependa únicamente de la interfaz gráfica y garantiza que las restricciones sean aplicadas en el servidor antes de consultar, crear o modificar información.

### Modelo de autenticación implementado

El sistema implementa un modelo de autenticación centralizado mediante la aplicación `accounts`, la cual concentra el inicio de sesión, cierre de sesión, usuario personalizado, dashboard y resolución de roles funcionales. El ingreso se realiza desde la ruta de login, donde el usuario suministra sus credenciales y Django valida la identidad contra el modelo `CustomUser`. Una vez autenticado, el sistema crea una sesión segura y redirige al usuario al dashboard correspondiente.

El cierre de sesión se gestiona mediante el mecanismo de logout de Django. Esta operación invalida la sesión activa y evita que otro usuario continúe utilizando el navegador con los permisos previamente asignados. La separación entre login, logout y dashboard permite mantener un flujo de autenticación claro: primero se valida la identidad, luego se crea la sesión y finalmente se presenta una navegación adaptada a los roles funcionales.

El modelo de usuario personalizado utiliza la tabla `usuario` como entidad central de identidad. A diferencia de un esquema basado exclusivamente en nombres de usuario, el sistema utiliza el correo electrónico como campo principal de autenticación. Esta decisión resulta adecuada para un contexto universitario, donde el correo institucional o personal constituye un identificador estable y comprensible para estudiantes, docentes y funcionarios administrativos.

Las sesiones autenticadas permiten que las vistas internas del sistema identifiquen al usuario activo en cada solicitud. A partir de ese usuario, el backend obtiene sus roles, determina su alcance y filtra los datos disponibles. Por tanto, la autenticación no se limita al acceso inicial, sino que se convierte en el punto de partida para todo el control de permisos de la aplicación.

### Modelo de autorización basado en roles

La autorización se organiza mediante roles funcionales. Estos roles representan responsabilidades reales dentro de la institución universitaria y permiten diferenciar los permisos de consulta, gestión y administración. Los roles identificados son `estudiante`, `docente`, `coordinador`, `decano`, `administrativo` y `superadmin`.

El rol `estudiante` está orientado al usuario que pertenece a un programa académico y requiere consultar su plan de estudios, inscripciones, notas, recibos, homologaciones e indicadores. Este rol tiene un alcance principalmente individual, por lo cual sus operaciones deben quedar restringidas a su propia información académica y financiera.

El rol `docente` representa al profesor encargado de grupos académicos. Su acceso se concentra en los grupos asignados, estudiantes inscritos, registro o consulta de notas e indicadores asociados a estudiantes con los que tiene relación académica. El docente no debe visualizar grupos ajenos ni información institucional que no esté vinculada a su carga académica.

El rol `coordinador` corresponde al responsable de un programa académico. Su autorización permite consultar y gestionar información relacionada con estudiantes, grupos, planes de estudio, homologaciones e indicadores dentro del programa que coordina. Este rol amplía el alcance respecto al estudiante y al docente, pero mantiene una frontera clara: el programa académico asignado.

El rol `decano` representa la autoridad de facultad. Su alcance se define sobre una facultad y los programas que pertenecen a ella. Desde esta perspectiva, puede consultar información consolidada sobre programas, docentes, grupos e indicadores académicos de la facultad, sin extenderse a facultades no asociadas.

El rol `administrativo` está enfocado en procesos financieros. Su autorización permite consultar y gestionar recibos, tarifas y matrículas dentro del alcance financiero asociado a su facultad. Este rol separa las responsabilidades administrativas de las académicas, evitando que la gestión financiera implique acceso indiscriminado a notas, homologaciones o auditoría institucional.

El rol `superadmin` posee acceso global dentro de la aplicación. Este rol se reserva para administración institucional amplia, consultas generales, auditoría y actividades de supervisión. Debido a su alcance total, debe asignarse únicamente a usuarios autorizados y controlados institucionalmente.

### Segmentación por alcance

La segmentación por alcance complementa la autorización por roles. Mientras el rol indica qué tipo de operaciones puede realizar un usuario, el alcance define sobre qué subconjunto de datos puede ejercerlas. Esta separación es fundamental en sistemas universitarios, porque dos usuarios con el mismo rol pueden tener ámbitos distintos; por ejemplo, dos coordinadores pueden compartir funciones, pero pertenecer a programas diferentes.

El estudiante solo visualiza su información personal, académica y financiera. Esto incluye sus inscripciones, notas, recibos, matrículas, homologaciones e indicadores. La aplicación obtiene el estudiante asociado al usuario autenticado y utiliza ese vínculo para restringir los querysets.

El docente visualiza únicamente los grupos que tiene asignados y la información académica derivada de esos grupos. Esto permite consultar estudiantes inscritos y notas relacionadas, pero evita que el profesor acceda a grupos de otros docentes o a información de programas sin relación con su carga académica.

El coordinador accede a información del programa académico que coordina. En consecuencia, sus consultas sobre estudiantes, grupos, homologaciones e indicadores se filtran por el identificador del programa. Esta regla permite descentralizar la gestión académica sin perder control sobre los límites institucionales.

El decano accede a información de su facultad. El sistema identifica la facultad asociada a la decanatura y deriva de ella los programas académicos visibles. Con este alcance, el decano puede consultar consolidados de facultad y datos académicos relevantes sin invadir la información de otras facultades.

El administrativo accede a la información financiera correspondiente a su facultad. Esta segmentación evita que un funcionario financiero consulte recibos, matrículas o estudiantes de facultades ajenas. Además, permite mantener independencia operativa entre unidades académicas.

El superadmin cuenta con acceso global. En términos de implementación, las funciones de alcance retornan un comportamiento no restringido para este rol, lo que permite consultar información institucional completa y acceder a módulos de auditoría o administración general.

### Protección de vistas y rutas

Las vistas internas del sistema se protegen mediante autenticación obligatoria y validación de roles. En Django, esta protección puede expresarse mediante `login_required` en vistas basadas en funciones o mediante `LoginRequiredMixin` en vistas basadas en clases; en el proyecto se utiliza el patrón de mixins para impedir el acceso de usuarios no autenticados. Además, el sistema incorpora un `RoleRequiredMixin` que verifica si el usuario posee alguno de los roles autorizados para una pantalla específica.

La protección de rutas no se limita a ocultar enlaces del menú. Aunque el dashboard presenta opciones según el rol, cada vista valida nuevamente en el backend si el usuario tiene permiso para acceder. Esta doble capa evita que un usuario ingrese manualmente una URL y obtenga información para la cual no está autorizado.

Las restricciones por queryset constituyen una parte central de la seguridad. Las vistas no consultan todos los registros de una tabla para luego decidir qué mostrar, sino que construyen consultas filtradas según el usuario autenticado. Para ello se emplean funciones de alcance que determinan estudiantes, grupos, docentes, programas o facultades visibles.

Los filtros según usuario autenticado garantizan que la autorización se aplique a nivel de consulta. Por ejemplo, un estudiante solo obtiene sus inscripciones; un docente solo obtiene los grupos donde figura como profesor; un coordinador obtiene estudiantes y grupos de su programa; y un decano obtiene información derivada de su facultad. Esta estrategia reduce el riesgo de exposición accidental de datos y mejora la coherencia entre reglas de negocio y consultas a la base de datos.

### Protección de operaciones críticas

Las operaciones críticas del sistema son aquellas que modifican información académica, financiera o administrativa con impacto institucional. Entre ellas se encuentran la modificación de notas, la inscripción académica, la evaluación de homologaciones y la gestión financiera de recibos, matrículas y tarifas.

La modificación de notas está restringida principalmente al docente responsable del grupo y al superadmin. Esta regla protege la integridad académica, dado que la calificación forma parte del historial del estudiante y puede incidir en promedio, aprobación de asignaturas, avance curricular y riesgo de deserción. El sistema valida el rol y el alcance antes de permitir la edición.

La inscripción académica se controla mediante reglas de negocio aplicadas en formularios y vistas. La operación verifica que el grupo esté en estado válido, que exista cupo disponible, que el estudiante no esté duplicando una inscripción incompatible y que exista matrícula activa cuando la regla académica lo exige. Estas validaciones impiden inconsistencias como estudiantes inscritos sin matrícula, cupos excedidos o múltiples registros equivalentes para la misma asignatura y periodo.

Las homologaciones se protegen mediante estados y roles diferenciados. El estudiante puede solicitar y consultar sus procesos; el coordinador puede asignar evaluador dentro de su programa; el docente evaluador puede registrar la decisión académica; y el superadmin puede intervenir de forma global. Esta separación respeta el flujo institucional de evaluación y evita que una homologación sea aprobada por usuarios no autorizados.

La gestión financiera está restringida a usuarios administrativos, coordinadores, decanos y superadmin según el caso de uso definido. Los recibos, tarifas y matrículas deben modificarse solo por perfiles autorizados, porque sus estados afectan la habilitación académica del estudiante y la trazabilidad financiera de la institución.

### Seguridad de contraseñas

El sistema utiliza el mecanismo seguro de autenticación de Django para el manejo de contraseñas. Las contraseñas no se almacenan en texto plano; se guardan mediante hash y se verifican con los métodos provistos por el framework. Esto reduce el impacto de una eventual exposición de la base de datos, ya que no se revelarían directamente las credenciales originales.

El uso de `AbstractBaseUser` y `PermissionsMixin` permite integrar el usuario personalizado con el ecosistema de seguridad de Django. De esta forma, el sistema conserva capacidades estándar como autenticación, estado activo del usuario, permisos administrativos y compatibilidad con grupos funcionales.

La autenticación segura de Django también permite validar usuarios inactivos, centralizar el proceso de verificación de credenciales y mantener una separación clara entre identidad, sesión y autorización funcional. Esta decisión evita implementar mecanismos manuales de contraseñas, los cuales suelen ser más propensos a errores de seguridad.

### Seguridad lógica implementada

La seguridad lógica se implementa mediante validaciones de backend que protegen la integridad de los procesos académicos y financieros. Estas validaciones son necesarias porque no todas las restricciones pueden expresarse únicamente como claves foráneas o restricciones de base de datos; muchas dependen del estado del proceso, el rol del usuario, el periodo académico o la relación entre entidades.

En el dominio académico se controlan reglas como cupos de grupos, estado de inscripción, matrícula activa, duplicidad de inscripciones, intentos académicos y edición de notas. Estas restricciones aseguran que los registros creados correspondan a situaciones institucionalmente válidas.

En el dominio financiero se controlan estados de recibos, matrículas, tarifas activas y anulaciones. La consistencia financiera es especialmente importante porque los pagos pueden condicionar el acceso a inscripción y continuidad académica. Por esta razón, los cambios de estado deben quedar restringidos y trazables.

El control de duplicados evita registros repetidos que puedan alterar reportes o generar conflictos administrativos. La aplicación considera duplicados en documentos de usuario, inscripciones por estudiante y grupo, inscripciones equivalentes por asignatura y periodo, y relaciones institucionales que deben permanecer únicas.

El control de cupos protege la disponibilidad real de los grupos. Al verificar el cupo antes de crear inscripciones, el sistema evita sobrecargar grupos académicos y mantiene coherencia entre oferta académica, capacidad docente e inscripción estudiantil.

### Seguridad a nivel de base de datos como propuesta conceptual

Aunque la versión actual concentra el control de seguridad en Django, la arquitectura puede fortalecerse en etapas posteriores mediante seguridad explícita a nivel de PostgreSQL. Esta propuesta no modifica el SQL existente, pero establece una dirección técnica para despliegues institucionales más robustos.

Una primera línea de fortalecimiento consiste en definir privilegios mediante `GRANT` y `REVOKE`. La institución podría crear roles técnicos de base de datos para lectura, escritura operativa, auditoría y administración, evitando que todos los procesos usen un mismo usuario con privilegios amplios.

Las vistas controladas permitirían exponer subconjuntos de datos previamente filtrados. En lugar de conceder acceso directo a tablas sensibles, se podrían conceder permisos sobre vistas que oculten campos privados o limiten filas según facultad, programa o periodo. Esta estrategia es coherente con el modelo de vistas lógicas documentado en este capítulo.

La separación de privilegios permitiría diferenciar operaciones de consulta, inserción, actualización y administración. Por ejemplo, un usuario técnico utilizado por reportes institucionales podría leer vistas consolidadas, pero no modificar notas ni estados financieros. A su vez, los procesos transaccionales podrían tener permisos acotados sobre tablas específicas.

El superusuario de PostgreSQL debe reservarse para tareas estrictamente administrativas, como mantenimiento de la base de datos, creación de extensiones, respaldo, restauración y configuración de replicación. La aplicación web no debería operar normalmente con credenciales de superusuario, debido al riesgo que implicaría una falla de aplicación o una mala configuración.

## Vistas lógicas y vistas materializadas

Las vistas son mecanismos de abstracción que permiten representar consultas complejas como objetos consultables de la base de datos. En el contexto del Sistema Distribuido de Gestión Académica Universitaria, las vistas resultan útiles para consolidar información dispersa entre usuarios, estudiantes, programas, grupos, inscripciones, recibos, matrículas, homologaciones e indicadores.

Una vista normal es una consulta almacenada en la base de datos que se ejecuta cada vez que es consultada. No almacena físicamente el resultado, sino la definición de la consulta. Su principal ventaja es que siempre refleja el estado actualizado de las tablas base, lo cual resulta adecuado para consultas operativas como inscripciones vigentes, notas actuales, recibos activos o grupos asignados.

Una vista materializada almacena físicamente el resultado de una consulta. A diferencia de la vista normal, no recalcula toda la información en cada consulta, sino que conserva una copia consolidada que debe actualizarse periódicamente. Este mecanismo es conveniente para reportes pesados, indicadores agregados, estadísticas institucionales e históricos académicos que requieren unir muchas tablas o calcular métricas complejas.

La diferencia principal entre ambas está en el equilibrio entre actualización y rendimiento. La vista normal favorece información siempre actualizada, pero puede ser más costosa si la consulta involucra muchas tablas. La vista materializada favorece rendimiento y consultas analíticas rápidas, pero requiere una política de refresco para mantener la información suficientemente actual.

En el proyecto se proponen vistas normales para consultas operativas frecuentes y vistas materializadas para reportes consolidados o indicadores institucionales. Esta separación permite que el sistema mantenga agilidad en las pantallas diarias y, al mismo tiempo, ofrezca información agregada para coordinaciones, decanaturas, dependencias financieras y rectoría.

### Vistas normales

Las vistas normales planeadas o implementables se orientan a simplificar consultas operativas y a reforzar el control de acceso mediante estructuras lógicas reutilizables. Cada vista integra tablas relacionadas y expone un resultado coherente para un conjunto de usuarios autorizados.

| Vista | Propósito | Tablas involucradas | Usuarios autorizados | Utilidad académica o administrativa |
|---|---|---|---|---|
| `vista_estudiante_inscripciones` | Presenta las materias inscritas por cada estudiante, incluyendo grupo, periodo, asignatura, estado de inscripción e información básica del programa. | `usuario`, `estudiante`, `programa_academico`, `programa_asignatura`, `asignatura`, `grupo`, `periodo_academico`, `inscripcion`. | Estudiante propietario, coordinador del programa, decano de la facultad y superadmin. | Permite consultar carga académica, validar inscripción vigente y soportar procesos de seguimiento académico individual. |
| `vista_estudiante_notas` | Consolida notas parciales, nota final, estado de inscripción e intento académico de cada asignatura cursada. | `usuario`, `estudiante`, `inscripcion`, `grupo`, `programa_asignatura`, `asignatura`, `periodo_academico`. | Estudiante propietario, docente del grupo, coordinador, decano y superadmin. | Facilita la consulta del rendimiento académico y reduce la complejidad de reportes de calificaciones. |
| `vista_docente_grupos` | Muestra los grupos asignados a cada docente, con periodo, asignatura, programa, cupo y estado del grupo. | `usuario`, `profesor`, `grupo`, `programa_asignatura`, `programa_academico`, `asignatura`, `periodo_academico`. | Docente propietario, coordinador del programa, decano de la facultad y superadmin. | Apoya la gestión de carga docente, consulta de grupos y seguimiento de oferta académica. |
| `vista_coordinador_programa` | Integra estudiantes, grupos, asignaturas y docentes asociados a un programa académico. | `coordinador`, `profesor`, `programa_academico`, `estudiante`, `grupo`, `programa_asignatura`, `asignatura`, `periodo_academico`. | Coordinador del programa, decano de la facultad y superadmin. | Permite una visión operativa del programa para seguimiento académico, planeación de grupos y acompañamiento estudiantil. |
| `vista_decano_facultad` | Consolida información académica por facultad, incluyendo programas, docentes, grupos y estudiantes. | `facultad`, `programa_academico`, `profesor`, `decano`, `grupo`, `programa_asignatura`, `estudiante`, `periodo_academico`. | Decano de la facultad y superadmin. | Facilita el seguimiento de facultad, evaluación de oferta académica y análisis de distribución docente. |
| `vista_financiera_estudiantes` | Presenta recibos, tarifas, pagos y estados de matrícula asociados a estudiantes. | `estudiante`, `usuario`, `programa_academico`, `tarifa_matricula`, `recibo`, `matricula`, `periodo_academico`. | Estudiante propietario, administrativo de la facultad, coordinador, decano y superadmin. | Permite verificar estado financiero, pagos realizados, recibos pendientes y habilitación de matrícula. |
| `vista_homologaciones_programa` | Agrupa solicitudes de homologación por programa, estudiante, asignatura homologable, evaluador y estado del proceso. | `homologacion`, `estudiante`, `usuario`, `programa_asignatura`, `asignatura`, `programa_academico`, `profesor`. | Estudiante propietario, docente evaluador, coordinador del programa, decano y superadmin. | Soporta la gestión de equivalencias académicas y la trazabilidad de decisiones de homologación. |
| `vista_indicadores_estudiante` | Expone indicadores de avance académico, rendimiento, asignaturas aprobadas o reprobadas y riesgo de deserción. | `estudiante`, `usuario`, `programa_academico`, `inscripcion`, `grupo`, `programa_asignatura`, `asignatura`, `recibo`, `matricula`. | Estudiante propietario, docente relacionado, coordinador, decano y superadmin. | Permite identificar alertas tempranas, desempeño académico y necesidades de acompañamiento. |
| `vista_auditoria` | Presenta acciones registradas en el sistema con usuario, fecha, acción y descripción. | `auditoria`, `usuario`. | Superadmin. | Facilita la revisión de trazabilidad, control institucional y análisis de operaciones sensibles. |

Estas vistas normales contribuyen a la claridad del modelo porque traducen relaciones relacionales complejas en objetos de consulta orientados al uso institucional. Además, pueden servir como base para reportes, filtros de interfaz y futuras políticas de privilegios en PostgreSQL.

### Vistas materializadas

Las vistas materializadas propuestas se enfocan en información agregada, histórica o analítica. Su materialización se justifica cuando la consulta combina muchas tablas, calcula métricas institucionales o se utiliza de forma repetitiva en reportes de coordinación, facultad o dirección universitaria.

| Vista materializada | Propósito | Justificación de materialización | Periodicidad de actualización | Ventajas de rendimiento | Utilidad institucional |
|---|---|---|---|---|---|
| `mv_historial_academico` | Consolidar el historial académico de cada estudiante, incluyendo asignaturas cursadas, notas, estados, intentos y periodos. | El historial requiere unir estudiantes, inscripciones, grupos, asignaturas, programas y periodos. Al materializarlo se evita recalcular trayectoria completa en cada consulta. | Diaria y adicionalmente al cierre de periodos académicos. | Reduce tiempos de consulta en kardex, certificados internos e informes de avance. | Sirve para seguimiento académico, revisión de requisitos de grado y análisis de permanencia. |
| `mv_rendimiento_programa` | Calcular promedios, tasas de aprobación, reprobación y avance por programa académico. | Las métricas por programa requieren agregaciones frecuentes sobre grandes volúmenes de inscripciones y notas. | Semanal durante el periodo y final al cierre académico. | Acelera reportes de coordinación y evita consultas agregadas repetitivas. | Permite evaluar desempeño curricular, detectar asignaturas críticas y apoyar decisiones de mejora. |
| `mv_riesgo_desercion` | Identificar estudiantes con posible riesgo de deserción según bajo rendimiento, repetición, inactividad o situaciones financieras. | El cálculo combina información académica y financiera, por lo cual resulta costoso en tiempo real. | Semanal o diaria durante semanas de inscripción, pagos y cierre de notas. | Permite consultar alertas rápidamente sin recalcular indicadores complejos. | Apoya programas de permanencia, bienestar universitario y acompañamiento académico. |
| `mv_carga_docente` | Consolidar cantidad de grupos, estudiantes inscritos y asignaturas por docente y periodo. | La carga docente depende de grupos, programas, asignaturas e inscripciones. Materializarla facilita reportes recurrentes. | Semanal y al inicio de cada periodo académico. | Optimiza consultas de decanatura y coordinación sobre asignación docente. | Ayuda a balancear carga académica, planear contratación y evaluar capacidad institucional. |
| `mv_estadisticas_facultad` | Agregar métricas por facultad: estudiantes activos, programas, grupos, docentes, aprobación y reprobación. | Las estadísticas de facultad integran varias entidades y múltiples niveles de agregación. | Semanal y al cierre del periodo. | Evita consultas complejas sobre toda la institución para cada reporte directivo. | Facilita análisis de gestión de facultad, comparación entre programas y seguimiento institucional. |
| `mv_estado_financiero` | Consolidar estados de recibos, pagos, matrículas y valores por programa, facultad y periodo. | Los reportes financieros requieren sumar montos, estados y vencimientos sobre múltiples tablas. | Diaria en periodos de pago y semanal en operación regular. | Mejora la velocidad de tableros financieros y reportes administrativos. | Apoya control de cartera, seguimiento de matrículas y análisis de recaudo institucional. |
| `mv_materias_reprobadas` | Identificar asignaturas con mayor frecuencia de pérdida académica por programa, docente, periodo y facultad. | El análisis de reprobación exige agregaciones históricas sobre inscripciones y notas. | Al cierre de cada corte o periodo académico. | Acelera informes de calidad académica y análisis curricular. | Permite detectar asignaturas críticas, ajustar acompañamiento y revisar estrategias pedagógicas. |

La actualización de estas vistas debe planearse de acuerdo con el ciclo académico. Algunas métricas requieren actualización diaria durante momentos de alta actividad, como inscripción, pagos o cierre de notas. Otras pueden refrescarse semanalmente o al final de cada periodo. Esta política evita sobrecargar la base transaccional y mantiene disponibles reportes institucionales con tiempos de respuesta adecuados.

## Estrategia de distribución de la base de datos

La distribución de la base de datos tiene como objetivo permitir que el sistema escale institucionalmente, reduzca la carga sobre un único servidor central y otorgue autonomía operativa a facultades o unidades académicas sin perder consistencia global. Dado que una universidad puede manejar grandes volúmenes de estudiantes, docentes, grupos, pagos, matrículas e históricos académicos, una arquitectura distribuida resulta pertinente para soportar crecimiento, disponibilidad y consultas institucionales.

La arquitectura distribuida propuesta combina fragmentación horizontal, fragmentación vertical, centralización de información crítica y vistas distribuidas. Esta combinación evita adoptar una única estrategia para todos los datos y reconoce que cada dominio tiene necesidades distintas. La información operativa por facultad puede distribuirse; la autenticación, roles, auditoría e indicadores institucionales deben mantenerse centralizados o consolidados; y los reportes pueden apoyarse en vistas federadas o materializadas.

Los beneficios esperados incluyen reducción de carga sobre el servidor principal, mayor autonomía por facultad, mejora en tiempos de consulta local, separación de responsabilidades administrativas y posibilidad de consolidar información para rectoría o dirección académica. Además, la distribución favorece una escalabilidad gradual: la institución puede iniciar con una base central y evolucionar hacia servidores por facultad, particionamiento o replicación según el crecimiento real.

La escalabilidad institucional se logra al diseñar la base para que las operaciones cotidianas de una facultad no dependan siempre de consultar toda la universidad. Al mismo tiempo, los datos centralizados y las vistas consolidadas aseguran que la institución mantenga integridad global, trazabilidad y capacidad de análisis.

### Fragmentación horizontal

La fragmentación horizontal consiste en dividir filas de una misma tabla o conjunto de tablas según un criterio institucional. En este proyecto, los criterios naturales son facultad, programa académico y periodo. Esta estrategia conserva la estructura de las tablas, pero distribuye subconjuntos de registros entre nodos o particiones.

Los estudiantes pueden fragmentarse por facultad a partir del programa académico al que pertenecen. Como cada estudiante está asociado a un programa y cada programa pertenece a una facultad, la facultad se convierte en un criterio estable de distribución. Esta división reduce la carga de consultas locales, permite que cada facultad gestione sus estudiantes y facilita reportes internos sin recorrer toda la población institucional.

Los docentes también pueden fragmentarse por facultad. La tabla de profesores contiene relación con facultad, lo que permite ubicar a cada docente dentro de una unidad académica. Esta distribución favorece la gestión de carga docente, decanaturas, coordinaciones y asignación de grupos dentro de la facultad correspondiente.

Los grupos pueden fragmentarse por facultad y periodo académico. La facultad se deriva del programa académico asociado a la asignatura del grupo, mientras que el periodo permite separar la operación temporal. Esta combinación resulta útil porque los grupos son altamente consultados durante inscripción, desarrollo de clases y cierre de notas. Dividirlos por facultad y periodo reduce el tamaño de las consultas operativas.

Las inscripciones pueden distribuirse como fragmentos derivados de los grupos. Si un grupo pertenece a una facultad y periodo determinados, las inscripciones de ese grupo deben ubicarse en el mismo fragmento o en un fragmento compatible. Esta estrategia mantiene cercanas las entidades que se consultan conjuntamente, como grupo, estudiante inscrito, notas y estado de inscripción.

Las matrículas pueden fragmentarse por facultad o periodo. La fragmentación por facultad facilita la operación administrativa local, mientras que la fragmentación por periodo permite archivar o aislar ciclos académicos cerrados. En ambos casos se reduce la carga sobre consultas de recibos y matrículas actuales.

Las homologaciones pueden fragmentarse por programa académico. Como una homologación se evalúa respecto a una asignatura del plan de estudios de un programa, este criterio permite que la coordinación correspondiente gestione sus solicitudes sin mezclar procesos de programas ajenos.

La principal ventaja de la fragmentación horizontal es que reduce el volumen de datos consultado por cada unidad académica. Además, incrementa la autonomía por facultad, permite políticas de mantenimiento diferenciadas y abre la posibilidad de ubicar servidores cercanos a las dependencias con mayor carga operativa.

### Fragmentación vertical

La fragmentación vertical consiste en separar columnas o grupos de atributos de una entidad según su sensibilidad, uso o dominio funcional. En este proyecto, esta estrategia resulta útil para proteger información privada, aislar datos financieros y mejorar el rendimiento de consultas que no requieren todos los atributos.

La separación entre datos personales y académicos permitiría almacenar información de identidad, contacto y documento en un componente distinto al historial académico, inscripciones y notas. Esta división reduce exposición de datos personales cuando solo se requieren consultas académicas agregadas.

La información financiera puede ubicarse en un fragmento vertical propio. Recibos, valores pagados, métodos de pago, estados financieros y matrículas tienen sensibilidad administrativa y no son necesarios para todos los procesos académicos. Separarlos mejora el control de permisos y permite que los módulos financieros operen con privilegios específicos.

La auditoría debe separarse verticalmente para preservar trazabilidad y control. Los registros de auditoría tienen un valor probatorio y administrativo; por ello, su consulta debe estar restringida y su almacenamiento debe protegerse frente a modificaciones no autorizadas.

La separación entre información pública y privada permite exponer datos institucionales de bajo riesgo, como facultades, programas, periodos y asignaturas, sin incluir datos sensibles de personas o finanzas. Esta distinción es útil para reportes, catálogos y posibles integraciones externas.

Una posible separación de credenciales y autenticación permitiría aislar los datos de seguridad, como hash de contraseña, estado del usuario, permisos y grupos funcionales. En una arquitectura más avanzada, este componente podría centralizarse como servicio de identidad institucional.

Las ventajas de seguridad de la fragmentación vertical se reflejan en menor exposición de datos sensibles y privilegios más específicos por módulo. Las ventajas de rendimiento surgen porque las consultas pueden acceder solo a los atributos necesarios. La modularidad mejora porque cada dominio, como académico, financiero, auditoría o autenticación, puede evolucionar con reglas y controles propios.

### Centralización

No toda la información debe distribuirse. Algunos datos requieren consistencia institucional fuerte y deben permanecer centralizados o, al menos, contar con una fuente central de verdad. Esta decisión evita divergencias entre facultades y permite mantener control administrativo global.

Los usuarios y la autenticación deben permanecer centralizados. Un usuario puede tener varios roles o participar en diferentes procesos, por lo cual la identidad institucional debe ser única. Centralizar la autenticación evita duplicidad de credenciales y facilita la gestión de sesiones, contraseñas, usuarios activos y permisos.

La auditoría institucional debe centralizarse para garantizar trazabilidad completa. Aunque existan operaciones locales por facultad, los eventos relevantes deben consolidarse en un repositorio común que permita reconstruir acciones, fechas, usuarios y módulos afectados.

Los pagos institucionales requieren control central o consolidado, porque impactan reportes financieros, cartera, matrícula y estados administrativos. Aunque la operación pueda originarse en facultades, la institución necesita una visión integral de recaudo y obligaciones.

El historial académico consolidado debe mantenerse centralizado o materializado institucionalmente. Un estudiante puede cambiar de programa, realizar homologaciones o requerir certificaciones oficiales. Por ello, la institución necesita un historial único, consistente y verificable.

Los indicadores institucionales deben centralizarse para permitir análisis global. Métricas de deserción, rendimiento, reprobación, avance y carga docente requieren comparación entre programas y facultades. Su consolidación permite decisiones de gobierno universitario.

Los roles y permisos deben administrarse centralmente. Esta decisión evita que cada facultad defina roles incompatibles o privilegios no autorizados. La seguridad institucional depende de una política homogénea de autorización.

Los catálogos institucionales, como facultades, programas, periodos académicos y asignaturas, deben contar con gobierno central. Aunque puedan replicarse para consulta local, su definición oficial debe mantenerse consistente para que las relaciones entre fragmentos sean válidas.

### Vistas distribuidas

Las vistas distribuidas permiten integrar información fragmentada sin obligar al usuario final a conocer la ubicación física de los datos. En una arquitectura con servidores por facultad o fragmentos por dominio, estas vistas actuarían como una capa lógica de consolidación para consultas institucionales.

Las vistas federadas podrían consultar datos en distintos nodos y presentar un resultado unificado. Por ejemplo, una vista institucional de estudiantes activos podría integrar fragmentos de cada facultad y exponerlos como una única relación consultable por superadmin o rectoría.

La consolidación académica integraría estudiantes, grupos, inscripciones, notas, homologaciones y programas distribuidos. Esto permitiría obtener reportes globales de rendimiento, avance curricular y reprobación sin eliminar la autonomía de cada facultad.

La consolidación financiera integraría recibos, matrículas, estados de pago y tarifas provenientes de fragmentos locales o particiones por periodo. Esta vista sería útil para áreas administrativas centrales que requieren conocer el estado financiero institucional.

Los indicadores globales se construirían a partir de vistas distribuidas o materializadas. La información calculada localmente podría sincronizarse hacia un nodo central, donde se consolidarían métricas por facultad, programa, periodo y población estudiantil.

Los reportes de rectoría y facultad podrían consultar distintas capas de vistas. Rectoría requeriría información global; decanatura necesitaría información de su facultad; coordinación consultaría su programa; y los módulos operativos accederían a vistas locales. Esta jerarquía mantiene coherencia entre distribución física y autorización funcional.

### Tecnologías y mecanismos propuestos

PostgreSQL Foreign Data Wrapper, especialmente `postgres_fdw`, puede utilizarse para consultar tablas remotas desde un nodo central. Este mecanismo permite construir vistas federadas que integren información de servidores por facultad sin replicar necesariamente todos los datos.

La replicación lógica permite copiar cambios de tablas seleccionadas hacia un nodo de consolidación. Es útil cuando se desea mantener una base institucional de reportes sin sobrecargar los servidores operativos. También facilita separar cargas transaccionales y analíticas.

Las vistas materializadas sirven como capa de rendimiento para reportes complejos. En una arquitectura distribuida, pueden refrescarse periódicamente a partir de fragmentos locales o vistas federadas, proporcionando respuestas rápidas para indicadores y tableros institucionales.

El particionamiento de PostgreSQL permite dividir tablas grandes por facultad, programa o periodo dentro de un mismo servidor lógico. Esta opción puede ser un paso intermedio antes de distribuir físicamente la base en servidores independientes.

La sincronización periódica permite trasladar información desde nodos locales hacia un repositorio central en horarios definidos. Esta estrategia es apropiada para métricas que no requieren actualización en tiempo real, como estadísticas semanales o cierres de periodo.

Los servidores por facultad constituyen una alternativa de distribución física. Cada facultad podría operar sus datos académicos y financieros locales, mientras un nodo central mantiene usuarios, permisos, catálogos, auditoría e indicadores consolidados. Esta arquitectura debe complementarse con políticas claras de sincronización, respaldo, monitoreo y control de privilegios.

En conjunto, estas tecnologías permiten una evolución gradual del sistema. La institución puede iniciar con una base centralizada, avanzar hacia particionamiento y vistas materializadas, incorporar replicación lógica para reportes y finalmente distribuir nodos por facultad cuando la escala operativa lo justifique.
