# NEXA Vote Back

Backend de NEXA Vote, una API Flask para registro de votantes, validacion multifactor, autenticacion, candidatos, emision de votos y consulta de resultados. El proyecto usa Supabase como proveedor de base de datos y autenticacion.

## Contenido de la documentacion

- [Arquitectura del proyecto](docs/ARCHITECTURE.md)
- [Referencia completa de API](docs/API.md)
- [Modelo de datos esperado en Supabase](docs/DATABASE.md)
- [Configuracion, ejecucion y despliegue](docs/DEPLOYMENT.md)
- [Mapa archivo por archivo](docs/FILE_MAP.md)
- [Limitaciones conocidas y pendientes tecnicos](docs/KNOWN_LIMITATIONS.md)

## Resumen funcional

El backend expone servicios para:

- Crear y actualizar votantes.
- Registrar identidad desde formulario o escaneo de DNI.
- Guardar descriptor facial del votante.
- Generar y guardar credenciales WebAuthn.
- Autenticar votantes por DNI y password.
- Validar MFA por DNI escaneado y descriptor facial.
- Listar candidatos activos.
- Registrar un voto por votante autenticado.
- Consultar resultados, total de votos y participacion.
- Autenticar administradores.

## Stack

- Python 3.11
- Flask
- Flask-CORS
- Supabase Python Client
- NumPy para comparacion de descriptores faciales
- Gunicorn para ejecucion en produccion
- Docker para despliegue contenedorizado

## Estructura

```text
.
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── biometric.py
│   │   ├── candidates.py
│   │   ├── mfa.py
│   │   ├── registration.py
│   │   ├── votes.py
│   │   └── webauthn.py
│   ├── services/
│   │   ├── admin_service.py
│   │   ├── auth_service.py
│   │   ├── biometric_service.py
│   │   ├── candidate_service.py
│   │   ├── mfa_service.py
│   │   ├── registration_service.py
│   │   ├── vote_service.py
│   │   └── webauthn_service.py
│   └── utils/
│       ├── supabase_client.py
│       └── validators.py
├── docs/
├── Dockerfile
├── requirements.txt
└── run.py
```

## Variables de entorno

La aplicacion carga variables desde el entorno y, en desarrollo, tambien desde un archivo `.env` gracias a `python-dotenv`.

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=anon-public-key
SUPABASE_SERVICE_ROLE_KEY=service-role-key
ALLOWED_ORIGINS=http://localhost:5173
PORT=10000
```

Importante: `SUPABASE_SERVICE_ROLE_KEY` tiene permisos administrativos. No debe exponerse en frontend, commits, logs publicos ni capturas.

## Ejecucion local

1. Crear entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Crear `.env` con las variables necesarias.

4. Ejecutar la API:

```bash
python run.py
```

La API queda disponible en:

```text
http://localhost:10000
```

El endpoint raiz `GET /` responde:

```json
{
  "status": "ok"
}
```

## Ejecucion con Docker

```bash
docker build -t nexa-vote-back .
docker run --env-file .env -p 10000:10000 nexa-vote-back
```

## Flujo principal de registro y voto

1. Registrar identidad con `POST /register/identity` o crear identidad inicial por escaneo con `POST /register/identity/scan`.
2. Guardar biometria facial con `POST /register/face`.
3. Registrar WebAuthn con `POST /webauthn/register/options` y `POST /webauthn/register/verify`.
4. Completar registro con `PUT /register/complete/<voter_id>`.
5. Iniciar sesion con `POST /api/auth/login`.
6. Validar MFA por DNI con `POST /api/mfa/validate-dni`.
7. Validar MFA facial con `POST /api/mfa/validate-face`.
8. Consultar candidatos con `GET /api/votes/candidates`.
9. Emitir voto con `POST /api/votes/cast`.
10. Consultar resultados con `GET /api/votes/results`.

## Convencion de respuestas

La mayoria de endpoints devuelven:

```json
{
  "success": true,
  "data": {}
}
```

En errores:

```json
{
  "success": false,
  "error": "Descripcion del error"
}
```

## Tablas esperadas

El codigo usa estas tablas de Supabase:

- `voters`
- `registration_status`
- `biometric_data`
- `webauthn_credentials`
- `votes`
- `candidates`
- `admins`

La documentacion del modelo esperado esta en [docs/DATABASE.md](docs/DATABASE.md).

## Estado actual del proyecto

El repositorio actual contiene la API y documentacion, pero no incluye pruebas automatizadas, migraciones SQL, archivo `.env.example` previo, ni definiciones formales del esquema de Supabase. Tambien se detecto que `app/services/webauthn_service.py` termina dentro de `verify_webauthn_login`, por lo que esa funcion parece incompleta. Estos puntos estan detallados en [docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md).
