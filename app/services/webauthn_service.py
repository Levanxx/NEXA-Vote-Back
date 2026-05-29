import os
import base64
from app.utils.supabase_client import get_supabase_admin


def generate_challenge():
    return base64.b64encode(os.urandom(32)).decode()


def save_webauthn(voter_id, credential_id):
    supabase_admin = get_supabase_admin()
    try:
        response = supabase_admin.table("webauthn_credentials").upsert({
            "voter_id": voter_id,
            "credential_id": credential_id,
            "public_key": "stored_by_browser",
            "sign_count": 0
        }, on_conflict="voter_id").execute()

        if response is None:
            raise Exception("No response from Supabase")
        if hasattr(response, "error") and response.error:
            raise Exception(response.error)
        if not response.data:
            raise Exception("No data returned from upsert")

        return response.data

    except Exception as e:
        print("ERROR save_webauthn:", str(e))
        raise


def verify_webauthn_login(voter_id, credential_id, session_token_hash):
    supabase_admin = get_supabase_admin()
    response = supabase_admin.table("webauthn_credentials") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .limit(1) \
        .execute()
    if not response.data:
        raise Exception("No hay WebAuthn registrado")
    saved = response.data[0]["credential_id"]
    if saved != credential_id:
        raise Exception("Credencial no coincide")

    # Marcar MFA completo
    supabase_admin.table("mfa_sessions") \
        .update({"webauthn_validated": True}) \
        .eq("voter_id", voter_id) \
        .eq("session_token_hash", session_token_hash) \
        .execute()

    return True