#!/usr/bin/env python3

from datetime import datetime
from app.extensions import db


class Partido(db.Model):
    __tablename__ = "partidos"

    id = db.Column(db.Integer, primary_key=True)
    id_externo = db.Column(db.Integer, unique=True, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    fase = db.Column(db.String(60))
    estado = db.Column(db.String(30))
    equipo_local = db.Column(db.String(100), nullable=False)
    equipo_visitante = db.Column(db.String(100), nullable=False)
    goles_local = db.Column(db.Integer)
    goles_visitante = db.Column(db.Integer)

    predicciones = db.relationship(
        "Prediccion", back_populates="partido", cascade="all, delete-orphan"
    )


class Prediccion(db.Model):
    __tablename__ = "predicciones"

    id = db.Column(db.Integer, primary_key=True)
    partido_id = db.Column(db.Integer, db.ForeignKey("partidos.id"), nullable=False)
    ganador = db.Column(db.String(10), nullable=False)  # LOCAL | EMPATE | VISITANTE
    goles_local = db.Column(db.Integer, nullable=False)
    goles_visitante = db.Column(db.Integer, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    partido = db.relationship("Partido", back_populates="predicciones")
