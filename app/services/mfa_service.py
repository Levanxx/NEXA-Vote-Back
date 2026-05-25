import numpy as np
import json
from app.utils.supabase_client import get_supabase, get_supabase_admin


def normalize_dni(dni):
    return str(dni).strip().replace(" ", "")


def validate_dni_mfa(token, dni_scanned):
    supabase = get_supabase()
    supabase_admin = get_supabase_admin()

    if not token:
        raise Exception("Token requerido")

    user_response = supabase.auth.get_user(token.replace("Bearer ", ""))

    if not user_response.user:
        raise Exception("Usuario no válido")

    user = user_response.user

    voter_response = supabase_admin.table("voters") \
        .select("*") \
        .eq("auth_user_id", user.id) \
        .limit(1) \
        .execute()

    if not voter_response.data:
        raise Exception("Votante no encontrado")

    voter = voter_response.data[0]

    if normalize_dni(voter["dni"]) != normalize_dni(dni_scanned):
        raise Exception("DNI no coincide con el usuario")

    supabase_admin.table("registration_status") \
        .update({
            "current_step": 2,
            "status": "dni_validated"
        }) \
        .eq("voter_id", voter["id"]) \
        .execute()

    return {
        "message": "DNI validado correctamente",
        "voter_id": voter["id"]
    }


def validate_face_mfa(token, descriptor_nuevo):
    supabase = get_supabase()
    supabase_admin = get_supabase_admin()

    if not token:
        raise Exception("Token requerido")

    user_response = supabase.auth.get_user(token.replace("Bearer ", ""))

    if not user_response.user:
        raise Exception("Usuario no válido")

    user = user_response.user

    voter_response = supabase_admin.table("voters") \
        .select("id") \
        .eq("auth_user_id", user.id) \
        .limit(1) \
        .execute()

    if not voter_response.data:
        raise Exception("Votante no encontrado")

    voter = voter_response.data[0]

    bio_response = supabase_admin.table("biometric_data") \
        .select("face_embedding") \
        .eq("voter_id", voter["id"]) \
        .limit(1) \
        .execute()

    if not bio_response.data:
        raise Exception("No hay biometría registrada")

    raw = bio_response.data[0]["face_embedding"]
    if isinstance(raw, str):
        raw = json.loads(raw)

    descriptor_guardado = np.array(raw, dtype=np.float64)
    descriptor_recibido = np.array(descriptor_nuevo, dtype=np.float64)

    if descriptor_guardado.shape[0] != 128 or descriptor_recibido.shape[0] != 128:
        raise Exception("Descriptor inválido")

    distancia = np.linalg.norm(descriptor_guardado - descriptor_recibido)
    print(f"DISTANCIA FACIAL: {distancia}")

    UMBRAL = 0.50
    if distancia > UMBRAL:
        raise Exception(f"Rostro no coincide (distancia: {round(distancia, 4)})")

    supabase_admin.table("registration_status") \
        .update({
            "current_step": 3,
            "status": "face_validated"
        }) \
        .eq("voter_id", voter["id"]) \
        .execute()

    return {
        "message": "Rostro validado correctamente",
        "voter_id": voter["id"],
        "distancia": round(distancia, 4)
    }