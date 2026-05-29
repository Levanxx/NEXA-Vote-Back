from flask import Blueprint, request, jsonify, g
from app.services.vote_service import cast_vote, get_results, get_total_votes, get_turnout, get_turnout_detailed
from app.middleware.auth_middleware import require_admin, require_auth
from app.extensions import limiter
from flask import current_app as app
from app.services.report_service import get_report, get_report_csv 

votes_bp = Blueprint("votes", __name__, url_prefix="/api/votes")


@votes_bp.route("/cast", methods=["POST"])
@limiter.limit("10 per minute")
@require_auth
def vote():
    data = request.get_json()
    candidate_id = data.get("candidate_id")

    if candidate_id is None or (candidate_id.lower() != "blank" and not candidate_id):
        return jsonify({"success": False, "error": "Datos incompletos"}), 400

    try:

        cast_vote(g.voter_id, candidate_id, g.session_token_hash) 

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
@require_admin
def results():
    try:
        data = get_results()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@votes_bp.route("/total", methods=["GET"])
@require_admin
def total():
    try:
        data = get_total_votes()
        return jsonify({"success": True, "total": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@votes_bp.route("/turnout", methods=["GET"])
@require_admin
def turnout():
    return jsonify({"success": True, "percentage": get_turnout()}), 200

@votes_bp.route("/turnout-detailed", methods=["GET"])
@require_admin
def turnout_detailed():
    return jsonify({
        "success": True,
        **get_turnout_detailed()
    }), 200


@votes_bp.route("/report", methods=["GET"])
@require_admin
def report():
    try:
        data = get_report()
        return jsonify({"success": True, "data": data}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@votes_bp.route("/report/csv", methods=["GET"])
@require_admin
def report_csv():
    try:
        csv_content = get_report_csv()
        response = app.make_response(csv_content)
        response.headers["Content-Type"] = "text/csv; charset=utf-8"
        response.headers["Content-Disposition"] = "attachment; filename=reporte_votacion.csv"
        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500