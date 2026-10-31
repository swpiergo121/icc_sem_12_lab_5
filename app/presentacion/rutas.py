#!/usr/bin/env python3

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.negocio import servicios

bp = Blueprint("web", __name__)


@bp.route("/")
def partidos():
    return render_template("partidos.html", partidos=servicios.listar_partidos())


@bp.route("/partidos/<int:partido_id>/prediccion", methods=["POST"])
def nueva_prediccion(partido_id):
    try:
        servicios.registrar_prediccion(
            partido_id,
            request.form.get("ganador"),
            request.form.get("goles_local"),
            request.form.get("goles_visitante"),
        )
        flash("Predicción registrada correctamente.", "ok")
    except servicios.ErrorValidacion as e:
        flash(str(e), "error")
    return redirect(url_for("web.partidos"))


@bp.route("/predicciones")
def predicciones():
    return render_template(
        "predicciones.html", predicciones=servicios.listar_predicciones()
    )
