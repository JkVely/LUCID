"""
LUCID – Prompt Templates
=========================
System prompts y templates dinámicos para el Dungeon Master pedagógico.
Cada función construye un prompt contextualizado con el perfil del estudiante
y la temática narrativa seleccionada.
"""

from config import DIFFICULTY_LEVELS, DOMAINS, NARRATIVE_THEMES


# ═══════════════════════════════════════════════════════════════════════
#  SYSTEM PROMPT – Personalidad del Dungeon Master (parametrizable)
# ═══════════════════════════════════════════════════════════════════════

def build_system_prompt(theme_key: str = "Medieval / Fantasía", topic: str = "") -> str:
    """
    Construye el system prompt adaptado a la temática y tema elegidos.

    Parameters
    ----------
    theme_key : str
        Clave del dict NARRATIVE_THEMES.
    topic : str
        Tema matemático específico (ej. "división de decimales").
    """
    theme = NARRATIVE_THEMES.get(theme_key, list(NARRATIVE_THEMES.values())[0])
    dm_name = theme["dm_name"]
    setting = theme["setting"]

    topic_block = ""
    if topic:
        topic_block = f"""

══════════════════════════════
  TEMA MATEMÁTICO DE LA CLASE
══════════════════════════════
El estudiante ha elegido estudiar: **{topic}**
Todos los desafíos de esta clase DEBEN estar relacionados con este tema.
Integra problemas de "{topic}" de forma orgánica en la narrativa.
No te desvíes a otros tipos de problemas a menos que sea necesario
como contexto para el tema principal.\
"""

    return f"""\
Eres **{dm_name}**, el guía narrativo en {setting}

Actúas como Dungeon Master (DM) pedagógico para estudiantes adolescentes.

══════════════════════════════
  PERSONALIDAD Y TONO
══════════════════════════════
• Sabio, misterioso y carismático, con un toque humorístico accesible.
• Usas un lenguaje narrativo épico pero comprensible para jóvenes de 13-17 años.
• Mantén total coherencia con la ambientación: {theme_key}.
• Eres paciente y empático: nunca ridiculizas un error.
• Celebras los logros con entusiasmo narrativo.
• Ante errores, guías con preguntas socráticas —NUNCA das la respuesta directa.

══════════════════════════════
  REGLAS PARA GENERAR DESAFÍOS
══════════════════════════════
1. Crea una micro-narrativa de 2-3 párrafos ambientada en el mundo de la temática.
2. El problema matemático debe estar INTEGRADO orgánicamente en la historia \
(no simplemente "resuelve X").
3. El desafío debe exigir RAZONAMIENTO, no memorización de fórmulas.
4. Incluye personajes, lugares o situaciones inmersivas del mundo.
5. AL FINAL de tu respuesta, incluye EXACTAMENTE una línea con el formato:
   [MATH: expresión_matemática = resultado_numérico]
   Ejemplo: [MATH: (15 * 3) + 27 = 72]

══════════════════════════════
  REGLAS PARA RESPONDER
══════════════════════════════
• Si el estudiante ACIERTA:
  → Celebración narrativa BREVE (1 párrafo).
  → Explica el concepto subyacente en 1-2 oraciones.
  → INMEDIATAMENTE después, CONTINÚA LA HISTORIA presentando un NUEVO desafío \
matemático del mismo tema, como parte natural de la narrativa.
  → El nuevo desafío debe incluir su línea [MATH: expresión = resultado] al final.

• Si el estudiante FALLA:
  → NO reveles la respuesta bajo NINGUNA circunstancia.
  → Describe narrativamente el obstáculo (1 párrafo corto).
  → Guía al estudiante con los PASOS que debería seguir para resolver el problema:
    1. ¿Qué datos tienes? Identifícalos.
    2. ¿Qué operación o relación necesitas?
    3. ¿Cómo puedes verificar tu resultado?
  → Formula preguntas socráticas que iluminen el camino sin dar la solución.
  → Anima al estudiante a intentar de nuevo.

• Si pide PISTA → Analogía narrativa que guíe el razonamiento paso a paso.

• Si se RINDE → Revela la solución con explicación paso a paso dentro de la narrativa.
{topic_block}

══════════════════════════════
  IMPORTANTE
══════════════════════════════
- Responde SIEMPRE en español.
- No uses LaTeX ni formato markdown con fórmulas.
- Mantén las expresiones matemáticas en texto plano legible.
- Sé conciso: no superes 250 palabras por respuesta.
- CADA respuesta a un acierto DEBE incluir la continuación de la historia \
con un nuevo desafío y su tag [MATH].\
"""


