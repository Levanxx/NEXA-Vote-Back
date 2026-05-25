# Limitaciones conocidas y pendientes tecnicos

Este documento lista hallazgos detectados al documentar el repositorio actual. No son cambios de comportamiento; son puntos que conviene revisar antes de produccion o evaluacion final.

## WebAuthn incompleto

`app/services/webauthn_service.py` termina dentro de `verify_webauthn_login` despues de ejecutar la consulta a Supabase. No se observa logica para:

- Validar que exista la credencial.
- Comparar `credential_id`.
- Retornar exito.
- Lanzar error si no coincide.

Impacto: `POST /webauthn/auth/verify` puede fallar o no validar correctamente.

## WebAuthn no valida criptograficamente

El backend genera challenges y guarda `credential_id`, pero no valida la respuesta WebAuthn/FIDO2 completa. La dependencia `fido2` esta en `requirements.txt`, pero el codigo actual no la usa para verificar firmas, challenge, origin, RP ID o sign count.

Impacto: la seguridad real de WebAuthn queda limitada.

## `requirements.txt` esta en UTF-16

El archivo `requirements.txt` esta codificado como UTF-16 little-endian con CRLF. Algunos entornos de `pip` o Docker pueden no leerlo correctamente.

Impacto: `pip install -r requirements.txt` puede fallar dependiendo del entorno.

## No hay migraciones SQL

El repositorio no incluye scripts para crear tablas, relaciones, indices ni politicas RLS en Supabase.

Impacto: otra persona no puede levantar el proyecto desde cero solo con el repo.

## No hay pruebas automatizadas

No existen pruebas unitarias, de integracion ni end-to-end.

Impacto: cambios en login, registro, MFA o votacion pueden romperse sin deteccion temprana.

## Doble voto depende de consulta previa

`cast_vote` revisa si existe un voto del `voter_id` antes de insertar. Si dos peticiones concurrentes llegan al mismo tiempo, la proteccion en codigo puede no ser suficiente.

Recomendacion: agregar restriccion unica en `votes.voter_id`.

## Total de votantes hardcodeado

`get_turnout` y `get_turnout_detailed` usan:

```python
TOTAL_VOTERS = 150
```

Impacto: la participacion no refleja automaticamente el numero real de votantes registrados.

## Logs con datos sensibles o personales

Algunas rutas imprimen datos recibidos o respuestas completas:

- `app/routes/biometric.py` imprime `DATA RECIBIDA`.
- `app/services/biometric_service.py` imprime `SUPABASE RESPONSE`.
- `app/services/mfa_service.py` imprime distancia facial.
- `app/services/webauthn_service.py` imprime credenciales guardadas/recibidas en una funcion auxiliar.

Impacto: puede exponer datos personales, biometricos o credenciales en logs.

## Validacion de body incompleta en algunas rutas

Algunas rutas llaman `data.get(...)` sin validar antes si `data` es `None`.

Ejemplos:

- `POST /api/auth/login`
- `POST /api/admin/login`
- `POST /api/votes/cast`
- `POST /api/mfa/validate-dni`
- `POST /api/mfa/validate-face`

Impacto: un body vacio puede causar errores 500 en lugar de respuestas 400 controladas.

## Registro y actualizacion crean usuarios Auth nuevos

`update_voter` crea un nuevo usuario de Supabase Auth en vez de actualizar el usuario existente.

Impacto: puede dejar usuarios Auth duplicados y cambiar `auth_user_id`.

## Privacidad del voto

La tabla `votes` guarda `voter_id` junto con `candidate_id`.

Impacto: el voto es auditable por usuario, pero no anonimo. Si se necesita secreto del voto, el modelo debe redisenarse.

## Falta politica clara de errores

Las rutas devuelven mensajes directos de excepciones en varios casos.

Impacto: puede filtrar detalles internos de base de datos o autenticacion.

## Sin documentacion de frontend consumidor

El backend asume un frontend en `http://localhost:5173`, pero este repositorio no contiene contrato de integracion de frontend ni ejemplos completos de llamadas desde cliente.
