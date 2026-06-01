# Documentacion consolidada de NEXA Vote Back

Documento unico del backend NEXA Vote. Alcance: rama `main`, commit `2d7c0eb0360d63763bd9cc8c9063e9276bee1d44`. La rama `Pruebas` se omite porque no existe en GitHub y el usuario pidio ignorarla.

## 1. Vision general

NEXA Vote Back es una API Flask que administra el ciclo de un sistema de votacion:

- Registro de identidad del votante.
- Registro y validacion de biometria facial.
- Registro y validacion WebAuthn/FIDO2.
- Login de votantes y administradores.
- MFA por DNI, rostro y WebAuthn.
- Emision de voto normal o voto en blanco.
- Resultados y reportes electorales.
- Protecciones basicas: rate limiting, headers de seguridad, token JWT y hash de sesion.

El backend usa Supabase para autenticacion y persistencia. Las operaciones privilegiadas usan `SUPABASE_SERVICE_ROLE_KEY`.

## 2. Stack tecnico

- Python 3.11.
- Flask 3.1.
- Flask-CORS.
- Flask-Limiter.
- Supabase Python Client.
- FIDO2/WebAuthn.
- Cryptography/Fernet para cifrado de datos sensibles.
- NumPy para comparacion de descriptores faciales.
- Gunicorn para produccion.
- Docker para contenedor.

## 3. Estructura del repositorio

```text
.
├── AGENTS.md
├── Dockerfile
├── README.md
├── requirements.txt
├── run.py
└── app/
    ├── __init__.py
    ├── config.py
    ├── extensions.py
    ├── middleware/
    │   ├── auth_middleware.py
    │   └── security_headers.py
    ├── routes/
    │   ├── admin.py
    │   ├── auth.py
    │   ├── biometric.py
    │   ├── candidates.py
    │   ├── mfa.py
    │   ├── registration.py
    │   ├── votes.py
    │   └── webauthn.py
    ├── services/
    │   ├── admin_service.py
    │   ├── audit_service.py
    │   ├── auth_service.py
    │   ├── biometric_service.py
    │   ├── candidate_service.py
    │   ├── mfa_service.py
    │   ├── registration_service.py
    │   ├── report_service.py
    │   ├── vote_service.py
    │   └── webauthn_service.py
    └── utils/
        ├── encryption.py
        ├── supabase_client.py
        └── validators.py
```

## 4. Configuracion

Variables leidas por `app/config.py`:

| Variable | Uso |
| --- | --- |
| `SUPABASE_URL` | URL del proyecto Supabase |
| `SUPABASE_KEY` | Llave anon/public para operaciones normales |
| `SUPABASE_SERVICE_ROLE_KEY` | Llave administrativa para Auth Admin y bypass de RLS |
| `VOTE_SECRET_KEY` | Secreto para hash de votos y cifrado Fernet derivado |
| `SECRET_KEY` | Secreto Flask/FIDO2 cuando aplique |
| `ALLOWED_ORIGINS` | Origenes permitidos por CORS y WebAuthn |
| `PORT` | Puerto de ejecucion, default `10000` |

