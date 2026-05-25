# Configuracion, ejecucion y despliegue

## Requisitos

- Python 3.11
- Cuenta/proyecto Supabase
- Tablas descritas en `docs/DATABASE.md`
- Variables de entorno configuradas

## Variables de entorno

| Variable | Obligatoria | Descripcion |
| --- | --- | --- |
| `SUPABASE_URL` | Si | URL del proyecto Supabase |
| `SUPABASE_KEY` | Si | Llave publica/anon para cliente normal |
| `SUPABASE_SERVICE_ROLE_KEY` | Si | Llave administrativa para operaciones privilegiadas |
| `ALLOWED_ORIGINS` | No | Origenes permitidos por CORS separados por coma |
| `PORT` | No | Puerto de ejecucion, por defecto `10000` |

Ejemplo:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=anon-public-key
SUPABASE_SERVICE_ROLE_KEY=service-role-key
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

Luego abrir:

```text
http://localhost:10000
```

## Produccion con Gunicorn

El `Dockerfile` ejecuta:

```bash
gunicorn -w 1 --timeout 120 -b 0.0.0.0:${PORT:-10000} 'run:app'
```

Parametros actuales:

- `-w 1`: un worker.
- `--timeout 120`: timeout de 120 segundos.
- `-b 0.0.0.0:${PORT:-10000}`: escucha en todas las interfaces y usa `PORT` o `10000`.

## Docker

Construir imagen:

```bash
docker build -t nexa-vote-back .
```

Ejecutar:

```bash
docker run --env-file .env -p 10000:10000 nexa-vote-back
```

## CORS

`ALLOWED_ORIGINS` se lee en `app/__init__.py`.

Valor por defecto:

```text
http://localhost:5173
```

Para varios origenes:

```env
ALLOWED_ORIGINS=http://localhost:5173,https://frontend.example.com
```

## Supabase

El backend crea dos clientes:

- Cliente normal con `SUPABASE_KEY`.
- Cliente administrativo con `SUPABASE_SERVICE_ROLE_KEY`.

La llave administrativa es necesaria para:

- Crear usuarios Auth desde el backend.
- Consultar tablas por `auth_user_id`.
- Insertar y actualizar registros protegidos.

## Verificacion basica despues del despliegue

1. Consultar salud:

```bash
curl http://localhost:10000/
```

2. Confirmar respuesta:

```json
{
  "status": "ok"
}
```

3. Probar que CORS permite el origen del frontend.
4. Probar login de administrador con un usuario existente en `admins`.
5. Probar registro de votante en un ambiente de prueba.

## Consideraciones operativas

- No publicar `.env`.
- Rotar `SUPABASE_SERVICE_ROLE_KEY` si se expone accidentalmente.
- Crear restricciones unicas en Supabase para datos criticos como `votes.voter_id`.
- Revisar logs porque algunas rutas imprimen datos recibidos y respuestas de Supabase.
- Agregar migraciones SQL o scripts de setup para que el despliegue sea reproducible.
