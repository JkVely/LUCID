"""
LUCID – Ventana Principal
==========================
Ensambla la UI completa y conecta las callbacks entre sidebar, chat y engine.
Incluye:
  - Diálogo de bienvenida al inicio (nombre, temática, tema, dificultad)
  - Zoom con Ctrl+/- para accesibilidad
  - Diálogo de configuración avanzada (API personalizada)
"""

from __future__ import annotations

import threading
import customtkinter as ctk

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, SIDEBAR_WIDTH, APP_NAME, APP_VERSION,
    NARRATIVE_THEMES, DIFFICULTY_LEVELS, DOMAINS,
    load_settings, save_settings,
)
from engine.orchestrator import GameOrchestrator
from engine.prompts import WELCOME_MESSAGE
from ui import theme
from ui.chat_view import ChatView
from ui.sidebar import Sidebar


# ══════════════════════════════════════════════════════════════════════
#  WELCOME DIALOG – Se muestra al iniciar la app
# ══════════════════════════════════════════════════════════════════════

class WelcomeDialog(ctk.CTkToplevel):
    """Diálogo de bienvenida con configuración inicial de clase."""

    def __init__(self, master: ctk.CTk, current_name: str = "Aventurero",
                 on_start: callable = None):
        super().__init__(master)

        self.title("LUCID — ¡Bienvenido!")
        self.geometry("600x700")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_DARKEST)

        self.transient(master)
        self.grab_set()
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 600) // 2
        y = master.winfo_y() + (master.winfo_height() - 700) // 2
        self.geometry(f"+{x}+{y}")

        self._on_start = on_start
        self._selected_theme: str = ""
        self._selected_difficulty: int = 1

        # Prevent closing without starting
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self._build_ui(current_name)

    def _build_ui(self, current_name: str) -> None:
        # ── Scrollable content ────────────────────────────────────────
        scroll = ctk.CTkScrollableFrame(
            self, fg_color="transparent",
            scrollbar_button_color=theme.ACCENT_PRIMARY,
        )
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        # ── Hero Banner ───────────────────────────────────────────────
        banner = ctk.CTkFrame(scroll, fg_color=theme.BG_SECONDARY, corner_radius=0,
                              height=160)
        banner.pack(fill="x")
        banner.pack_propagate(False)

        glow_line = ctk.CTkFrame(banner, height=3, fg_color=theme.ACCENT_PRIMARY,
                                 corner_radius=0)
        glow_line.pack(fill="x", side="top")

        hero_icon = ctk.CTkLabel(
            banner, text="⚔ 🐉 ⚔",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_HERO),
            text_color=theme.ACCENT_PRIMARY,
        )
        hero_icon.pack(pady=(theme.PAD_LG, theme.PAD_XS))

        hero_title = ctk.CTkLabel(
            banner, text="L U C I D",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_HERO, "bold"),
            text_color=theme.TEXT_PRIMARY,
        )
        hero_title.pack()

        hero_sub = ctk.CTkLabel(
            banner, text="Dungeon Master Matemático  ·  v" + APP_VERSION,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM),
            text_color=theme.TEXT_SECONDARY,
        )
        hero_sub.pack(pady=(0, theme.PAD_SM))

        glow_line2 = ctk.CTkFrame(banner, height=2,
                                  fg_color=theme.ACCENT_SECONDARY, corner_radius=0)
        glow_line2.pack(fill="x", side="bottom")

        # ── Container ────────────────────────────────────────────────
        container = ctk.CTkFrame(scroll, fg_color="transparent")
        container.pack(fill="x", padx=theme.PAD_2XL, pady=theme.PAD_LG)

        # ── 1. Nombre ─────────────────────────────────────────────────
        self._section_label(container, "👤  ¿Cómo te llamas, aventurero?")

        self.name_entry = ctk.CTkEntry(
            container,
            placeholder_text="Escribe tu nombre...",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_LG),
            fg_color=theme.BG_TERTIARY,
            border_color=theme.ACCENT_PRIMARY,
            border_width=2,
            text_color=theme.TEXT_PRIMARY,
            placeholder_text_color=theme.TEXT_MUTED,
            corner_radius=theme.CORNER_RADIUS_MD,
            height=44,
        )
        self.name_entry.pack(fill="x", pady=(theme.PAD_XS, theme.PAD_LG))
        if current_name and current_name != "Aventurero":
            self.name_entry.insert(0, current_name)

        # ── 2. Temática Narrativa ────────────────────────────────────
        self._section_label(container, "🎭  Elige tu mundo narrativo")

        themes_frame = ctk.CTkFrame(
            container, fg_color="transparent",
        )
        themes_frame.pack(fill="x", pady=(theme.PAD_XS, theme.PAD_LG))

        self._theme_buttons: dict[str, ctk.CTkButton] = {}
        # 2 columns grid
        themes_frame.grid_columnconfigure(0, weight=1)
        themes_frame.grid_columnconfigure(1, weight=1)

        for i, (key, info) in enumerate(NARRATIVE_THEMES.items()):
            row = i // 2
            col = i % 2
            btn = ctk.CTkButton(
                themes_frame,
                text=f"{info['icon']}\n{key}",
                font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM, "bold"),
                fg_color=theme.BG_TERTIARY,
                hover_color=theme.ACCENT_PRIMARY,
                text_color=theme.TEXT_PRIMARY,
                corner_radius=theme.CORNER_RADIUS_MD,
                height=70,
                border_width=2,
                border_color=theme.BORDER,
                command=lambda k=key: self._select_theme(k),
            )
            btn.grid(row=row, column=col, padx=theme.PAD_XS,
                     pady=theme.PAD_XS, sticky="ew")
            self._theme_buttons[key] = btn

        # Default theme
        first_key = list(NARRATIVE_THEMES.keys())[0]
        self._select_theme(first_key)

        # ── 3. Tema Matemático ────────────────────────────────────────
        self._section_label(container, "🎯  ¿Qué tema quieres practicar?")

        self.topic_entry = ctk.CTkEntry(
            container,
            placeholder_text="Ej: división de decimales, fracciones, ecuaciones...",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BASE),
            fg_color=theme.BG_TERTIARY,
            border_color=theme.ACCENT_SECONDARY,
            border_width=2,
            text_color=theme.TEXT_PRIMARY,
            placeholder_text_color=theme.TEXT_MUTED,
            corner_radius=theme.CORNER_RADIUS_MD,
            height=40,
        )
        self.topic_entry.pack(fill="x", pady=(theme.PAD_XS, theme.PAD_LG))

        # ── 4. Dificultad ─────────────────────────────────────────────
        self._section_label(container, "⚡  Nivel de dificultad")

        diff_frame = ctk.CTkFrame(container, fg_color="transparent")
        diff_frame.pack(fill="x", pady=(theme.PAD_XS, 0))
        diff_frame.grid_columnconfigure(0, weight=1)

        self.diff_slider = ctk.CTkSlider(
            diff_frame, from_=1, to=5, number_of_steps=4,
            fg_color=theme.BG_TERTIARY,
            progress_color=theme.ACCENT_PRIMARY,
            button_color=theme.ACCENT_SECONDARY,
            button_hover_color=theme.ACCENT_GOLD,
            height=18,
            command=self._on_diff_slide,
        )
        self.diff_slider.set(1)
        self.diff_slider.pack(fill="x")

        self.diff_label = ctk.CTkLabel(
            diff_frame,
            text="🌱  Aprendiz — Conceptos fundamentales",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM),
            text_color=theme.TEXT_ACCENT,
        )
        self.diff_label.pack(anchor="w", pady=(theme.PAD_XS, theme.PAD_LG))

        # ── 5. Botón COMENZAR ─────────────────────────────────────────
        self.start_btn = ctk.CTkButton(
            container,
            text="🚀  ¡COMENZAR AVENTURA!",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_XL, "bold"),
            fg_color=theme.ACCENT_PRIMARY,
            hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=theme.CORNER_RADIUS_LG,
            height=54,
            border_width=2,
            border_color=theme.ACCENT_HOVER,
            command=self._on_start_click,
        )
        self.start_btn.pack(fill="x", pady=(theme.PAD_SM, theme.PAD_SM))

        # Settings link
        settings_link = ctk.CTkButton(
            container,
            text="⚙️  Configuración avanzada (API personalizada)",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM),
            fg_color="transparent",
            hover_color=theme.BG_TERTIARY,
            text_color=theme.TEXT_MUTED,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=30,
            command=lambda: SettingsDialog(self),
        )
        settings_link.pack(pady=(0, theme.PAD_LG))

        # Focus name entry
        self.after(200, lambda: self.name_entry.focus_set())

    def _section_label(self, parent, text: str) -> None:
        lbl = ctk.CTkLabel(
            parent, text=text,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BASE, "bold"),
            text_color=theme.TEXT_ACCENT, anchor="w",
        )
        lbl.pack(anchor="w", pady=(theme.PAD_SM, 0))

    def _select_theme(self, key: str) -> None:
        self._selected_theme = key
        for k, btn in self._theme_buttons.items():
            if k == key:
                btn.configure(
                    fg_color=theme.ACCENT_PRIMARY,
                    text_color="#FFFFFF",
                    border_color=theme.ACCENT_GOLD,
                )
            else:
                btn.configure(
                    fg_color=theme.BG_TERTIARY,
                    text_color=theme.TEXT_PRIMARY,
                    border_color=theme.BORDER,
                )

    def _on_diff_slide(self, val: float) -> None:
        level = int(round(val))
        self._selected_difficulty = level
        info = DIFFICULTY_LEVELS.get(level, DIFFICULTY_LEVELS[1])
        self.diff_label.configure(
            text=f"{info['icon']}  {info['name']} — {info['desc']}"
        )

    def _on_start_click(self) -> None:
        name = self.name_entry.get().strip() or "Aventurero"
        topic = self.topic_entry.get().strip()

        if not topic:
            self.topic_entry.configure(border_color=theme.ERROR)
            self.topic_entry.configure(
                placeholder_text="⚠️ Escribe un tema matemático para comenzar..."
            )
            return

        if self._on_start:
            self._on_start(
                name,
                self._selected_theme,
                topic,
                self._selected_difficulty,
            )
        self.destroy()


