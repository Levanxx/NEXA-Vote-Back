from app.utils.supabase_client import  get_supabase_admin
from app.services.audit_service import log_action

def login_admin(email, password):
         
    supabase_admin = get_supabase_admin()  

    auth_response = supabase_admin.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not auth_response.session:
        log_action("ADMIN_LOGIN", "failed", metadata={"email": email})  # ← acá
        raise Exception("Credenciales inválidas")

    user = auth_response.user

    admin_response = supabase_admin.table("admins") \
        .select("*") \
        .eq("auth_user_id", user.id) \
        .maybe_single() \
        .execute()

    if not admin_response.data:
        log_action("ADMIN_LOGIN", "failed", metadata={"email": email, "reason": "not_admin"})  # ← acá
        raise Exception("No es administrador")


    log_action("ADMIN_LOGIN", "success", metadata={"email": email})

    return {
        "token": auth_response.session.access_token,
        "admin": admin_response.data
    }


def get_audit_logs():
    supabase_admin = get_supabase_admin()
    response = supabase_admin.table("audit_logs") \
        .select("*") \
        .order("created_at", desc=True) \
        .execute()
    return response.data