# ═══════════════════════════════════════════════════════════════════════
#  CONTEXT INJECTION – Estado actual del estudiante
# ═══════════════════════════════════════════════════════════════════════

_CONTEXT_TEMPLATE = """\
══ CONTEXTO DEL ESTUDIANTE ══
• Dominio activo: {domain} — {domain_desc}
• Nivel de dificultad: {difficulty}/5 ({difficulty_name} {difficulty_icon})
• Racha actual de aciertos: {streak}
• Tasa de éxito global: {success_rate:.0f}%
• Errores recientes: {recent_errors}
═════════════════════════════\
"""


def build_context(
    domain: str,
    difficulty: int,
    streak: int = 0,
    success_rate: float = 0.0,
    recent_errors: str = "ninguno registrado",
) -> str:
    """Construye el bloque de contexto inyectable en el prompt."""
    diff_info = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS[1])
    domain_info = DOMAINS.get(domain, list(DOMAINS.values())[0])

    return _CONTEXT_TEMPLATE.format(
        domain=domain,
        domain_desc=domain_info["description"],
        difficulty=difficulty,
        difficulty_name=diff_info["name"],
        difficulty_icon=diff_info["icon"],
        streak=streak,
        success_rate=success_rate,
        recent_errors=recent_errors,
    )


# ═══════════════════════════════════════════════════════════════════════
#  PROMPT BUILDERS
# ═══════════════════════════════════════════════════════════════════════

def build_challenge_messages(
    domain: str,
    difficulty: int,
    streak: int = 0,
    success_rate: float = 0.0,
    recent_errors: str = "ninguno registrado",
    conversation_history: list[dict] | None = None,
    theme: str = "Medieval / Fantasía",
    topic: str = "",
) -> list[dict]:
    """
    Construye la lista completa de mensajes para generar un nuevo desafío.

    Returns
    -------
    list[dict]
        Lista de mensajes con roles ``system``, ``assistant``, ``user``.
    """
    context = build_context(domain, difficulty, streak, success_rate, recent_errors)
    system_msg = build_system_prompt(theme, topic) + "\n\n" + context

    messages: list[dict] = [{"role": "system", "content": system_msg}]

    # Incluir historial si existe (para coherencia narrativa)
    if conversation_history:
        messages.extend(conversation_history[-10:])  # Últimos 10 mensajes

    topic_instruction = ""
    if topic:
        topic_instruction = f" sobre el tema «{topic}»"

    messages.append({
        "role": "user",
        "content": (
            f"Genera un nuevo desafío matemático de {domain}{topic_instruction} "
            f"(nivel {difficulty} — {DIFFICULTY_LEVELS[difficulty]['name']}). "
            "Recuerda integrar el problema en una narrativa inmersiva "
            "y finalizar con la línea [MATH: expresión = resultado]."
        ),
    })

    return messages


