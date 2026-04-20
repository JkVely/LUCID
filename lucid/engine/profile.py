"""
LUCID – Perfil del Estudiante
==============================
Modelo de datos con persistencia en JSON para el perfil adaptativo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

from config import (
    DATA_DIR,
    PROFILE_PATH,
    STREAK_TO_LEVEL_UP,
    ERRORS_TO_LEVEL_DOWN,
    DIFFICULTY_LEVELS,
)


@dataclass
class StudentProfile:
    """Estado del estudiante con algoritmo adaptativo integrado."""

    name: str = "Aventurero"
    level: int = 1
    domain: str = "Aritmética"
    total_correct: int = 0
    total_incorrect: int = 0
    current_streak: int = 0
    best_streak: int = 0
    consecutive_errors: int = 0
    challenges_played: int = 0
    domain_scores: dict[str, dict[str, int]] = field(default_factory=lambda: {
        "Aritmética": {"correct": 0, "incorrect": 0},
        "Álgebra":    {"correct": 0, "incorrect": 0},
        "Geometría":  {"correct": 0, "incorrect": 0},
    })
    history: list[dict[str, Any]] = field(default_factory=list)

    # ── Propiedades calculadas ────────────────────────────────────────

    @property
    def success_rate(self) -> float:
        """Porcentaje de éxito global."""
        total = self.total_correct + self.total_incorrect
        return (self.total_correct / total * 100) if total > 0 else 0.0

    @property
    def level_name(self) -> str:
        """Nombre legible del nivel actual."""
        return DIFFICULTY_LEVELS.get(self.level, DIFFICULTY_LEVELS[1])["name"]

    @property
    def level_icon(self) -> str:
        """Icono del nivel actual."""
        return DIFFICULTY_LEVELS.get(self.level, DIFFICULTY_LEVELS[1])["icon"]

    @property
    def domain_progress(self) -> dict[str, float]:
        """Porcentaje de éxito por dominio."""
        progress = {}
        for dom, scores in self.domain_scores.items():
            total = scores["correct"] + scores["incorrect"]
            progress[dom] = (scores["correct"] / total * 100) if total > 0 else 0.0
        return progress

    @property
    def recent_errors_summary(self) -> str:
        """Resumen de errores recientes para el prompt."""
        errors = [h for h in self.history[-10:] if not h.get("correct", True)]
        if not errors:
            return "ninguno registrado"
        domains = set(e.get("domain", "?") for e in errors)
        return f"{len(errors)} errores recientes en: {', '.join(domains)}"

    # ── Algoritmo Adaptativo ─────────────────────────────────────────

    def record_answer(self, correct: bool, domain: str, expression: str = "") -> str:
        """
        Registra una respuesta y aplica el algoritmo adaptativo.

        Returns
        -------
        str
            Evento adaptativo: ``"level_up"``, ``"level_down"``, o ``""``.
        """
        self.challenges_played += 1
        event = ""

        # Actualizar contadores
        if correct:
            self.total_correct += 1
            self.current_streak += 1
            self.consecutive_errors = 0
            self.best_streak = max(self.best_streak, self.current_streak)

            if domain in self.domain_scores:
                self.domain_scores[domain]["correct"] += 1

            # ¿Subir de nivel?
            if self.current_streak >= STREAK_TO_LEVEL_UP and self.level < 5:
                self.level += 1
                # Mantener la racha visible; solo resetear al iniciar nueva
                # serie después del level_up para que la UI muestre el valor.
                event = "level_up"
        else:
            self.total_incorrect += 1
            self.current_streak = 0
            self.consecutive_errors += 1

            if domain in self.domain_scores:
                self.domain_scores[domain]["incorrect"] += 1

            # ¿Bajar de nivel?
            if self.consecutive_errors >= ERRORS_TO_LEVEL_DOWN and self.level > 1:
                self.level -= 1
                self.consecutive_errors = 0
                event = "level_down"

        # Registrar en historial (últimos 50)
        self.history.append({
            "domain": domain,
            "correct": correct,
            "expression": expression,
            "level": self.level,
        })
        if len(self.history) > 50:
            self.history = self.history[-50:]

        return event

    # ── Persistencia ─────────────────────────────────────────────────

    def save(self) -> None:
        """Guarda el perfil en disco como JSON."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(PROFILE_PATH, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls) -> StudentProfile:
        """Carga el perfil desde disco, o crea uno nuevo si no existe."""
        if PROFILE_PATH.exists():
            try:
                with open(PROFILE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except (json.JSONDecodeError, TypeError, KeyError):
                pass  # Perfil corrupto → crear nuevo
        profile = cls()
        profile.save()
        return profile

    def reset(self) -> None:
        """Reinicia el perfil manteniendo el nombre."""
        name = self.name
        self.__init__()  # type: ignore[misc]
        self.name = name
        self.save()
