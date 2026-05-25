from supabase import create_client, Client
from app.config import Config

_supabase: Client = None
_supabase_admin: Client = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_KEY
        )
    return _supabase

def get_supabase_admin() -> Client:
    global _supabase_admin
    if _supabase_admin is None:
        _supabase_admin = create_client(
            Config.SUPABASE_URL,
            Config.SUPABASE_SERVICE_ROLE_KEY
        )
    return _supabase_admin