#!/usr/bin/env python3

from datetime import datetime

from app.extensions import db
from app.datos import fuente_api
from app.datos.modelos import Partido, Prediccion

GANADORES_VALIDOS = {"LOCAL", "EMPATE", "VISITANTE"}


class ErrorValidacion(ValueError):
    """Error de regla de negocio, mostrable al usuario."""


def sincronizar_partidos():
    """Consume la API y guarda o actualiza cada partido (upsert por id_externo)."""
    nuevos = actualizados = 0
    for d in fuente_api.obtener_partidos():
        partido = Partido.query.filter_by(id_externo=d["id"]).first()
        if partido is None:
            partido = Partido(id_externo=d["id"])
            db.session.add(partido)
            nuevos += 1
        else:
            actualizados += 1

        fecha = datetime.fromisoformat(d["utcDate"].replace("Z", "+00:00"))
        partido.fecha = fecha.replace(tzinfo=None)
        partido.fase = d.get("stage")
        partido.estado = d.get("status")
        partido.equipo_local = d["homeTeam"]["name"]
        partido.equipo_visitante = d["awayTeam"]["name"]
        marcador = d["score"]["fullTime"]
        partido.goles_local = marcador["home"]
        partido.goles_visitante = marcador["away"]

    db.session.commit()
    return nuevos, actualizados


def listar_partidos():
    return Partido.query.order_by(Partido.fecha).all()


def registrar_prediccion(partido_id, ganador, goles_local, goles_visitante):
    partido = db.session.get(Partido, partido_id)
    if partido is None:
        raise ErrorValidacion("El partido no existe.")
    if partido.estado == "FINISHED":
        raise ErrorValidacion("No se puede predecir un partido ya finalizado.")

    ganador = (ganador or "").upper()
    if ganador not in GANADORES_VALIDOS:
        raise ErrorValidacion("Ganador no válido.")

    try:
        gl, gv = int(goles_local), int(goles_visitante)
    except (TypeError, ValueError):
        raise ErrorValidacion("El marcador debe ser numérico.")
    if gl < 0 or gv < 0:
        raise ErrorValidacion("El marcador no puede ser negativo.")

    # Coherencia entre ganador y marcador
    if ganador == "LOCAL" and not gl > gv:
        raise ErrorValidacion("Si gana el local, sus goles deben superar a los del visitante.")
    if ganador == "VISITANTE" and not gv > gl:
        raise ErrorValidacion("Si gana el visitante, sus goles deben superar a los del local.")
    if ganador == "EMPATE" and gl != gv:
        raise ErrorValidacion("En un empate, ambos marcadores deben ser iguales.")

    prediccion = Prediccion(
        partido_id=partido.id,
        ganador=ganador,
        goles_local=gl,
        goles_visitante=gv,
    )
    db.session.add(prediccion)
    db.session.commit()
    return prediccion


def listar_predicciones():
    return Prediccion.query.order_by(Prediccion.creado_en.desc()).all()
