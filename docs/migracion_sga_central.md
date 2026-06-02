# Migracion a sga_central

## Base default

El proyecto Django usa `sga_central` como base principal. No se debe volver a
usar `gestion_academica_local` como `POSTGRES_DB` default durante esta fase.

La fuente operativa de login de Django es:

```text
sga_central.public.usuario
```

Las tablas `personas.*` y `seguridad.*` siguen existiendo dentro del modelo
distribuido, pero el login de Django depende de:

```text
public.usuario
public.usuario_groups
public.auth_group
public.django_session
```

## Comandos de usuarios centrales

Preparar usuario demo central:

```bash
uv run python backend/manage.py ensure_central_demo_user
```

Sincronizar usuarios legacy desde `gestion_academica_local`:

```bash
uv run python backend/manage.py sync_legacy_users_to_central --apply
```

Auditar usuarios centrales sin imprimir hashes:

```bash
uv run python backend/manage.py audit_central_users
```

Normalizar contrasenas demo locales:

```bash
uv run python backend/manage.py reset_demo_users_passwords --password 'Demo12345*' --all-users --apply
```

Probar un login central:

```bash
uv run python backend/manage.py test_central_login --email admin.fing@universidad.edu --password 'Demo12345*'
```

## Advertencia

`reset_demo_users_passwords` es solo para entorno demo/local. No debe usarse en
produccion porque cambia la contrasena de todos los usuarios seleccionados.
