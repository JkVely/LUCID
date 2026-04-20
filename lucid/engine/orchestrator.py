"""
LUCID – Orquestador del Juego
===============================
Coordina el flujo completo: perfil → prompt → LLM → validación → feedback.
Soporta temáticas narrativas configurables y auto-avance tras respuesta correcta.
"""

from __future__ import annotations

import logging
from typing import Any, Callable

from engine.llm_client import LLMClient
from engine.validator import MathValidator
from engine.profile import StudentProfile
from engine.prompts import (
    build_challenge_messages,
    build_answer_check_messages,
    build_hint_messages,
    build_give_up_messages,
)

logger = logging.getLogger(__name__)


class GameOrchestrator:
    """
    Motor central de LUCID.

    Gestiona el ciclo de vida de cada clase:
    perfil → prompt contextualizado → LLM → validación SymPy → feedback → perfil.
    """

    def __init__(self) -> None:
        self.profile = StudentProfile.load()
        self.llm = LLMClient()
        self.validator = MathValidator()

        # Estado de la sesión activa
        self._conversation_history: list[dict[str, str]] = []
        self._current_challenge_text: str = ""
        self._current_math_expr: str = ""
        self._current_expected: str = ""
        self._challenge_active: bool = False
        self._hints_used: int = 0

        # Temática y tema de la clase actual
        self._current_theme: str = "Medieval / Fantasía"
        self._current_topic: str = ""

    # ── Propiedades ───────────────────────────────────────────────────

    @property
    def has_active_challenge(self) -> bool:
        return self._challenge_active

    @property
    def llm_status(self) -> str:
        return self.llm.status_text

    @property
    def current_theme(self) -> str:
        return self._current_theme

    @property
    def current_topic(self) -> str:
        return self._current_topic

    # ── Iniciar Clase ─────────────────────────────────────────────────

    def start_class(self, theme: str, topic: str) -> None:
        """
        Configura una nueva clase con la temática y tema elegidos.

        Parameters
        ----------
        theme : str
            Clave de NARRATIVE_THEMES (ej. "Piratas").
        topic : str
            Tema matemático libre (ej. "división de decimales").
        """
        self._current_theme = theme
        self._current_topic = topic
        self._conversation_history.clear()
        self._challenge_active = False
        self._current_challenge_text = ""
        self._current_math_expr = ""
        self._current_expected = ""
        self._hints_used = 0
        logger.info("📚 Nueva clase: tema='%s', temática='%s'", topic, theme)

    # ── Generar Desafío ───────────────────────────────────────────────

    def generate_challenge(self) -> str:
        """
        Genera un nuevo desafío narrativo-matemático.

        Returns
        -------
        str
            Texto del desafío (narrativa con problema matemático integrado).
        """
        messages = build_challenge_messages(
            domain=self.profile.domain,
            difficulty=self.profile.level,
            streak=self.profile.current_streak,
            success_rate=self.profile.success_rate,
            recent_errors=self.profile.recent_errors_summary,
            conversation_history=self._conversation_history,
            theme=self._current_theme,
            topic=self._current_topic,
        )

        response = self.llm.generate(messages)

        # Extraer la parte matemática
        math_data = self.validator.extract_math(response)
        if math_data:
            self._current_math_expr, self._current_expected = math_data
            # Validar que la expresión sea correcta
            if not self.validator.validate_expression(
                self._current_math_expr, self._current_expected
            ):
                logger.warning(
                    "⚠️ Expresión del LLM no validada: %s = %s",
                    self._current_math_expr,
                    self._current_expected,
                )
        else:
            self._current_math_expr = ""
            self._current_expected = ""
            logger.warning("No se encontró tag [MATH] en la respuesta del LLM.")

        # Limpiar el tag [MATH] del texto para el usuario
        display_text = response
        if "[MATH:" in response:
            lines = response.split("\n")
            display_lines = [
                ln for ln in lines
                if not ln.strip().startswith("[MATH:")
            ]
            display_text = "\n".join(display_lines).strip()

        self._current_challenge_text = display_text
        self._challenge_active = True
        self._hints_used = 0

        # Guardar en historial de conversación
        self._conversation_history.append({
            "role": "assistant",
            "content": response,
        })

        return display_text

    # ── Verificar Respuesta ───────────────────────────────────────────

    def check_answer(self, user_answer: str) -> dict[str, Any]:
        """
        Verifica la respuesta del estudiante.

        Returns
        -------
        dict
            ``{"correct": bool, "feedback": str, "event": str,
               "new_challenge": str | None}``
            Si la respuesta es correcta, ``new_challenge`` contendrá el texto
            de la continuación automática de la historia (que ya incluye un
            nuevo desafío). Si es None, no se generó continuación.
        """
        if not self._challenge_active:
            return {
                "correct": False,
                "feedback": "🎲 No hay un desafío activo. Pulsa «Nueva Clase» para comenzar.",
                "event": "",
                "new_challenge": None,
            }

        # Verificar con SymPy
        is_correct = False
        if self._current_expected:
            is_correct = self.validator.check_user_answer(
                user_answer, self._current_expected
            )

        # Generar feedback narrativo con el LLM
        messages = build_answer_check_messages(
            challenge_narrative=self._current_challenge_text,
            user_answer=user_answer,
            is_correct=is_correct,
            expected_answer=self._current_expected,
            domain=self.profile.domain,
            difficulty=self.profile.level,
            conversation_history=self._conversation_history,
            theme=self._current_theme,
            topic=self._current_topic,
        )

        feedback = self.llm.generate(messages)

        # Actualizar perfil
        event = self.profile.record_answer(
            correct=is_correct,
            domain=self.profile.domain,
            expression=self._current_math_expr,
        )
        self.profile.save()

        # Guardar en historial
        self._conversation_history.append(
            {"role": "user", "content": user_answer}
        )
        self._conversation_history.append(
            {"role": "assistant", "content": feedback}
        )

        new_challenge_text = None

        if is_correct:
            # Intentar extraer nuevo desafío del feedback (la historia continúa)
            math_data = self.validator.extract_math(feedback)
            if math_data:
                self._current_math_expr, self._current_expected = math_data
                # Validar la nueva expresión
                if not self.validator.validate_expression(
                    self._current_math_expr, self._current_expected
                ):
                    logger.warning(
                        "⚠️ Nueva expresión del LLM no validada: %s = %s",
                        self._current_math_expr,
                        self._current_expected,
                    )

                # Limpiar el tag [MATH] del feedback
                if "[MATH:" in feedback:
                    lines = feedback.split("\n")
                    display_lines = [
                        ln for ln in lines
                        if not ln.strip().startswith("[MATH:")
                    ]
                    feedback = "\n".join(display_lines).strip()

                self._current_challenge_text = feedback
                self._challenge_active = True
                self._hints_used = 0
                new_challenge_text = "auto"  # Señal de que hay nuevo desafío inline
            else:
                # El LLM no generó continuación → el desafío se cierra
                self._challenge_active = False
        # Si es incorrecto, el desafío sigue activo para reintentar

        return {
            "correct": is_correct,
            "feedback": feedback,
            "event": event,
            "new_challenge": new_challenge_text,
        }

    # ── Pista ─────────────────────────────────────────────────────────

    def get_hint(self) -> str:
        """Genera una pista socrática para el desafío actual."""
        if not self._challenge_active:
            return "🎲 No hay un desafío activo. Pulsa «Nueva Clase» para comenzar."

        self._hints_used += 1

        messages = build_hint_messages(
            challenge_narrative=self._current_challenge_text,
            expected_answer=self._current_expected,
            domain=self.profile.domain,
            difficulty=self.profile.level,
            conversation_history=self._conversation_history,
            theme=self._current_theme,
            topic=self._current_topic,
        )

        hint = self.llm.generate(messages)

        self._conversation_history.append(
            {"role": "user", "content": "Necesito una pista."}
        )
        self._conversation_history.append(
            {"role": "assistant", "content": hint}
        )

        return hint

    # ── Rendirse ──────────────────────────────────────────────────────

    def give_up(self) -> str:
        """El estudiante se rinde: revelar la solución."""
        if not self._challenge_active:
            return "🎲 No hay un desafío activo."

        messages = build_give_up_messages(
            challenge_narrative=self._current_challenge_text,
            expected_answer=self._current_expected,
            math_expression=self._current_math_expr,
            domain=self.profile.domain,
            difficulty=self.profile.level,
            conversation_history=self._conversation_history,
            theme=self._current_theme,
            topic=self._current_topic,
        )

        explanation = self.llm.generate(messages)

        # Registrar como error
        event = self.profile.record_answer(
            correct=False,
            domain=self.profile.domain,
            expression=self._current_math_expr,
        )
        self.profile.save()

        self._challenge_active = False

        self._conversation_history.append(
            {"role": "user", "content": "Me rindo."}
        )
        self._conversation_history.append(
            {"role": "assistant", "content": explanation}
        )

        return explanation

    # ── Utilidades ────────────────────────────────────────────────────

    def change_domain(self, domain: str) -> None:
        """Cambia el dominio matemático activo."""
        self.profile.domain = domain
        self.profile.save()

    def change_difficulty(self, level: int) -> None:
        """Cambia el nivel de dificultad manualmente."""
        self.profile.level = max(1, min(5, level))
        self.profile.save()

    def update_name(self, name: str) -> None:
        """Actualiza el nombre del estudiante."""
        self.profile.name = name.strip() or "Aventurero"
        self.profile.save()

    def reset_session(self) -> None:
        """Reinicia la sesión de conversación (no el perfil)."""
        self._conversation_history.clear()
        self._challenge_active = False
        self._current_challenge_text = ""
        self._current_math_expr = ""
        self._current_expected = ""

    def reset_profile(self) -> None:
        """Reinicia completamente el perfil."""
        self.profile.reset()
        self.reset_session()

    def reconnect_llm(self) -> bool:
        """Reintenta conexión con Ollama o Gemini."""
        return self.llm.reconnect()
