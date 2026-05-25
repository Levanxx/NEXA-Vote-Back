# Referencia de API

Base URL local sugerida:

```text
http://localhost:10000
```

Todas las respuestas usan JSON. En general:

- `success: true` indica operacion correcta.
- `success: false` indica error y suele incluir `error`.

## Salud

### `GET /`

Verifica que la API esta activa.

Respuesta `200`:

```json
{
  "status": "ok"
}
```

## Registro de votantes

### `POST /register/identity`

Crea un usuario de Supabase Auth y un registro en `voters`. Tambien crea un registro inicial en `registration_status`.

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

Validaciones:

- `dni`, `full_name`, `birth_date` y `email` son obligatorios.
- `password` se usa en el servicio, por lo que tambien debe enviarse aunque el validador actual no lo revise explicitamente.
- El DNI debe tener 8 digitos.
- El nombre debe tener entre 3 y 100 caracteres.
- La fecha debe estar en formato `YYYY-MM-DD`.
- El votante debe tener entre 18 y 100 anos.

Respuesta `201`:

```json
{
  "success": true,
  "message": "Registro creado correctamente",
  "data": {
    "voter_id": "uuid"
  }
}
```

Errores:

- `400` si el body esta vacio o no pasa validacion.
- `500` si Supabase o el servidor fallan.

### `POST /register/identity/scan`

Crea un votante parcial desde datos escaneados de DNI.

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
  "data": {
    "voter_id": "uuid"
  }
}
```

El servicio inserta:

- `birth_date: null`
- `email: null`
- `auth_user_id: null`
- `registration_step: 1`
- `registration_status.current_step: 1`
- `registration_status.status: pending`

### `GET /register/voter/<voter_id>`

Obtiene un votante por ID.

Respuesta `200`:

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "dni": "12345678",
    "full_name": "Nombre Apellido",
    "birth_date": "1995-01-20",
    "email": "votante@example.com",
    "auth_user_id": "uuid",
    "registration_step": 2
  }
}
```

Errores:

- `404` si no existe el votante.
- `500` si falla la consulta.

### `PUT /register/identity/<voter_id>`

Actualiza la identidad del votante y crea un nuevo usuario en Supabase Auth con el email/password enviados.

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

Respuesta `200`:

```json
{
  "success": true,
  "message": "Actualizado correctamente"
}
```

### `GET /register/summary/<voter_id>`

Devuelve resumen del registro de un votante.

Respuesta `200`:

```json
{
  "success": true,
  "data": {
    "voter": {},
    "face_registered": true,
    "webauthn_registered": true,
    "status": {}
  }
}
```

### `PUT /register/complete/<voter_id>`

Marca el registro como completado en `registration_status`.

Respuesta `200`:

```json
{
  "success": true,
  "message": "Registro completado"
}
```

## Biometria

### `POST /register/face`

Guarda o actualiza el descriptor facial del votante en `biometric_data`.

Body:

```json
{
  "voter_id": "uuid",
  "descriptor": [0.12, -0.04, 0.88]
}
```

Notas:

- El codigo convierte cada valor del descriptor a `float`.
- Para MFA facial, el descriptor esperado debe tener 128 posiciones.
- El upsert usa `voter_id` como conflicto.

Respuesta `200`:

```json
{
  "success": true,
  "message": "Rostro guardado correctamente"
}
```

Errores:

- `400` si falta `voter_id` o `descriptor`.
- `500` si falla Supabase o la conversion del descriptor.

## WebAuthn

### `POST /webauthn/register/options`

Genera un challenge aleatorio en base64.

Respuesta `200`:

```json
{
  "success": true,
  "challenge": "base64-challenge"
}
```

### `POST /webauthn/register/verify`

Guarda una credencial WebAuthn asociada a un votante.

Body:

```json
{
  "voter_id": "uuid",
  "id": "credential-id"
}
```

Respuesta `200`:

```json
{
  "success": true,
  "message": "WebAuthn guardado correctamente"
}
```

Notas:

- El servicio guarda `credential_id`.
- `public_key` queda con el valor fijo `stored_by_browser`.
- `sign_count` queda en `0`.
- No se valida criptograficamente la respuesta WebAuthn en el backend actual.

### `POST /webauthn/auth/options`

Genera un challenge aleatorio para autenticacion WebAuthn.

Respuesta `200`:

```json
{
  "success": true,
  "challenge": "base64-challenge"
}
```

### `POST /webauthn/auth/verify`

Intenta validar una credencial WebAuthn de login.

Body:

```json
{
  "voter_id": "uuid",
  "id": "credential-id"
}
```

