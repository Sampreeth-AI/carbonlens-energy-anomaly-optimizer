"""Flask application factory for CarbonLens."""
import os
from dotenv import load_dotenv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.getenv("SECRET_KEY", "local-development-key"), SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///carbonlens.db"), SQLALCHEMY_TRACK_MODIFICATIONS=False, MAX_CONTENT_LENGTH=8 * 1024 * 1024)
    db.init_app(app)
    from app.api import api
    app.register_blueprint(api, url_prefix="/api/v1")

    @app.get("/")
    def home():
        return render_template("index.html")

    with app.app_context():
        from app.models import EnergyRun
        db.create_all()
    return app
