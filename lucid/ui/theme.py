"""
LUCID – Tema Visual RPG
========================
Paleta de colores, tipografía y constantes de estilo
para la interfaz de fantasía oscura.
Soporta escalado dinámico de fuentes con Ctrl+/-.
"""

# ── Font Scale ────────────────────────────────────────────────────────
# Offset global sumado a todos los tamaños de fuente (Ctrl+/- lo modifica)
_font_scale_offset: int = 0

def get_font_scale() -> int:
    return _font_scale_offset

def set_font_scale(offset: int) -> None:
    global _font_scale_offset
    _font_scale_offset = max(-4, min(8, offset))

def scaled(size: int) -> int:
    """Retorna el tamaño de fuente escalado."""
    return max(8, size + _font_scale_offset)

# ── Backgrounds ───────────────────────────────────────────────────────
BG_DARKEST   = "#080B12"   # Fondo más profundo (header)
BG_DARK      = "#0B0E14"   # Fondo principal del chat
BG_SECONDARY = "#111621"   # Sidebar y paneles
BG_TERTIARY  = "#1A1F2E"   # Cards y secciones
BG_INPUT     = "#151A27"   # Campo de entrada

# ── Accent Colors ─────────────────────────────────────────────────────
ACCENT_PRIMARY    = "#8B5CF6"   # Violeta mágico
ACCENT_HOVER      = "#A78BFA"   # Violeta claro (hover)
ACCENT_SECONDARY  = "#06D6A0"   # Esmeralda cristal
ACCENT_GOLD       = "#FFD700"   # Oro (logros)
ACCENT_CYAN       = "#22D3EE"   # Cyan brillante

# ── Message Bubbles ───────────────────────────────────────────────────
NARRATOR_BG       = "#1B1040"   # Púrpura oscuro para el DM
NARRATOR_BORDER   = "#2D1B69"   # Borde de burbuja narrador
USER_BG           = "#0E2A3D"   # Cyan oscuro para el usuario
USER_BORDER       = "#164E63"   # Borde de burbuja usuario

# ── Text ──────────────────────────────────────────────────────────────
TEXT_PRIMARY   = "#E8EDF5"   # Texto principal (off-white)
TEXT_SECONDARY = "#8B949E"   # Texto secundario
TEXT_MUTED     = "#484F58"   # Texto atenuado
TEXT_ACCENT    = "#C4B5FD"   # Texto con acento violeta

# ── Semantic Colors ───────────────────────────────────────────────────
SUCCESS    = "#22C55E"
SUCCESS_BG = "#0A2E1A"
ERROR      = "#EF4444"
ERROR_BG   = "#2E0A0A"
WARNING    = "#F59E0B"

# ── Borders & Separators ─────────────────────────────────────────────
BORDER       = "#2A2F3E"
BORDER_LIGHT = "#363D4F"

# ── Typography ────────────────────────────────────────────────────────
FONT_FAMILY       = "Segoe UI"
FONT_MONO         = "Cascadia Code"
FONT_SIZE_XS      = 10
FONT_SIZE_SM      = 11
FONT_SIZE_BASE    = 13
FONT_SIZE_LG      = 15
FONT_SIZE_XL      = 18
FONT_SIZE_2XL     = 22
FONT_SIZE_TITLE   = 28
FONT_SIZE_HERO    = 42

# ── Spacing ───────────────────────────────────────────────────────────
PAD_XS  = 4
PAD_SM  = 8
PAD_MD  = 12
PAD_LG  = 16
PAD_XL  = 24
PAD_2XL = 32

# ── Widget Dimensions ────────────────────────────────────────────────
CORNER_RADIUS_SM  = 6
CORNER_RADIUS_MD  = 10
CORNER_RADIUS_LG  = 16
CORNER_RADIUS_XL  = 20
BUBBLE_WRAP       = 440    # Ancho de wrapping de burbuja de chat
PROGRESS_HEIGHT   = 8

# ── Icons / Emojis ────────────────────────────────────────────────────
ICON_DM       = "🐉"
ICON_USER     = "⚔️"
ICON_HINT     = "💡"
ICON_GIVE_UP  = "🏳️"
ICON_NEW      = "🎲"
ICON_SEND     = "➤"
ICON_SUCCESS  = "✨"
ICON_ERROR    = "💥"
ICON_THINKING = "🔮"
ICON_CROWN    = "👑"
ICON_SHIELD   = "🛡️"
ICON_SETTINGS = "⚙️"
ICON_ZOOM_IN  = "🔍+"
ICON_ZOOM_OUT = "🔍-"
