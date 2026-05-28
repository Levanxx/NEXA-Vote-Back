import os
from flask import Flask, jsonify, g
from flask_cors import CORS
from app.middleware.auth_middleware import require_auth
from app.extensions import limiter

from app.routes.registration import registration_bp
from app.routes.biometric import biometric_bp
from app.routes.webauthn import webauthn_bp
from app.routes.auth import auth_bp
from app.routes.mfa import mfa_bp
from app.routes.candidates import candidates_bp
from app.routes.votes import votes_bp
from app.routes.admin import admin_bp



def create_app():
    app = Flask(__name__)
    limiter.init_app(app)

    allowed_origins = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:5173"
    ).split(",")

    @app.route("/")
    def health():
        return {"status": "ok"}, 200
    

    @app.route("/auth/me")
    @require_auth
    def auth_me():
        from app.services.registration_service import get_voter
        voter = get_voter(g.voter_id)
        if not voter:
            return jsonify({"success": False, "error": "Votante no encontrado"}), 404
        return jsonify({"success": True, "data": voter}), 200
    

    CORS(app, origins=allowed_origins)

    app.register_blueprint(registration_bp)
    app.register_blueprint(biometric_bp)
    app.register_blueprint(webauthn_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mfa_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(votes_bp)
    app.register_blueprint(admin_bp)

    return app