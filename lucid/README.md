# LUCID – Prototipo Funcional

**Large-language-model Unified Curriculum Intelligent Designer**

Framework de IA Generativa para la Gamificación Matemática Adaptativa.

## Stack Tecnológico

| Componente | Tecnología |
|---|---|
| Motor LLM | **Gemma 4** (vía Ollama local) |
| Validación | **SymPy** (oráculo simbólico) |
| Interfaz | **CustomTkinter** (tema RPG oscuro) |
| Gestión deps | **uv** |

## Requisitos Previos

1. **Python 3.11+**
2. **uv** — Gestor de paquetes ultrarrápido
   ```bash
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
3. **Ollama** *(opcional, para IA real)*
   - Descargar de [ollama.com](https://ollama.com)
   - Descargar el modelo:
     ```bash
     ollama pull gemma4:e4b
     ```

> **Nota:** Sin Ollama, la app funciona en **modo demo** con retos pregenerados.

## Instalación y Ejecución

```bash
# Desde la raíz del proyecto, entrar al directorio del código
cd lucid

# Instalar dependencias (automático con uv)
uv sync

# Ejecutar la aplicación
uv run python main.py
```

## Estructura del Proyecto

```
lucid/
├── main.py              # Punto de entrada
├── config.py            # Configuración central
├── pyproject.toml       # Manifiesto del proyecto (uv)
├── engine/              # Motor del sistema
│   ├── llm_client.py    # Cliente Ollama (Gemma 4)
│   ├── orchestrator.py  # Orquestador del juego
│   ├── profile.py       # Perfil adaptativo del estudiante
│   ├── prompts.py       # Templates del Dungeon Master
│   └── validator.py     # Validación simbólica (SymPy)
├── ui/                  # Interfaz gráfica
│   ├── app.py           # Ventana principal
│   ├── chat_view.py     # Panel de chat RPG
│   ├── sidebar.py       # Panel lateral (perfil + stats)
│   └── theme.py         # Tema visual RPG oscuro
└── data/                # Persistencia local
    └── student_profile.json
```

## Uso

1. **Selecciona un dominio** (Aritmética, Álgebra, Geometría) en el panel lateral
2. **Ajusta la dificultad** con el slider (1-5)
3. **Pulsa "Nuevo Reto"** para generar un desafío narrativo
4. **Escribe tu respuesta** en el campo de texto y pulsa Enter
5. El sistema valida tu respuesta y te da feedback narrativo
6. Usa **"Pista"** si necesitas ayuda o **"Rendirse"** para ver la solución

## Licencia

MIT — Proyecto académico, Universidad Distrital Francisco José de Caldas.
