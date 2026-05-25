from app.utils.supabase_client import get_supabase_admin
import uuid
import hashlib


def get_voter_from_token(request):

    auth = request.headers.get("Authorization")

    if not auth:
        raise Exception("No token")

    token = auth.replace("Bearer ", "")

    user = get_supabase_admin.auth.get_user(token)

    if not user or not user.user:
        raise Exception("Token inválido")

    auth_user_id = user.user.id

    voter = get_supabase_admin.table("voters") \
        .select("id") \
        .eq("auth_user_id", auth_user_id) \
        .maybe_single() \
        .execute()

    if not voter.data:
        raise Exception("Votante no encontrado")

    return voter.data["id"]

def cast_vote(voter_id, candidate_id):

    # 1. verificar voto previo
    existing = get_supabase_admin.table("votes") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .execute()

    if existing.data:
        raise Exception("El votante ya emitió su voto")

    # 2. generar voto
    vote_code = str(uuid.uuid4())

    vote_hash = hashlib.sha256(
        f"{voter_id}{candidate_id}{vote_code}".encode()
    ).hexdigest()

    # 3. insertar
    response = get_supabase_admin.table("votes").insert({
        "voter_id": voter_id,
        "candidate_id": candidate_id,
        "vote_code": vote_code,
        "vote_hash": vote_hash
    }).execute()

    return response.data

def get_results():
    candidates = get_supabase_admin.table("candidates") \
        .select("id, name, photo_url") \
        .execute().data

    votes = get_supabase_admin.table("votes") \
        .select("candidate_id") \
        .execute().data

    results = {}

    # inicializar todos en 0
    for c in candidates:
        results[c["id"]] = {
            "candidate_id": c["id"],
            "candidate_name": c["name"],
            "photo_url": c["photo_url"],
            "total": 0
        }

    # contar votos
    for v in votes:
        cid = v["candidate_id"]
        if cid in results:
            results[cid]["total"] += 1

    return list(results.values())

def get_total_votes():
    response = get_supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()

    return response.count or 0

def get_turnout():
    TOTAL_VOTERS = 150  # mock fijo

    total_votes = get_supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()

    voted = total_votes.count or 0

    return round((voted / TOTAL_VOTERS) * 100, 2)

def get_turnout_detailed():
    TOTAL_VOTERS = 150

    total_votes = get_supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()

    voted = total_votes.count or 0

    percentage = round((voted / TOTAL_VOTERS) * 100, 2)

    return {
        "voted": voted,
        "total_voters": TOTAL_VOTERS,
        "percentage": percentage
    }