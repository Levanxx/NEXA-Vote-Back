# NEXA-Vote Backend

## Stack
Flask 3.1, Python 3.11, Supabase (supabase-py 2.30), WebAuthn/FIDO2, gunicorn.

## Comandos

| Acción | Comando |
|---|---|
| Dev | `python run.py` (puerto `PORT`, default `10000`) |
| Prod | `gunicorn -w 1 --timeout 120 -b 0.0.0.0:${PORT:-10000} 'run:app'` |

No existe test runner, linter, typechecker, CI, Makefile ni `pyproject.toml`.

## Variables de entorno (`.env` gitignorado)
- `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `ALLOWED_ORIGINS` — origenes CORS separados por coma (default `http://localhost:5173`)
- `PORT` — default `10000`

## Clientes Supabase (`app/utils/supabase_client.py`)
- `get_supabase()` — anon key (lecturas públicas)
- `get_supabase_admin()` — service-role key (escritura, bypass RLS, crear usuarios Auth)
- Casi todas las operaciones de escritura usan el cliente admin.

## Rutas

| Prefijo | Blueprint | Archivo |
|---|---|---|
| `/` | health → `{"status": "ok"}` | `app/__init__.py` |
| `/register/...` | `registration_bp` | `routes/registration.py` |
| `/api/auth/...` | `auth_bp` | `routes/auth.py` |
| `/api/admin/...` | `admin_bp` | `routes/admin.py` |
| `/api/votes/...` | `votes_bp`, `candidates_bp` | `routes/votes.py`, `routes/candidates.py` |
| `/api/mfa/...` | `mfa_bp` | `routes/mfa.py` |
| `/webauthn/...` | `webauthn_bp` | `routes/webauthn.py` |

## Tablas Supabase (sin migraciones locales)
`voters`, `registration_status`, `biometric_data`, `webauthn_credentials`, `candidates`, `votes`

## Auth
- Token JWT de Supabase en header `Authorization: Bearer <token>`
- Resolución: `supabase_admin.auth.get_user(token)` (`app/services/vote_service.py:6-30`)
- Login de admin independiente en `app/services/admin_service.py`

## Notas
- No hay tests, linter, typechecker ni CI. Cualquier herramienta nueva debe crearse desde cero.
- Uploads faciales van a `app/uploads/face/` (gitignorado excepto `.gitkeep`).
- Factory pattern: `app.create_app()` en `run.py`.

## Reportes electorales — Integración Frontend

### Endpoints (requieren token admin en `Authorization: Bearer <token>`)

| Método | Ruta | Formato | Descripción |
|--------|------|---------|-------------|
| GET | `/api/votes/report` | JSON | Datos completos para gráficos |
| GET | `/api/votes/report/csv` | CSV | Descarga del reporte en tabla |

### Estructura del JSON (`/api/votes/report`)

```json
{
  "results": [
    { "candidate_id": "uuid", "name": "Ana López", "party": "Partido Azul",
      "photo_url": "...", "total": 3500, "percentage": 35.0 }
  ],
  "blank_votes": { "total": 150, "percentage": 1.5 },
  "total_voters": 18000,
  "total_votes": 12000,
  "turnout_percentage": 66.67,
  "turnout_by_age": {
    "18-25": { "total": 5000, "voted": 3200, "percentage": 64.0 },
    "26-40": { "total": 8000, "voted": 5600, "percentage": 70.0 },
    "41-60": { "total": 4000, "voted": 3000, "percentage": 75.0 },
    "60+":   { "total": 1000, "voted": 600,  "percentage": 60.0 }
  }
}
```

### Ejemplos de gráficos con Recharts

#### 1. Barras — Resultados por candidato

```jsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function ResultadosChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data.results}>
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip formatter={(v) => `${v} votos`} />
        <Bar dataKey="total" fill="#4f46e5" radius={[4,4,0,0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
```

#### 2. Dona — Participación por edad

```jsx
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

const COLORS = ["#6366f1", "#22c55e", "#f59e0b", "#ef4444"];

function EdadChart({ data }) {
  const pieData = Object.entries(data.turnout_by_age).map(([rango, v]) => ({
    name: rango, value: v.percentage
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={100}>
          {pieData.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
        </Pie>
        <Tooltip formatter={(v) => `${v}%`} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
```

#### 3. Progreso circular — Participación total

```jsx
function TurnoutGauge({ percentage }) {
  const r = 70;
  const circumference = 2 * Math.PI * r;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <svg width="160" height="160" viewBox="0 0 160 160">
      <circle cx="80" cy="80" r={r} fill="none" stroke="#e5e7eb" strokeWidth="12" />
      <circle cx="80" cy="80" r={r} fill="none" stroke="#4f46e5" strokeWidth="12"
        strokeDasharray={circumference} strokeDashoffset={offset}
        transform="rotate(-90 80 80)" strokeLinecap="round" />
      <text x="80" y="80" textAnchor="middle" dominantBaseline="central" fontSize="24" fontWeight="bold">
        {percentage}%
      </text>
    </svg>
  );
}
```

### Cómo cargar los datos

```javascript
import { useState, useEffect } from "react";

function Dashboard() {
  const [report, setReport] = useState(null);
  const token = sessionStorage.getItem("admin_token");

  useEffect(() => {
    if (!token) return;
    fetch("http://localhost:10000/api/votes/report", {
      headers: { Authorization: `Bearer ${token}` }
    })
      .then(r => r.json())
      .then(r => r.success && setReport(r.data));
  }, [token]);

  if (!report) return <p>Cargando...</p>;
  return (
    <>
      <ResultadosChart data={report} />
      <EdadChart data={report} />
      <TurnoutGauge percentage={report.turnout_percentage} />
    </>
  );
}
```
