#!/usr/bin/env python3

import os
import uuid

from flask import current_app

from app.datos import proveedores
from app.datos.modelos import Campana, Guion, Medio
from app.extensions import db

EXTENSIONES = {"jpg", "jpeg", "png", "webp"}


class ErrorValidacion(ValueError):
    """Error de regla de negocio, mostrable al usuario."""


def crear_campana(empresa, producto, archivo):
    empresa, producto = (empresa or "").strip(), (producto or "").strip()
    if not empresa or not producto:
        raise ErrorValidacion("La empresa y el producto son obligatorios.")
    if archivo is None or not archivo.filename or "." not in archivo.filename:
        raise ErrorValidacion("Debes subir una foto.")
    ext = archivo.filename.rsplit(".", 1)[-1].lower()
    if ext not in EXTENSIONES:
        raise ErrorValidacion("Formato de imagen no válido (jpg, png o webp).")

    # Primero la IA: si falla, no se guarda nada
    try:
        textos = proveedores.generar_guiones(empresa, producto)
    except Exception:
        current_app.logger.exception("Error generando guiones con OpenAI")
        raise ErrorValidacion("No se pudieron generar los guiones. Revisa la API key y los logs.")

    carpeta = os.path.join(current_app.config["MEDIA_DIR"], "originales")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, f"{uuid.uuid4().hex}.{ext}")
    archivo.save(ruta)

    campana = Campana(empresa=empresa, producto=producto, foto_original=ruta)
    db.session.add(campana)
    db.session.flush()
    for i, texto in enumerate(textos, start=1):
        db.session.add(Guion(campana_id=campana.id, orden=i, texto=texto))
    db.session.commit()
    return campana


def elegir_guion(campana, guion_id):
    # Permite reintentar si la generación anterior falló
    if campana.estado not in ("GUIONES_PROPUESTOS", "ERROR"):
        raise ErrorValidacion("Esta campaña ya tiene un guion elegido.")
    guion = next((g for g in campana.guiones if g.id == guion_id), None)
    if guion is None:
        raise ErrorValidacion("El guion seleccionado no es válido.")

    for g in campana.guiones:
        g.elegido = g.id == guion.id
    campana.estado = "GENERANDO"
    db.session.commit()

    try:
        carpeta = os.path.join(current_app.config["MEDIA_DIR"], f"campana_{campana.id}")
        os.makedirs(carpeta, exist_ok=True)
        imagenes = proveedores.generar_imagenes(
            campana.foto_original, campana.empresa, campana.producto, guion.texto, carpeta
        )
        for m in list(campana.medios):
            db.session.delete(m)
        for ruta in imagenes:
            db.session.add(Medio(campana_id=campana.id, tipo="imagen", ruta=ruta))
        campana.estado = "IMAGENES_LISTAS"
        db.session.commit()
    except Exception:
        current_app.logger.exception("Error generando imágenes de la campaña %s", campana.id)
        db.session.rollback()
        campana = db.session.get(Campana, campana.id)
        campana.estado = "ERROR"
        db.session.commit()
        raise ErrorValidacion("No se pudieron generar las imágenes. Puedes elegir otro guion para reintentar.")
