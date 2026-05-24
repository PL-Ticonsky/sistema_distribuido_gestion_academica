# 17. Usuarios y credenciales demo

## 1. Propósito del documento

Este documento define usuarios y credenciales ficticias para probar el acceso local al sistema Django durante la fase de desarrollo.

Las credenciales aquí descritas sirven como referencia funcional para validar pantallas, dashboards y permisos por rol. No representan usuarios reales ni credenciales productivas.

## 2. Advertencia de seguridad

Las credenciales documentadas son ficticias y solo deben usarse en ambiente local de desarrollo.

La contraseña demo estándar definida para estos usuarios es:

```text
Demo12345*
```

Estas credenciales pueden estar en GitHub porque no son reales, no dan acceso a servicios externos y no corresponden a secretos institucionales.

No se deben guardar en GitHub ni en la documentación credenciales reales de:

```text
PostgreSQL
Azure
.env
SECRET_KEY
correos personales
servicios externos
tokens o claves privadas
```

El archivo `.env` real debe mantenerse fuera del repositorio.

## 3. Usuarios demo por rol

| Rol | Nombre | Correo | Contraseña demo | Pantalla inicial esperada | Observación funcional |
|---|---|---|---|---|---|
| Administrador funcional | Claudia Benitez | claudia.benitez@universidad.edu | Demo12345* | Dashboard administrativo | Usuario orientado a administración funcional, estructura institucional, matrícula, recibos y auditoría. |
| Estudiante | Sofia Herrera | sofia.herrera@universidad.edu | Demo12345* | Dashboard de estudiante | Estudiante de Ingeniería de Sistemas con inscripciones, recibo y matrícula activa. |
| Profesor | Carolina Vargas | carolina.vargas@universidad.edu | Demo12345* | Dashboard de profesor | Profesora asociada a Ciencias Básicas con grupos académicos y evaluación de homologaciones. |
| Coordinador | Miguel Rojas | miguel.rojas@universidad.edu | Demo12345* | Dashboard de coordinador | Profesor coordinador del programa Ingeniería de Sistemas durante el periodo 2026-1. |
| Decano | Laura Perez | laura.perez@universidad.edu | Demo12345* | Dashboard de decano | Profesora asignada como decana de la Facultad de Ingeniería durante el periodo 2026-1. |
| Administrativo | Hector Suarez | hector.suarez@universidad.edu | Demo12345* | Dashboard administrativo | Administrativo de Ciencias Básicas para validar flujos de apoyo institucional. |

## 4. Relación con los datos operativos SQL

El archivo `sql/03_inserts_operativos.sql` contiene usuarios de prueba con correos y roles funcionales, pero el valor insertado en el campo `password` es un placeholder de texto.

Ese valor no debe considerarse una contraseña final de login si no fue generado por Django.

En Django, las contraseñas no deben guardarse en texto plano. El campo `usuario.password` debe contener un hash generado por el sistema de autenticación de Django.

## 5. Recomendación para creación futura de usuarios demo

Más adelante se recomienda crear un comando local de Django llamado:

```text
seed_demo_users
```

Ese comando deberá crear o actualizar usuarios demo usando `set_password()` para que el campo `password` almacene un hash válido de Django.

El comando también deberá asignar los roles funcionales correspondientes en las tablas de especialización:

```text
estudiante
profesor
administrativo
coordinador
decano
```

Esta recomendación aplica solo para ambiente local. La creación de usuarios reales deberá manejarse mediante flujos seguros de administración y nunca mediante credenciales hardcodeadas.
