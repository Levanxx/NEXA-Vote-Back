from flask import Blueprint, request, jsonify
from app.services.admin_service import login_admin, get_audit_logs
from app.middleware.auth_middleware import require_admin
from app.extensions import limiter

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    try:
        result = login_admin(email, password)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 401

@admin_bp.route("/audit-logs", methods=["GET"])
@require_admin
def audit_logs():
    try:
        data = get_audit_logs()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500