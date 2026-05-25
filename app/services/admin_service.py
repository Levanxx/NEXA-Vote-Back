from app.utils.supabase_client import get_supabase, get_supabase_admin


def login_admin(email, password):

    auth_response = get_supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not auth_response.session:
        raise Exception("Credenciales inválidas")

    user = auth_response.user

    admin_response = get_supabase_admin.table("admins") \
        .select("*") \
        .eq("auth_user_id", user.id) \
        .maybe_single() \
        .execute()

    if not admin_response.data:
        raise Exception("No es administrador")

    return {
        "token": auth_response.session.access_token,
        "admin": admin_response.data
    }