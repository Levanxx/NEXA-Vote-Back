from app.utils.supabase_client import supabase, supabase_admin
import uuid


def create_voter(data):
    # 1. VALIDAR PRIMERO (IMPORTANTE)
    # DNI duplicado, email duplicado, etc

    # 2. crear auth user
    auth_user = supabase_admin.auth.admin.create_user({
        "email": data["email"],
        "password": data["password"],
        "email_confirm": True
    })

    user_id = auth_user.user.id

    # 3. guardar voter
    voter_response = supabase_admin.table("voters").insert({
        "dni": data["dni"],
        "full_name": data["full_name"],
        "birth_date": data["birth_date"],
        "email": data["email"],
        "auth_user_id": user_id
    }).execute()

    voter = voter_response.data[0]

    # 4. status
    supabase_admin.table("registration_status").insert({
        "voter_id": voter["id"],
        "current_step": 1,
        "status": "pending"
    }).execute()

    return voter

def register_user_auth(email, password):
    return supabase.auth.admin.create_user({
        "email": email,
        "password": password,
        "email_confirm": True
    })


def get_voter(voter_id):
    response = supabase_admin.table("voters") \
        .select("*") \
        .eq("id", voter_id) \
        .single() \
        .execute()

    return response.data

def update_voter(voter_id, data):
    response = supabase_admin.table("voters") \
        .update({
            "dni": data["dni"],
            "full_name": data["full_name"],
            "birth_date": data["birth_date"],
            "email": data["email"]
        }) \
        .eq("id", voter_id) \
        .execute()

    return response.data



def get_face(voter_id):

    response = supabase.table("biometric_data") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .maybe_single() \
        .execute()

    return response.data


def get_webauthn(voter_id):

    response = supabase.table("webauthn_credentials") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .maybe_single() \
        .execute()

    return response.data


def get_status(voter_id):

    response = supabase.table("registration_status") \
        .select("*") \
        .eq("voter_id", voter_id) \
        .single() \
        .execute()

    return response.data


def complete_registration_service(voter_id):

    response = supabase.table("registration_status") \
        .update({
            "current_step": 4,
            "status": "completed"
        }) \
        .eq("voter_id", voter_id) \
        .execute()

    return response.data