from app.utils.supabase_client import get_supabase_admin


def save_face(voter_id, descriptor):
    supabase_admin = get_supabase_admin()  

    if not isinstance(descriptor, list) or len(descriptor) != 128:   
        raise Exception("Descriptor debe tener exactamente 128 valores")

    descriptor_limpio = [float(x) for x in descriptor]

    response = supabase_admin.table("biometric_data").upsert({
        "voter_id": voter_id,
        "face_embedding": descriptor_limpio
    }, on_conflict="voter_id").execute()

    print("SUPABASE RESPONSE:", response)

    if response.data is None:
        raise Exception("Error guardando biometría")

    return response.data