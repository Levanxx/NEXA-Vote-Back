from app.utils.supabase_client import get_supabase, get_supabase_admin


def login_voter(dni, password):


    voter_response = get_supabase_admin.table("voters") \
        .select("*") \
        .eq("dni", dni) \
        .maybe_single() \
        .execute()

    if not voter_response.data:
        raise Exception("Votante no encontrado")

    voter = voter_response.data
    email = voter["email"]

    auth_response = get_supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not auth_response.session:
        raise Exception("Credenciales inválidas")

    session = auth_response.session

    voter_id = voter["id"]  

    existing = get_supabase_admin.table("votes") \
        .select("id") \
        .eq("voter_id", voter_id) \
        .execute()

    has_voted = len(existing.data) > 0

    return {
        "token": session.access_token,
        "user": {
            "id": voter["id"],
            "dni": voter["dni"],
            "email": voter["email"]
        },
        "has_voted": has_voted   
    }