#!/usr/bin/env python3

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'marketing.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MEDIA_DIR = os.getenv("MEDIA_DIR", str(BASE_DIR / "media"))
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_TEXT_MODEL = os.getenv("OPENAI_TEXT_MODEL", "gpt-5")
    OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    IMAGE_QUALITY = os.getenv("IMAGE_QUALITY", "medium")
