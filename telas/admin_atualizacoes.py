"""
Painel de Administração de Atualizações - CW Transportadora

Interface para usuários Mestre administrarem o sistema de atualizações.
Exibe histórico completo, estatísticas e informações detalhadas.

Features:
- Versão atual instalada
- Última versão publicada por canal
- Histórico completo de publicações
- Estatísticas de sucesso/falha
- Informações detalhadas de cada release
- Status do servidor de atualizações
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

import customtkinter as ctk

from config.settings import settings
from services.release_service import release_service, Channel, ReleaseInfo, ReleaseStatus
from services.auth_service import auth_service
from telas.theme import setup_theme


class TelaAdminAtualizacoes(ctk.CTkFrame):
    """Painel de administração do sistema de atualizações."""

    def __init__(self, master, voltar_callback):
        self.cores = setup_theme(settings)
        self._ff = self.cores["font_family"]
        self._voltar_callback = voltar_callback

        super().__init__(master, fg_color=self.cores["fundo"])
        self._criar_interface()
        self._carregar_dados()

    def _criar_interface(self):
        # Header
        from telas.theme import criar_header
        criar_header(
            self,
            tag="ADMINISTRAÇÃO",
            titulo="Painel de Atualizações",
            subtitulo="Gerencie publicações e visualize histórico de versões",
            cores=self.cores
        )

        # Container principal
        container = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16)
        container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Seção: Status Atual
        self._criar_secao_status(container)

        # Seção: Últimas Versões por Canal
        self._criar_secao_ultimas_versoes(container)

        # Seção: Estatísticas
        self._criar_secao_estatisticas(container)

        # Seção: Histórico de Publicações
        self._criar_secao_historico(container)

        # Botão Voltar
        self._criar_botao_voltar(container)

    def _criar_secao_status(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=(20, 12))

        ctk.CTkLabel(
            frame, text="Status do Sistema",
            font=(self._ff, 16, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w")

        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(8, 0))

        # Versão atual
        ctk.CTkLabel(
            grid_frame, text="Versão Instalada:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._label_versao_atual = ctk.CTkLabel(
            grid_frame, text="--",
            font=(self._ff, 12, "bold"), text_color=self.cores["texto"]
        )
        self._label_versao_atual.grid(row=0, column=1, sticky="w")

        # Fonte de atualização
        ctk.CTkLabel(
            grid_frame, text="Fonte de Atualização:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))

        self._label_fonte = ctk.CTkLabel(
            grid_frame, text="--",
            font=(self._ff, 12), text_color=self.cores["texto"]
        )
        self._label_fonte.grid(row=1, column=1, sticky="w", pady=(8, 0))

        # Tipo de servidor
        ctk.CTkLabel(
            grid_frame, text="Tipo de Servidor:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0))

        self._label_tipo_servidor = ctk.CTkLabel(
            grid_frame, text="--",
            font=(self._ff, 12), text_color=self.cores["texto"]
        )
        self._label_tipo_servidor.grid(row=2, column=1, sticky="w", pady=(8, 0))

    def _criar_secao_ultimas_versoes(self, parent):
        frame = ctk.CTkFrame(parent, fg_color=self.cores["surface"], corner_radius=12)
        frame.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(
            frame, text="Últimas Versões por Canal",
            font=(self._ff, 14, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w", padx=16, pady=(12, 8))

        # Grid de canais
        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=16, pady=(0, 12))

        for i, canal in enumerate([Channel.STABLE, Channel.BETA, Channel.DEV]):
            self._criar_card_canal(grid_frame, canal, i)

    def _criar_card_canal(self, parent, canal: Channel, col: int):
        card = ctk.CTkFrame(
            parent, fg_color=self.cores["card_bg"], corner_radius=8
        )
        card.grid(row=0, column=col, padx=(0, 8 if col < 2 else 0), sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(
            card, text=canal.value.upper(),
            font=(self._ff, 12, "bold"), text_color=self.cores["texto"],
        ).pack(pady=(12, 4))

        self._label_canal_versao = ctk.CTkLabel(
            card, text="--",
            font=(self._ff, 18, "bold"), text_color=self.cores.get("principal", "#DC2626")
        )
        self._label_canal_versao.pack(pady=(0, 4))

        self._label_canal_data = ctk.CTkLabel(
            card, text="--",
            font=(self._ff, 10), text_color=self.cores["texto_suave"]
        )
        self._label_canal_data.pack(pady=(0, 12))

        # Armazenar referência para atualização
        setattr(self, f"_label_{canal.value}_versao", self._label_canal_versao)
        setattr(self, f"_label_{canal.value}_data", self._label_canal_data)

    def _criar_secao_estatisticas(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=12)

        ctk.CTkLabel(
            frame, text="Estatísticas de Publicações",
            font=(self._ff, 14, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w")

        grid_frame = ctk.CTkFrame(frame, fg_color="transparent")
        grid_frame.pack(fill="x", pady=(8, 0))

        # Total
        ctk.CTkLabel(
            grid_frame, text="Total de Publicações:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._label_total = ctk.CTkLabel(
            grid_frame, text="0",
            font=(self._ff, 12, "bold"), text_color=self.cores["texto"]
        )
        self._label_total.grid(row=0, column=1, sticky="w")

        # Sucesso
        ctk.CTkLabel(
            grid_frame, text="Sucesso:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(8, 0))

        self._label_sucesso = ctk.CTkLabel(
            grid_frame, text="0",
            font=(self._ff, 12, "bold"), text_color="#10B981"
        )
        self._label_sucesso.grid(row=1, column=1, sticky="w", pady=(8, 0))

        # Falha
        ctk.CTkLabel(
            grid_frame, text="Falha:",
            font=(self._ff, 12), text_color=self.cores["texto_suave"],
        ).grid(row=2, column=0, sticky="w", padx=(0, 8), pady=(8, 0))

        self._label_falha = ctk.CTkLabel(
            grid_frame, text="0",
            font=(self._ff, 12, "bold"), text_color="#EF4444"
        )
        self._label_falha.grid(row=2, column=1, sticky="w", pady=(8, 0))

    def _criar_secao_historico(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(12, 8))

        ctk.CTkLabel(
            frame, text="Histórico de Publicações",
            font=(self._ff, 14, "bold"), text_color=self.cores["texto"],
        ).pack(anchor="w")

        # Scrollable frame para histórico
        scroll_frame = ctk.CTkScrollableFrame(
            frame, fg_color=self.cores["surface"], height=200,
            label_text=""
        )
        scroll_frame.pack(fill="both", expand=True, pady=(8, 0))

        self._historico_container = scroll_frame

    def _criar_botao_voltar(self, parent):
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(8, 20))

        btn_voltar = ctk.CTkButton(
            btn_frame, text="Voltar", height=40, width=120,
            font=(self._ff, 13, "bold"),
            fg_color="#6B7280", hover_color="#4B5563",
            command=self._voltar_callback
        )
        btn_voltar.pack(side="left")

    def _carregar_dados(self):
        """Carrega os dados do painel."""
        try:
            dados = release_service.get_admin_panel_data()

            # Atualizar status atual
            self._label_versao_atual.configure(text=dados["current_version"])
            self._label_fonte.configure(text=dados["server_type"].upper())
            self._label_tipo_servidor.configure(text=dados["server_type"].upper())

            # Atualizar canais
            for canal in [Channel.STABLE, Channel.BETA, Channel.DEV]:
                latest = dados["latest_by_channel"].get(canal.value)
                label_versao = getattr(self, f"_label_{canal.value}_versao")
                label_data = getattr(self, f"_label_{canal.value}_data")

                if latest:
                    label_versao.configure(text=latest.version)
                    label_data.configure(text=latest.release_date)
                else:
                    label_versao.configure(text="--")
                    label_data.configure(text="Nenhuma versão")

            # Atualizar estatísticas
            self._label_total.configure(text=str(dados["total_releases"]))
            self._label_sucesso.configure(text=str(dados["successful_releases"]))
            self._label_falha.configure(text=str(dados["failed_releases"]))

            # Carregar histórico
            self._carregar_historico(dados["history"])

        except Exception as e:
            print(f"Erro ao carregar dados: {e}")

    def _carregar_historico(self, historico: list):
        """Carrega o histórico de publicações."""
        # Limpar container
        for widget in self._historico_container.winfo_children():
            widget.destroy()

        for release in historico[:10]:  # Mostrar últimas 10
            self._criar_item_historico(release)

    def _criar_item_historico(self, release: ReleaseInfo):
        """Cria um item do histórico."""
        item = ctk.CTkFrame(
            self._historico_container, fg_color=self.cores["card_bg"],
            corner_radius=8
        )
        item.pack(fill="x", pady=4, padx=8)

        # Status indicator
        status_color = "#10B981" if release.status == ReleaseStatus.SUCCESS.value else "#EF4444"
        status_text = "✓" if release.status == ReleaseStatus.SUCCESS.value else "✗"

        # Grid de informações
        grid = ctk.CTkFrame(item, fg_color="transparent")
        grid.pack(fill="x", padx=12, pady=8)

        # Versão e canal
        ctk.CTkLabel(
            grid, text=f"v{release.version}",
            font=(self._ff, 13, "bold"), text_color=self.cores["texto"]
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            grid, text=f"({release.channel})",
            font=(self._ff, 11), text_color=self.cores["texto_suave"]
        ).grid(row=0, column=1, sticky="w", padx=(4, 0))

        # Status
        ctk.CTkLabel(
            grid, text=status_text,
            font=(self._ff, 14, "bold"), text_color=status_color
        ).grid(row=0, column=2, sticky="e")

        # Data e usuário
        ctk.CTkLabel(
            grid, text=f"{release.release_date} • {release.published_by}",
            font=(self._ff, 10), text_color=self.cores["texto_suave"]
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(4, 0))


def abrir_admin_atualizacoes(master, voltar_callback):
    """Abre o painel de administração de atualizações."""
    # Verificar permissão Mestre
    if not auth_service.tem_permissao("mestre"):
        from tkinter import messagebox
        messagebox.showerror(
            "Acesso Negado",
            "Apenas usuários com nível Mestre podem acessar o painel de administração."
        )
        return

    TelaAdminAtualizacoes(master, voltar_callback).pack(fill="both", expand=True)
