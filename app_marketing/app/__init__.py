#!/usr/bin/env python3

import os

from flask import Flask

from app.config import Config
from app.extensions import db
from app.presentacion.rutas import bp


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="presentacion/templates")
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        from app.datos import modelos  # noqa: F401
        db.create_all()

    os.makedirs(app.config["MEDIA_DIR"], exist_ok=True)
    return app
