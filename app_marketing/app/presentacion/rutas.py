#!/usr/bin/env python3

from flask import (Blueprint, flash, redirect, render_template,
                   request, send_file, url_for)

from app.datos.modelos import Campana, Medio
from app.extensions import db
from app.negocio import campanas as servicios

bp = Blueprint("web", __name__)


@bp.route("/")
def inicio():
    lista = Campana.query.order_by(Campana.creada_en.desc()).all()
    return render_template("index.html", campanas=lista)


@bp.route("/campanas", methods=["POST"])
def crear():
    try:
        campana = servicios.crear_campana(
            request.form.get("empresa"), request.form.get("producto"), request.files.get("foto")
        )
        flash("Campaña creada. Elige uno de los guiones.", "ok")
        return redirect(url_for("web.detalle", campana_id=campana.id))
    except servicios.ErrorValidacion as e:
        flash(str(e), "error")
        return redirect(url_for("web.inicio"))


@bp.route("/campanas/<int:campana_id>")
def detalle(campana_id):
    return render_template("campana.html", c=db.get_or_404(Campana, campana_id))


@bp.route("/campanas/<int:campana_id>/elegir", methods=["POST"])
def elegir(campana_id):
    campana = db.get_or_404(Campana, campana_id)
    try:
        servicios.elegir_guion(campana, request.form.get("guion_id", type=int))
        flash("Se generaron 3 imágenes con IA.", "ok")
    except servicios.ErrorValidacion as e:
        flash(str(e), "error")
    return redirect(url_for("web.detalle", campana_id=campana.id))


@bp.route("/campanas/<int:campana_id>/original")
def foto_original(campana_id):
    return send_file(db.get_or_404(Campana, campana_id).foto_original)


@bp.route("/medios/<int:medio_id>")
def medio(medio_id):
    return send_file(db.get_or_404(Medio, medio_id).ruta, conditional=True)
