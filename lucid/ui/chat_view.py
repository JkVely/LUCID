"""
LUCID – Chat View
==================
Panel de chat RPG con burbujas diferenciadas para narrador y usuario.
Incluye campo de entrada, indicador de escritura y acciones.
Soporta zoom dinámico de fuentes con theme.scaled().
"""

from __future__ import annotations

import datetime
import threading
import customtkinter as ctk

from ui import theme


class ChatView(ctk.CTkFrame):
    """Panel principal de conversación estilo chat RPG."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_send: callable = None,
        on_hint: callable = None,
        on_give_up: callable = None,
        **kwargs,
    ):
        super().__init__(master, fg_color=theme.BG_DARK, corner_radius=0, **kwargs)

        self._on_send = on_send
        self._on_hint = on_hint
        self._on_give_up = on_give_up
        self._typing_label: ctk.CTkLabel | None = None
        self._typing_frame_ref: ctk.CTkFrame | None = None
        self._typing_anim_id: str | None = None
        self._typing_dots = 0
        self._is_processing = False

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_chat_area()
        self._build_input_area()

    # ── Header ────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        s = theme.scaled
        self.header = ctk.CTkFrame(
            self, height=52, fg_color=theme.BG_DARKEST, corner_radius=0,
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(1, weight=1)

        self.header_icon = ctk.CTkLabel(
            self.header, text="🏰", font=(theme.FONT_FAMILY, s(22)),
            fg_color="transparent",
        )
        self.header_icon.grid(row=0, column=0,
                              padx=(theme.PAD_LG, theme.PAD_SM), pady=theme.PAD_SM)

        self.header_title = ctk.CTkLabel(
            self.header,
            text="LUCID — Dungeon Master Matemático",
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_LG), "bold"),
            text_color=theme.TEXT_PRIMARY,
            fg_color="transparent",
        )
        self.header_title.grid(row=0, column=1, sticky="w", pady=theme.PAD_SM)

        self.header_subtitle = ctk.CTkLabel(
            self.header,
            text="Aritmética · Nivel 1",
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_SM)),
            text_color=theme.TEXT_SECONDARY,
            fg_color="transparent",
        )
        self.header_subtitle.grid(row=0, column=2, padx=theme.PAD_LG, pady=theme.PAD_SM)

    def update_header(self, domain: str, level: int, level_name: str) -> None:
        self.header_subtitle.configure(text=f"{domain} · Nivel {level} — {level_name}")

    def update_class_info(self, theme_icon: str, theme_name: str, topic: str) -> None:
        self.header_icon.configure(text=theme_icon)
        self.header_title.configure(text=f"{theme_name} — {topic}")

    # ── Chat Area ─────────────────────────────────────────────────────

    def _build_chat_area(self) -> None:
        self.chat_area = ctk.CTkScrollableFrame(
            self,
            fg_color=theme.BG_DARK,
            corner_radius=0,
            scrollbar_button_color=theme.ACCENT_PRIMARY,
            scrollbar_button_hover_color=theme.ACCENT_HOVER,
        )
        self.chat_area.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.chat_area.grid_columnconfigure(0, weight=1)

    # ── Input Area ────────────────────────────────────────────────────

    def _build_input_area(self) -> None:
        s = theme.scaled
        self.input_frame = ctk.CTkFrame(
            self, height=110, fg_color=theme.BG_SECONDARY, corner_radius=0,
        )
        self.input_frame.grid(row=2, column=0, sticky="ew")
        self.input_frame.grid_propagate(False)
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Botones de acción
        actions = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        actions.grid(row=0, column=0, columnspan=2, sticky="ew",
                     padx=theme.PAD_LG, pady=(theme.PAD_SM, 0))

        self.hint_btn = ctk.CTkButton(
            actions,
            text=f"{theme.ICON_HINT} Pista",
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_SM)),
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.BORDER_LIGHT,
            text_color=theme.TEXT_ACCENT,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=28, width=90,
            command=self._handle_hint,
        )
        self.hint_btn.pack(side="left", padx=(0, theme.PAD_SM))

        self.give_up_btn = ctk.CTkButton(
            actions,
            text=f"{theme.ICON_GIVE_UP} Rendirse",
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_SM)),
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.ERROR_BG,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=28, width=100,
            command=self._handle_give_up,
        )
        self.give_up_btn.pack(side="left")

        # Zoom hint
        zoom_label = ctk.CTkLabel(
            actions, text="Ctrl +/- zoom",
            font=(theme.FONT_FAMILY, 9),
            text_color=theme.TEXT_MUTED, fg_color="transparent",
        )
        zoom_label.pack(side="right", padx=theme.PAD_SM)

        # Campo de entrada + botón enviar
        input_row = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        input_row.grid(row=1, column=0, columnspan=2, sticky="ew",
                       padx=theme.PAD_LG, pady=theme.PAD_SM)
        input_row.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            input_row,
            placeholder_text="Escribe tu respuesta...",
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_BASE)),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            placeholder_text_color=theme.TEXT_MUTED,
            corner_radius=theme.CORNER_RADIUS_MD,
            height=42,
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, theme.PAD_SM))
        self.entry.bind("<Return>", lambda e: self._handle_send())

        self.send_btn = ctk.CTkButton(
            input_row,
            text=theme.ICON_SEND,
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_XL)),
            fg_color=theme.ACCENT_PRIMARY,
            hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=theme.CORNER_RADIUS_MD,
            width=50, height=42,
            command=self._handle_send,
        )
        self.send_btn.grid(row=0, column=1)

    # ── Messages ──────────────────────────────────────────────────────

    def add_message(self, text: str, sender: str = "narrator") -> None:
        s = theme.scaled
        is_user = sender == "user"
        is_system = sender == "system"

        outer = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        outer.grid(sticky="ew", padx=theme.PAD_SM, pady=theme.PAD_XS)
        outer.grid_columnconfigure(0 if not is_user else 1, weight=1)

        if is_system:
            sys_label = ctk.CTkLabel(
                outer, text=text,
                font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_SM), "italic"),
                text_color=theme.ACCENT_GOLD,
                fg_color="transparent",
                wraplength=500, justify="center",
            )
            sys_label.grid(row=0, column=0, columnspan=2, pady=theme.PAD_XS)
            self._scroll_to_bottom()
            return

        if is_user:
            bg = theme.USER_BG
            icon_text = theme.ICON_USER
            border = theme.USER_BORDER
        else:
            bg = theme.NARRATOR_BG
            icon_text = theme.ICON_DM
            border = theme.NARRATOR_BORDER

        bubble = ctk.CTkFrame(
            outer, fg_color=bg, corner_radius=theme.CORNER_RADIUS_LG,
            border_width=1, border_color=border,
        )

        if is_user:
            bubble.grid(row=0, column=1, sticky="e", padx=(80, 0))
        else:
            bubble.grid(row=0, column=0, sticky="w", padx=(0, 60))

        bubble.grid_columnconfigure(1, weight=1)

        icon_label = ctk.CTkLabel(
            bubble, text=icon_text, font=(theme.FONT_FAMILY, s(20)),
            fg_color="transparent",
        )
        icon_label.grid(
            row=0, column=0, padx=(theme.PAD_MD, theme.PAD_XS),
            pady=(theme.PAD_MD, theme.PAD_XS), sticky="nw",
        )

        text_label = ctk.CTkLabel(
            bubble, text=text,
            wraplength=theme.BUBBLE_WRAP,
            justify="left",
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_BASE)),
            text_color=theme.TEXT_PRIMARY,
            fg_color="transparent", anchor="w",
        )
        text_label.grid(
            row=0, column=1,
            padx=(theme.PAD_XS, theme.PAD_LG),
            pady=(theme.PAD_MD, theme.PAD_XS),
            sticky="w",
        )

        now = datetime.datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(
            bubble, text=now,
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_XS)),
            text_color=theme.TEXT_MUTED,
            fg_color="transparent",
        )
        time_label.grid(
            row=1, column=1,
            padx=(theme.PAD_XS, theme.PAD_LG),
            pady=(0, theme.PAD_SM),
            sticky="e",
        )

        self._scroll_to_bottom()

    # ── Typing Indicator ──────────────────────────────────────────────

    def show_typing(self) -> None:
        s = theme.scaled
        self._is_processing = True

        outer = ctk.CTkFrame(self.chat_area, fg_color="transparent")
        outer.grid(sticky="ew", padx=theme.PAD_SM, pady=theme.PAD_XS)
        outer.grid_columnconfigure(1, weight=1)

        bubble = ctk.CTkFrame(
            outer, fg_color=theme.NARRATOR_BG,
            corner_radius=theme.CORNER_RADIUS_LG,
            border_width=1, border_color=theme.NARRATOR_BORDER,
        )
        bubble.grid(row=0, column=0, sticky="w", padx=(0, 60))

        icon = ctk.CTkLabel(
            bubble, text=theme.ICON_THINKING, font=(theme.FONT_FAMILY, s(20)),
            fg_color="transparent",
        )
        icon.grid(row=0, column=0,
                  padx=(theme.PAD_MD, theme.PAD_XS), pady=theme.PAD_MD)

        self._typing_label = ctk.CTkLabel(
            bubble, text="El Guardián medita",
            font=(theme.FONT_FAMILY, s(theme.FONT_SIZE_BASE), "italic"),
            text_color=theme.TEXT_ACCENT,
            fg_color="transparent",
        )
        self._typing_label.grid(
            row=0, column=1,
            padx=(theme.PAD_XS, theme.PAD_LG), pady=theme.PAD_MD,
        )

        self._typing_frame_ref = outer
        self._typing_dots = 0
        self._animate_typing()
        self._scroll_to_bottom()

    def _animate_typing(self) -> None:
        if not self._is_processing or self._typing_label is None:
            return
        dots = "." * (self._typing_dots % 4)
        try:
            self._typing_label.configure(text=f"El Guardián medita{dots}")
        except Exception:
            return
        self._typing_dots += 1
        self._typing_anim_id = self.after(500, self._animate_typing)

    def hide_typing(self) -> None:
        self._is_processing = False
        if self._typing_anim_id:
            self.after_cancel(self._typing_anim_id)
            self._typing_anim_id = None
        if self._typing_frame_ref:
            try:
                self._typing_frame_ref.destroy()
            except Exception:
                pass
            self._typing_frame_ref = None
        self._typing_label = None

    # ── Actions ───────────────────────────────────────────────────────

    def _handle_send(self) -> None:
        text = self.entry.get().strip()
        if not text or self._is_processing:
            return
        self.entry.delete(0, "end")
        if self._on_send:
            self._on_send(text)

    def _handle_hint(self) -> None:
        if self._is_processing:
            return
        if self._on_hint:
            self._on_hint()

    def _handle_give_up(self) -> None:
        if self._is_processing:
            return
        if self._on_give_up:
            self._on_give_up()

    def set_input_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.entry.configure(state=state)
        self.send_btn.configure(state=state)
        self.hint_btn.configure(state=state)
        self.give_up_btn.configure(state=state)

    def clear_chat(self) -> None:
        for widget in self.chat_area.winfo_children():
            widget.destroy()

    # ── Scroll ────────────────────────────────────────────────────────

    def _scroll_to_bottom(self) -> None:
        self.after(100, lambda: self.chat_area._parent_canvas.yview_moveto(1.0))
