# Modelo de datos esperado en Supabase

El repositorio no incluye migraciones SQL ni definicion formal del esquema. Este documento describe el modelo inferido desde el codigo actual.

## `voters`

Tabla principal de votantes.

| Campo | Tipo esperado | Uso en codigo |
| --- | --- | --- |
| `id` | UUID | Identificador del votante |
| `dni` | Texto | Login, validacion MFA y registro |
| `full_name` | Texto | Datos de identidad |
| `birth_date` | Fecha o texto `YYYY-MM-DD` | Datos de identidad |
| `email` | Texto | Login via Supabase Auth |
| `auth_user_id` | UUID | Relacion con Supabase Auth |
| `registration_step` | Entero | Paso de registro inicial |

Operaciones:

- Insert en `create_voter`.
- Insert parcial en `create_voter_from_scan`.
- Update en `update_voter`.
- Select por `id`, `dni` y `auth_user_id`.

## `registration_status`

Guarda el avance del proceso de registro/MFA.

| Campo | Tipo esperado | Uso en codigo |
| --- | --- | --- |
| `id` | UUID o autogenerado | No se usa directamente |
| `voter_id` | UUID | Relacion con `voters.id` |
| `current_step` | Entero | Paso actual |
| `status` | Texto | Estado textual |
| `completed_at` | Timestamp | Usado por `complete_mfa_webauthn`, aunque la funcion no esta conectada a una ruta |

Estados usados:

- `pending`
- `dni_validated`
- `face_validated`
- `completed`

Pasos usados:

- `1`: identidad registrada desde escaneo.
- `2`: identidad registrada o DNI validado.
- `3`: rostro validado.
- `4`: registro completado.

## `biometric_data`

Guarda el descriptor facial del votante.

| Campo | Tipo esperado | Uso en codigo |
| --- | --- | --- |
| `id` | UUID o autogenerado | No se usa directamente |
| `voter_id` | UUID | Relacion con `voters.id` |
| `face_embedding` | Array JSON/numerico | Descriptor facial |

Requisitos inferidos:

- `voter_id` debe ser unico para que `upsert(..., on_conflict="voter_id")` funcione.
- Para validacion MFA, `face_embedding` debe representar un vector de 128 numeros.

## `webauthn_credentials`

Guarda credenciales WebAuthn por votante.

| Campo | Tipo esperado | Uso en codigo |
| --- | --- | --- |
| `id` | UUID o autogenerado | No se usa directamente |
| `voter_id` | UUID | Relacion con `voters.id` |
| `credential_id` | Texto | Identificador de credencial |
| `public_key` | Texto | Actualmente se guarda `stored_by_browser` |
| `sign_count` | Entero | Actualmente se guarda `0` |

Requisitos inferidos:

- `voter_id` debe ser unico para el upsert.
- El codigo actual compara credenciales por `credential_id`, pero no valida firma WebAuthn completa.

## `votes`

Guarda votos emitidos.

| Campo | Tipo esperado | Uso en codigo |
| --- | --- | --- |
| `id` | UUID o autogenerado | Conteo y busqueda |
| `voter_id` | UUID | Evita doble voto |
| `candidate_id` | UUID | Candidato elegido |
| `vote_code` | Texto UUID | Codigo aleatorio generado por backend |
| `vote_hash` | Texto SHA-256 | Hash de `voter_id + candidate_id + vote_code` |

Reglas inferidas:

- Debe existir a lo mas un voto por `voter_id`.
- Conviene reforzar esta regla con una restriccion unica en base de datos.

## `candidates`

Guarda candidatos.

| Campo | Tipo esperado | Uso en codigo |
| --- | --- | --- |
| `id` | UUID | Identificador del candidato |
| `name` | Texto | Nombre mostrado en resultados |
| `photo_url` | Texto | Imagen del candidato |
| `is_active` | Booleano | Filtro para listar candidatos activos |

Operaciones:

- Select completo de candidatos activos.
- Select de `id`, `name`, `photo_url` para resultados.

## `admins`

Guarda usuarios con permiso administrativo.

| Campo | Tipo esperado | Uso en codigo |
| --- | --- | --- |
| `id` | UUID | Identificador del admin |
| `auth_user_id` | UUID | Relacion con Supabase Auth |

El login de administrador primero autentica con Supabase Auth y luego valida que el `auth_user_id` exista en `admins`.

## Relaciones recomendadas

- `registration_status.voter_id` -> `voters.id`
- `biometric_data.voter_id` -> `voters.id`
- `webauthn_credentials.voter_id` -> `voters.id`
- `votes.voter_id` -> `voters.id`
- `votes.candidate_id` -> `candidates.id`
- `admins.auth_user_id` -> usuario de Supabase Auth
- `voters.auth_user_id` -> usuario de Supabase Auth

## Restricciones recomendadas

Estas restricciones no estan definidas en el repo, pero el codigo las asume:

- `voters.dni` unico.
- `voters.email` unico cuando no sea null.
- `voters.auth_user_id` unico cuando no sea null.
- `registration_status.voter_id` unico.
- `biometric_data.voter_id` unico.
- `webauthn_credentials.voter_id` unico.
- `votes.voter_id` unico para impedir doble voto incluso bajo concurrencia.
