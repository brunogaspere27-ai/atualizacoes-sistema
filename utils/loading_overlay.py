"""
Utilitário para overlay de carregamento em telas CustomTkinter.
"""

import customtkinter as ctk


class LoadingOverlay(ctk.CTkFrame):
    """Overlay de carregamento com spinner e mensagem."""

    def __init__(self, parent, message: str = "Carregando..."):
        super().__init__(
            parent,
            fg_color="#374151",
            corner_radius=0,
        )

        self.spinner = None
        self.label = None

        self.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.lift()
        self.grab_set()

        container = ctk.CTkFrame(
            self,
            fg_color="#1F2937",
            corner_radius=16,
            width=300,
            height=150,
        )
        container.place(relx=0.5, rely=0.5, anchor="center")

        self.spinner = ctk.CTkProgressBar(
            container,
            width=200,
            height=8,
            mode="indeterminate",
        )
        self.spinner.place(relx=0.5, rely=0.4, anchor="center")
        self.spinner.start()

        self.label = ctk.CTkLabel(
            container,
            text=message,
            font=("Arial", 14),
            text_color="#FFFFFF",
        )
        self.label.place(relx=0.5, rely=0.65, anchor="center")

    def set_message(self, message: str):
        """Atualiza a mensagem de carregamento."""
        if self.label is not None:
            self.label.configure(text=message)

    def destroy(self):
        """Para o spinner e remove o overlay."""
        if self.spinner is not None:
            try:
                self.spinner.stop()
            except Exception:
                pass
        super().destroy()


def show_loading(parent, message: str = "Carregando...") -> LoadingOverlay:
    """
    Mostra overlay de carregamento.

    Args:
        parent: Widget pai
        message: Mensagem a exibir

    Returns:
        Instância do LoadingOverlay
    """
    return LoadingOverlay(parent, message)


class LoadingButton(ctk.CTkButton):
    """Botão que mostra estado de carregamento."""

    def __init__(self, *args, **kwargs):
        self.original_text = kwargs.get("text", "")
        self.original_command = kwargs.get("command", None)
        self.is_loading = False

        super().__init__(*args, **kwargs)

    def set_loading(self, loading: bool, message: str = "Carregando..."):
        """
        Define estado de carregamento.

        Args:
            loading: Se está carregando
            message: Mensagem quando carregando
        """
        self.is_loading = loading

        if loading:
            self.configure(
                text=message,
                state="disabled",
                fg_color="#6B7280",
            )
        else:
            self.configure(
                text=self.original_text,
                state="normal",
                fg_color=self._fg_color,
            )

    def enable(self):
        """Habilita o botão."""
        self.set_loading(False)

    def disable(self):
        """Desabilita o botão."""
        self.set_loading(True)
