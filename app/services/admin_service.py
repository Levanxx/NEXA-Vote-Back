from app.utils.supabase_client import get_supabase_admin, get_supabase 
from app.services.audit_service import log_action

def login_admin(email, password):
         
    supabase = get_supabase()  

    auth_response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })

    if not auth_response or not auth_response.session:
        raise Exception("Credenciales inválidas")
    

    supabase_admin = get_supabase_admin()

    admin_response = supabase_admin.table("admins") \
        .select("*") \
        .eq("auth_user_id", auth_response.user.id) \
        .maybe_single() \
        .execute()

    if not admin_response.data:
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