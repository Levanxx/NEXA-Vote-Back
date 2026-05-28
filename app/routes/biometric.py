from flask import Blueprint, request, jsonify
from app.services.biometric_service import save_face
from app.middleware.auth_middleware import require_auth

biometric_bp = Blueprint("biometric", __name__)


@biometric_bp.route("/register/face", methods=["POST"])
@require_auth
def register_face():

    data = request.get_json()

    print("DATA RECIBIDA:", data)  

    try:
        voter_id = data.get("voter_id")
        descriptor = data.get("descriptor")

        if not voter_id or not descriptor:
            return jsonify({
                "success": False,
                "error": "Datos incompletos"
            }), 400

        save_face(voter_id, descriptor)

        return jsonify({
            "success": True,
            "message": "Rostro guardado correctamente"
        })

    except Exception as e:
        print("ERROR BACKEND:", str(e))  
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500