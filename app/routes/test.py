from flask import Blueprint, jsonify
from app.utils.supabase_client import supabase

test_bp = Blueprint("test", __name__)

@test_bp.route("/test", methods=["GET"])
def test():
    data = supabase.table("voters").select("*").limit(1).execute()
    return jsonify(data.data)