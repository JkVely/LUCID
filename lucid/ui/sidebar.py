"""
LUCID – Sidebar
=================
Panel lateral con perfil del estudiante, estadísticas de progreso,
selectores de dominio/dificultad y controles del juego.
"""

from __future__ import annotations

import customtkinter as ctk

from ui import theme
from config import DOMAINS, DIFFICULTY_LEVELS, APP_NAME, APP_SUBTITLE, APP_VERSION


class Sidebar(ctk.CTkFrame):
    """Panel lateral RPG con perfil, stats y controles."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_new_challenge: callable = None,
        on_domain_change: callable = None,
        on_difficulty_change: callable = None,
        on_name_change: callable = None,
        on_reconnect: callable = None,
        on_settings: callable = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=theme.BG_SECONDARY,
            corner_radius=0,
            **kwargs,
        )

        self._on_new_challenge = on_new_challenge
        self._on_domain_change = on_domain_change
        self._on_difficulty_change = on_difficulty_change
        self._on_name_change = on_name_change
        self._on_reconnect = on_reconnect
        self._on_settings = on_settings

        self.grid_rowconfigure(6, weight=1)  # Spacer
        self.grid_columnconfigure(0, weight=1)

        self._build_logo()
        self._build_profile_card()
        self._build_domain_selector()
        self._build_difficulty_selector()
        self._build_stats_card()
        self._build_progress_bars()
        self._build_actions()
        self._build_footer()

    # ── Logo ──────────────────────────────────────────────────────────

    def _build_logo(self) -> None:
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=theme.PAD_LG,
                        pady=(theme.PAD_XL, theme.PAD_SM))

        title = ctk.CTkLabel(
            logo_frame,
            text=f"⚔  {APP_NAME}  ⚔",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_TITLE), "bold"),
            text_color=theme.ACCENT_PRIMARY,
            fg_color="transparent",
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            logo_frame,
            text=APP_SUBTITLE,
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM)),
            text_color=theme.TEXT_SECONDARY,
            fg_color="transparent",
        )
        subtitle.pack()

        # Divider
        divider = ctk.CTkFrame(self, height=1, fg_color=theme.BORDER)
        divider.grid(row=1, column=0, sticky="ew", padx=theme.PAD_LG, pady=theme.PAD_XS)

    # ── Profile Card ──────────────────────────────────────────────────

    def _build_profile_card(self) -> None:
        card = ctk.CTkFrame(
            self, fg_color=theme.BG_TERTIARY,
            corner_radius=theme.CORNER_RADIUS_MD,
        )
        card.grid(row=2, column=0, sticky="ew", padx=theme.PAD_LG, pady=theme.PAD_SM)
        card.grid_columnconfigure(1, weight=1)

        header = ctk.CTkLabel(
            card, text="🧙  Perfil",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM), "bold"),
            text_color=theme.TEXT_ACCENT,
            fg_color="transparent",
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w",
                    padx=theme.PAD_MD, pady=(theme.PAD_SM, theme.PAD_XS))

        name_label = ctk.CTkLabel(
            card, text="Nombre:",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM)),
            text_color=theme.TEXT_SECONDARY,
            fg_color="transparent",
        )
        name_label.grid(row=1, column=0, sticky="w", padx=theme.PAD_MD, pady=theme.PAD_XS)

        self.name_entry = ctk.CTkEntry(
            card,
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM)),
            fg_color=theme.BG_INPUT,
            border_color=theme.BORDER,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=28,
        )
        self.name_entry.grid(row=1, column=1, sticky="ew",
                             padx=(0, theme.PAD_MD), pady=theme.PAD_XS)
        self.name_entry.insert(0, "Aventurero")
        self.name_entry.bind("<Return>", lambda e: self._handle_name_change())
        self.name_entry.bind("<FocusOut>", lambda e: self._handle_name_change())

        self.level_label = ctk.CTkLabel(
            card,
            text="🌱  Nivel 1 — Aprendiz",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_BASE), "bold"),
            text_color=theme.ACCENT_SECONDARY,
            fg_color="transparent",
        )
        self.level_label.grid(
            row=2, column=0, columnspan=2, sticky="w",
            padx=theme.PAD_MD, pady=(theme.PAD_XS, theme.PAD_SM),
        )

    # ── Domain Selector ───────────────────────────────────────────────

    def _build_domain_selector(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=0, sticky="ew", padx=theme.PAD_LG, pady=theme.PAD_XS)

        label = ctk.CTkLabel(
            frame, text="📚  Dominio",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM), "bold"),
            text_color=theme.TEXT_ACCENT,
            fg_color="transparent",
        )
        label.pack(anchor="w")

        domain_names = list(DOMAINS.keys())
        self.domain_menu = ctk.CTkOptionMenu(
            frame,
            values=domain_names,
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM)),
            fg_color=theme.BG_TERTIARY,
            button_color=theme.ACCENT_PRIMARY,
            button_hover_color=theme.ACCENT_HOVER,
            dropdown_fg_color=theme.BG_TERTIARY,
            dropdown_hover_color=theme.ACCENT_PRIMARY,
            text_color=theme.TEXT_PRIMARY,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=32,
            command=self._handle_domain_change,
        )
        self.domain_menu.pack(fill="x", pady=(theme.PAD_XS, 0))

    # ── Difficulty Selector ───────────────────────────────────────────

    def _build_difficulty_selector(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=4, column=0, sticky="ew", padx=theme.PAD_LG, pady=theme.PAD_SM)

        self.diff_header_label = ctk.CTkLabel(
            frame, text="⚡  Dificultad: 1/5",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM), "bold"),
            text_color=theme.TEXT_ACCENT,
            fg_color="transparent",
        )
        self.diff_header_label.pack(anchor="w")

        self.difficulty_slider = ctk.CTkSlider(
            frame, from_=1, to=5, number_of_steps=4,
            fg_color=theme.BG_TERTIARY,
            progress_color=theme.ACCENT_PRIMARY,
            button_color=theme.ACCENT_SECONDARY,
            button_hover_color=theme.ACCENT_GOLD,
            height=16,
            command=self._handle_difficulty_change,
        )
        self.difficulty_slider.set(1)
        self.difficulty_slider.pack(fill="x", pady=(theme.PAD_XS, 0))

        self.diff_name_label = ctk.CTkLabel(
            frame,
            text="🌱 Aprendiz — Conceptos fundamentales",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_XS)),
            text_color=theme.TEXT_MUTED,
            fg_color="transparent",
        )
        self.diff_name_label.pack(anchor="w", pady=(2, 0))

    # ── Stats Card ────────────────────────────────────────────────────

    def _build_stats_card(self) -> None:
        card = ctk.CTkFrame(
            self, fg_color=theme.BG_TERTIARY,
            corner_radius=theme.CORNER_RADIUS_MD,
        )
        card.grid(row=5, column=0, sticky="ew", padx=theme.PAD_LG, pady=theme.PAD_SM)
        card.grid_columnconfigure(1, weight=1)

        header = ctk.CTkLabel(
            card, text="📊  Estadísticas",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM), "bold"),
            text_color=theme.TEXT_ACCENT,
            fg_color="transparent",
        )
        header.grid(row=0, column=0, columnspan=2, sticky="w",
                    padx=theme.PAD_MD, pady=(theme.PAD_SM, theme.PAD_XS))

        self._stat_streak = self._add_stat_row(card, 1, "Racha:", "0")
        self._stat_best = self._add_stat_row(card, 2, "Mejor:", "0")
        self._stat_success = self._add_stat_row(card, 3, "Éxito:", "0%")
        self._stat_total = self._add_stat_row(card, 4, "Total:", "0")

    def _add_stat_row(
        self, parent: ctk.CTkFrame, row: int, label: str, value: str,
    ) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            parent, text=label,
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM)),
            text_color=theme.TEXT_SECONDARY,
            fg_color="transparent",
        )
        lbl.grid(row=row, column=0, sticky="w", padx=theme.PAD_MD, pady=1)

        val = ctk.CTkLabel(
            parent, text=value,
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM), "bold"),
            text_color=theme.TEXT_PRIMARY,
            fg_color="transparent",
        )
        val.grid(row=row, column=1, sticky="e", padx=theme.PAD_MD, pady=1)
        return val

    # ── Progress Bars ─────────────────────────────────────────────────

    def _build_progress_bars(self) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=6, column=0, sticky="new", padx=theme.PAD_LG, pady=theme.PAD_SM)
        frame.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            frame, text="🗺️  Progreso por Dominio",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM), "bold"),
            text_color=theme.TEXT_ACCENT,
            fg_color="transparent",
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, theme.PAD_XS))

        self._progress_bars: dict[str, tuple[ctk.CTkProgressBar, ctk.CTkLabel]] = {}
        row = 1
        colors = [theme.ACCENT_PRIMARY, theme.ACCENT_SECONDARY, theme.ACCENT_GOLD]

        for i, (domain, info) in enumerate(DOMAINS.items()):
            lbl = ctk.CTkLabel(
                frame,
                text=f"{info['icon']}  {domain}",
                font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_XS)),
                text_color=theme.TEXT_SECONDARY,
                fg_color="transparent",
            )
            lbl.grid(row=row, column=0, sticky="w", pady=(theme.PAD_XS, 0))

            bar_frame = ctk.CTkFrame(frame, fg_color="transparent")
            bar_frame.grid(row=row + 1, column=0, sticky="ew", pady=(0, theme.PAD_XS))
            bar_frame.grid_columnconfigure(0, weight=1)

            bar = ctk.CTkProgressBar(
                bar_frame,
                height=theme.PROGRESS_HEIGHT,
                fg_color=theme.BG_DARKEST,
                progress_color=colors[i % len(colors)],
                corner_radius=4,
            )
            bar.set(0)
            bar.grid(row=0, column=0, sticky="ew", padx=(0, theme.PAD_SM))

            pct = ctk.CTkLabel(
                bar_frame, text="0%",
                font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_XS)),
                text_color=theme.TEXT_MUTED,
                fg_color="transparent",
                width=35,
            )
            pct.grid(row=0, column=1)

            self._progress_bars[domain] = (bar, pct)
            row += 2

    # ── Actions ───────────────────────────────────────────────────────

    def _build_actions(self) -> None:
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=7, column=0, sticky="ew", padx=theme.PAD_LG, pady=theme.PAD_SM)

        self.new_challenge_btn = ctk.CTkButton(
            actions,
            text=f"{theme.ICON_NEW}  Nueva Clase",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_BASE), "bold"),
            fg_color=theme.ACCENT_PRIMARY,
            hover_color=theme.ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=theme.CORNER_RADIUS_MD,
            height=44,
            command=self._handle_new_challenge,
        )
        self.new_challenge_btn.pack(fill="x", pady=(0, theme.PAD_XS))

        # Settings button
        settings_btn = ctk.CTkButton(
            actions,
            text=f"{theme.ICON_SETTINGS}  Configuración",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM)),
            fg_color=theme.BG_TERTIARY,
            hover_color=theme.BORDER_LIGHT,
            text_color=theme.TEXT_SECONDARY,
            corner_radius=theme.CORNER_RADIUS_SM,
            height=32,
            command=self._handle_settings,
        )
        settings_btn.pack(fill="x", pady=(0, theme.PAD_SM))

    # ── Footer ────────────────────────────────────────────────────────

    def _build_footer(self) -> None:
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=8, column=0, sticky="ew", padx=theme.PAD_LG,
                    pady=(0, theme.PAD_SM))
        footer.grid_columnconfigure(0, weight=1)

        div = ctk.CTkFrame(footer, height=1, fg_color=theme.BORDER)
        div.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, theme.PAD_SM))

        self.status_label = ctk.CTkLabel(
            footer,
            text="⚠️ Modo Demo",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_XS)),
            text_color=theme.TEXT_MUTED,
            fg_color="transparent",
        )
        self.status_label.grid(row=1, column=0, sticky="w")

        reconnect_btn = ctk.CTkButton(
            footer,
            text="🔄",
            font=(theme.FONT_FAMILY, theme.scaled(theme.FONT_SIZE_SM)),
            fg_color="transparent",
            hover_color=theme.BG_TERTIARY,
            text_color=theme.TEXT_SECONDARY,
            width=28, height=28,
            corner_radius=theme.CORNER_RADIUS_SM,
            command=self._handle_reconnect,
        )
        reconnect_btn.grid(row=1, column=1, sticky="e")

        version = ctk.CTkLabel(
            footer,
            text=f"v{APP_VERSION} · Ctrl+/- Zoom",
            font=(theme.FONT_FAMILY, 9),
            text_color=theme.TEXT_MUTED,
            fg_color="transparent",
        )
        version.grid(row=2, column=0, columnspan=2, sticky="w", pady=(2, 0))

    # ── Handlers ──────────────────────────────────────────────────────

    def _handle_new_challenge(self) -> None:
        if self._on_new_challenge:
            self._on_new_challenge()

    def _handle_domain_change(self, value: str) -> None:
        if self._on_domain_change:
            self._on_domain_change(value)

    def _handle_difficulty_change(self, value: float) -> None:
        level = int(round(value))
        info = DIFFICULTY_LEVELS.get(level, DIFFICULTY_LEVELS[1])
        self.diff_header_label.configure(text=f"⚡  Dificultad: {level}/5")
        self.diff_name_label.configure(
            text=f"{info['icon']} {info['name']} — {info['desc']}"
        )
        if self._on_difficulty_change:
            self._on_difficulty_change(level)

    def _handle_name_change(self) -> None:
        name = self.name_entry.get().strip()
        if self._on_name_change and name:
            self._on_name_change(name)

    def _handle_reconnect(self) -> None:
        if self._on_reconnect:
            self._on_reconnect()

    def _handle_settings(self) -> None:
        if self._on_settings:
            self._on_settings()

    # ── Public Update Methods ─────────────────────────────────────────

    def update_profile(
        self, name: str, level: int, streak: int, best_streak: int,
        success_rate: float, total: int,
        domain_progress: dict[str, float],
    ) -> None:
        """Actualiza todos los widgets con datos del perfil."""
        current = self.name_entry.get()
        if current != name:
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, name)

        info = DIFFICULTY_LEVELS.get(level, DIFFICULTY_LEVELS[1])
        self.level_label.configure(
            text=f"{info['icon']}  Nivel {level} — {info['name']}"
        )

        self.difficulty_slider.set(level)
        self.diff_header_label.configure(text=f"⚡  Dificultad: {level}/5")
        self.diff_name_label.configure(
            text=f"{info['icon']} {info['name']} — {info['desc']}"
        )

        self._stat_streak.configure(text=str(streak))
        self._stat_best.configure(text=str(best_streak))
        self._stat_success.configure(text=f"{success_rate:.0f}%")
        self._stat_total.configure(text=str(total))

        for domain, (bar, pct_label) in self._progress_bars.items():
            pct = domain_progress.get(domain, 0.0)
            bar.set(pct / 100.0)
            pct_label.configure(text=f"{pct:.0f}%")

    def update_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    def set_new_challenge_enabled(self, enabled: bool) -> None:
        self.new_challenge_btn.configure(state="normal" if enabled else "disabled")
