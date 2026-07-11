"""
Tela de historico de versoes do CW Transportadora.

Exibe versao instalada, ultima atualizacao e lista de releases anteriores.
"""

from __future__ import annotations

import threading
from tkinter import messagebox

import customtkinter as ctk

from config.settings import settings
from services.update_service import update_service
from telas.theme import setup_theme
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaHistoricoVersoes(ctk.CTkFrame):
    """Tela com historico de versoes do sistema."""

    def __init__(self, master):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])
        self._ff = self.cores["font_family"]
        self._criar_layout()
        self._carregar_dados()

    def _criar_layout(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="#1E293B", corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)

        ctk.CTkLabel(
            header, text="HISTORICO DE VERSOES",
            font=(self._ff, 22, "bold"), text_color="white",
        ).pack(anchor="w", padx=24, pady=(18, 4))

        ctk.CTkLabel(
            header, text="Informacoes de atualizacoes e releases do sistema",
            font=(self._ff, 12), text_color="#94A3B8",
        ).pack(anchor="w", padx=24, pady=(0, 14))

        # Container scrollavel
        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True, padx=20, pady=12)

        # Card versao atual
        self._card_atual = ctk.CTkFrame(
            self._scroll, fg_color="white", corner_radius=16,
            border_width=1, border_color="#E5E7EB",
        )
        self._card_atual.pack(fill="x", pady=(0, 12))

        self._label_versao = ctk.CTkLabel(
            self._card_atual, text="Versao instalada: carregando...",
            font=(self._ff, 16, "bold"), text_color="#111827",
        )
        self._label_versao.pack(anchor="w", padx=22, pady=(16, 4))

        self._label_data = ctk.CTkLabel(
            self._card_atual, text="",
            font=(self._ff, 12), text_color="#6B7280",
        )
        self._label_data.pack(anchor="w", padx=22, pady=(0, 14))

        # Botao verificar agora
        btn_frame = ctk.CTkFrame(self._card_atual, fg_color="transparent")
        btn_frame.pack(fill="x", padx=22, pady=(0, 16))

        ctk.CTkButton(
            btn_frame, text="Verificar Atualizacoes", height=40, width=200,
            font=(self._ff, 13, "bold"),
            fg_color="#2563EB", hover_color="#1D4ED8",
            command=self._verificar_agora,
        ).pack(side="left")

        self._label_status = ctk.CTkLabel(
            btn_frame, text="",
            font=(self._ff, 12), text_color="#6B7280",
        )
        self._label_status.pack(side="left", padx=16)

        # Loading label
        self._label_loading = ctk.CTkLabel(
            self._scroll, text="Carregando historico...",
            font=(self._ff, 13), text_color="#6B7280",
        )
        self._label_loading.pack(pady=30)

    def _carregar_dados(self):
        """Carrega versao instalada e historico em background."""

        def _tarefa():
            try:
                info = update_service.obter_versao_instalada()
                versao = info.get("versao", "0.0.0")
                data = info.get("data", "")
                nome = info.get("nome", "CW Transportadora")

                historico = update_service.obter_historico_versoes(limit=20)

                if self.winfo_exists():
                    self.after(0, lambda: self._renderizar(
                        versao, data, nome, historico
                    ))
            except Exception as e:
                logger.error(f"Erro ao carregar historico: {e}")
                if self.winfo_exists():
                    self.after(0, lambda: self._renderizar_erro(str(e)))

        threading.Thread(target=_tarefa, daemon=True).start()

    def _renderizar(self, versao, data, nome, historico):
        if not self.winfo_exists():
            return

        self._label_versao.configure(
            text=f"{nome}  v{versao}"
        )
        self._label_data.configure(
            text=f"Data da versao: {data or 'N/A'}"
        )

        # Remover loading
        self._label_loading.destroy()

        # Titulo historico
        ctk.CTkLabel(
            self._scroll, text="Releases anteriores",
            font=(self._ff, 16, "bold"), text_color="#111827",
        ).pack(anchor="w", pady=(8, 8))

        if not historico:
            ctk.CTkLabel(
                self._scroll, text="Nenhum release encontrado na API.",
                font=(self._ff, 12), text_color="#6B7280",
            ).pack(anchor="w", pady=10)
            return

        for release in historico:
            self._criar_item_release(release)

    def _criar_item_release(self, release):
        versao = release.get("versao", "?")
        data = release.get("data", "")
        notas = release.get("notas", "")
        prerelease = release.get("prerelease", False)

        card = ctk.CTkFrame(
            self._scroll, fg_color="white", corner_radius=12,
            border_width=1, border_color="#E5E7EB",
        )
        card.pack(fill="x", pady=4)

        row_top = ctk.CTkFrame(card, fg_color="transparent")
        row_top.pack(fill="x", padx=18, pady=(12, 4))

        tag = "BETA" if prerelease else "STABLE"
        tag_cor = "#F59E0B" if prerelease else "#16A34A"

        ctk.CTkLabel(
            row_top, text=f"v{versao}",
            font=(self._ff, 14, "bold"), text_color="#111827",
        ).pack(side="left")

        ctk.CTkLabel(
            row_top, text=f"  {tag}",
            font=(self._ff, 10, "bold"), text_color=tag_cor,
        ).pack(side="left", padx=8)

        if data:
            ctk.CTkLabel(
                row_top, text=data,
                font=(self._ff, 11), text_color="#6B7280",
            ).pack(side="right")

        if notas:
            notas_preview = notas[:200] + ("..." if len(notas) > 200 else "")
            ctk.CTkLabel(
                card, text=notas_preview,
                font=(self._ff, 11), text_color="#4B5563",
                wraplength=600, justify="left",
            ).pack(anchor="w", padx=18, pady=(0, 12))
        else:
            # Just add bottom padding
            ctk.CTkFrame(card, fg_color="transparent", height=6).pack()

    def _renderizar_erro(self, erro):
        if not self.winfo_exists():
            return
        self._label_loading.configure(
            text=f"Erro ao carregar historico: {erro}",
            text_color="#DC2626",
        )

    def _verificar_agora(self):
        """Verifica atualizacoes manualmente."""
        self._label_status.configure(text="Verificando...", text_color="#F59E0B")

        def _tarefa():
            try:
                resultado = update_service.check_for_updates(channel="stable")
                if self.winfo_exists():
                    self.after(0, lambda: self._resultado_verificacao(resultado))
            except Exception as e:
                if self.winfo_exists():
                    self.after(0, lambda: self._label_status.configure(
                        text=f"Erro: {e}", text_color="#DC2626"
                    ))

        threading.Thread(target=_tarefa, daemon=True).start()

    def _resultado_verificacao(self, resultado):
        if not self.winfo_exists():
            return

        if resultado.get("error"):
            self._label_status.configure(
                text=f"Erro: {resultado['error']}", text_color="#DC2626"
            )
            return

        if resultado.get("has_update"):
            self._label_status.configure(
                text=f"Nova versao: {resultado['latest_version']}",
                text_color="#16A34A",
            )
            # Abrir dialog de atualizacao
            from telas.atualizacao import TelaAtualizacao
            TelaAtualizacao(self.winfo_toplevel(), resultado)
        else:
            self._label_status.configure(
                text="Sistema atualizado!", text_color="#16A34A"
            )
