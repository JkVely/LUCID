"""
LUCID – Validación Matemática Simbólica
=========================================
Usa SymPy para verificar la corrección de expresiones y respuestas.
Actúa como "oráculo de verdad" determinista.
"""

import re
from sympy import sympify, simplify, N, SympifyError


# Patrón para extraer la línea [MATH: expresión = resultado]
_MATH_TAG_RE = re.compile(
    r"\[MATH:\s*(.+?)\s*=\s*(.+?)\s*\]",
    re.IGNORECASE,
)


class MathValidator:
    """Oráculo de validación simbólica con SymPy."""

    @staticmethod
    def extract_math(llm_response: str) -> tuple[str, str] | None:
        """
        Extrae la expresión y resultado esperado de la respuesta del LLM.

        Parameters
        ----------
        llm_response : str
            Texto completo generado por el LLM.

        Returns
        -------
        tuple[str, str] | None
            ``(expression, expected_result)`` o ``None`` si no se encontró.
        """
        match = _MATH_TAG_RE.search(llm_response)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None

    @staticmethod
    def validate_expression(expression: str, expected_result: str) -> bool:
        """
        Verifica que ``expression`` evalúe a ``expected_result``.

        Returns
        -------
        bool
            ``True`` si la expresión es matemáticamente correcta.
        """
        try:
            expr_val = sympify(expression)
            result_val = sympify(expected_result)
            return bool(simplify(expr_val - result_val) == 0)
        except (SympifyError, TypeError, ValueError):
            # Fallback: comparación numérica
            try:
                expr_num = float(N(sympify(expression)))
                result_num = float(expected_result)
                return abs(expr_num - result_num) < 1e-6
            except Exception:
                return False

    @staticmethod
    def check_user_answer(user_answer: str, expected_result: str) -> bool:
        """
        Compara la respuesta del estudiante con el resultado esperado.

        Intenta comparación simbólica primero, luego numérica, y finalmente
        una comparación textual como fallback.

        Parameters
        ----------
        user_answer : str
            Respuesta escrita por el estudiante.
        expected_result : str
            Resultado correcto extraído del tag [MATH].

        Returns
        -------
        bool
            ``True`` si la respuesta es correcta.
        """
        # Limpieza básica
        user_clean = user_answer.strip().replace(",", ".").replace(" ", "")
        expected_clean = expected_result.strip().replace(",", ".").replace(" ", "")

        # 1. Comparación textual directa
        if user_clean == expected_clean:
            return True

        # 2. Comparación simbólica con SymPy
        try:
            user_val = sympify(user_clean)
            expected_val = sympify(expected_clean)
            if simplify(user_val - expected_val) == 0:
                return True
        except (SympifyError, TypeError, ValueError):
            pass

        # 3. Comparación numérica (tolerancia)
        try:
            user_num = float(user_clean)
            expected_num = float(expected_clean)
            return abs(user_num - expected_num) < 1e-6
        except (ValueError, TypeError):
            pass

        return False

    @staticmethod
    def is_solvable(expression: str) -> bool:
        """Verifica que la expresión sea evaluable (el reto es resoluble)."""
        try:
            result = sympify(expression)
            _ = float(N(result))
            return True
        except Exception:
            return False
