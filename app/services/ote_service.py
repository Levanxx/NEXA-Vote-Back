from app.utils.supabase_client import supabase_admin
import uuid
import hashlib

def cast_vote(voter_id, candidate_id):

    # 1. verificar si ya votó
    existing = supabase_admin.table("votes") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .execute()

    if existing.data:
        raise Exception("El votante ya emitió su voto")

    # 2. generar código de voto
    vote_code = str(uuid.uuid4())

    # 3. hash simple (puedes mejorar luego)
    vote_hash = hashlib.sha256(
        f"{voter_id}{candidate_id}{vote_code}".encode()
    ).hexdigest()

    # 4. insertar voto
    response = supabase_admin.table("votes").insert({
        "voter_id": voter_id,
        "candidate_id": candidate_id,
        "vote_code": vote_code,
        "vote_hash": vote_hash
    }).execute()

    return response.data