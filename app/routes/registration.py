from flask import Blueprint, request, jsonify
from app.services.registration_service import (
    create_voter,
    get_voter,
    update_voter
)
from app.utils.validators import validate_identity

registration_bp = Blueprint("registration", __name__)



@registration_bp.route("/register/identity", methods=["POST"])
def register_identity():

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
        voter = create_voter(data)

        return jsonify({
            "success": True,
            "message": "Registro creado correctamente",
            "data": {
                "voter_id": voter["id"]
            }
        }), 201

    except Exception as e:
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
        })

    except Exception:
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
        update_voter(voter_id, data)

        return jsonify({
            "success": True,
            "message": "Actualizado correctamente"
        })

    except Exception:
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500