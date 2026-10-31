#!/usr/bin/env python3

import requests
from flask import current_app


def _p(id_, fecha, local, visitante, fase="LEAGUE_STAGE"):
    """Construye un partido con el mismo esquema que devuelve football-data.org."""
    return {
        "id": id_,
        "utcDate": fecha,
        "stage": fase,
        "status": "SCHEDULED",
        "homeTeam": {"name": local},
        "awayTeam": {"name": visitante},
        "score": {"fullTime": {"home": None, "away": None}},
    }


SIMULADOS = [
    _p(1001, "2026-11-03T20:00:00Z", "Real Madrid CF", "Manchester City FC"),
    _p(1002, "2026-11-03T20:00:00Z", "FC Bayern München", "Paris Saint-Germain FC"),
    _p(1003, "2026-11-04T17:45:00Z", "FC Barcelona", "Liverpool FC"),
    _p(1004, "2026-11-04T20:00:00Z", "Arsenal FC", "Inter Milan"),
    _p(1005, "2026-11-25T20:00:00Z", "Manchester City FC", "FC Bayern München"),
    _p(1006, "2026-11-26T20:00:00Z", "Paris Saint-Germain FC", "Real Madrid CF"),
]


def obtener_partidos():
    """Devuelve la lista cruda de partidos desde la API externa o desde datos simulados."""
    token = current_app.config["FOOTBALL_API_TOKEN"]
    if not token:
        print("no token: ", token)
        print("---------------------------------------------------")
        current_app.logger.warning("Sin FOOTBALL_API_TOKEN: usando datos simulados")
        return SIMULADOS

    respuesta = requests.get(
        current_app.config["FOOTBALL_API_URL"],
        headers={"X-Auth-Token": token},
        timeout=10,
    )
    respuesta.raise_for_status()
    return respuesta.json().get("matches", [])
