"""
Dialog profissional de atualizacao do sistema CW Transportadora.

Features:
- Informacoes da nova versao (notas, tamanho)
- Download com barra de progresso, velocidade e ETA
- Instalacao com backup automatico
- Tratamento de erros com retry
"""

from __future__ import annotations

import threading
import time
from tkinter import messagebox
from typing import Dict, Optional

import customtkinter as ctk

from config.settings import settings
from services.update_service import update_service
from telas.theme import setup_theme
from utils.logger import get_logger

logger = get_logger(__name__)


def _formatar_tamanho(bytes_size: int) -> str:
    if bytes_size <= 0:
        return "Desconhecido"
    if bytes_size < 1024:
        return f"{bytes_size} B"
    if bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    return f"{bytes_size / (1024 * 1024):.1f} MB"


def _formatar_velocidade(bps: float) -> str:
    if bps <= 0:
        return "--"
    if bps < 1024:
        return f"{bps:.0f} B/s"
    if bps < 1024 * 1024:
        return f"{bps / 1024:.1f} KB/s"
    return f"{bps / (1024 * 1024):.1f} MB/s"


def _formatar_tempo(segundos: float) -> str:
    if segundos <= 0 or segundos > 36000:
        return "--"
    if segundos < 60:
        return f"{int(segundos)}s"
    if segundos < 3600:
        return f"{int(segundos // 60)}m {int(segundos % 60)}s"
    return f"{int(segundos // 3600)}h {int((segundos % 3600) // 60)}m"


