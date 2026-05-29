import os
from app.utils.supabase_client import get_supabase_admin
from app.services.audit_service import log_action
from app.config import Config
import uuid
import hashlib


def get_voter_from_token(request):
    supabase_admin = get_supabase_admin()

    auth = request.headers.get("Authorization")
    if not auth:
        raise Exception("No token")

    token = auth.replace("Bearer ", "")
    user = supabase_admin.auth.get_user(token)

    if not user or not user.user:
        raise Exception("Token inválido")

    auth_user_id = user.user.id

    voter = supabase_admin.table("voters") \
        .select("id") \
        .eq("auth_user_id", auth_user_id) \
        .maybe_single() \
        .execute()

    if not voter.data:
        raise Exception("Votante no encontrado")

    return voter.data["id"]


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
        log_action("VOTE_FAILED", "failed", voter_id, metadata={"reason": "already_voted"})  # ← acá
        raise Exception("El votante ya emitió su voto")
    

    vote_code = str(uuid.uuid4())
    token = str(uuid.uuid4())
    secret = Config.VOTE_SECRET_KEY
    if not secret:
        raise Exception("Error de configuración del sistema de votación")
    
    token_hash = hashlib.sha256(f"{token}{secret}".encode()).hexdigest()


    supabase_admin.table("vote_tokens").insert({
        "voter_id": voter_id,
        "token": token
    }).execute()
    response = supabase_admin.table("votes").insert({
        "token_hash": token_hash,
        "candidate_id": candidate_id,
        "vote_code": vote_code
    }).execute()

    log_action("VOTE_CAST", "success") 

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