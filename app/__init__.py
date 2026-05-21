from flask import Flask
from flask_cors import CORS

from app.routes.registration import registration_bp
from app.routes.biometric import biometric_bp
from app.routes.webauthn import webauthn_bp


def create_app():

    app = Flask(__name__)

    CORS(app, origins=["http://localhost:5173"])


    app.register_blueprint(registration_bp)
    app.register_blueprint(biometric_bp)
    app.register_blueprint(webauthn_bp)

    print("\n=== ROUTES REGISTRADAS ===")
    for rule in app.url_map.iter_rules():
        print(rule)

    return app