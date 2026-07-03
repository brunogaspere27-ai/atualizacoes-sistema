"""
Splash screen profissional para inicialização do sistema.
"""

import customtkinter as ctk
from PIL import Image
import os


class SplashScreen(ctk.CTkToplevel):
    """Tela de splash elegante com animação de carregamento."""

    def __init__(self, parent, logo_path: str = None):
        super().__init__(parent)

        self.title("CW Transportadora")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Centralizar na tela
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.configure(fg_color="#0F172A")
        self.attributes("-topmost", True)
        self.grab_set()

        # Background com gradiente simulado
        bg_frame = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        bg_frame.pack(fill="both", expand=True)

        # Container central
        container = ctk.CTkFrame(bg_frame, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=60)

        # Logo ou título
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image.open(logo_path)
                logo.thumbnail((200, 120), Image.Resampling.LANCZOS)
                photo = ctk.CTkImage(light_image=logo, dark_image=logo, size=(200, 120))
                logo_label = ctk.CTkLabel(container, image=photo, text="")
                logo_label.pack(pady=(20, 10))
            except Exception:
                pass

        # Título
        ctk.CTkLabel(
            container,
            text="CW TRANSPORTADORA",
            font=("Arial", 36, "bold"),
            text_color="#FFFFFF",
        ).pack(pady=(10, 5))

        # Subtítulo
        ctk.CTkLabel(
            container,
            text="Sistema de Gestão Logística V6",
            font=("Arial", 14),
            text_color="#93C5FD",
        ).pack(pady=(0, 30))

        # Barra de progresso
        self.progress = ctk.CTkProgressBar(
            container,
            width=280,
            height=8,
            mode="indeterminate",
        )
        self.progress.pack(pady=20)
        self.progress.start()

        # Status text
        self.status_label = ctk.CTkLabel(
            container,
            text="Inicializando...",
            font=("Arial", 12),
            text_color="#CBD5E1",
        )
        self.status_label.pack(pady=(15, 0))

        # Rodapé
        ctk.CTkLabel(
            container,
            text="© 2026 CW Transportadora - Todos os direitos reservados",
            font=("Arial", 9),
            text_color="#64748B",
        ).pack(side="bottom", pady=10)

    def update_status(self, message: str):
        """Atualiza a mensagem de status."""
        if self.status_label.winfo_exists():
            self.status_label.configure(text=message)
            self.update_idletasks()

    def close(self):
        """Fecha o splash screen."""
        if self.progress.winfo_exists():
            self.progress.stop()
        self.destroy()
