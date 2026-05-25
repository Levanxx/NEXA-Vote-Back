# Mapa archivo por archivo

Este documento enumera todos los archivos funcionales del repositorio y su responsabilidad dentro del backend.

## Raiz del proyecto

| Archivo | Responsabilidad |
| --- | --- |
| `README.md` | Guia principal del proyecto, instalacion, estructura y enlaces a la documentacion completa |
| `.env.example` | Plantilla de variables de entorno necesarias para ejecutar la API |
| `Dockerfile` | Define la imagen Docker basada en Python 3.11 y ejecuta Gunicorn |
| `requirements.txt` | Lista de dependencias Python del proyecto |
| `run.py` | Punto de entrada para crear y ejecutar la aplicacion Flask |

## `app`

| Archivo | Responsabilidad |
| --- | --- |
| `app/__init__.py` | Crea Flask, configura CORS, registra rutas y define health check |
| `app/config.py` | Carga variables de entorno y expone configuracion de Supabase |

## `app/routes`

| Archivo | Endpoints | Responsabilidad |
| --- | --- | --- |
| `app/routes/registration.py` | `/register/identity`, `/register/voter/<voter_id>`, `/register/identity/<voter_id>`, `/register/summary/<voter_id>`, `/register/complete/<voter_id>`, `/register/identity/scan` | Registro, actualizacion, resumen y finalizacion de votantes |
| `app/routes/biometric.py` | `/register/face` | Registro del descriptor facial |
| `app/routes/webauthn.py` | `/webauthn/register/options`, `/webauthn/register/verify`, `/webauthn/auth/options`, `/webauthn/auth/verify` | Challenge y guardado/verificacion de credenciales WebAuthn |
| `app/routes/auth.py` | `/api/auth/login` | Login de votantes |
| `app/routes/mfa.py` | `/api/mfa/validate-dni`, `/api/mfa/validate-face` | Validaciones MFA por DNI y rostro |
| `app/routes/candidates.py` | `/api/votes/candidates` | Listado de candidatos activos |
| `app/routes/votes.py` | `/api/votes/cast`, `/api/votes/results`, `/api/votes/total`, `/api/votes/turnout`, `/api/votes/turnout-detailed` | Emision de votos, resultados y participacion |
| `app/routes/admin.py` | `/api/admin/login` | Login de administradores |

## `app/services`

| Archivo | Funciones | Responsabilidad |
| --- | --- | --- |
| `app/services/registration_service.py` | `create_voter`, `register_user_auth`, `get_voter`, `update_voter`, `get_face`, `get_webauthn`, `get_status`, `complete_registration_service`, `create_voter_from_scan` | Logica de registro, consulta y estado de votantes |
| `app/services/biometric_service.py` | `save_face` | Normaliza y guarda descriptor facial en Supabase |
| `app/services/webauthn_service.py` | `generate_challenge`, `save_webauthn`, `complete_mfa_webauthn`, `verify_webauthn_login` | Genera challenges y maneja credenciales WebAuthn; la ultima funcion aparece incompleta |
| `app/services/auth_service.py` | `login_voter` | Login de votante por DNI/password y calculo de `has_voted` |
| `app/services/mfa_service.py` | `normalize_dni`, `validate_dni_mfa`, `validate_face_mfa` | Validacion de DNI escaneado y comparacion facial por distancia euclidiana |
| `app/services/candidate_service.py` | `get_active_candidates` | Consulta candidatos activos |
| `app/services/vote_service.py` | `get_voter_from_token`, `cast_vote`, `get_results`, `get_total_votes`, `get_turnout`, `get_turnout_detailed` | Obtiene votante autenticado, registra votos y calcula resultados/participacion |
| `app/services/admin_service.py` | `login_admin` | Login de administrador y validacion contra tabla `admins` |

## `app/utils`

| Archivo | Funciones | Responsabilidad |
| --- | --- | --- |
| `app/utils/supabase_client.py` | `get_supabase`, `get_supabase_admin` | Crea y reutiliza clientes Supabase normal y administrativo |
| `app/utils/validators.py` | `validate_identity` | Valida DNI, nombre, fecha de nacimiento, email y edad |

## Archivos no presentes pero recomendados

El proyecto actualmente no incluye:

- Migraciones SQL de Supabase.
- Pruebas automatizadas.
- Configuracion de lint/format.
- Coleccion Postman/Insomnia.
- CI/CD.

Estos pendientes estan descritos en `docs/KNOWN_LIMITATIONS.md`.
