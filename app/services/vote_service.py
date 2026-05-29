from app.utils.supabase_client import get_supabase_admin
from app.config import Config
import uuid
import hashlib


def cast_vote(voter_id, candidate_id, session_token_hash):
    supabase_admin = get_supabase_admin()

    mfa = supabase_admin.table("mfa_sessions") \
        .select("id") \
        .eq("voter_id", voter_id) \
        .eq("session_token_hash", session_token_hash) \
        .eq("dni_validated", True) \
        .eq("face_validated", True) \
        .eq("webauthn_validated", True) \
        .maybe_single() \
        .execute()
    if not mfa.data:
        raise Exception("Debes completar la verificación de identidad antes de votar")


    if candidate_id.lower() != "blank":
        candidate = supabase_admin.table("candidates") \
            .select("id") \
            .eq("id", candidate_id) \
            .maybe_single() \
            .execute()
        if not candidate.data:
            raise Exception("Candidato no encontrado")
    

    existing = supabase_admin.table("vote_tokens") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .execute()
    if existing.data:
        raise Exception("El votante ya emitió su voto")
    

    vote_code = str(uuid.uuid4())
    token = str(uuid.uuid4())
    secret = Config.VOTE_SECRET_KEY
    if not secret:
        raise Exception("Error de configuración del sistema de votación")
    
    if candidate_id.lower() == "blank":
        candidate_id = None


    token_hash = hashlib.sha256(f"{token}{secret}".encode()).hexdigest()
    vote_hash = hashlib.sha256(f"{token}{candidate_id}{secret}".encode()).hexdigest()


    supabase_admin.table("vote_tokens").insert({
        "voter_id": voter_id,
        "token": token
    }).execute()


    response = supabase_admin.table("votes").insert({
        "token_hash": token_hash,
        "candidate_id": candidate_id,
        "vote_code": vote_code,
        "vote_hash": vote_hash
    }).execute()



    return response.data


def get_results():
    supabase_admin = get_supabase_admin()

    candidates = supabase_admin.table("candidates") \
        .select("id, name, photo_url") \
        .execute().data

    votes = supabase_admin.table("votes") \
        .select("candidate_id") \
        .execute().data

    results = {}
    for c in candidates:
        results[c["id"]] = {
            "candidate_id": c["id"],
            "candidate_name": c["name"],
            "photo_url": c["photo_url"],
            "total": 0
        }

    for v in votes:
        cid = v["candidate_id"]
        if cid in results:
            results[cid]["total"] += 1

    return list(results.values())


def get_total_votes():
    supabase_admin = get_supabase_admin()
    response = supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()
    return response.count or 0


def get_turnout():
    supabase_admin = get_supabase_admin()
    total_voters = supabase_admin.table("voters") \
        .select("id", count="exact") \
        .execute()
    TOTAL_VOTERS = total_voters.count or 0
    total_votes = supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()
    voted = total_votes.count or 0
    if TOTAL_VOTERS == 0:
        return 0.0
    return round((voted / TOTAL_VOTERS) * 100, 2)


def get_turnout_detailed():
    supabase_admin = get_supabase_admin()
    total_voters = supabase_admin.table("voters") \
        .select("id", count="exact") \
        .execute()
    TOTAL_VOTERS = total_voters.count or 0
    total_votes = supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()
    voted = total_votes.count or 0
    if TOTAL_VOTERS == 0:
        return {"voted": 0, "total_voters": 0, "percentage": 0.0}
    percentage = round((voted / TOTAL_VOTERS) * 100, 2)
    return {
        "voted": voted,
        "total_voters": TOTAL_VOTERS,
        "percentage": percentage
    }