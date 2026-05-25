import os
import base64
from app.utils.supabase_client import get_supabase, get_supabase_admin


def generate_challenge():
    return base64.b64encode(os.urandom(32)).decode()


def save_webauthn(voter_id, credential_id):

    try:
        response = get_supabase_admin.table("webauthn_credentials").upsert({
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

def complete_mfa_webauthn(voter_id, credential_id):

    response = get_supabase_admin.table("webauthn_credentials") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .limit(1) \
        .execute()

    if not response.data:
        raise Exception("No existe WebAuthn registrado")

    saved = response.data[0]["credential_id"]

    print("SAVED:", saved)
    print("RECEIVED:", credential_id)

    if saved != credential_id:
        raise Exception("Credential inválida")

    get_supabase_admin.table("registration_status") \
        .update({
            "current_step": 4,
            "status": "completed",
            "completed_at": "now()"
        }) \
        .eq("voter_id", voter_id) \
        .execute()

    return True


def verify_webauthn_login(voter_id, credential_id):
    response = get_supabase_admin.table("webauthn_credentials") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .limit(1) \
        .execute()