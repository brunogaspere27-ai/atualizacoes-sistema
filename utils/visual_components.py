"""
Componentes visuais reutilizáveis para melhor apresentação.
"""

import customtkinter as ctk
from typing import Callable, Optional
from telas.theme import FONT_FAMILY


class AnimatedButton(ctk.CTkButton):
    """Botão estilizado reutilizável (animação removida — era no-op)."""

    def __init__(self, *args, **kwargs):
        # Garante defaults consistentes
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("height", 42)
        super().__init__(*args, **kwargs)


class ShadowCard(ctk.CTkFrame):
    """Card com efeito de sombra e border refinado."""

    def __init__(self, master, **kwargs):
        bg_color = kwargs.pop("bg_color", "#FFFFFF")
        border_color = kwargs.pop("border_color", "#E5E7EB")
        corner_radius = kwargs.pop("corner_radius", 16)

        super().__init__(
            master,
            fg_color=bg_color,
            corner_radius=corner_radius,
            border_width=1,
            border_color=border_color,
            **kwargs,
        )

        self.bg_color = bg_color
        self.border_color = border_color

    def bind_hover(self, on_enter: Callable, on_leave: Callable):
        """Vincula eventos de hover ao card."""
        self.bind("<Enter>", lambda e: on_enter())
        self.bind("<Leave>", lambda e: on_leave())

        for child in self.winfo_children():
            child.bind("<Enter>", lambda e: on_enter())
            child.bind("<Leave>", lambda e: on_leave())


class GradientFrame(ctk.CTkFrame):
    """Frame com efeito de gradiente (simulado com cores)."""

    def __init__(self, master, colors: list, **kwargs):
        super().__init__(master, **kwargs)

        self.colors = colors
        self._create_gradient()

    def _create_gradient(self):
        """Cria efeito de gradiente com frames."""
        if len(self.colors) < 2:
            return

        height = 1
        width = len(self.colors)

        for i, color in enumerate(self.colors):
            gradient_frame = ctk.CTkFrame(
                self,
                fg_color=color,
                height=height,
                width=1,
            )
            gradient_frame.pack(fill="x", padx=0, pady=0)


class StatCard(ctk.CTkFrame):
    """Card para exibir estatísticas com estilo."""

    def __init__(
        self,
        master,
        titulo: str,
        valor: str,
        unidade: str,
        cor: str = "#DC2626",
        card_bg: str = "#FFFFFF",
        font_family: str = FONT_FAMILY,
        **kwargs,
    ):
        super().__init__(master, fg_color=card_bg, corner_radius=14, **kwargs)

        ff = font_family

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=16)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            header,
            text=titulo,
            font=(ff, 12, "bold"),
            text_color="#64748B",
        ).pack(anchor="w")

        valor_frame = ctk.CTkFrame(container, fg_color="transparent")
        valor_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(
            valor_frame,
            text=valor,
            font=(ff, 28, "bold"),
            text_color=cor,
        ).pack(anchor="w")

        ctk.CTkLabel(
            valor_frame,
            text=unidade,
            font=(ff, 11),
            text_color="#94A3B8",
        ).pack(anchor="w", pady=(2, 0))


class ModernHeader(ctk.CTkFrame):
    """Header moderno com design refinado — usa tokens do tema."""

    def __init__(self, master, titulo: str, subtitulo: str = "", **kwargs):
        fg = kwargs.pop("fg_color", "#0F172A")
        font_family = kwargs.pop("font_family", FONT_FAMILY)
        super().__init__(master, fg_color=fg, corner_radius=0, **kwargs)

        self.pack_propagate(False)

        ff = font_family
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(
            container,
            text="🔹 SEÇÃO",
            font=(ff, 11, "bold"),
            text_color="#93C5FD",
        ).pack(anchor="w", pady=(0, 8))

        ctk.CTkLabel(
            container,
            text=titulo,
            font=(ff, 32, "bold"),
            text_color="#FFFFFF",
        ).pack(anchor="w", pady=(0, 6))

        if subtitulo:
            ctk.CTkLabel(
                container,
                text=subtitulo,
                font=(ff, 13),
                text_color="#CBD5E1",
            ).pack(anchor="w")


class SmoothProgressBar(ctk.CTkProgressBar):
    """Barra de progresso com animação suave."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.current_value = 0.0
        self.target_value = 0.0

    def set_smooth(self, value: float, steps: int = 20):
        """Define o valor com transição suave."""
        self.target_value = max(0.0, min(1.0, value))
        self.current_value = self.get()
        self._animate_progress(steps)

    def _animate_progress(self, steps: int):
        """Anima a barra de progresso."""
        if steps <= 0 or abs(self.target_value - self.current_value) < 0.001:
            self.set(self.target_value)
            return

        step_size = (self.target_value - self.current_value) / steps
        self.current_value += step_size
        self.set(self.current_value)

        self.after(15, lambda: self._animate_progress(steps - 1))
