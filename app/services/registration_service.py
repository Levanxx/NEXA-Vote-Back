from app.utils.supabase_client import supabase, supabase_admin
import uuid


def create_voter(data):

    auth_user = supabase_admin.auth.admin.create_user({
        "email": data["email"],
        "password": data["password"],
        "email_confirm": True
    })

    user_id = auth_user.user.id

    voter_response = supabase_admin.table("voters").insert({
        "dni": data["dni"],
        "full_name": data["full_name"],
        "birth_date": data["birth_date"],
        "email": data["email"],
        "auth_user_id": user_id,
        "registration_step": 2
    }).execute()

    voter = voter_response.data[0]

    supabase_admin.table("registration_status").insert({
        "voter_id": voter["id"],
        "current_step": 2,
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

    # 1. CREAR AUTH USER (SI NO EXISTE)
    auth_user = supabase_admin.auth.admin.create_user({
        "email": data["email"],
        "password": data["password"],
        "email_confirm": True
    })

    user_id = auth_user.user.id


    response = supabase_admin.table("voters") \
        .update({
            "dni": data["dni"],
            "full_name": data["full_name"],
            "birth_date": data.get("birth_date"),
            "email": data["email"],
            "auth_user_id": user_id   
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


def create_voter_from_scan(data):

    voter_response = supabase_admin.table("voters").insert({
        "dni": data["dni"],
        "full_name": data["full_name"],
        "birth_date": None,
        "email": None,
        "auth_user_id": None,
        "registration_step": 1
    }).execute()

    voter = voter_response.data[0]

    supabase_admin.table("registration_status").insert({
        "voter_id": voter["id"],
        "current_step": 1,
        "status": "pending"
    }).execute()

    return voter