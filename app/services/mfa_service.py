import numpy as np
import json
from app.utils.supabase_client import get_supabase_admin
from app.config import Config
from supabase import create_client
import hashlib

def normalize_dni(dni):
    return str(dni).strip().replace(" ", "")


def _resolve_voter(token):
    """Valida JWT con cliente descartable y retorna datos del votante."""
    if not token:
        return None
    clean = token.replace("Bearer ", "")
    temp = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
    try:
        resp = temp.auth.get_user(clean)
        if not resp or not resp.user:
            return None
    except Exception:
        return None
    supabase_admin = get_supabase_admin()
    voter = supabase_admin.table("voters") \
        .select("id, dni") \
        .eq("auth_user_id", resp.user.id) \
        .maybe_single() \
        .execute()
    if not voter.data:
        return None
    return {"id": voter.data["id"], "dni": voter.data["dni"]}


def validate_dni_mfa(token, dni_scanned):
    voter = _resolve_voter(token)
    if not voter:
        raise Exception("Usuario no válido")

    if normalize_dni(voter["dni"]) != normalize_dni(dni_scanned):
        raise Exception("DNI no coincide con el usuario")

    clean = token.replace("Bearer ", "")
    session_token_hash = hashlib.sha256(clean.encode()).hexdigest()
    supabase_admin = get_supabase_admin()
    supabase_admin.table("mfa_sessions") \
        .update({"dni_validated": True}) \
        .eq("voter_id", voter["id"]) \
        .eq("session_token_hash", session_token_hash) \
        .execute()

    return {
        "message": "DNI validado correctamente",
        "voter_id": voter["id"]
    }


def validate_face_mfa(token, descriptor_nuevo):
    voter = _resolve_voter(token)
    if not voter:
        raise Exception("Usuario no válido")

    supabase_admin = get_supabase_admin()
    bio_response = supabase_admin.table("biometric_data") \
        .select("face_embedding") \
        .eq("voter_id", voter["id"]) \
        .limit(1) \
        .execute()

    if not bio_response or not bio_response.data:
        return {"error": "face_not_found"}

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

    session_token_hash = hashlib.sha256(token.replace("Bearer ", "").encode()).hexdigest()
    supabase_admin.table("mfa_sessions") \
        .update({"face_validated": True}) \
        .eq("voter_id", voter["id"]) \
        .eq("session_token_hash", session_token_hash) \
        .execute()

    return {
        "message": "Rostro validado correctamente",
        "voter_id": voter["id"],
        "distancia": round(distancia, 4)
    }