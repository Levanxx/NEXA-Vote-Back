from app.utils.supabase_client import supabase


def login_voter(dni, password):

    # 1. buscar voter por DNI
    voter_response = supabase.table("voters") \
        .select("*") \
        .eq("dni", dni) \
        .single() \
        .execute()

    if not voter_response.data:
        raise Exception("Votante no encontrado")

    voter = voter_response.data
    email = voter["email"]

    # 2. login en Supabase Auth
    auth_response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not auth_response.session:
        raise Exception("Credenciales inválidas")

    session = auth_response.session

    return {
        "token": session.access_token,
        "user": {
            "id": voter["id"],
            "dni": voter["dni"],
            "email": voter["email"]
        }
    }