# Referencia completa de API

Base local sugerida: `http://localhost:10000`.

Convencion general:

```json
{ "success": true, "data": {} }
```

Errores:

```json
{ "success": false, "error": "Mensaje" }
```

## Autenticacion

Las rutas protegidas usan:

```http
Authorization: Bearer <access_token>
```

- Rutas de votante: decorador `require_auth`.
- Rutas administrativas: decorador `require_admin`.

## Salud y perfil

### `GET /`

Devuelve estado de la API.

Respuesta `200`:

```json
{ "status": "ok" }
```

### `GET /auth/me`

Requiere token de votante. Devuelve el votante autenticado.

Respuesta `200`:

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "dni": "12345678",
    "full_name": "Nombre Apellido",
    "email": "votante@example.com"
  }
}
```

## Registro

### `POST /register/identity`

Crea usuario en Supabase Auth, crea votante y estado de registro.

Rate limit: `5 per minute`.

Body:

```json
{
  "dni": "12345678",
  "full_name": "Nombre Apellido",
  "birth_date": "1995-01-20",
  "email": "votante@example.com",
  "password": "password-seguro"
}
```

Respuesta `201`:

```json
{
  "success": true,
  "message": "Registro creado correctamente",
  "data": { "voter_id": "uuid" }
}
```

### `POST /register/identity/scan`

Crea votante parcial desde escaneo de DNI.

Rate limit: `5 per hour`.

Body:

```json
{
  "dni": "12345678",
  "full_name": "Nombre Apellido"
}
```

Respuesta `201`:

```json
{
  "success": true,
  "message": "DNI registrado correctamente",
  "data": { "voter_id": "uuid" }
}
```

### `GET /register/voter/<voter_id>`

Devuelve un votante por ID.

### `PUT /register/identity/<voter_id>`

Actualiza identidad. Si el votante ya tiene `auth_user_id`, actualiza el email del usuario Auth; si no, crea usuario Auth nuevo. Luego hace login y devuelve token.

Body igual a `POST /register/identity`.

Respuesta `200`:

```json
{
  "success": true,
  "message": "Actualizado correctamente",
  "token": "jwt"
}
```

### `GET /register/summary/<voter_id>`

Requiere token del mismo votante. Devuelve identidad, flags de rostro/WebAuthn y estado de registro.

### `PUT /register/complete/<voter_id>`

Requiere token del mismo votante. Actualiza `registration_status` a `current_step = 4` y `status = completed`.

## Biometria

### `POST /register/face`

Guarda o actualiza descriptor facial.

Body:

```json
{
  "voter_id": "uuid",
  "descriptor": [0.12, -0.03, 0.44]
}
```

Respuesta:

```json
{
  "success": true,
  "message": "Rostro guardado correctamente"
}
```

El descriptor se convierte a `float`. Para MFA se espera vector de 128 posiciones.

## WebAuthn/FIDO2

Todas las rutas requieren token de votante y tienen rate limit `30 per minute`.

### `POST /webauthn/register/options`

Genera opciones de registro WebAuthn para el votante autenticado.

Respuesta:

```json
{
  "success": true,
  "data": {},
  "state": {}
}
```

### `POST /webauthn/register/verify`

Completa registro WebAuthn y guarda credencial cifrada.

Body esperado: respuesta del navegador mas `state` devuelto por options.

Respuesta:

```json
{
  "success": true,
  "message": "WebAuthn registrado correctamente"
}
```

### `POST /webauthn/auth/options`

Genera challenge de autenticacion WebAuthn.

### `POST /webauthn/auth/verify`

Verifica assertion WebAuthn y marca `mfa_sessions.webauthn_validated = true` para la sesion actual.

## Login de votante

### `POST /api/auth/login`

Body:

```json
{
  "dni": "12345678",
  "password": "password-seguro"
}
```

Respuesta:

```json
{
  "success": true,
  "data": {
    "token": "jwt",
    "user": {
      "id": "uuid",
      "dni": "12345678",
      "email": "votante@example.com"
    },
    "has_voted": false
  }
}
```

Efecto: crea una fila en `mfa_sessions` con `session_token_hash`.

## MFA

### `POST /api/mfa/validate-dni`

Rate limit: `30 per minute`.

Body:

```json
{ "dni_scanned": "12345678" }
```

Marca `dni_validated = true` en `mfa_sessions` para la sesion actual.

### `POST /api/mfa/validate-face`

Rate limit: `30 per minute`.

Body:

```json
{ "descriptor": [0.12, -0.03, 0.44] }
```

Reglas:

- Descriptor guardado y recibido deben tener 128 dimensiones.
- Distancia euclidiana maxima: `0.50`.
- Si no hay rostro registrado, devuelve error `face_not_found` con `404`.
- Si valida, marca `face_validated = true`.

## Candidatos y votos

### `GET /api/votes/candidates`

Lista candidatos activos.

Respuesta:

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Candidato",
      "party": "Partido",
      "photo_url": "https://...",
      "is_active": true
    }
  ]
}
```

### `POST /api/votes/cast`

Requiere token de votante. Rate limit: `10 per minute`.

Body para candidato:

```json
{ "candidate_id": "uuid" }
```

Body para voto en blanco:

```json
{ "candidate_id": "blank" }
```

Antes de votar exige sesion MFA completa:

- `dni_validated = true`
- `face_validated = true`
- `webauthn_validated = true`

Respuesta:

```json
{
  "success": true,
  "message": "Voto registrado correctamente"
}
```

### `GET /api/votes/results`

Requiere admin. Devuelve votos por candidato.

### `GET /api/votes/total`

Requiere admin. Devuelve total de votos.

### `GET /api/votes/turnout`

Requiere admin. Devuelve porcentaje de participacion usando total real de `voters`.

### `GET /api/votes/turnout-detailed`

Requiere admin. Devuelve `voted`, `total_voters` y `percentage`.

### `GET /api/votes/report`

Requiere admin. Devuelve reporte completo para dashboard:

- Resultados ordenados por candidato.
- Votos en blanco.
- Total de votantes.
- Total de votos.
- Participacion general.
- Participacion por edad.

### `GET /api/votes/report/csv`

Requiere admin. Devuelve CSV con `Content-Disposition: attachment; filename=reporte_votacion.csv`.

## Administracion

### `POST /api/admin/login`

Body:

```json
{
  "email": "admin@example.com",
  "password": "password-seguro"
}
```

Autentica con Supabase Auth y valida que `auth_user_id` exista en `admins`.
