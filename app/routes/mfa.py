from flask import Blueprint, request, jsonify
from app.services.mfa_service import validate_dni_mfa
from app.services.mfa_service import validate_face_mfa

mfa_bp = Blueprint("mfa", __name__, url_prefix="/api/mfa")


@mfa_bp.route("/validate-dni", methods=["POST"])
def validate_dni():

    data = request.get_json()
    token = request.headers.get("Authorization")

    dni_scanned = data.get("dni_scanned")

    if not dni_scanned:
        return jsonify({
            "success": False,
            "error": "DNI escaneado requerido"
        }), 400

    try:
        result = validate_dni_mfa(token, dni_scanned)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 401
    

@mfa_bp.route("/validate-face", methods=["POST"])
def validate_face():

    data  = request.get_json()
    token = request.headers.get("Authorization")

    descriptor_nuevo = data.get("descriptor")

    if not descriptor_nuevo:
        return jsonify({
            "success": False,
            "error": "Descriptor facial requerido"
        }), 400

    try:
        result = validate_face_mfa(token, descriptor_nuevo)

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 401