# ══════════════════════════════════════════════════════════════════════
#  SETTINGS DIALOG – Configuración de API personalizada
# ══════════════════════════════════════════════════════════════════════

class SettingsDialog(ctk.CTkToplevel):
    """Diálogo de configuración avanzada."""

    def __init__(self, master):
        super().__init__(master)

        self.title("⚙️ Configuración – LUCID")
        self.geometry("480x460")
        self.resizable(False, False)
        self.configure(fg_color=theme.BG_SECONDARY)

        self.transient(master)
        self.grab_set()
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - 480) // 2
        y = master.winfo_y() + (master.winfo_height() - 460) // 2
        self.geometry(f"+{x}+{y}")

        self._settings = load_settings()
        self._build_ui()

    def _build_ui(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=theme.PAD_XL, pady=theme.PAD_LG)

        # Title
        title = ctk.CTkLabel(
            container,
            text="⚙️  Configuración Avanzada",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_2XL, "bold"),
            text_color=theme.ACCENT_PRIMARY,
        )
        title.pack(pady=(0, theme.PAD_LG))

        # ── Backend preference ────────────────────────────────────────
        self._section(container, "🤖  Backend LLM preferido")

        self.backend_menu = ctk.CTkOptionMenu(
            container,
            values=["auto", "ollama", "gemini", "custom"],
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM),
            fg_color=theme.BG_TERTIARY,
            button_color=theme.ACCENT_PRIMARY,
            button_hover_color=theme.ACCENT_HOVER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=34,
        )
        self.backend_menu.set(self._settings.get("preferred_backend", "auto"))
        self.backend_menu.pack(fill="x", pady=(theme.PAD_XS, theme.PAD_MD))

        # ── Custom API ────────────────────────────────────────────────
        self._section(container, "🔑  API Key personalizada")

        self.api_key_entry = ctk.CTkEntry(
            container,
            placeholder_text="sk-... o AIzaSy...",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM),
            fg_color=theme.BG_TERTIARY, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY, show="•",
            corner_radius=theme.CORNER_RADIUS_SM, height=34,
        )
        self.api_key_entry.pack(fill="x", pady=(theme.PAD_XS, theme.PAD_MD))
        if self._settings.get("custom_api_key"):
            self.api_key_entry.insert(0, self._settings["custom_api_key"])

        self._section(container, "📝  Nombre del modelo")

        self.model_entry = ctk.CTkEntry(
            container,
            placeholder_text="Ej: gemini-3.0-flash, gpt-4o-mini...",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM),
            fg_color=theme.BG_TERTIARY, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.CORNER_RADIUS_SM, height=34,
        )
        self.model_entry.pack(fill="x", pady=(theme.PAD_XS, theme.PAD_MD))
        if self._settings.get("custom_model"):
            self.model_entry.insert(0, self._settings["custom_model"])

        self._section(container, "🌐  Endpoint (URL base)")

        self.endpoint_entry = ctk.CTkEntry(
            container,
            placeholder_text="Ej: https://generativelanguage.googleapis.com",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM),
            fg_color=theme.BG_TERTIARY, border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.CORNER_RADIUS_SM, height=34,
        )
        self.endpoint_entry.pack(fill="x", pady=(theme.PAD_XS, theme.PAD_LG))
        if self._settings.get("custom_endpoint"):
            self.endpoint_entry.insert(0, self._settings["custom_endpoint"])

        # ── Buttons ───────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x")

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾  Guardar",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BASE, "bold"),
            fg_color=theme.ACCENT_PRIMARY, hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF", corner_radius=theme.CORNER_RADIUS_MD,
            height=40,
            command=self._save,
        )
        save_btn.pack(side="left", expand=True, fill="x", padx=(0, theme.PAD_SM))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_BASE),
            fg_color=theme.BG_TERTIARY, hover_color=theme.BORDER_LIGHT,
            text_color=theme.TEXT_SECONDARY, corner_radius=theme.CORNER_RADIUS_MD,
            height=40,
            command=self.destroy,
        )
        cancel_btn.pack(side="right", expand=True, fill="x")

    def _section(self, parent, text: str) -> None:
        lbl = ctk.CTkLabel(
            parent, text=text,
            font=(theme.FONT_FAMILY, theme.FONT_SIZE_SM, "bold"),
            text_color=theme.TEXT_ACCENT, anchor="w",
        )
        lbl.pack(anchor="w")

    def _save(self) -> None:
        self._settings["preferred_backend"] = self.backend_menu.get()
        self._settings["custom_api_key"] = self.api_key_entry.get().strip()
        self._settings["custom_model"] = self.model_entry.get().strip()
        self._settings["custom_endpoint"] = self.endpoint_entry.get().strip()
        save_settings(self._settings)
        self.destroy()


