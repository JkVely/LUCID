"""
LUCID – Configuración Central
==============================
Constantes, rutas y parámetros del sistema.
Incluye persistencia de configuración del usuario.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# ── Cargar .env ───────────────────────────────────────────────────────
load_dotenv(Path(__file__).parent / ".env")

# ── Paths ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROFILE_PATH = DATA_DIR / "student_profile.json"
SETTINGS_PATH = DATA_DIR / "settings.json"

# ── Ollama / LLM ─────────────────────────────────────────────────────
OLLAMA_MODEL: str = os.environ.get("LUCID_MODEL", "gemma4:e4b")
OLLAMA_HOST: str = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_TEMPERATURE: float = 0.75
LLM_MAX_TOKENS: int = 1200
LLM_TOP_P: float = 0.9

# ── Gemini API (Fallback) ────────────────────────────────────────────
GEMINI_API_KEY: str = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.environ.get("GEMINI_MODEL", "gemini-3.0-flash")

# ── Math Domains ──────────────────────────────────────────────────────
DOMAINS: dict[str, dict] = {
    "Aritmética": {
        "description": "Operaciones básicas, fracciones, porcentajes y proporciones",
        "icon": "🔢",
    },
    "Álgebra": {
        "description": "Ecuaciones, expresiones algebraicas y funciones",
        "icon": "📐",
    },
    "Geometría": {
        "description": "Áreas, perímetros, volúmenes y ángulos",
        "icon": "📏",
    },
}

# ── Difficulty Levels ─────────────────────────────────────────────────
DIFFICULTY_LEVELS: dict[int, dict] = {
    1: {"name": "Aprendiz",   "icon": "🌱", "desc": "Conceptos fundamentales"},
    2: {"name": "Explorador", "icon": "🗺️",  "desc": "Aplicaciones básicas"},
    3: {"name": "Aventurero", "icon": "⚔️",  "desc": "Problemas combinados"},
    4: {"name": "Héroe",      "icon": "🛡️",  "desc": "Razonamiento avanzado"},
    5: {"name": "Leyenda",    "icon": "👑", "desc": "Desafíos de maestría"},
}

# ── Narrative Themes ──────────────────────────────────────────────────
NARRATIVE_THEMES: dict[str, dict] = {
    "Medieval / Fantasía": {
        "icon": "🏰",
        "desc": "Reinos, dragones, magos y caballeros",
        "setting": (
            "un mundo de fantasía medieval llamado Numeralia, donde la matemática "
            "es la fuente de toda magia. Hay castillos, bosques encantados, dragones, "
            "magos y caballeros."
        ),
        "dm_name": "El Guardián del Saber",
    },
    "Ciencia Ficción": {
        "icon": "🚀",
        "desc": "Naves, planetas, robots y tecnología",
        "setting": (
            "una galaxia futurista llamada Nexus-7, donde la matemática impulsa "
            "la tecnología interestelar. Hay naves espaciales, estaciones orbitales, "
            "inteligencias artificiales y mundos alienígenas."
        ),
        "dm_name": "La IA Centinela",
    },
    "Piratas": {
        "icon": "🏴‍☠️",
        "desc": "Mares, tesoros, islas y aventura",
        "setting": (
            "los Siete Mares de Cifra, un archipiélago de islas donde cada tesoro "
            "está protegido por acertijos matemáticos. Hay barcos piratas, mapas del "
            "tesoro, tormentas, criaturas marinas y puertos misteriosos."
        ),
        "dm_name": "El Capitán Números",
    },
    "Exploración Espacial": {
        "icon": "🌌",
        "desc": "Astronautas, descubrimientos y cosmos",
        "setting": (
            "el Programa de Exploración Cósmica del año 3025, donde los astronautas "
            "deben resolver problemas matemáticos para navegar entre estrellas, "
            "reparar sistemas de soporte vital y descifrar señales alienígenas."
        ),
        "dm_name": "El Comandante Estelar",
    },
    "Steampunk": {
        "icon": "⚙️",
        "desc": "Engranajes, vapor, inventos y victoriano",
        "setting": (
            "la ciudad de Cogsworth, una metrópolis victoriana impulsada por vapor "
            "y engranajes donde los inventores resuelven problemas matemáticos para "
            "crear autómatas, dirigibles y máquinas extraordinarias."
        ),
        "dm_name": "El Gran Inventor",
    },
    "Mundo Submarino": {
        "icon": "🐙",
        "desc": "Océanos, criaturas marinas y misterios",
        "setting": (
            "el Reino de Abyssia, una civilización submarina donde las matemáticas "
            "controlan las corrientes, la bioluminiscencia y las puertas de coral. "
            "Hay ciudades de cristal, ballenas sabias, arrecifes mágicos y fosas abisales."
        ),
        "dm_name": "El Oráculo del Abismo",
    },
}

# ── Adaptive Algorithm ────────────────────────────────────────────────
STREAK_TO_LEVEL_UP: int = 3
ERRORS_TO_LEVEL_DOWN: int = 2

# ── Application Metadata ─────────────────────────────────────────────
APP_NAME: str = "LUCID"
APP_SUBTITLE: str = "Dungeon Master Matemático"
APP_VERSION: str = "0.2.0"
WINDOW_WIDTH: int = 1100
WINDOW_HEIGHT: int = 720
SIDEBAR_WIDTH: int = 290


# ── User Settings (persistable) ──────────────────────────────────────

_DEFAULT_SETTINGS = {
    "custom_api_key": "",
    "custom_model": "",
    "custom_endpoint": "",
    "font_scale": 0,
    "preferred_backend": "auto",  # "auto" | "ollama" | "gemini" | "custom"
}


def load_settings() -> dict:
    """Carga la configuración del usuario desde disco."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Merge con defaults para campos nuevos
            merged = {**_DEFAULT_SETTINGS, **data}
            return merged
        except (json.JSONDecodeError, TypeError):
            pass
    return dict(_DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    """Guarda la configuración del usuario en disco."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)
