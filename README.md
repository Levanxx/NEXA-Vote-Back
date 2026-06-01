# NEXA Vote Back

Backend Flask para NEXA Vote: registro de votantes, autenticacion, MFA por DNI/rostro/WebAuthn, emision de votos, voto en blanco, resultados, reportes electorales y login administrativo sobre Supabase.

Esta documentacion corresponde al estado actualizado de `main` en el commit `2d7c0eb0360d63763bd9cc8c9063e9276bee1d44`.

## Documentacion

- [Arquitectura del proyecto](docs/ARCHITECTURE.md)
- [Referencia completa de API](docs/API.md)
- [Modelo de datos esperado en Supabase](docs/DATABASE.md)
- [Configuracion, ejecucion y despliegue](docs/DEPLOYMENT.md)
- [Diagramas y flujos del sistema](docs/DIAGRAMS.md)
- [Mapa archivo por archivo](docs/FILE_MAP.md)
- [Limitaciones conocidas y pendientes tecnicos](docs/KNOWN_LIMITATIONS.md)

## Resumen funcional

El backend permite:

- Registrar votantes desde formulario o escaneo de DNI.
- Actualizar identidad y asociar usuarios de Supabase Auth.
- Registrar biometria facial.
- Registrar y validar WebAuthn/FIDO2.
- Iniciar sesion como votante o administrador.
- Crear sesiones MFA y validar DNI, rostro y WebAuthn.
- Emitir un voto por votante autenticado y verificado.
- Registrar voto en blanco con `candidate_id = "blank"`.
- Consultar resultados, total de votos, participacion y reportes JSON/CSV.
- Aplicar rate limiting, headers de seguridad y decoradores de autorizacion.

## Stack

- Python 3.11
- Flask 3.1
- Flask-CORS
- Flask-Limiter
- Supabase Python Client
- FIDO2/WebAuthn
- Cryptography/Fernet
- NumPy
- Gunicorn
- Docker

## Arranque rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

La API queda disponible en `http://localhost:10000` y `GET /` devuelve:

```json
{
  "status": "ok"
}
```

## Variables de entorno

Copia `.env.example` a `.env` y completa las llaves reales:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=anon-public-key
SUPABASE_SERVICE_ROLE_KEY=service-role-key
VOTE_SECRET_KEY=cambia-este-secreto-de-votacion
SECRET_KEY=cambia-este-secreto-de-flask
ALLOWED_ORIGINS=http://localhost:5173
PORT=10000
```

Nunca subas secretos reales al repositorio.
