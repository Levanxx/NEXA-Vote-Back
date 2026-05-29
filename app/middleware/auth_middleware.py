from functools import wraps
from flask import request, jsonify, g
from app.utils.supabase_client import get_supabase_admin
from app.config import Config
from supabase import create_client
import hashlib


def _validate_token(token):
    """Valida JWT con cliente descartable — no contamina el singleton."""
    if not token:
        return None
    temp = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
    try:
        user = temp.auth.get_user(token)
        if not user or not user.user:
            return None
        return user.user
    except Exception:
        return None


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            return jsonify({"success": False, "error": "Token requerido"}), 401

        token = auth.replace("Bearer ", "")
        user = _validate_token(token)
        if not user:
            return jsonify({"success": False, "error": "Token inválido o expirado"}), 401

        supabase_admin = get_supabase_admin()
        voter = supabase_admin.table("voters") \
            .select("id") \
            .eq("auth_user_id", user.id) \
            .maybe_single() \
            .execute()

        g.voter_id = voter.data["id"] if voter.data else None
        g.auth_user_id = user.id
        g.session_token_hash = hashlib.sha256(token.encode()).hexdigest()

        return f(*args, **kwargs)

    return decorated


def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            return jsonify({"success": False, "error": "Token requerido"}), 401

        token = auth.replace("Bearer ", "")
        user = _validate_token(token)
        if not user:
            return jsonify({"success": False, "error": "Token inválido o expirado"}), 401

        supabase_admin = get_supabase_admin()
        admin = supabase_admin.table("admins") \
            .select("*") \
            .eq("auth_user_id", user.id) \
            .maybe_single() \
            .execute()

        if not admin.data:
            return jsonify({"success": False, "error": "No autorizado"}), 403

        g.admin_id = admin.data["id"]
        g.auth_user_id = user.id

        return f(*args, **kwargs)

    return decorated