class TelaAtualizacao(ctk.CTkToplevel):
    """Dialog modal profissional para atualizacao do sistema."""

    def __init__(self, master, resultado: Dict, on_instalar=None):
        super().__init__(master)
        self.cores = setup_theme(settings)
        self._ff = self.cores["font_family"]
        self._resultado = resultado
        self._on_instalar = on_instalar
        self._master = master
        self._downloading = False

        self.title("Atualizacao do Sistema")
        self.geometry("560x620")
        self.resizable(False, False)
        self.configure(fg_color="#F8FAFC")
        self.grab_set()

        self._criar_interface()

    def _criar_interface(self):
        r = self._resultado
        latest = r.get("latest_version", "?")
        current = r.get("current_version", "?")
        size = r.get("release_size", 0)
        notes = r.get("release_notes", "Sem informacoes disponiveis.")

        # Header
        header = ctk.CTkFrame(self, fg_color="#1E40AF", corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header, text="Nova Versao Disponivel",
            font=(self._ff, 22, "bold"), text_color="white",
        ).pack(anchor="w", padx=24, pady=(20, 4))

        ctk.CTkLabel(
            header, text=f"Versao {current} -> {latest}",
            font=(self._ff, 14), text_color="#BFDBFE",
        ).pack(anchor="w", padx=24, pady=(0, 16))

        # Info card
        info_card = ctk.CTkFrame(self, fg_color="white", corner_radius=16,
                                 border_width=1, border_color="#E5E7EB")
        info_card.pack(fill="x", padx=20, pady=(16, 8))

        row_info = ctk.CTkFrame(info_card, fg_color="transparent")
        row_info.pack(fill="x", padx=18, pady=14)

        ctk.CTkLabel(
            row_info, text=f"Tamanho: {_formatar_tamanho(size)}",
            font=(self._ff, 12, "bold"), text_color="#374151",
        ).pack(side="left")

        if r.get("release_date"):
            ctk.CTkLabel(
                row_info, text=f"Data: {r['release_date']}",
                font=(self._ff, 12), text_color="#6B7280",
            ).pack(side="right")

        # Release notes
        notes_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=16,
                                   border_width=1, border_color="#E5E7EB")
        notes_frame.pack(fill="both", expand=True, padx=20, pady=8)

        ctk.CTkLabel(
            notes_frame, text="Novidades desta versao",
            font=(self._ff, 14, "bold"), text_color="#111827",
        ).pack(anchor="w", padx=18, pady=(14, 6))

        notes_scroll = ctk.CTkTextbox(
            notes_frame, fg_color="#F9FAFB", font=(self._ff, 12),
            text_color="#374151", wrap="word", height=180,
        )
        notes_scroll.pack(fill="both", expand=True, padx=18, pady=(0, 14))
        notes_scroll.insert("1.0", notes)
        notes_scroll.configure(state="disabled")

        # Progress area (hidden initially)
        self._progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._progress_frame.pack(fill="x", padx=20, pady=(4, 0))

        self._progress_bar = ctk.CTkProgressBar(self._progress_frame, width=500, height=14)
        self._progress_bar.pack(pady=(4, 4))
        self._progress_bar.set(0)

        self._label_progress = ctk.CTkLabel(
            self._progress_frame, text="",
            font=(self._ff, 11), text_color="#6B7280",
        )
        self._label_progress.pack()

        self._label_speed = ctk.CTkLabel(
            self._progress_frame, text="",
            font=(self._ff, 11, "bold"), text_color="#374151",
        )
        self._label_speed.pack()

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(8, 16))

        self._btn_atualizar = ctk.CTkButton(
            btn_frame, text="Atualizar Agora", height=46, width=200,
            font=(self._ff, 14, "bold"),
            fg_color="#16A34A", hover_color="#15803D",
            command=self._iniciar_download,
        )
        self._btn_atualizar.pack(side="left", padx=(0, 10))

        self._btn_depois = ctk.CTkButton(
            btn_frame, text="Depois", height=46, width=120,
            font=(self._ff, 14, "bold"),
            fg_color="#6B7280", hover_color="#4B5563",
            command=self.destroy,
        )
        self._btn_depois.pack(side="left")

        self._btn_cancelar = ctk.CTkButton(
            btn_frame, text="Cancelar", height=46, width=120,
            font=(self._ff, 14, "bold"),
            fg_color="#DC2626", hover_color="#B91C1C",
            command=self.destroy,
        )

    def _iniciar_download(self):
        if self._downloading:
            return

        self._downloading = True
        self._btn_atualizar.configure(state="disabled", text="Baixando...")
        self._btn_depois.configure(state="disabled")

        download_url = self._resultado.get("download_url")
        if not download_url:
            messagebox.showerror("Erro", "URL de download nao disponivel.")
            self._downloading = False
            self._btn_atualizar.configure(state="normal", text="Atualizar Agora")
            self._btn_depois.configure(state="normal")
            return

        def _tarefa():
            def _progresso(downloaded, total, speed, eta):
                if not self.winfo_exists():
                    return
                pct = downloaded / total if total > 0 else 0
                self.after(0, lambda: self._progress_bar.set(pct))
                self.after(0, lambda: self._label_progress.configure(
                    text=f"{downloaded / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB ({pct*100:.0f}%)"
                ))
                self.after(0, lambda: self._label_speed.configure(
                    text=f"{_formatar_velocidade(speed)}  |  Tempo restante: {_formatar_tempo(eta)}"
                ))

            success, result = update_service.download_update(download_url, _progresso)

            if not self.winfo_exists():
                return

            self.after(0, lambda: self._download_concluido(success, result))

        threading.Thread(target=_tarefa, daemon=True).start()

    def _download_concluido(self, success: bool, result: str):
        self._downloading = False

        if not success:
            messagebox.showerror("Erro no Download", result)
            self._btn_atualizar.configure(state="normal", text="Tentar Novamente")
            self._btn_depois.configure(state="normal")
            self._progress_bar.set(0)
            self._label_progress.configure(text="Download falhou.")
            self._label_speed.configure(text="")
            return

        # Download OK - perguntar sobre instalacao
        self._progress_bar.set(1.0)
        self._label_progress.configure(text="Download concluido!")
        self._label_speed.configure(text="")

        if not messagebox.askyesno(
            "Download Concluido",
            "A atualizacao foi baixada com sucesso.\n\n"
            "Deseja instalar agora?\n\n"
            "O sistema sera fechado e reaberto automaticamente.\n"
            "Um backup sera criado antes da instalacao.",
        ):
            self.destroy()
            return

        # Instalar
        self._btn_atualizar.configure(state="disabled", text="Instalando...")
        self._btn_cancelar.pack_forget()
        self._label_progress.configure(text="Criando backup e instalando...")

        def _instalar():
            ok, msg = update_service.install_update(result)
            if self.winfo_exists():
                self.after(0, lambda: self._instalacao_resultado(ok, msg))

        threading.Thread(target=_instalar, daemon=True).start()

    def _instalacao_resultado(self, success: bool, msg: str):
        if success:
            messagebox.showinfo("Instalacao", msg)
            if self._on_instalar:
                self._on_instalar()
            else:
                self._master.fechar_sistema()
        else:
            messagebox.showerror("Erro na Instalacao", msg)
            self.destroy()