Respuesta esperada por la ruta si el servicio valida:

```json
{
  "success": true,
  "message": "WebAuthn validado"
}
```

Limitacion actual: `verify_webauthn_login` aparece incompleta en `app/services/webauthn_service.py`; por eso esta ruta puede fallar o no validar correctamente hasta completar esa funcion.

## Autenticacion de votante

### `POST /api/auth/login`

Autentica un votante usando DNI y password.

Body:

```json
{
  "dni": "12345678",
  "password": "password-seguro"
}
```

Respuesta `200`:

```json
{
  "success": true,
  "data": {
    "token": "jwt-access-token",
    "user": {
      "id": "uuid",
      "dni": "12345678",
      "email": "votante@example.com"
    },
    "has_voted": false
  }
}
```

Errores:

- `400` si falta DNI o password.
- `401` si el votante no existe o las credenciales no son validas.

## MFA

Los endpoints MFA requieren header:

```http
Authorization: Bearer <access_token>
```

### `POST /api/mfa/validate-dni`

Valida que el DNI escaneado coincida con el votante autenticado.

Body:

```json
{
  "dni_scanned": "12345678"
}
```

Respuesta `200`:

```json
{
  "success": true,
  "data": {
    "message": "DNI validado correctamente",
    "voter_id": "uuid"
  }
}
```

Efecto en base de datos:

- `registration_status.current_step = 2`
- `registration_status.status = dni_validated`

### `POST /api/mfa/validate-face`

Valida que el descriptor facial recibido coincida con el descriptor guardado.

Body:

```json
{
  "descriptor": [0.12, -0.04, 0.88]
}
```

Respuesta `200`:

```json
{
  "success": true,
  "data": {
    "message": "Rostro validado correctamente",
    "voter_id": "uuid",
    "distancia": 0.3742
  }
}
```

Reglas:

- Descriptor guardado y descriptor recibido deben tener 128 posiciones.
- Se calcula distancia euclidiana con NumPy.
- Umbral actual: `0.50`.
- Si la distancia es mayor al umbral, se rechaza.

Efecto en base de datos:

- `registration_status.current_step = 3`
- `registration_status.status = face_validated`

## Candidatos y votos

### `GET /api/votes/candidates`

Lista candidatos activos desde `candidates`.

Respuesta `200`:

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Candidato",
      "photo_url": "https://example.com/photo.png",
      "is_active": true
    }
  ]
}
```

### `POST /api/votes/cast`

Registra un voto para el votante autenticado.

Header:

```http
Authorization: Bearer <access_token>
```

Body:

```json
{
  "candidate_id": "uuid"
}
```

Respuesta `200`:

```json
{
  "success": true,
  "message": "Voto registrado correctamente"
}
```

Reglas:

- Se obtiene el votante desde el token.
- Se rechaza si ya existe un voto para ese `voter_id`.
- Se genera `vote_code` con UUID.
- Se genera `vote_hash` con SHA-256 sobre `voter_id + candidate_id + vote_code`.

Errores:

- `400` si falta `candidate_id`, el token es invalido, el votante no existe o ya voto.

### `GET /api/votes/results`

Devuelve los votos acumulados por candidato.

Respuesta `200`:

```json
{
  "success": true,
  "data": [
    {
      "candidate_id": "uuid",
      "candidate_name": "Candidato",
      "photo_url": "https://example.com/photo.png",
      "total": 10
    }
  ]
}
```

### `GET /api/votes/total`

Devuelve el total de votos registrados.

Respuesta `200`:

```json
{
  "success": true,
  "total": 25
}
```

### `GET /api/votes/turnout`

Devuelve porcentaje de participacion.

Respuesta `200`:

```json
{
  "success": true,
  "percentage": 16.67
}
```

Nota: el total de votantes esta hardcodeado como `150`.

### `GET /api/votes/turnout-detailed`

Devuelve participacion detallada.

Respuesta `200`:

```json
{
  "success": true,
  "voted": 25,
  "total_voters": 150,
  "percentage": 16.67
}
```

## Administracion

### `POST /api/admin/login`

Autentica un administrador con email/password y valida que exista en la tabla `admins`.

Body:

```json
{
  "email": "admin@example.com",
  "password": "password-seguro"
}
```

Respuesta `200`:

```json
{
  "success": true,
  "data": {
    "token": "jwt-access-token",
    "admin": {
      "id": "uuid",
      "auth_user_id": "uuid"
    }
  }
}
```

Errores:

- `401` si las credenciales son invalidas o el usuario autenticado no existe en `admins`.
