# Diagramas y flujos del sistema

Este archivo concentra los graficos Mermaid para entender el backend, sus flujos y sus dependencias.

## Arquitectura general

```mermaid
flowchart TB
    subgraph Client[Cliente]
        Web[Frontend / App]
    end

    subgraph API[Flask API]
        CORS[CORS]
        Limiter[Rate Limiter]
        Headers[Security Headers]
        Auth[Auth Middleware]
        Routes[Blueprints]
        Services[Services]
    end

    subgraph Supabase[Supabase]
        SAuth[Auth]
        SDB[(Database)]
    end

    Web --> CORS
    CORS --> Limiter
    Limiter --> Headers
    Headers --> Auth
    Auth --> Routes
    Routes --> Services
    Services --> SAuth
    Services --> SDB
```

## Registro de votante

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as Flask API
    participant SA as Supabase Auth
    participant DB as Supabase DB

    FE->>API: POST /register/identity
    API->>API: validate_identity(data)
    API->>SA: create_user(email,password)
    SA-->>API: auth_user_id
    API->>DB: insert voters
    API->>DB: insert registration_status pending
    API-->>FE: voter_id
```

## Registro por escaneo de DNI

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as Flask API
    participant DB as Supabase DB

    FE->>API: POST /register/identity/scan
    API->>DB: insert voters con datos parciales
    API->>DB: insert registration_status step 1
    API-->>FE: voter_id
```

## Login y creacion de sesion MFA

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as Flask API
    participant SA as Supabase Auth
    participant DB as Supabase DB

    FE->>API: POST /api/auth/login dni,password
    API->>DB: buscar voter por dni
    API->>SA: sign_in_with_password(email,password)
    SA-->>API: access_token
    API->>DB: insert mfa_sessions(session_token_hash)
    API->>DB: consultar vote_tokens
    API-->>FE: token, user, has_voted
```

## MFA completo antes de votar

```mermaid
flowchart TD
    A[Login votante] --> B[mfa_sessions creada]
    B --> C[POST /api/mfa/validate-dni]
    C --> D[dni_validated = true]
    D --> E[POST /api/mfa/validate-face]
    E --> F[face_validated = true]
    F --> G[POST /webauthn/auth/options]
    G --> H[POST /webauthn/auth/verify]
    H --> I[webauthn_validated = true]
    I --> J[Puede votar]
```

## WebAuthn registro y autenticacion

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as Flask API
    participant FIDO as Fido2Server
    participant DB as Supabase DB

    FE->>API: POST /webauthn/register/options
    API->>FIDO: register_begin
    API-->>FE: options + state
    FE->>API: POST /webauthn/register/verify
    API->>FIDO: register_complete
    API->>DB: upsert webauthn_credentials cifradas

    FE->>API: POST /webauthn/auth/options
    API->>DB: leer credential_raw
    API->>FIDO: authenticate_begin
    API-->>FE: request options + state
    FE->>API: POST /webauthn/auth/verify
    API->>FIDO: authenticate_complete
    API->>DB: mfa_sessions.webauthn_validated = true
```

## Emision de voto

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as Flask API
    participant DB as Supabase DB

    FE->>API: POST /api/votes/cast Authorization + candidate_id
    API->>API: require_auth resuelve voter_id y token hash
    API->>DB: validar mfa_sessions completa
    API->>DB: validar candidato si no es blank
    API->>DB: consultar vote_tokens por voter_id
    alt Ya voto
        API-->>FE: 400 El votante ya emitio su voto
    else Puede votar
        API->>DB: insert vote_tokens
        API->>DB: insert votes token_hash/candidate_id/vote_hash
        API-->>FE: Voto registrado correctamente
    end
```

## Reportes electorales

```mermaid
flowchart LR
    Admin[Admin autenticado] --> API[GET /api/votes/report]
    API --> Candidates[(candidates)]
    API --> Votes[(votes)]
    API --> Voters[(voters)]
    API --> Tokens[(vote_tokens)]
    Candidates --> Report[Reporte JSON]
    Votes --> Report
    Voters --> Age[Participacion por edad]
    Tokens --> Age
    Age --> Report
    Report --> Dashboard[Dashboard]
    Report --> CSV[GET /api/votes/report/csv]
```

## Modelo relacional inferido

```mermaid
erDiagram
    voters ||--o| registration_status : has
    voters ||--o| biometric_data : has
    voters ||--o| webauthn_credentials : has
    voters ||--o{ mfa_sessions : creates
    voters ||--o| vote_tokens : receives
    vote_tokens ||--o| votes : anonymizes
    candidates ||--o{ votes : receives
    admins }o--|| auth_users : maps
    voters }o--|| auth_users : maps
```