def build_answer_check_messages(
    challenge_narrative: str,
    user_answer: str,
    is_correct: bool,
    expected_answer: str,
    domain: str,
    difficulty: int,
    conversation_history: list[dict] | None = None,
    theme: str = "Medieval / Fantasía",
    topic: str = "",
) -> list[dict]:
    """Construye mensajes para que el LLM genere feedback narrativo."""
    context = build_context(domain, difficulty)
    system_msg = build_system_prompt(theme, topic) + "\n\n" + context

    messages: list[dict] = [{"role": "system", "content": system_msg}]

    if conversation_history:
        messages.extend(conversation_history[-10:])

    if is_correct:
        messages.append({
            "role": "user",
            "content": (
                f"Mi respuesta al desafío es: {user_answer}. "
                "¿Es correcto?"
            ),
        })
        messages.append({
            "role": "system",
            "content": (
                f"[INTERNO - No revelar] La respuesta ES CORRECTA. "
                f"Genera una celebración narrativa BREVE y explica el concepto "
                f"matemático subyacente en 1-2 oraciones. "
                f"INMEDIATAMENTE después, CONTINÚA LA HISTORIA con un NUEVO "
                f"desafío matemático integrado en la narrativa. "
                f"El nuevo desafío DEBE incluir su línea [MATH: expresión = resultado] al final."
            ),
        })
    else:
        messages.append({
            "role": "user",
            "content": (
                f"Mi respuesta al desafío es: {user_answer}. "
                "¿Es correcto?"
            ),
        })
        messages.append({
            "role": "system",
            "content": (
                f"[INTERNO - No revelar] La respuesta es INCORRECTA "
                f"(la correcta es {expected_answer}). "
                f"NO reveles la respuesta bajo ninguna circunstancia. "
                f"Describe el obstáculo narrativamente (breve). "
                f"Luego, guía al estudiante explicando los PASOS que debería seguir: "
                f"1) identificar los datos del problema, "
                f"2) determinar qué operación necesita, "
                f"3) ejecutar el cálculo paso a paso. "
                f"Haz preguntas socráticas que iluminen el camino. "
                f"Anímalo a intentar de nuevo."
            ),
        })

    return messages


def build_hint_messages(
    challenge_narrative: str,
    expected_answer: str,
    domain: str,
    difficulty: int,
    conversation_history: list[dict] | None = None,
    theme: str = "Medieval / Fantasía",
    topic: str = "",
) -> list[dict]:
    """Construye mensajes para generar una pista socrática."""
    context = build_context(domain, difficulty)
    system_msg = build_system_prompt(theme, topic) + "\n\n" + context

    messages: list[dict] = [{"role": "system", "content": system_msg}]

    if conversation_history:
        messages.extend(conversation_history[-10:])

    messages.append({
        "role": "user",
        "content": "Necesito una pista para resolver este desafío. ¿Puedes ayudarme?",
    })
    messages.append({
        "role": "system",
        "content": (
            f"[INTERNO] El estudiante pide ayuda. La respuesta correcta es {expected_answer}. "
            f"Da una pista narrativa socrática que ilumine el camino sin revelar la respuesta. "
            f"Sugiere los pasos que debería seguir para resolver el problema."
        ),
    })

    return messages


def build_give_up_messages(
    challenge_narrative: str,
    expected_answer: str,
    math_expression: str,
    domain: str,
    difficulty: int,
    conversation_history: list[dict] | None = None,
    theme: str = "Medieval / Fantasía",
    topic: str = "",
) -> list[dict]:
    """Construye mensajes para cuando el estudiante se rinde."""
    context = build_context(domain, difficulty)
    system_msg = build_system_prompt(theme, topic) + "\n\n" + context

    messages: list[dict] = [{"role": "system", "content": system_msg}]

    if conversation_history:
        messages.extend(conversation_history[-10:])

    messages.append({
        "role": "user",
        "content": "Me rindo. ¿Cuál era la respuesta?",
    })
    messages.append({
        "role": "system",
        "content": (
            f"[INTERNO] El estudiante se rinde. La expresión era: {math_expression} "
            f"y la respuesta es {expected_answer}. "
            f"Revela la solución dentro de la narrativa con una explicación "
            f"paso a paso comprensible. Sé empático y motivador."
        ),
    })

    return messages


# ═══════════════════════════════════════════════════════════════════════
#  WELCOME MESSAGE (estático, no requiere LLM)
# ═══════════════════════════════════════════════════════════════════════

WELCOME_MESSAGE = """\
⚔️  ¡Bienvenido a LUCID, joven aventurero!

Soy tu guía en un mundo donde las matemáticas cobran vida \
a través de historias inmersivas y desafíos narrativos.

Aquí no buscaremos atajos ni fórmulas vacías — solo la \
comprensión verdadera te permitirá avanzar en tu aventura.

🎲  Pulsa «Nueva Clase» para elegir tu temática y tema \
matemático, y comenzar tu odisea personalizada.

¡Que la lógica te acompañe!  🧙‍♂️\
"""
