#!/usr/bin/env python3

import uuid
from datetime import datetime

from app.extensions import db


class Campana(db.Model):
    __tablename__ = "campanas"

    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(120), nullable=False)
    producto = db.Column(db.Text, nullable=False)
    foto_original = db.Column(db.String(255), nullable=False)
    # GUIONES_PROPUESTOS -> GENERANDO -> LISTA_PARA_PUBLICAR -> PUBLICADA (o ERROR)
    estado = db.Column(db.String(30), nullable=False, default="GUIONES_PROPUESTOS")
    creada_en = db.Column(db.DateTime, default=datetime.utcnow)

    guiones = db.relationship("Guion", back_populates="campana",
                              cascade="all, delete-orphan", order_by="Guion.orden")
    medios = db.relationship("Medio", back_populates="campana", cascade="all, delete-orphan")
    publicaciones = db.relationship("Publicacion", back_populates="campana",
                                    cascade="all, delete-orphan")


class Guion(db.Model):
    __tablename__ = "guiones"

    id = db.Column(db.Integer, primary_key=True)
    campana_id = db.Column(db.Integer, db.ForeignKey("campanas.id"), nullable=False)
    orden = db.Column(db.Integer, nullable=False)
    texto = db.Column(db.Text, nullable=False)
    elegido = db.Column(db.Boolean, default=False, nullable=False)

    campana = db.relationship("Campana", back_populates="guiones")


class Medio(db.Model):
    __tablename__ = "medios"

    id = db.Column(db.Integer, primary_key=True)
    campana_id = db.Column(db.Integer, db.ForeignKey("campanas.id"), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)  # imagen
    ruta = db.Column(db.String(255), nullable=False)
    # Token aleatorio para la URL pública que descarga TikTok (no adivinable)
    token = db.Column(db.String(64), unique=True, nullable=False,
                      default=lambda: uuid.uuid4().hex)

    campana = db.relationship("Campana", back_populates="medios")


class Publicacion(db.Model):
    __tablename__ = "publicaciones"

    id = db.Column(db.Integer, primary_key=True)
    campana_id = db.Column(db.Integer, db.ForeignKey("campanas.id"), nullable=False)
    red = db.Column(db.String(20), nullable=False)  # tiktok
    estado = db.Column(db.String(40), nullable=False)
    id_externo = db.Column(db.String(100))  # publish_id de TikTok
    creada_en = db.Column(db.DateTime, default=datetime.utcnow)

    campana = db.relationship("Campana", back_populates="publicaciones")


class CuentaTikTok(db.Model):
    __tablename__ = "cuentas_tiktok"

    id = db.Column(db.Integer, primary_key=True)
    open_id = db.Column(db.String(100), unique=True, nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=False)
    expira_en = db.Column(db.DateTime, nullable=False)
    actualizada_en = db.Column(db.DateTime, default=datetime.utcnow)
