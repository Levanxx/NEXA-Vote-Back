from flask import Blueprint, request, jsonify
from app.services.vote_service import cast_vote, get_voter_from_token, get_results, get_total_votes, get_turnout

votes_bp = Blueprint("votes", __name__, url_prefix="/api/votes")


@votes_bp.route("/cast", methods=["POST"])
def vote():
    data = request.get_json()
    candidate_id = data.get("candidate_id")

    if not candidate_id:
        return jsonify({
            "success": False,
            "error": "Datos incompletos"
        }), 400

    try:
        voter_id = get_voter_from_token(request)

        cast_vote(voter_id, candidate_id)

        return jsonify({
            "success": True,
            "message": "Voto registrado correctamente"
        }), 200

    except Exception as e:
        print("ERROR EN VOTE:", str(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    
@votes_bp.route("/results", methods=["GET"])
def results():
    try:
        data = get_results()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@votes_bp.route("/total", methods=["GET"])
def total():
    try:
        data = get_total_votes()
        return jsonify({"success": True, "total": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@votes_bp.route("/turnout", methods=["GET"])
def turnout():
    return jsonify({"success": True, "percentage": get_turnout()}), 200