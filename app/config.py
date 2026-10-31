#!/usr/bin/env python3

import os
from pathlib import Path
from dotenv import load_dotenv

# Carga .env desde la raíz del proyecto (un nivel por encima de app/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "1234")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///champions.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FOOTBALL_API_TOKEN = os.getenv("FOOTBALL_API_TOKEN", "")
    FOOTBALL_API_URL = os.getenv(
        "FOOTBALL_API_URL",
        "https://api.football-data.org/v4/competitions/CL/matches",
    )