Ejemplo:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=anon-public-key
SUPABASE_SERVICE_ROLE_KEY=service-role-key
VOTE_SECRET_KEY=clave-larga-para-votos
SECRET_KEY=clave-larga-de-sesion
ALLOWED_ORIGINS=http://localhost:5173
PORT=10000
```

## 5. Arranque y despliegue

Desarrollo local:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Produccion segun Dockerfile:

```bash
gunicorn -w 1 --timeout 120 -b 0.0.0.0:${PORT:-10000} 'run:app'
```

Docker:

```bash
docker build -t nexa-vote-back .
docker run --env-file .env -p 10000:10000 nexa-vote-back
```

## 6. Ciclo de vida de Flask

`run.py` importa `create_app`, crea `app` y escucha en `0.0.0.0:${PORT:-10000}` si se ejecuta directamente.

`app/__init__.py`:

- Crea la instancia Flask.
- Inicializa `limiter` desde `app/extensions.py`.
- Registra `security_headers` como `after_request`.
- Configura CORS con `ALLOWED_ORIGINS`.
- Registra blueprints.
- Expone `GET /` como health check.
- Expone `GET /auth/me` protegido por `require_auth`.

## 7. Middleware y seguridad

### `require_auth`

Archivo: `app/middleware/auth_middleware.py`.

- Lee `Authorization: Bearer <token>`.
- Valida el JWT con Supabase usando un cliente temporal con service role.
- Busca el votante por `auth_user_id`.
- Guarda en `flask.g`:
  - `g.voter_id`
  - `g.auth_user_id`
  - `g.session_token_hash`, hash SHA-256 del access token.

### `require_admin`

- Valida el JWT igual que `require_auth`.
- Busca el usuario en la tabla `admins`.
- Si no existe, responde `403 No autorizado`.
- Guarda `g.admin_id` y `g.auth_user_id`.

### Headers de seguridad

Archivo: `app/middleware/security_headers.py`.

Agrega:

- `Content-Security-Policy: default-src 'self'`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

### Rate limiting

Archivo: `app/extensions.py`.

Usa `Flask-Limiter` con IP remota como llave. Rutas sensibles tienen limites como `5 per minute`, `5 per hour`, `10 per minute` o `30 per minute`.

## 8. Cifrado

Archivo: `app/utils/encryption.py`.

- Deriva una llave Fernet desde `VOTE_SECRET_KEY` ajustandola a 32 caracteres.
- `encrypt_text(plain)` cifra texto.
- `decrypt_text(token)` descifra tokens Fernet.
- Mantiene compatibilidad hacia atras: si el valor no empieza con `gAAAAA`, lo devuelve como texto plano.

Se usa para datos como `credential_raw` de WebAuthn y descriptores faciales guardados como texto cifrado.

## 9. Clientes Supabase

Archivo: `app/utils/supabase_client.py`.

- `get_supabase()`: cliente con `SUPABASE_KEY`.
- `get_supabase_admin()`: cliente con `SUPABASE_SERVICE_ROLE_KEY`.

Los clientes se crean bajo demanda y quedan cacheados en variables globales.

## 10. Validaciones de identidad

Archivo: `app/utils/validators.py`.

`validate_identity(data)` valida:

- `dni`, `full_name`, `birth_date`, `email` obligatorios.
- DNI numerico de 8 digitos.
- Nombre entre 3 y 100 caracteres, solo letras y espacios.
- Email con regex basico.
- Fecha `YYYY-MM-DD`.
- Edad entre 18 y 100 anos.

Nota: `password` es necesario para crear/login de usuario, pero el validador de identidad no lo valida explicitamente.

## 11. Endpoints

### Salud

| Metodo | Ruta | Auth | Descripcion |
| --- | --- | --- | --- |
| GET | `/` | No | Health check, devuelve `{ "status": "ok" }` |
| GET | `/auth/me` | Votante | Devuelve el votante autenticado |

### Registro

| Metodo | Ruta | Auth | Rate limit | Descripcion |
| --- | --- | --- | --- | --- |
| POST | `/register/identity` | No | `5 per minute` | Crea usuario Supabase Auth, votante y estado de registro |
| POST | `/register/identity/scan` | No | `5 per hour` | Crea votante parcial desde escaneo de DNI |
| GET | `/register/voter/<voter_id>` | No | No definido | Consulta votante por ID |
| PUT | `/register/identity/<voter_id>` | No | No definido | Actualiza identidad; reutiliza Auth si existe o crea usuario |
| GET | `/register/summary/<voter_id>` | Votante | No definido | Resumen del registro del votante autenticado |
| PUT | `/register/complete/<voter_id>` | Votante | No definido | Marca registro como completado |

### Biometria

| Metodo | Ruta | Auth | Descripcion |
| --- | --- | --- | --- |
| POST | `/register/face` | Segun ruta actual | Guarda o actualiza descriptor facial |

El servicio normaliza los valores del descriptor a `float`. La validacion MFA espera 128 dimensiones.

### WebAuthn

| Metodo | Ruta | Auth | Rate limit | Descripcion |
| --- | --- | --- | --- | --- |
| POST | `/webauthn/register/options` | Votante | `30 per minute` | Genera opciones FIDO2 de registro |
| POST | `/webauthn/register/verify` | Votante | `30 per minute` | Completa registro y guarda credencial cifrada |
| POST | `/webauthn/auth/options` | Votante | `30 per minute` | Genera opciones de autenticacion WebAuthn |
| POST | `/webauthn/auth/verify` | Votante | `30 per minute` | Verifica assertion WebAuthn y marca MFA WebAuthn |

La implementacion actual usa `Fido2Server`, valida origin contra `ALLOWED_ORIGINS`, requiere user verification y guarda `credential_raw`, `credential_id`, `public_key` y `sign_count`.

### Auth de votante

| Metodo | Ruta | Auth | Descripcion |
| --- | --- | --- | --- |
| POST | `/api/auth/login` | No | Login por DNI/password |

Flujo:

1. Busca votante por DNI.
2. Usa el email del votante para `sign_in_with_password`.
3. Inserta una fila en `mfa_sessions` con hash del access token.
4. Consulta `vote_tokens` para calcular `has_voted`.
5. Devuelve token, datos basicos del usuario y `has_voted`.

### MFA

| Metodo | Ruta | Auth | Rate limit | Descripcion |
| --- | --- | --- | --- | --- |
| POST | `/api/mfa/validate-dni` | Token en header | `30 per minute` | Compara DNI escaneado con DNI registrado |
| POST | `/api/mfa/validate-face` | Token en header | `30 per minute` | Compara descriptor facial recibido con el guardado |

`validate-dni` marca `mfa_sessions.dni_validated = true`.

`validate-face`:

- Resuelve el votante desde el token.
- Lee `biometric_data.face_embedding`.
- Si esta cifrado, lo descifra.
- Convierte descriptor guardado y recibido a NumPy.
- Requiere 128 dimensiones.
- Calcula distancia euclidiana.
- Usa umbral `0.50`.
- Marca `mfa_sessions.face_validated = true`.

### Candidatos y votos

| Metodo | Ruta | Auth | Descripcion |
| --- | --- | --- | --- |
| GET | `/api/votes/candidates` | Segun ruta actual | Lista candidatos activos |
| POST | `/api/votes/cast` | Votante | Emite voto normal o blanco |
| GET | `/api/votes/results` | Admin | Resultados por candidato |
| GET | `/api/votes/total` | Admin | Total de votos |
| GET | `/api/votes/turnout` | Admin | Porcentaje de participacion |
| GET | `/api/votes/turnout-detailed` | Admin | Participacion con total y votantes |
| GET | `/api/votes/report` | Admin | Reporte completo para dashboard |
| GET | `/api/votes/report/csv` | Admin | Reporte descargable CSV |

`POST /api/votes/cast` exige que la sesion MFA tenga:

- `dni_validated = true`
- `face_validated = true`
- `webauthn_validated = true`

Acepta `candidate_id = "blank"` para voto en blanco. Si no es blanco, valida que el candidato exista.

Privacidad del voto actual:

- Se registra `vote_tokens` con `voter_id` y `token`.
- Se registra `votes` con `token_hash`, `candidate_id`, `vote_code`, `vote_hash`.
- La doble votacion se controla consultando `vote_tokens` por `voter_id`.

### Administracion

| Metodo | Ruta | Auth | Descripcion |
| --- | --- | --- | --- |
| POST | `/api/admin/login` | No | Login de administrador |

El login autentica por Supabase Auth y luego valida que el `auth_user_id` exista en `admins`.

## 12. Reportes electorales

Archivo: `app/services/report_service.py`.

`get_report()` construye:

```json
{
  "results": [
    {
      "candidate_id": "uuid",
      "name": "Nombre",
      "party": "Partido",
      "photo_url": "url",
      "total": 10,
      "percentage": 50.0
    }
  ],
  "blank_votes": { "total": 1, "percentage": 5.0 },
  "total_voters": 100,
  "total_votes": 20,
  "turnout_percentage": 20.0,
  "turnout_by_age": {
    "18-25": { "total": 10, "voted": 5, "percentage": 50.0 },
    "26-40": { "total": 20, "voted": 10, "percentage": 50.0 },
    "41-60": { "total": 15, "voted": 8, "percentage": 53.33 },
    "60+": { "total": 5, "voted": 2, "percentage": 40.0 }
  }
}
```

`get_report_csv()` genera CSV con:

- Resultados por candidato.
- Votos en blanco.
- Totales generales.
- Participacion por edad.

## 13. Modelo de datos esperado

El repositorio no incluye migraciones. Este modelo se infiere del codigo.

### `voters`

| Campo | Uso |
| --- | --- |
| `id` | Identificador del votante |
| `dni` | Login y validacion de DNI |
| `full_name` | Nombre completo |
| `birth_date` | Fecha usada para edad y reportes |
| `email` | Login Supabase |
| `auth_user_id` | Relacion con Supabase Auth |
| `registration_step` | Paso visible de registro |

### `registration_status`

| Campo | Uso |
| --- | --- |
| `voter_id` | Relacion con votante |
| `current_step` | Paso actual |
| `status` | Estado textual: `pending`, `completed`, etc. |

### `biometric_data`

| Campo | Uso |
| --- | --- |
| `voter_id` | Relacion con votante |
| `face_embedding` | Descriptor facial, texto cifrado o dato legado plano |

### `webauthn_credentials`

| Campo | Uso |
| --- | --- |
| `voter_id` | Relacion con votante |
| `credential_raw` | Credencial FIDO2 cifrada |
| `credential_id` | ID websafe de credencial |
| `public_key` | Public key codificada |
| `sign_count` | Contador de autenticador |

### `mfa_sessions`

| Campo | Uso |
| --- | --- |
| `voter_id` | Votante autenticado |
| `session_token_hash` | SHA-256 del token de sesion |
| `dni_validated` | DNI validado |
| `face_validated` | Rostro validado |
| `webauthn_validated` | WebAuthn validado |

### `vote_tokens`

| Campo | Uso |
| --- | --- |
| `voter_id` | Control de doble voto |
| `token` | Token aleatorio interno del voto |

### `votes`

| Campo | Uso |
| --- | --- |
| `token_hash` | Hash del token con secreto |
| `candidate_id` | Candidato elegido o `null` para blanco |
| `vote_code` | UUID publico/interno del voto |
| `vote_hash` | Hash del token, candidato y secreto |

### `candidates`

| Campo | Uso |
| --- | --- |
| `id` | Identificador |
| `name` | Nombre del candidato |
| `party` | Partido, usado en reportes |
| `photo_url` | Foto |
| `is_active` | Filtro de candidatos activos |

### `admins`

| Campo | Uso |
| --- | --- |
| `id` | Identificador admin |
| `auth_user_id` | Usuario Supabase autorizado |

### `audit_logs`

| Campo | Uso |
| --- | --- |
| `voter_id` | Votante relacionado, opcional |
| `action_type` | Tipo de evento |
| `status` | Resultado |
| `ip_address` | IP remota |
| `metadata` | Datos adicionales |

## 14. Flujos principales

### Registro completo

1. `POST /register/identity` crea Auth user, votante y `registration_status`.
2. `POST /register/face` guarda biometria.
3. `POST /webauthn/register/options` genera opciones FIDO2.
4. `POST /webauthn/register/verify` guarda credencial WebAuthn.
5. `PUT /register/complete/<voter_id>` marca estado completado.

### Login y MFA

1. `POST /api/auth/login` devuelve token y crea `mfa_sessions`.
2. `POST /api/mfa/validate-dni` marca DNI validado.
3. `POST /api/mfa/validate-face` marca rostro validado.
4. `POST /webauthn/auth/options` genera challenge.
5. `POST /webauthn/auth/verify` marca WebAuthn validado.

### Voto

1. Frontend envia `Authorization: Bearer <token>`.
2. `require_auth` resuelve `g.voter_id` y `g.session_token_hash`.
3. `cast_vote` valida que la sesion MFA este completa.
4. Se valida candidato o voto blanco.
5. Se verifica que no exista `vote_tokens` para ese votante.
6. Se inserta token interno y voto hash.

## 15. Mapa archivo por archivo

| Archivo | Responsabilidad |
| --- | --- |
| `run.py` | Punto de entrada de Flask |
| `app/__init__.py` | Factory, CORS, limiter, headers, rutas |
| `app/config.py` | Variables de entorno |
| `app/extensions.py` | Instancia compartida de limiter |
| `app/middleware/auth_middleware.py` | Decoradores de auth votante/admin |
| `app/middleware/security_headers.py` | Headers de seguridad |
| `app/routes/registration.py` | Endpoints de registro |
| `app/routes/biometric.py` | Endpoint facial |
| `app/routes/webauthn.py` | Endpoints FIDO2/WebAuthn |
| `app/routes/auth.py` | Login votante |
| `app/routes/mfa.py` | MFA DNI y rostro |
| `app/routes/candidates.py` | Candidatos activos |
| `app/routes/votes.py` | Votos, resultados y reportes |
| `app/routes/admin.py` | Login admin |
| `app/services/registration_service.py` | Persistencia de votantes y estado |
| `app/services/auth_service.py` | Login votante y creacion de sesion MFA |
| `app/services/mfa_service.py` | Validaciones DNI/rostro |
| `app/services/webauthn_service.py` | FIDO2 registro/autenticacion |
| `app/services/vote_service.py` | Emision, resultados y participacion |
| `app/services/report_service.py` | Reporte JSON/CSV |
| `app/services/biometric_service.py` | Guardado de descriptor facial |
| `app/services/candidate_service.py` | Consulta de candidatos |
| `app/services/admin_service.py` | Login admin |
| `app/services/audit_service.py` | Insercion de logs de auditoria |
| `app/utils/supabase_client.py` | Clientes Supabase |
| `app/utils/encryption.py` | Cifrado/descifrado |
| `app/utils/validators.py` | Validaciones de identidad |

## 16. Riesgos y pendientes conocidos

- No hay migraciones SQL versionadas para crear el esquema.
- No hay pruebas automatizadas, CI, linter ni typechecker.
- La proteccion contra doble voto debe reforzarse con restriccion unica en `vote_tokens.voter_id`.
- `VOTE_SECRET_KEY` tiene default de desarrollo; en produccion debe ser obligatorio y fuerte.
- La llave Fernet deriva de `VOTE_SECRET_KEY` con padding/truncado; cambiar el secreto puede impedir descifrar datos previos.
- Algunas rutas llaman `request.get_json().get(...)`; un body vacio podria causar error si no esta controlado en todas las rutas.
- El uso de `SUPABASE_SERVICE_ROLE_KEY` exige que el backend nunca se exponga como cliente publico.
- `audit_service.log_action` existe, pero su uso efectivo debe revisarse porque no todas las operaciones criticas parecen auditarse.
- CSP `default-src 'self'` puede ser demasiado restrictivo si el frontend o recursos externos se sirven desde otros dominios.

## 17. Recomendaciones siguientes

- Agregar migraciones SQL o scripts reproducibles para Supabase.
- Agregar pruebas para login, MFA, WebAuthn, voto blanco, doble voto y reportes.
- Validar body JSON en todas las rutas antes de usar `.get`.
- Crear indices y constraints unicos para `voters.dni`, `voters.auth_user_id`, `mfa_sessions`, `vote_tokens.voter_id` y credenciales WebAuthn.
- Rotar secretos de desarrollo antes de produccion.
- Definir politicas RLS claras y documentarlas junto al esquema.
