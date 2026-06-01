# Limitaciones conocidas y pendientes tecnicos

Este documento lista riesgos y pendientes detectados al documentar el estado actualizado de `main`.

## No hay migraciones SQL

El repositorio no incluye scripts SQL, migraciones ni seeders para crear:

- Tablas.
- Relaciones.
- Indices.
- Constraints unicos.
- Politicas RLS.
- Datos iniciales de candidatos/admins.

Impacto: otra persona no puede levantar Supabase desde cero solo con el repositorio.

## No hay pruebas automatizadas

No se observan tests unitarios, integracion, end-to-end, CI, linter ni typechecker.

Riesgo: cambios en Auth, MFA, WebAuthn o votacion pueden romperse sin deteccion temprana.

## Doble voto debe reforzarse en base de datos

El backend consulta `vote_tokens` por `voter_id` antes de insertar. Esto debe complementarse con un constraint unico en `vote_tokens.voter_id` para evitar condiciones de carrera.

## Secretos con valores por defecto

`VOTE_SECRET_KEY` y `SECRET_KEY` tienen defaults de desarrollo en `app/config.py`.

Riesgo: si se despliega sin variables reales, el sistema queda usando secretos predecibles.

## Rotacion de `VOTE_SECRET_KEY`

`VOTE_SECRET_KEY` se usa para hash de votos y para derivar la llave Fernet de cifrado. Cambiarlo puede impedir descifrar credenciales o datos guardados previamente.

Recomendacion: definir estrategia de rotacion y migracion.

## Validacion de JSON incompleta en algunas rutas

Algunas rutas usan `request.get_json()` y luego `.get(...)`. Si el body viene vacio o invalido, puede haber errores no controlados.

Recomendacion: validar `if not data` antes de acceder al body en todas las rutas.

## Auditoria existe pero no cubre todo

`audit_service.log_action` existe, pero no todas las operaciones criticas parecen llamar auditoria.

Operaciones candidatas a auditar:

- Login exitoso/fallido.
- Registro de identidad.
- Validaciones MFA.
- Registro WebAuthn.
- Emision de voto.
- Intentos de doble voto.
- Acceso a reportes admin.

## CSP posiblemente restrictivo

`Content-Security-Policy: default-src 'self'` puede bloquear recursos externos si el frontend, imagenes o assets se sirven desde otros dominios.

## WebAuthn depende de `ALLOWED_ORIGINS`

`rp_id` se deriva del primer origen de `ALLOWED_ORIGINS`. En produccion debe coincidir exactamente con el dominio del frontend.

## Descriptor facial y logs

La validacion facial imprime distancia facial. Conviene revisar logs para no exponer informacion sensible en produccion.

## Falta contrato formal frontend-backend

La API esta documentada, pero no hay coleccion Postman/Insomnia, OpenAPI ni SDK del frontend.

## Falta documentar RLS

El codigo usa `SUPABASE_SERVICE_ROLE_KEY` para muchas operaciones. Es importante documentar politicas RLS y permisos esperados por tabla.

## Recomendaciones prioritarias

1. Crear migraciones SQL.
2. Agregar tests de Auth, MFA, voto y reportes.
3. Agregar constraints unicos para doble voto e identidad.
4. Hacer obligatorios `VOTE_SECRET_KEY` y `SECRET_KEY` en produccion.
5. Agregar OpenAPI o coleccion de requests.
6. Ampliar auditoria en flujos criticos.
