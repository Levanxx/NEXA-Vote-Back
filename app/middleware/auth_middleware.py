from functools import wraps
from flask import request, jsonify, g
from app.utils.supabase_client import get_supabase_admin
import hashlib


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        if not auth:
            return jsonify({"success": False, "error": "Token requerido"}), 401
        
        token = auth.replace("Bearer ", "")
        supabase_admin = get_supabase_admin()
        
        try:
            user = supabase_admin.auth.get_user(token)
            if not user or not user.user:
                raise Exception("Token inválido")
        except Exception:
            return jsonify({"success": False, "error": "Token inválido o expirado"}), 401
        
        # Resolver voter_id
        voter = supabase_admin.table("voters") \
            .select("id") \
            .eq("auth_user_id", user.user.id) \
            .maybe_single() \
            .execute()
        
        g.voter_id = voter.data["id"] if voter.data else None
        g.auth_user_id = user.user.id
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
        supabase_admin = get_supabase_admin()
        try:
            user = supabase_admin.auth.get_user(token)
            if not user or not user.user:
                raise Exception("Token inválido")
        except Exception:
            return jsonify({"success": False, "error": "Token inválido o expirado"}), 401
        # Verificar si está en la tabla admins
        admin = supabase_admin.table("admins") \
            .select("*") \
            .eq("auth_user_id", user.user.id) \
            .maybe_single() \
            .execute()
        if not admin.data:
            return jsonify({"success": False, "error": "No autorizado"}), 403
        g.admin_id = admin.data["id"]
        g.auth_user_id = user.user.id
        return f(*args, **kwargs)
    return decorated