import os
import base64
from app.utils.supabase_client import supabase


def generate_challenge():
    return base64.b64encode(os.urandom(32)).decode()


def save_webauthn(voter_id, credential_id):

    try:
        response = supabase.table("webauthn_credentials").upsert({
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