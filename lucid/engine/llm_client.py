"""
LUCID – Cliente LLM (Ollama + Gemini Fallback)
================================================
Comunicación con el servidor Ollama local para inferencia con Gemma 4.
Si Ollama no está disponible, usa la API de Google Gemini como fallback.
Incluye modo demo de respaldo final.
"""

from __future__ import annotations

import logging
from typing import Any

from config import (
    OLLAMA_MODEL, OLLAMA_HOST,
    LLM_TEMPERATURE, LLM_MAX_TOKENS, LLM_TOP_P,
    GEMINI_API_KEY, GEMINI_MODEL,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
#  DEMO CHALLENGES (fallback cuando ni Ollama ni Gemini están disponibles)
# ═══════════════════════════════════════════════════════════════════════

_DEMO_CHALLENGES: list[dict[str, str]] = [
    {
        "domain": "Aritmética",
        "text": (
            "🏰 Las Puertas de Calculia se alzan ante ti, cubiertas de runas doradas.\n\n"
            "El guardián de piedra despierta y te observa con ojos de cristal:\n\n"
            "«Viajero, tres mercaderes cruzaron hoy estas puertas. El primero llevaba "
            "24 monedas de oro, el segundo el doble que el primero, y el tercero "
            "la mitad de lo que llevaban los dos primeros juntos. "
            "¿Cuántas monedas de oro pasaron en total por mis puertas?»\n\n"
            "El guardián cruza sus brazos de granito, esperando tu respuesta.\n\n"
            "[MATH: 24 + (24*2) + (24 + 24*2)/2 = 108]"
        ),
    },
    {
        "domain": "Álgebra",
        "text": (
            "📜 En la Biblioteca Arcana de Numeralia, descubres un pergamino misterioso.\n\n"
            "La bibliotecaria, una elfa de cabello plateado, te susurra:\n\n"
            "«Este pergamino contiene un enigma ancestral: existe un número mágico. "
            "Si lo multiplicas por 3 y le sumas 12, obtienes exactamente 45. "
            "Descubre el número mágico y el pergamino revelará sus secretos.»\n\n"
            "La elfa te observa con una media sonrisa, confiando en tu ingenio.\n\n"
            "[MATH: 3*x + 12 = 45 -> x = 11]"
        ),
    },
    {
        "domain": "Geometría",
        "text": (
            "🗡️ En la Forja del Dragón, el herrero enano Thorin te ofrece un trato:\n\n"
            "«¡Necesito tu ayuda, aventurero! Debo cubrir con láminas de acero "
            "un escudo rectangular que mide 8 unidades de largo por 5 de ancho. "
            "Pero en el centro tiene un agujero circular de radio 1 unidad "
            "para la empuñadura. ¿Cuánta área de acero necesito? "
            "Usa 3.14 para el valor de pi.»\n\n"
            "El calor de la forja te envuelve mientras calculas mentalmente.\n\n"
            "[MATH: (8*5) - (3.14 * 1**2) = 36.86]"
        ),
    },
    {
        "domain": "Aritmética",
        "text": (
            "🌙 En la Posada del Cuervo Sabio, un anciano misterioso te reta:\n\n"
            "«Joven viajero, escucha bien: tengo una bolsa con gemas. "
            "Si reparto las gemas entre 7 aventureros, a cada uno le tocan 13 gemas "
            "y me sobran 4. ¿Cuántas gemas tengo en mi bolsa?»\n\n"
            "El anciano acaricia su barba blanca, esperando.\n\n"
            "[MATH: 7 * 13 + 4 = 95]"
        ),
    },
    {
        "domain": "Álgebra",
        "text": (
            "⚗️ En el Laboratorio de la Alquimista, las pociones burbujean.\n\n"
            "«Para crear el Elixir de la Sabiduría necesito combinar ingredientes.» "
            "dice la alquimista. «Si al triple de gotas de esencia lunar le resto 7, "
            "obtengo el mismo resultado que sumar 20 gotas de rocío estelar. "
            "¿Cuántas gotas de esencia lunar necesito exactamente?»\n\n"
            "Los frascos brillan con luz propia mientras reflexionas.\n\n"
            "[MATH: 3*x - 7 = 20 -> x = 9]"
        ),
    },
]

_DEMO_CORRECT = (
    "✨ ¡MAGNÍFICO, aventurero! ¡Tu respuesta es CORRECTA!\n\n"
    "Las runas del portal se iluminan con un resplandor dorado, "
    "reconociendo tu dominio sobre los números. "
    "Has demostrado verdadera comprensión al resolver este enigma.\n\n"
    "🌟 Tu poder crece con cada desafío superado. ¡Adelante!"
)

_DEMO_INCORRECT = (
    "🌀 Hmm... el portal parpadea y se oscurece. Esa no es la respuesta correcta, "
    "pero no te rindas.\n\n"
    "Piensa en esto: ¿has considerado todas las partes del problema? "
    "A veces, un enigma esconde pasos intermedios. "
    "Vuelve a leer el desafío con calma y descomponlo en partes más pequeñas.\n\n"
    "💡 Cada intento es un paso hacia la sabiduría."
)

_DEMO_HINT = (
    "💡 El Guardián del Saber se inclina y te susurra al oído:\n\n"
    "«No intentes resolverlo todo de golpe, joven. "
    "Divide el problema... ¿qué operaciones necesitas hacer paso a paso? "
    "Empieza por lo que conoces con certeza y avanza desde ahí.»\n\n"
    "El eco de sus palabras resuena en la sala, iluminando tu camino."
)

_DEMO_GIVE_UP = (
    "🏳️ El Guardián asiente comprensivamente:\n\n"
    "«No hay vergüenza en reconocer un obstáculo, aventurero. "
    "Déjame mostrarte el camino...\n\n"
    "La clave estaba en descomponer el problema paso a paso.»\n\n"
    "📖 Recuerda: cada derrota es una lección. La próxima vez, este tipo de "
    "desafío será más familiar para ti."
)


class LLMClient:
    """
    Cliente LLM con cadena de fallback:  Ollama → Gemini API → Demo.

    Intenta conectar con Ollama primero. Si no está disponible,
    intenta usar la API de Google Gemini. Si tampoco está disponible,
    cae al modo demo con retos hardcodeados.
    """

    def __init__(self, model: str = OLLAMA_MODEL, host: str = OLLAMA_HOST):
        self.model = model
        self.host = host
        self._ollama = None
        self._ollama_available = False
        self._gemini_model = None
        self._gemini_available = False
        self._backend = "demo"  # "ollama" | "gemini" | "demo"
        self._demo_index = 0
        self._connect()

    def _connect(self) -> None:
        """Intenta conectar con Ollama, luego Gemini como fallback."""
        # 1. Intentar Ollama
        self._try_ollama()
        if self._ollama_available:
            self._backend = "ollama"
            return

        # 2. Intentar Gemini
        self._try_gemini()
        if self._gemini_available:
            self._backend = "gemini"
            return

        # 3. Modo demo
        self._backend = "demo"
        logger.warning("⚠️  Ni Ollama ni Gemini disponibles — Modo DEMO activo.")

    def _try_ollama(self) -> None:
        """Intenta conectar con Ollama."""
        try:
            import ollama
            self._ollama = ollama.Client(host=self.host)
            models = self._ollama.list()
            model_names = [m.model for m in models.models] if models.models else []
            model_base = self.model.split(":")[0]
            self._ollama_available = any(model_base in name for name in model_names)
            if not self._ollama_available:
                logger.warning(
                    "Modelo '%s' no encontrado en Ollama. "
                    "Modelos disponibles: %s.",
                    self.model, model_names,
                )
            else:
                logger.info("✅ Conectado a Ollama con modelo: %s", self.model)
        except Exception as e:
            logger.warning("⚠️  No se pudo conectar a Ollama: %s", e)
            self._ollama_available = False

    def _try_gemini(self) -> None:
        """Intenta configurar la API de Google Gemini."""
        if not GEMINI_API_KEY:
            logger.info("No hay GEMINI_API_KEY configurada. Saltando Gemini.")
            self._gemini_available = False
            return
        try:
            from google import generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            self._gemini_model = genai.GenerativeModel(
                GEMINI_MODEL,
                generation_config=genai.GenerationConfig(
                    temperature=LLM_TEMPERATURE,
                    max_output_tokens=LLM_MAX_TOKENS,
                    top_p=LLM_TOP_P,
                ),
            )
            # Test rápido: verificar que el modelo responde
            self._gemini_available = True
            logger.info("✅ Gemini API configurada con modelo: %s", GEMINI_MODEL)
        except Exception as e:
            logger.warning("⚠️  No se pudo configurar Gemini: %s", e)
            self._gemini_available = False

    @property
    def is_available(self) -> bool:
        """``True`` si algún LLM real (Ollama o Gemini) está disponible."""
        return self._backend in ("ollama", "gemini")

    @property
    def status_text(self) -> str:
        """Texto descriptivo del estado de conexión."""
        if self._backend == "ollama":
            return f"✅ {self.model}"
        elif self._backend == "gemini":
            return f"✅ Gemini ({GEMINI_MODEL})"
        return "⚠️ Modo Demo"

    def generate(self, messages: list[dict[str, str]]) -> str:
        """
        Genera una respuesta usando la cadena de fallback.

        Parameters
        ----------
        messages : list[dict]
            Lista de mensajes con ``role`` y ``content``.

        Returns
        -------
        str
            Texto generado.
        """
        # 1. Intentar Ollama
        if self._backend == "ollama" and self._ollama is not None:
            try:
                response = self._ollama.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        "temperature": LLM_TEMPERATURE,
                        "num_predict": LLM_MAX_TOKENS,
                        "top_p": LLM_TOP_P,
                    },
                )
                return response["message"]["content"]
            except Exception as e:
                logger.error("Error en Ollama, intentando Gemini: %s", e)
                # Fallback a Gemini si Ollama falla durante runtime
                if self._gemini_available:
                    return self._generate_gemini(messages)

        # 2. Intentar Gemini
        if self._backend == "gemini" or (
            self._gemini_available and self._backend != "demo"
        ):
            try:
                return self._generate_gemini(messages)
            except Exception as e:
                logger.error("Error en Gemini: %s", e)

        # 3. Modo DEMO
        return self._demo_fallback(messages)

    def _generate_gemini(self, messages: list[dict[str, str]]) -> str:
        """Genera respuesta usando la API de Google Gemini."""
        if self._gemini_model is None:
            raise RuntimeError("Gemini no está configurado")

        # Convertir formato OpenAI/Ollama → Gemini
        # Gemini usa 'user' y 'model' como roles, y el system prompt
        # se pasa como system_instruction o como primer mensaje.
        gemini_contents = []
        system_text = ""

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            if role == "system":
                # Acumular system prompts como contexto
                system_text += content + "\n\n"
            elif role == "user":
                gemini_contents.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_contents.append({"role": "model", "parts": [content]})

        # Si hay system prompt, inyectarlo como primer mensaje de usuario
        # con prefijo para que Gemini lo trate como instrucciones
        if system_text and gemini_contents:
            # Prepend system instructions al primer mensaje de usuario
            first_user_idx = None
            for i, c in enumerate(gemini_contents):
                if c["role"] == "user":
                    first_user_idx = i
                    break
            if first_user_idx is not None:
                original = gemini_contents[first_user_idx]["parts"][0]
                gemini_contents[first_user_idx]["parts"][0] = (
                    f"[INSTRUCCIONES DEL SISTEMA]\n{system_text}\n"
                    f"[FIN INSTRUCCIONES]\n\n{original}"
                )
        elif system_text:
            gemini_contents.append({
                "role": "user",
                "parts": [system_text],
            })

        # Asegurar que la conversación alterna user/model correctamente
        # Gemini requiere alternancia estricta
        fixed_contents = self._fix_gemini_turns(gemini_contents)

        response = self._gemini_model.generate_content(fixed_contents)
        return response.text

    @staticmethod
    def _fix_gemini_turns(contents: list[dict]) -> list[dict]:
        """
        Asegura que los turnos alternen entre user y model.
        Gemini requiere alternancia estricta.
        """
        if not contents:
            return contents

        fixed = [contents[0]]
        for msg in contents[1:]:
            if msg["role"] == fixed[-1]["role"]:
                # Mismo rol consecutivo → fusionar
                fixed[-1]["parts"].extend(msg["parts"])
            else:
                fixed.append(msg)

        # Asegurar que el último mensaje sea de user
        if fixed and fixed[-1]["role"] == "model":
            fixed.append({"role": "user", "parts": ["Continúa."]})

        return fixed

    def _demo_fallback(self, messages: list[dict[str, str]]) -> str:
        """Genera respuestas de demo según el contexto."""
        last_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"].lower()
                break

        if "nuevo desafío" in last_user_msg or "genera" in last_user_msg or "nueva clase" in last_user_msg:
            challenge = _DEMO_CHALLENGES[self._demo_index % len(_DEMO_CHALLENGES)]
            self._demo_index += 1
            return challenge["text"]
        elif "correcto" in last_user_msg or "respuesta" in last_user_msg:
            for msg in reversed(messages):
                if msg["role"] == "system" and "CORRECTA" in msg["content"]:
                    return _DEMO_CORRECT
                elif msg["role"] == "system" and "INCORRECTA" in msg["content"]:
                    return _DEMO_INCORRECT
            return _DEMO_INCORRECT
        elif "pista" in last_user_msg:
            return _DEMO_HINT
        elif "rindo" in last_user_msg:
            return _DEMO_GIVE_UP
        else:
            challenge = _DEMO_CHALLENGES[self._demo_index % len(_DEMO_CHALLENGES)]
            self._demo_index += 1
            return challenge["text"]

    def reconnect(self) -> bool:
        """Reintenta la conexión con Ollama o Gemini."""
        self._connect()
        return self.is_available
