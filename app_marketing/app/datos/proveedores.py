#!/usr/bin/env python3

import base64
import io
import json
import os
import re
import uuid

from flask import current_app
from openai import OpenAI
from PIL import Image

ESTILOS = [
    "fotografía publicitaria limpia, luz natural y fondo neutro",
    "colores vivos, contraste alto y estilo de catálogo premium",
    "ambiente lifestyle, con personas usando el producto y fondo desenfocado",
]
TAMANO_IMAGEN = "1024x1536"  # vertical 2:3


def _cliente():
    clave = current_app.config["OPENAI_API_KEY"]
    if not clave:
        raise RuntimeError("Falta OPENAI_API_KEY en la configuración.")
    return OpenAI(api_key=clave, timeout=180)


def generar_guiones(empresa, producto):
    """Pide 3 guiones en JSON a un modelo de texto."""
    instrucciones = (
        "Eres un experto en marketing para redes sociales. "
        "Escribe 3 guiones cortos (máximo 30 palabras cada uno) para un anuncio vertical. "
        "Cada guion debe tener un enfoque distinto: problema-solución, historia de cliente "
        "y oferta con llamada a la acción. "
        'Responde solo con JSON válido con esta forma: {"guiones": ["...", "...", "..."]}. '
        "Escribe en español."
    )
    entrada = f"Empresa: {empresa}\nProducto o servicio: {producto}"
    respuesta = _cliente().responses.create(
        model=current_app.config["OPENAI_TEXT_MODEL"],
        instructions=instrucciones,
        input=entrada,
    )
    texto = re.sub(r"^```(?:json)?|```$", "", respuesta.output_text.strip()).strip()
    guiones = json.loads(texto)["guiones"]
    if len(guiones) != 3 or not all(isinstance(g, str) and g.strip() for g in guiones):
        raise ValueError("El modelo no devolvió exactamente 3 guiones válidos.")
    return [g.strip() for g in guiones]


def generar_imagenes(ruta_foto, empresa, producto, guion, carpeta):
    """Crea 3 imágenes a partir de la foto original. Se guardan como JPEG."""
    cliente = _cliente()
    modelo = current_app.config["OPENAI_IMAGE_MODEL"]
    calidad = current_app.config["IMAGE_QUALITY"]
    rutas = []

    for i, estilo in enumerate(ESTILOS, start=1):
        prompt = (
            f"Crea una imagen publicitaria para redes sociales de {empresa}, "
            f"producto: {producto}. Usa como referencia el producto de la foto. "
            f"Estilo: {estilo}. Formato vertical. "
            f'Incluye como texto breve, con tipografía legible: "{guion[:90]}".'
        )
        with open(ruta_foto, "rb") as f:
            respuesta = cliente.images.edit(
                model=modelo, image=f, prompt=prompt,
                size=TAMANO_IMAGEN, quality=calidad,
            )
        datos = base64.b64decode(respuesta.data[0].b64_json)
        imagen = Image.open(io.BytesIO(datos)).convert("RGB")
        ruta = os.path.join(carpeta, f"imagen_{i}_{uuid.uuid4().hex[:6]}.jpg")
        imagen.save(ruta, "JPEG", quality=92)
        rutas.append(ruta)
    return rutas
