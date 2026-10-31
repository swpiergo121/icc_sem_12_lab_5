#!/usr/bin/env python3

from flask import Flask

from app.config import Config
from app.extensions import db
from app.presentacion.rutas import bp
from app.negocio import servicios


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="presentacion/templates")
    app.config.from_object(config_class)

    db.init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        from app.datos import modelos  # noqa: F401  (registra los modelos)
        db.create_all()
        # Requerimiento 2: al iniciar, se almacenan los partidos recuperados
        nuevos, actualizados = servicios.sincronizar_partidos()
        app.logger.info("Partidos sincronizados: %s nuevos, %s actualizados", nuevos, actualizados)

    return app
