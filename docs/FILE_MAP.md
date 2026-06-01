# Mapa archivo por archivo

Este documento describe todos los archivos funcionales del backend en el estado actualizado de `main`.

## Raiz

| Archivo | Responsabilidad |
| --- | --- |
| `README.md` | Indice y guia rapida del proyecto |
| `.env.example` | Plantilla de variables de entorno |
| `AGENTS.md` | Notas tecnicas y contexto operativo para agentes/desarrollo |
| `Dockerfile` | Imagen Python 3.11 y comando Gunicorn |
| `requirements.txt` | Dependencias Python |
| `run.py` | Punto de entrada; crea app y arranca Flask local |

## `app`

| Archivo | Responsabilidad |
| --- | --- |
| `app/__init__.py` | Factory Flask, CORS, limiter, headers, health, `/auth/me` y blueprints |
| `app/config.py` | Carga variables `SUPABASE_*`, `VOTE_SECRET_KEY` y `SECRET_KEY` |
| `app/extensions.py` | Instancia global de `Flask-Limiter` |

## `app/middleware`

| Archivo | Responsabilidad |
| --- | --- |
| `app/middleware/auth_middleware.py` | Decoradores `require_auth` y `require_admin`; valida JWT y llena `flask.g` |
| `app/middleware/security_headers.py` | Agrega CSP, `nosniff` y `X-Frame-Options` |

## `app/routes`

| Archivo | Endpoints principales | Responsabilidad |
| --- | --- | --- |
| `app/routes/registration.py` | `/register/identity`, `/register/identity/scan`, `/register/voter/<id>`, `/register/summary/<id>`, `/register/complete/<id>` | Registro y estado de votantes |
| `app/routes/biometric.py` | `/register/face` | Registro de descriptor facial |
| `app/routes/webauthn.py` | `/webauthn/register/options`, `/webauthn/register/verify`, `/webauthn/auth/options`, `/webauthn/auth/verify` | Registro y autenticacion WebAuthn/FIDO2 |
| `app/routes/auth.py` | `/api/auth/login` | Login de votante |
| `app/routes/mfa.py` | `/api/mfa/validate-dni`, `/api/mfa/validate-face` | Validacion MFA por DNI y rostro |
| `app/routes/candidates.py` | `/api/votes/candidates` | Consulta de candidatos activos |
| `app/routes/votes.py` | `/api/votes/cast`, `/results`, `/total`, `/turnout`, `/turnout-detailed`, `/report`, `/report/csv` | Voto, resultados y reportes |
| `app/routes/admin.py` | `/api/admin/login` | Login de administradores |

## `app/services`

| Archivo | Funciones relevantes | Responsabilidad |
| --- | --- | --- |
| `app/services/registration_service.py` | `create_voter`, `update_voter`, `get_voter`, `get_status`, `complete_registration_service` | Persistencia de votantes y estado |
| `app/services/auth_service.py` | `login_voter` | Login de votante y creacion de sesion MFA |
| `app/services/mfa_service.py` | `validate_dni_mfa`, `validate_face_mfa` | Validaciones de identidad por sesion |
| `app/services/webauthn_service.py` | `register_begin`, `register_complete`, `auth_begin`, `auth_complete` | WebAuthn/FIDO2 completo |
| `app/services/vote_service.py` | `cast_vote`, `get_results`, `get_total_votes`, `get_turnout`, `get_turnout_detailed` | Emision de voto y metricas |
| `app/services/report_service.py` | `get_report`, `get_report_csv` | Reportes JSON y CSV para admin/dashboard |
| `app/services/biometric_service.py` | `save_face` | Guarda descriptor facial |
| `app/services/candidate_service.py` | `get_active_candidates` | Lista candidatos activos |
| `app/services/admin_service.py` | `login_admin` | Login y validacion de administradores |
| `app/services/audit_service.py` | `log_action` | Inserta eventos en `audit_logs` |

## `app/utils`

| Archivo | Responsabilidad |
| --- | --- |
| `app/utils/supabase_client.py` | Clientes Supabase anon y admin cacheados |
| `app/utils/encryption.py` | Cifrado/descifrado Fernet con compatibilidad legado |
| `app/utils/validators.py` | Validacion de identidad del votante |

## Documentacion

| Archivo | Responsabilidad |
| --- | --- |
| `docs/ARCHITECTURE.md` | Arquitectura, capas y seguridad |
| `docs/API.md` | Endpoints y contratos HTTP |
| `docs/DATABASE.md` | Modelo de datos inferido |
| `docs/DEPLOYMENT.md` | Configuracion y despliegue |
| `docs/DIAGRAMS.md` | Graficos Mermaid de flujos |
| `docs/FILE_MAP.md` | Este mapa archivo por archivo |
| `docs/KNOWN_LIMITATIONS.md` | Pendientes, riesgos y recomendaciones |
