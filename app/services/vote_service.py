from app.utils.supabase_client import supabase_admin
import uuid
import hashlib


def get_voter_from_token(request):

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

def cast_vote(voter_id, candidate_id):

    # 1. verificar voto previo
    existing = supabase_admin.table("votes") \
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
    response = supabase_admin.table("votes").insert({
        "voter_id": voter_id,
        "candidate_id": candidate_id,
        "vote_code": vote_code,
        "vote_hash": vote_hash
    }).execute()

    return response.data

def get_results():
    response = supabase_admin.table("vote_results").select("*").execute()
    return response.data


def get_total_votes():
    response = supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()

    return response.count or 0

def get_turnout():
    TOTAL_VOTERS = 100  # mock fijo

    total_votes = supabase_admin.table("votes") \
        .select("id", count="exact") \
        .execute()

    voted = total_votes.count or 0

    return round((voted / TOTAL_VOTERS) * 100, 2)