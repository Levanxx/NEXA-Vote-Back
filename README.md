# NEXA Vote Back

Backend Flask para NEXA Vote: registro de votantes, autenticacion, MFA por DNI/rostro/WebAuthn, emision de votos, resultados, reportes electorales y login administrativo sobre Supabase.

La documentacion consolidada del proyecto esta en:

- [docs/DOCUMENTACION.md](docs/DOCUMENTACION.md)

## Arranque rapido

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

La API levanta por defecto en `http://localhost:10000` y expone `GET /` como health check.

## Variables principales

Copia `.env.example` a `.env` y completa las llaves reales de Supabase y votacion. Nunca subas valores reales de `SUPABASE_SERVICE_ROLE_KEY`, `VOTE_SECRET_KEY` ni `SECRET_KEY`.

## Estado documentado

Esta documentacion corresponde al estado actualizado de `main` en el commit `2d7c0eb0360d63763bd9cc8c9063e9276bee1d44`. La rama `Pruebas` fue omitida porque no existe en el repositorio remoto, segun la correccion solicitada.
