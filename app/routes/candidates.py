from flask import Blueprint, jsonify
from app.services.candidate_service import get_active_candidates

candidates_bp = Blueprint("candidates", __name__, url_prefix="/api/votes")


@candidates_bp.route("/candidates", methods=["GET"])
def list_candidates():

    try:
        data = get_active_candidates()

        return jsonify({
            "success": True,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500