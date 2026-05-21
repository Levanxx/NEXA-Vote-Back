from app.utils.supabase_client import supabase


def save_face(voter_id, descriptor):

    response = supabase.table("biometric_data").upsert({
        "voter_id": voter_id,
        "face_embedding": descriptor
    }, on_conflict="voter_id").execute()

    # DEBUG REAL
    print("SUPABASE RESPONSE:", response)

    # NO usar response.error
    if response.data is None:
        raise Exception("Error guardando biometría")

    return response.data