# NEXA-Vote Backend

## Stack
Flask 3.1, Python 3.11, Supabase (supabase-py 2.30), WebAuthn/FIDO2, gunicorn.

## Comandos

| Acción | Comando |
|---|---|
| Dev | `python run.py` (puerto `PORT`, default `10000`) |
| Prod | `gunicorn -w 1 --timeout 120 -b 0.0.0.0:${PORT:-10000} 'run:app'` |

No existe test runner, linter, typechecker, CI, Makefile ni `pyproject.toml`.

## Variables de entorno (`.env` gitignorado)
- `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `ALLOWED_ORIGINS` — origenes CORS separados por coma (default `http://localhost:5173`)
- `PORT` — default `10000`

## Clientes Supabase (`app/utils/supabase_client.py`)
- `get_supabase()` — anon key (lecturas públicas)
- `get_supabase_admin()` — service-role key (escritura, bypass RLS, crear usuarios Auth)
- Casi todas las operaciones de escritura usan el cliente admin.

## Rutas

| Prefijo | Blueprint | Archivo |
|---|---|---|
| `/` | health → `{"status": "ok"}` | `app/__init__.py` |
| `/register/...` | `registration_bp` | `routes/registration.py` |
| `/api/auth/...` | `auth_bp` | `routes/auth.py` |
| `/api/admin/...` | `admin_bp` | `routes/admin.py` |
| `/api/votes/...` | `votes_bp`, `candidates_bp` | `routes/votes.py`, `routes/candidates.py` |
| `/api/mfa/...` | `mfa_bp` | `routes/mfa.py` |
| `/webauthn/...` | `webauthn_bp` | `routes/webauthn.py` |

## Tablas Supabase (sin migraciones locales)
`voters`, `registration_status`, `biometric_data`, `webauthn_credentials`, `candidates`, `votes`

## Auth
- Token JWT de Supabase en header `Authorization: Bearer <token>`
- Resolución: `supabase_admin.auth.get_user(token)` (`app/services/vote_service.py:6-30`)
- Login de admin independiente en `app/services/admin_service.py`

## Notas
- No hay tests, linter, typechecker ni CI. Cualquier herramienta nueva debe crearse desde cero.
- Uploads faciales van a `app/uploads/face/` (gitignorado excepto `.gitkeep`).
- Factory pattern: `app.create_app()` en `run.py`.
