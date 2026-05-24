# Introducción y descripción general del sistema

## 1. Introducción

El presente proyecto corresponde al diseño de una base de datos distribuida para un sistema de gestión académica universitaria.

El objetivo principal es plantear un modelo de datos que permita administrar:

- Usuarios.
- Estudiantes.
- Docentes.
- Administrativos.
- Facultades.
- Programas académicos.
- Asignaturas.
- Grupos.
- Inscripciones.
- Matrículas.
- Pagos.
- Homologaciones.
- Procesos académicos asociados.

El sistema se concibe como una solución orientada a una arquitectura distribuida. Bajo esta idea, cada facultad conserva autonomía sobre la información académica que administra, pero al mismo tiempo se mantiene la posibilidad de realizar consultas institucionales consolidadas.

Esta primera entrega no implementa todavía la distribución física. Su función es dejar construido el planteamiento lógico y relacional necesario para etapas posteriores.

El documento incluye:

- Descripción general del sistema.
- Alcance de la entrega.
- Reglas de negocio principales.
- Diseño conceptual del modelo Entidad-Relación.
- Modelo relacional.
- Esquema de tablas.
- Identificación de claves primarias y foráneas.
- Diccionario de datos preliminar.

## 2. Descripción general del sistema propuesto

El sistema propuesto corresponde a una plataforma universitaria para la gestión académica y administrativa de una institución organizada por facultades.

Cada facultad administra sus programas académicos, docentes, estudiantes, grupos y procesos asociados. Al mismo tiempo, la institución conserva información común necesaria para la operación general, como:

- Usuarios.
- Periodos académicos.
- Auditoría.
- Pagos.
- Matrículas.
- Reportes institucionales.

## Propósito del sistema

El sistema busca integrar la gestión académica universitaria mediante una base de datos que permita registrar, consultar y controlar información de estudiantes, profesores, administrativos, programas académicos, asignaturas, grupos, inscripciones, notas, matrículas, pagos y homologaciones.

## 2.1. Componentes principales

| Componente | Descripción |
|---|---|
| Usuarios y roles | Registra las personas del sistema y sus especializaciones como estudiantes, docentes o administrativos. |
| Facultades y programas | Representa la estructura académica institucional. |
| Asignaturas y planes | Permite asociar asignaturas a programas académicos mediante planes de estudio. |
| Grupos académicos | Modela la oferta concreta de asignaturas por periodo académico. |
| Inscripciones y notas | Registra las asignaturas cursadas por los estudiantes, sus notas, intentos y estado académico. |
| Matrícula y pagos | Gestiona tarifas, recibos individuales y estados de matrícula. |
| Homologaciones | Permite solicitar y evaluar equivalencias de asignaturas cursadas en otras instituciones. |
| Auditoría | Registra acciones relevantes ejecutadas por usuarios del sistema. |
