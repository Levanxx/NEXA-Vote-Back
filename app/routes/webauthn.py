from flask import Blueprint, request, jsonify
from app.services.webauthn_service import generate_challenge, save_webauthn, verify_webauthn_login

webauthn_bp = Blueprint("webauthn", __name__)


@webauthn_bp.route("/webauthn/register/options", methods=["POST"])
def options():

    return jsonify({
        "success": True,
        "challenge": generate_challenge()
    }), 200


@webauthn_bp.route("/webauthn/register/verify", methods=["POST"])
def verify():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Body requerido"
        }), 400

    voter_id = data.get("voter_id")
    credential_id = data.get("id")  

    if not voter_id or not credential_id:
        return jsonify({
            "success": False,
            "error": "Datos incompletos"
        }), 400

    try:
        save_webauthn(voter_id, credential_id)

        return jsonify({
            "success": True,
            "message": "WebAuthn guardado correctamente"
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@webauthn_bp.route("/webauthn/auth/options", methods=["POST"])
def auth_options():

    return jsonify({
        "success": True,
        "challenge": generate_challenge()
    }), 200


@webauthn_bp.route("/webauthn/auth/verify", methods=["POST"])
def auth_verify():

    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "error": "Body requerido"
        }), 400

    voter_id = data.get("voter_id")
    credential_id = data.get("id")

    try:

        verify_webauthn_login(voter_id, credential_id)

        return jsonify({
            "success": True,
            "message": "WebAuthn validado"
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 401