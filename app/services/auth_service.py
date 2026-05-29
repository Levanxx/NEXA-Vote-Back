from app.utils.supabase_client import get_supabase_admin
from app.services.audit_service import log_action
import hashlib

def login_voter(dni, password):
    supabase_admin = get_supabase_admin()

    voter_response = supabase_admin.table("voters") \
        .select("*") \
        .eq("dni", dni) \
        .maybe_single() \
        .execute()

    if not voter_response.data:
        raise Exception("Votante no encontrado")

    voter = voter_response.data
    email = voter["email"]

    auth_response = supabase_admin.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not auth_response.session:
        raise Exception("Credenciales inválidas")

    session = auth_response.session
    voter_id = voter["id"]

    session_token_hash = hashlib.sha256(session.access_token.encode()).hexdigest()
    supabase_admin.table("mfa_sessions").insert({
        "voter_id": voter_id,
        "session_token_hash": session_token_hash
    }).execute()

    existing = supabase_admin.table("vote_tokens") \
        .select("id") \
        .eq("voter_id", voter_id) \
        .execute()

    has_voted = len(existing.data) > 0


    return {
        "token": session.access_token,
        "user": {
            "id": voter["id"],
            "dni": voter["dni"],
            "email": voter["email"]
        },
        "has_voted": has_voted
    }