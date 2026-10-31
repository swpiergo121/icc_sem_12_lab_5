#!/usr/bin/env python3

from abc import ABC, abstractmethod


class Publicador(ABC):
    """Contrato que debe cumplir cualquier red social."""

    nombre = "base"

    @abstractmethod
    def publicar(self, campana):
        """Recibe una Campana con guion elegido e imágenes listas.
        Devuelve un dict: {"estado": str, "id_externo": str | None}."""

    @abstractmethod
    def estado(self, id_externo):
        """Devuelve el estado actual de una publicación."""


PUBLICADORES: dict[str, Publicador] = {}


def registrar(publicador: Publicador):
    PUBLICADORES[publicador.nombre] = publicador


def obtener(nombre: str) -> Publicador:
    if nombre not in PUBLICADORES:
        raise ValueError(f"Red no disponible: {nombre}")
    return PUBLICADORES[nombre]
