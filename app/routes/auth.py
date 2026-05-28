from flask import Blueprint, request, jsonify
from app.services.auth_service import login_voter
from app.extensions import limiter

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    data = request.get_json()

    dni = data.get("dni")
    password = data.get("password")

    if not dni or not password:
        return jsonify({
            "success": False,
            "error": "DNI y password requeridos"
        }), 400

    try:
        result = login_voter(dni, password)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 401