# ══════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════

class LucidApp(ctk.CTk):
    """Ventana raíz de la aplicación LUCID."""

    def __init__(self) -> None:
        super().__init__()

        # ── Window Config ─────────────────────────────────────────────
        self.title(f"{APP_NAME} — Dungeon Master Matemático")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(900, 600)
        self.configure(fg_color=theme.BG_DARK)

        # Centrar ventana
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y = (self.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        # ── Load settings ─────────────────────────────────────────────
        self._settings = load_settings()
        theme.set_font_scale(self._settings.get("font_scale", 0))

        # ── Engine ────────────────────────────────────────────────────
        self.engine = GameOrchestrator()

        # ── Layout ────────────────────────────────────────────────────
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)   # sidebar fijo
        self.grid_columnconfigure(1, weight=1)    # chat se expande

        # Sidebar
        self.sidebar = Sidebar(
            self,
            width=SIDEBAR_WIDTH,
            on_new_challenge=self._on_new_class,
            on_domain_change=self._on_domain_change,
            on_difficulty_change=self._on_difficulty_change,
            on_name_change=self._on_name_change,
            on_reconnect=self._on_reconnect,
            on_settings=self._on_settings,
        )
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        # Chat
        self.chat = ChatView(
            self,
            on_send=self._on_send,
            on_hint=self._on_hint,
            on_give_up=self._on_give_up,
        )
        self.chat.grid(row=0, column=1, sticky="nsew")

        # ── Keyboard Bindings (Zoom) ──────────────────────────────────
        self.bind("<Control-plus>", lambda e: self._zoom(1))
        self.bind("<Control-equal>", lambda e: self._zoom(1))
        self.bind("<Control-minus>", lambda e: self._zoom(-1))
        self.bind("<Control-0>", lambda e: self._zoom_reset())
        # Numpad + and -
        self.bind("<Control-KP_Add>", lambda e: self._zoom(1))
        self.bind("<Control-KP_Subtract>", lambda e: self._zoom(-1))

        # ── Initial State ─────────────────────────────────────────────
        self._refresh_ui()
        self.sidebar.update_status(self.engine.llm_status)

        # Show welcome dialog on startup
        self.after(300, self._show_welcome)

    # ══════════════════════════════════════════════════════════════════
    #  ZOOM
    # ══════════════════════════════════════════════════════════════════

    def _zoom(self, delta: int) -> None:
        """Incrementa o decrementa el zoom de fuentes."""
        current = theme.get_font_scale()
        theme.set_font_scale(current + delta)
        self._settings["font_scale"] = theme.get_font_scale()
        save_settings(self._settings)
        self._rebuild_chat_fonts()
        self.chat.add_message(
            f"🔍 Zoom: {'+' if theme.get_font_scale() >= 0 else ''}"
            f"{theme.get_font_scale()} (Ctrl+0 para resetear)",
            sender="system",
        )

    def _zoom_reset(self) -> None:
        """Resetea el zoom a 0."""
        theme.set_font_scale(0)
        self._settings["font_scale"] = 0
        save_settings(self._settings)
        self._rebuild_chat_fonts()
        self.chat.add_message("🔍 Zoom reseteado", sender="system")

    def _rebuild_chat_fonts(self) -> None:
        """Reconstruye la fuente del entry y futuros mensajes."""
        s = theme.scaled
        self.chat.entry.configure(
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_BASE))
        )

    # ══════════════════════════════════════════════════════════════════
    #  WELCOME DIALOG
    # ══════════════════════════════════════════════════════════════════

    def _show_welcome(self) -> None:
        """Muestra el diálogo de bienvenida al iniciar."""
        WelcomeDialog(
            self,
            current_name=self.engine.profile.name,
            on_start=self._on_welcome_start,
        )

    def _on_welcome_start(self, name: str, theme_key: str, topic: str,
                          difficulty: int) -> None:
        """Callback del diálogo de bienvenida."""
        # Actualizar nombre
        self.engine.update_name(name)
        # Actualizar dificultad
        self.engine.change_difficulty(difficulty)
        # Iniciar clase
        self._start_class(theme_key, topic)

    # ══════════════════════════════════════════════════════════════════
    #  CALLBACKS
    # ══════════════════════════════════════════════════════════════════

    def _on_new_class(self) -> None:
        """Abre el diálogo de configuración de nueva clase."""
        WelcomeDialog(
            self,
            current_name=self.engine.profile.name,
            on_start=self._on_welcome_start,
        )

    def _start_class(self, theme_key: str, topic: str) -> None:
        """Inicia la clase con la temática y tema seleccionados."""
        self.engine.start_class(theme_key, topic)

        # Actualizar header con info de la clase
        theme_info = NARRATIVE_THEMES.get(theme_key, {})
        theme_icon = theme_info.get("icon", "📚")
        self.chat.update_class_info(theme_icon, theme_key, topic)

        # Limpiar chat previo
        self.chat.clear_chat()

        # Mensaje de inicio de clase
        self.chat.add_message(
            f"📚 ¡Nueva clase iniciada!\n\n"
            f"🎭 Temática: {theme_icon} {theme_key}\n"
            f"🎯 Tema: {topic}\n\n"
            f"Preparando tu primera aventura...",
            sender="system",
        )

        self._refresh_ui()
        self._generate_challenge()

    def _generate_challenge(self) -> None:
        """Genera un nuevo desafío en un hilo de fondo."""
        self._set_processing(True)
        self.chat.show_typing()

        def _run():
            text = self.engine.generate_challenge()
            self.after(0, lambda: self._show_challenge(text))

        threading.Thread(target=_run, daemon=True).start()

    def _show_challenge(self, text: str) -> None:
        self.chat.hide_typing()
        self.chat.add_message(text, sender="narrator")
        self._set_processing(False)
        self._refresh_ui()

    def _on_send(self, text: str) -> None:
        """El usuario envía una respuesta."""
        if not self.engine.has_active_challenge:
            self.chat.add_message(text, sender="user")
            self.chat.add_message(
                "🎲 No hay un desafío activo. Pulsa «Nueva Clase» para comenzar.",
                sender="system",
            )
            return

        self.chat.add_message(text, sender="user")
        self._set_processing(True)
        self.chat.show_typing()

        def _run():
            result = self.engine.check_answer(text)
            self.after(0, lambda: self._show_feedback(result))

        threading.Thread(target=_run, daemon=True).start()

    def _show_feedback(self, result: dict) -> None:
        self.chat.hide_typing()
        self.chat.add_message(result["feedback"], sender="narrator")

        event = result.get("event", "")
        if event == "level_up":
            self.chat.add_message(
                f"🌟 ¡SUBISTE DE NIVEL! Ahora eres: "
                f"{self.engine.profile.level_icon} {self.engine.profile.level_name}",
                sender="system",
            )
        elif event == "level_down":
            self.chat.add_message(
                f"📉 Nivel ajustado a: "
                f"{self.engine.profile.level_icon} {self.engine.profile.level_name}. "
                f"¡No te rindas!",
                sender="system",
            )

        self._set_processing(False)
        self._refresh_ui()

        # Auto-avance si fue correcto pero el LLM no generó nuevo desafío inline
        if result["correct"] and result.get("new_challenge") is None:
            self.chat.add_message(
                "✨ ¡Excelente! Preparando el siguiente desafío...",
                sender="system",
            )
            self.after(2000, self._generate_challenge)

    def _on_hint(self) -> None:
        if not self.engine.has_active_challenge:
            self.chat.add_message(
                "🎲 Primero inicia una clase con «Nueva Clase».",
                sender="system",
            )
            return

        self._set_processing(True)
        self.chat.show_typing()

        def _run():
            hint = self.engine.get_hint()
            self.after(0, lambda: self._show_hint(hint))

        threading.Thread(target=_run, daemon=True).start()

    def _show_hint(self, hint: str) -> None:
        self.chat.hide_typing()
        self.chat.add_message(hint, sender="narrator")
        self._set_processing(False)

    def _on_give_up(self) -> None:
        if not self.engine.has_active_challenge:
            self.chat.add_message(
                "🎲 No hay un desafío activo del cual rendirse.",
                sender="system",
            )
            return

        self._set_processing(True)
        self.chat.show_typing()

        def _run():
            explanation = self.engine.give_up()
            self.after(0, lambda: self._show_give_up(explanation))

        threading.Thread(target=_run, daemon=True).start()

    def _show_give_up(self, explanation: str) -> None:
        self.chat.hide_typing()
        self.chat.add_message(explanation, sender="narrator")
        self._set_processing(False)
        self._refresh_ui()

    def _on_domain_change(self, domain: str) -> None:
        self.engine.change_domain(domain)
        self._refresh_ui()

    def _on_difficulty_change(self, level: int) -> None:
        self.engine.change_difficulty(level)
        self._refresh_ui()

    def _on_name_change(self, name: str) -> None:
        self.engine.update_name(name)

    def _on_reconnect(self) -> None:
        ok = self.engine.reconnect_llm()
        self.sidebar.update_status(self.engine.llm_status)
        if ok:
            self.chat.add_message(
                f"✅ Conexión restaurada: {self.engine.llm_status}",
                sender="system",
            )
        else:
            self.chat.add_message(
                "⚠️ No se pudo conectar. Verifica Ollama o tu conexión.",
                sender="system",
            )

    def _on_settings(self) -> None:
        """Abre el diálogo de configuración."""
        SettingsDialog(self)

    # ══════════════════════════════════════════════════════════════════
    #  UI HELPERS
    # ══════════════════════════════════════════════════════════════════

    def _refresh_ui(self) -> None:
        p = self.engine.profile
        self.sidebar.update_profile(
            name=p.name,
            level=p.level,
            streak=p.current_streak,
            best_streak=p.best_streak,
            success_rate=p.success_rate,
            total=p.challenges_played,
            domain_progress=p.domain_progress,
        )
        self.chat.update_header(p.domain, p.level, p.level_name)

    def _set_processing(self, processing: bool) -> None:
        self.chat.set_input_enabled(not processing)
        self.sidebar.set_new_challenge_enabled(not processing)
