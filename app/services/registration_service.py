from app.utils.supabase_client import supabase


def create_voter(data):

    voter_response = supabase.table("voters").insert({
        "dni": data["dni"],
        "full_name": data["full_name"],
        "birth_date": data["birth_date"],
        "email": data["email"]
    }).execute()

    voter = voter_response.data[0]

    supabase.table("registration_status").insert({
        "voter_id": voter["id"],
        "current_step": 1,
        "status": "pending"
    }).execute()

    return voter


def get_voter(voter_id):

    response = supabase.table("voters") \
        .select("*") \
        .eq("id", voter_id) \
        .single() \
        .execute()

    return response.data

def update_voter(voter_id, data):

    response = supabase.table("voters") \
        .update({
            "dni": data["dni"],
            "full_name": data["full_name"],
            "birth_date": data["birth_date"],
            "email": data["email"]
        }) \
        .eq("id", voter_id) \
        .execute()

    return response.data