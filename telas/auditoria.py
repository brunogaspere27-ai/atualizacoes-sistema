"""
Tela de auditoria do sistema CW Transportadora.

Acessivel apenas pelo Administrador Mestre.

Features:
- Tabela com logs de auditoria
- Filtros por usuario, acao, data e modulo
- Paginacao (100 registros por pagina)
- Export CSV
- Cards resumo do dia
"""

from __future__ import annotations

import csv
import threading
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import customtkinter as ctk

from config.settings import settings
from services.auditoria_service import auditoria_service
from telas.theme import setup_theme, criar_header
from utils.logger import get_logger

logger = get_logger(__name__)

_POR_PAGINA = 100


class TelaAuditoria(ctk.CTkFrame):
    def __init__(self, master):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])

        self._pagina_atual = 0
        self._total_registros = 0
        self._dados: list = []

        self._criar_layout()
        self._carregar_dados()

    def _criar_layout(self) -> None:
        ff = self.cores["font_family"]

        criar_header(
            self,
            tag="ADMINISTRACAO",
            titulo="Auditoria do Sistema",
            subtitulo="Registro completo de todas as acoes realizadas no sistema.",
            cores=self.cores,
        )

        # Cards resumo
        self._frame_cards = ctk.CTkFrame(self, fg_color="transparent")
        self._frame_cards.pack(fill="x", padx=25, pady=(8, 0))
        self._card_logins = self._criar_card("Logins hoje", "0")
        self._card_falhas = self._criar_card("Tentativas falhas", "0")
        self._card_alteracoes = self._criar_card("Alteracoes hoje", "0")

        # Filtros
        filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        filtros.pack(fill="x", padx=25, pady=(8, 8))

        # Acao
        ctk.CTkLabel(
            filtros, text="Acao:", font=(ff, 11, "bold"), text_color="#374151",
        ).pack(side="left", padx=(12, 4), pady=10)

        self.combo_acao = ctk.CTkComboBox(
            filtros, values=["Todas"], width=170, height=36, font=(ff, 12),
        )
        self.combo_acao.set("Todas")
        self.combo_acao.pack(side="left", padx=4, pady=10)

        # Modulo
        ctk.CTkLabel(
            filtros, text="Modulo:", font=(ff, 11, "bold"), text_color="#374151",
        ).pack(side="left", padx=(10, 4), pady=10)

        self.combo_modulo = ctk.CTkComboBox(
            filtros,
            values=["Todos", "auth", "usuarios", "viagens", "financeiro", "sistema"],
            width=130, height=36, font=(ff, 12),
        )
        self.combo_modulo.set("Todos")
        self.combo_modulo.pack(side="left", padx=4, pady=10)

        # Data inicio
        ctk.CTkLabel(
            filtros, text="De:", font=(ff, 11, "bold"), text_color="#374151",
        ).pack(side="left", padx=(10, 4), pady=10)

        self.entry_data_inicio = ctk.CTkEntry(
            filtros, width=110, height=36, font=(ff, 12),
            placeholder_text="YYYY-MM-DD",
        )
        self.entry_data_inicio.pack(side="left", padx=4, pady=10)

        # Data fim
        ctk.CTkLabel(
            filtros, text="Ate:", font=(ff, 11, "bold"), text_color="#374151",
        ).pack(side="left", padx=(10, 4), pady=10)

        self.entry_data_fim = ctk.CTkEntry(
            filtros, width=110, height=36, font=(ff, 12),
            placeholder_text="YYYY-MM-DD",
        )
        self.entry_data_fim.pack(side="left", padx=4, pady=10)

        # Botoes
        ctk.CTkButton(
            filtros, text="Buscar", width=90, height=36,
            font=(ff, 12, "bold"), fg_color="#2563EB", hover_color="#1D4ED8",
            command=self._buscar,
        ).pack(side="right", padx=6, pady=10)

        ctk.CTkButton(
            filtros, text="Exportar CSV", width=110, height=36,
            font=(ff, 12, "bold"), fg_color="#10B981", hover_color="#059669",
            command=self._exportar_csv,
        ).pack(side="right", padx=6, pady=10)

        # Tabela
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=25, pady=(0, 8))

        colunas = ("id", "data_hora", "usuario", "acao", "modulo", "registro", "detalhes")
        self.tabela = ttk.Treeview(card, columns=colunas, show="headings", height=16)

        titulos = {
            "id": "ID", "data_hora": "Data/Hora", "usuario": "Usuario",
            "acao": "Acao", "modulo": "Modulo",
            "registro": "Registro Afetado", "detalhes": "Detalhes",
        }
        larguras = {
            "id": 50, "data_hora": 150, "usuario": 140, "acao": 150,
            "modulo": 100, "registro": 140, "detalhes": 250,
        }
        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, anchor="center", width=larguras[col])

        self.tabela.pack(fill="both", expand=True, padx=15, pady=15)

        # Paginacao
        pag = ctk.CTkFrame(card, fg_color="transparent")
        pag.pack(fill="x", padx=15, pady=(0, 10))

        self.btn_anterior = ctk.CTkButton(
            pag, text="< Anterior", width=100, height=34,
            font=(ff, 12, "bold"), fg_color="#374151", hover_color="#1F2937",
            command=self._pagina_anterior,
        )
        self.btn_anterior.pack(side="left", padx=4)

        self.label_pagina = ctk.CTkLabel(
            pag, text="Pagina 1", font=(ff, 12, "bold"), text_color="#374151",
        )
        self.label_pagina.pack(side="left", padx=16)

        self.btn_proximo = ctk.CTkButton(
            pag, text="Proximo >", width=100, height=34,
            font=(ff, 12, "bold"), fg_color="#374151", hover_color="#1F2937",
            command=self._pagina_proxima,
        )
        self.btn_proximo.pack(side="left", padx=4)

        self.label_total = ctk.CTkLabel(
            pag, text="0 registros", font=(ff, 11), text_color="#6B7280",
        )
        self.label_total.pack(side="right", padx=8)

    def _criar_card(self, titulo: str, valor: str) -> ctk.CTkLabel:
        ff = self.cores["font_family"]
        card = ctk.CTkFrame(self._frame_cards, fg_color="white", corner_radius=14)
        card.pack(side="left", fill="x", expand=True, padx=5, pady=4)

        ctk.CTkLabel(
            card, text=titulo, font=(ff, 11), text_color="#6B7280",
        ).pack(pady=(8, 0))

        label = ctk.CTkLabel(
            card, text=valor, font=(ff, 22, "bold"), text_color="#111827",
        )
        label.pack(pady=(0, 8))
        return label

    def _get_filtros(self) -> dict:
        acao = self.combo_acao.get()
        modulo = self.combo_modulo.get()
        data_inicio = self.entry_data_inicio.get().strip()
        data_fim = self.entry_data_fim.get().strip()

        return {
            "acao": acao if acao != "Todas" else None,
            "modulo": modulo if modulo != "Todos" else None,
            "data_inicio": data_inicio or None,
            "data_fim": data_fim or None,
        }

    def _buscar(self) -> None:
        self._pagina_atual = 0
        self._carregar_dados()

    def _carregar_dados(self) -> None:
        filtros = self._get_filtros()
        offset = self._pagina_atual * _POR_PAGINA

        self._dados = auditoria_service.listar(
            acao=filtros["acao"],
            modulo=filtros["modulo"],
            data_inicio=filtros["data_inicio"],
            data_fim=filtros["data_fim"],
            limite=_POR_PAGINA,
            offset=offset,
        )
        self._total_registros = auditoria_service.contar_total(
            acao=filtros["acao"],
            modulo=filtros["modulo"],
            data_inicio=filtros["data_inicio"],
            data_fim=filtros["data_fim"],
        )

        self._renderizar_tabela()
        self._renderizar_paginacao()
        self._renderizar_cards()

    def _renderizar_tabela(self) -> None:
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for row in self._dados:
            self.tabela.insert("", "end", values=(
                row["id"],
                row["criado_em"],
                row["usuario_nome"],
                row["acao"],
                row["modulo"],
                row["registro_afetado"],
                row["detalhes"],
            ))

    def _renderizar_paginacao(self) -> None:
        total_paginas = max(1, (self._total_registros + _POR_PAGINA - 1) // _POR_PAGINA)
        self.label_pagina.configure(
            text=f"Pagina {self._pagina_atual + 1} de {total_paginas}"
        )
        self.label_total.configure(text=f"{self._total_registros} registros")

        self.btn_anterior.configure(
            state="normal" if self._pagina_atual > 0 else "disabled"
        )
        self.btn_proximo.configure(
            state="normal"
            if (self._pagina_atual + 1) * _POR_PAGINA < self._total_registros
            else "disabled"
        )

    def _renderizar_cards(self) -> None:
        stats = auditoria_service.estatisticas_hoje()
        self._card_logins.configure(text=str(stats.get("logins", 0)))
        self._card_falhas.configure(text=str(stats.get("tentativas_falhas", 0)))
        self._card_alteracoes.configure(text=str(stats.get("alteracoes", 0)))

    def _pagina_anterior(self) -> None:
        if self._pagina_atual > 0:
            self._pagina_atual -= 1
            self._carregar_dados()

    def _pagina_proxima(self) -> None:
        self._pagina_atual += 1
        self._carregar_dados()

    def _exportar_csv(self) -> None:
        if not self._dados:
            messagebox.showwarning("Atencao", "Nenhum dado para exportar.")
            return

        caminho = filedialog.asksaveasfilename(
            title="Exportar Auditoria",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile=f"auditoria_{datetime.now().strftime('%d%m%Y_%H%M%S')}.csv",
        )
        if not caminho:
            return

        try:
            with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow([
                    "ID", "Data/Hora", "Usuario", "Acao",
                    "Modulo", "Registro", "Detalhes",
                ])
                for row in self._dados:
                    writer.writerow([
                        row["id"], row["criado_em"], row["usuario_nome"],
                        row["acao"], row["modulo"], row["registro_afetado"],
                        row["detalhes"],
                    ])
            messagebox.showinfo("Sucesso", f"Auditoria exportada:\n{caminho}")
        except Exception as erro:
            messagebox.showerror("Erro", str(erro))
