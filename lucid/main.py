"""
LUCID – Punto de Entrada
==========================

    Large-language-model Unified Curriculum Intelligent Designer

Framework de IA Generativa para la Gamificación Matemática Adaptativa.
Usa Gemma 4 (vía Ollama) o Gemini 3 Flash (vía API) como Dungeon
Master pedagógico y SymPy como oráculo de validación simbólica.

Ejecución:
    uv run python main.py
"""

import sys
import os
import logging

# Asegurar que el directorio del script esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk


def main() -> None:
    """Inicializa y ejecuta la aplicación LUCID."""

    # ── Logging ───────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("lucid")
    logger.info("🐉 Iniciando LUCID v0.2.0 ...")

    # ── CustomTkinter Config ──────────────────────────────────────
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # ── Launch ────────────────────────────────────────────────────
    from ui.app import LucidApp

    app = LucidApp()
    logger.info("✅ UI lista. ¡Que comience la aventura!")
    app.mainloop()


if __name__ == "__main__":
    main()
