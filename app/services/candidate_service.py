from app.utils.supabase_client import get_supabase_admin


def get_active_candidates():
    response = get_supabase_admin.table("candidates") \
        .select("*") \
        .eq("is_active", True) \
        .execute()

    if not response.data:
        return []

    return response.data