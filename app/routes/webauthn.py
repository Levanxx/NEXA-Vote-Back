from flask import Blueprint, request, jsonify, g 
from app.services.webauthn_service import register_begin, register_complete, auth_begin, auth_complete
from app.middleware.auth_middleware import require_auth
from app.extensions import limiter


webauthn_bp = Blueprint("webauthn", __name__)


@webauthn_bp.route("/webauthn/register/options", methods=["POST"])
@limiter.limit("30 per minute")
@require_auth
def options():

    from app.services.registration_service import get_voter
    voter = get_voter(g.voter_id)
    result, state = register_begin(g.voter_id, voter["email"], voter["full_name"])
    return jsonify({"success": True, "data": dict(result), "state": state}), 200


@webauthn_bp.route("/webauthn/register/verify", methods=["POST"])
@limiter.limit("30 per minute")
@require_auth
def verify():
    data = request.get_json()
    register_complete(g.voter_id, data, data["state"])
    return jsonify({"success": True, "message": "WebAuthn registrado correctamente"}), 200
    


@webauthn_bp.route("/webauthn/auth/options", methods=["POST"])
@limiter.limit("30 per minute")
@require_auth 
def auth_options():
    result, state = auth_begin(g.voter_id)
    return jsonify({"success": True, "data": dict(result), "state": state}), 200




@webauthn_bp.route("/webauthn/auth/verify", methods=["POST"])
@limiter.limit("30 per minute")
@require_auth
def auth_verify():
    data = request.get_json()
    auth_complete(g.voter_id, data, g.session_token_hash, data["state"])
    
    return jsonify({"success": True, "message": "WebAuthn validado"}), 200