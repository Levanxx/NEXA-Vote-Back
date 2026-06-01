# Configuracion, ejecucion y despliegue

## Requisitos

- Python 3.11.
- Proyecto Supabase configurado.
- Tablas indicadas en `docs/DATABASE.md`.
- Variables de entorno reales.
- Frontend autorizado en `ALLOWED_ORIGINS`.

## Variables de entorno

| Variable | Obligatoria | Descripcion |
| --- | --- | --- |
| `SUPABASE_URL` | Si | URL del proyecto Supabase |
| `SUPABASE_KEY` | Si | Llave anon/public |
| `SUPABASE_SERVICE_ROLE_KEY` | Si | Llave administrativa del backend |
| `VOTE_SECRET_KEY` | Si en produccion | Secreto para hashes de voto y cifrado |
| `SECRET_KEY` | Si en produccion | Secreto de Flask/sesion |
| `ALLOWED_ORIGINS` | Recomendado | Origenes CORS y WebAuthn separados por coma |
| `PORT` | No | Puerto, default `10000` |

Ejemplo:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=anon-public-key
SUPABASE_SERVICE_ROLE_KEY=service-role-key
VOTE_SECRET_KEY=clave-larga-para-votos
SECRET_KEY=clave-larga-de-flask
ALLOWED_ORIGINS=http://localhost:5173
PORT=10000
```

## Instalacion local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Verificar:

```bash
curl http://localhost:10000/
```

Respuesta esperada:

```json
{ "status": "ok" }
```

## Docker

Construir:

```bash
docker build -t nexa-vote-back .
```

Ejecutar:

```bash
docker run --env-file .env -p 10000:10000 nexa-vote-back
```

## Gunicorn

El `Dockerfile` ejecuta:

```bash
gunicorn -w 1 --timeout 120 -b 0.0.0.0:${PORT:-10000} 'run:app'
```

Parametros:

- `-w 1`: un worker.
- `--timeout 120`: timeout de 120 segundos.
- `0.0.0.0`: escucha conexiones externas dentro del contenedor.

## CORS y WebAuthn

`ALLOWED_ORIGINS` se usa para CORS y tambien para validar origins WebAuthn.

Ejemplo multiple:

```env
ALLOWED_ORIGINS=http://localhost:5173,https://nexa-vote.example.com
```

El primer origen se usa para derivar `rp_id` WebAuthn. En produccion debe coincidir con el dominio real del frontend.

## Checklist de despliegue

- Crear tablas Supabase.
- Agregar constraints unicos recomendados.
- Configurar usuarios administradores en `admins`.
- Cargar candidatos activos en `candidates`.
- Configurar variables de entorno reales.
- Verificar `ALLOWED_ORIGINS` con el dominio del frontend.
- Probar login de votante.
- Probar MFA completo.
- Probar voto en candidato y voto blanco en ambiente de prueba.
- Probar reportes admin.

## Seguridad operativa

- No exponer `SUPABASE_SERVICE_ROLE_KEY` al frontend.
- No commitear `.env` real.
- Usar `VOTE_SECRET_KEY` y `SECRET_KEY` fuertes.
- No cambiar `VOTE_SECRET_KEY` sin plan de rotacion porque afecta cifrado y hashes.
- Revisar logs para evitar exposicion de datos biometricos.
- Restringir RLS en Supabase y permitir que solo el backend use operaciones administrativas.

## Verificacion minima post-deploy

1. `GET /` devuelve `200`.
2. Login admin funciona.
3. Login votante crea `mfa_sessions`.
4. WebAuthn genera options con origin correcto.
5. `POST /api/votes/cast` bloquea si MFA esta incompleto.
6. `GET /api/votes/report` requiere admin y devuelve estructura esperada.
