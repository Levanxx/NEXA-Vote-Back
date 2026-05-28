from app.utils.supabase_client import get_supabase_admin
from flask import request

def log_action(action_type, status, voter_id=None, metadata=None):
    supabase_admin = get_supabase_admin()
    ip_address = request.remote_addr if request else None
    supabase_admin.table("audit_logs").insert({
        "voter_id": voter_id,
        "action_type": action_type,
        "status": status,
        "ip_address": ip_address,
        "metadata": metadata
    }).execute()