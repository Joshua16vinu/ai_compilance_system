import os
import sys
import subprocess
import requests
import time

from flask import Flask
from flask_cors import CORS
from backend.routes.upload_routes import upload_bp
from backend.routes.health_routes import health_bp
from backend.routes.analyze_domain import analyze_bp

def ensure_ollama():
    try:
        requests.get("http://localhost:11434")
    except:
        subprocess.Popen(["ollama", "serve"])
        time.sleep(3)

ensure_ollama()
# Add project root to Python path so we can import 'backend' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def create_app():
    app = Flask(__name__)
    CORS(app)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "data", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(analyze_bp, url_prefix="/api")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)
