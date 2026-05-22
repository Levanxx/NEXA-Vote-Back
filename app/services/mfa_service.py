from app.utils.supabase_client import supabase, supabase_admin

def validate_dni_mfa(token, dni_scanned):

    if not token:
        raise Exception("Token requerido")

    # 1. validar JWT
    user_response = supabase.auth.get_user(token.replace("Bearer ", ""))

    if not user_response.user:
        raise Exception("Usuario no válido")

    user = user_response.user

    # 2. 🔥 USAR ADMIN CLIENT (ESTO ARREGLA EL ERROR 42501)
    voter_response = supabase_admin.table("voters") \
        .select("*") \
        .eq("auth_user_id", user.id) \
        .single() \
        .execute()

    voter = voter_response.data

    if not voter:
        raise Exception("Votante no encontrado")

    # 3. validar DNI
    if str(voter["dni"]) != str(dni_scanned):
        raise Exception("DNI no coincide con el usuario")

    # 4. actualizar estado MFA (también admin)
    supabase_admin.table("registration_status") \
        .update({
            "current_step": 2,
            "status": "dni_validated"
        }) \
        .eq("voter_id", voter["id"]) \
        .execute()

    return {
        "message": "DNI validado correctamente",
        "voter_id": voter["id"]
    }