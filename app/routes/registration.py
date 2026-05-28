from flask import Blueprint, request, jsonify
from app.middleware.auth_middleware import require_auth
from app.extensions import limiter

from app.services.registration_service import (
    create_voter,
    get_voter,
    update_voter,
    get_face,
    get_webauthn,
    get_status,
    complete_registration_service,
    create_voter_from_scan
)

from app.utils.validators import validate_identity

registration_bp = Blueprint("registration", __name__)


@registration_bp.route("/register/identity", methods=["POST"])
@limiter.limit("5 per minute")
def register_identity():

    data = request.get_json()


    if not data:
        print("BODY VACÍO")
        return jsonify({
            "success": False,
            "error": "Body vacío o inválido"
        }), 400

    error = validate_identity(data)

    if error:
        return jsonify({
            "success": False,
            "error": error
        }), 400

    try:
        voter = create_voter(data)


        return jsonify({
            "success": True,
            "message": "Registro creado correctamente",
            "data": {
                "voter_id": voter["id"]
            }
        }), 201

    except Exception as e:
        print("ERROR REGISTER:", e)

        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@registration_bp.route("/register/voter/<voter_id>", methods=["GET"])
def get_voter_route(voter_id):

    try:

        voter = get_voter(voter_id)

        if not voter:
            return jsonify({
                "success": False,
                "error": "Votante no encontrado"
            }), 404

        return jsonify({
            "success": True,
            "data": voter
        }), 200

    except Exception as e:
        print("ERROR GET VOTER:", e)

        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500


@registration_bp.route("/register/identity/<voter_id>", methods=["PUT"])
def update_identity(voter_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Body vacío o inválido"
        }), 400

    error = validate_identity(data)

    if error:
        return jsonify({
            "success": False,
            "error": error
        }), 400

    try:

        voter_data, token = update_voter(voter_id, data)

        return jsonify({
            "success": True,
            "message": "Actualizado correctamente",
            "token": token 
        }), 200

    except Exception as e:
        print("ERROR UPDATE:", e)

        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500



@registration_bp.route("/register/summary/<voter_id>", methods=["GET"])
@require_auth
def registration_summary(voter_id):

    try:

        voter = get_voter(voter_id)

        face = get_face(voter_id)

        webauthn = get_webauthn(voter_id)

        status = get_status(voter_id)

        return jsonify({
            "success": True,
            "data": {
                **(voter or {}),
                "face_registered": face is not None,
                "webauthn_registered": webauthn is not None,
                "registration_step": status.get("current_step") if status else None,
                "registration_status": status.get("status") if status else None
            }
        }), 200

    except Exception as e:
        print("ERROR SUMMARY:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



@registration_bp.route("/register/complete/<voter_id>", methods=["PUT"])
@require_auth
def complete_registration(voter_id):

    try:

        complete_registration_service(voter_id)

        return jsonify({
            "success": True,
            "message": "Registro completado"
        }), 200

    except Exception as e:
        print("ERROR COMPLETE:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    

@registration_bp.route("/register/identity/scan", methods=["POST"])
@limiter.limit("5 per hour") 
def register_identity_scan():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Body vacío"
        }), 400

    try:

        voter = create_voter_from_scan(data)

        return jsonify({
            "success": True,
            "message": "DNI registrado correctamente",
            "data": {
                "voter_id": voter["id"]
            }
        }), 201

    except Exception as e:

        print("ERROR SCAN:", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500