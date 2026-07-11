"""
Dashboard Executivo profissional do CW Transportadora.

Features:
- 12 KPIs com tendencia e crescimento percentual
- 7 graficos modernos (matplotlib)
- Filtros: Hoje, Semana, Mes, Ano, Personalizado
- Auto-refresh a cada 60 segundos
"""

import threading
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from config.settings import settings
from services.dashboard_service import dashboard_service
from telas.theme import setup_theme
from utils.helpers import formatar_moeda, formatar_peso
from utils.logger import get_logger

logger = get_logger(__name__)

_INTERVALO_REFRESH_MS = 60_000

# Definicoes dos 12 KPIs
_KPI_DEFS = [
    ("receita_total",     "RECEITA TOTAL",       "moeda",   "#2563EB", "#DBEAFE"),
    ("lucro_estimado",    "LUCRO ESTIMADO",       "moeda",   "#16A34A", "#DCFCE7"),
    ("fretes_realizados", "FRETES REALIZADOS",    "int",     "#7C3AED", "#EDE9FE"),
    ("fretes_andamento",  "FRETES EM ANDAMENTO",  "int",     "#F59E0B", "#FEF3C7"),
    ("clientes_ativos",   "CLIENTES ATIVOS",      "int",     "#0891B2", "#CFFAFE"),
    ("motoristas_ativos", "MOTORISTAS ATIVOS",    "int",     "#9333EA", "#F3E8FF"),
    ("valor_recebido",    "VALOR RECEBIDO",       "moeda",   "#059669", "#D1FAE5"),
    ("valor_pendente",    "VALOR PENDENTE",       "moeda",   "#DC2626", "#FEE2E2"),
    ("total_abastecido",  "TOTAL ABASTECIDO",     "moeda",   "#EA580C", "#FFEDD5"),
    ("consumo_medio",     "CONSUMO MEDIO (km/L)", "float",   "#0D9488", "#CCFBF1"),
    ("quilometragem",     "QUILOMETRAGEM",        "km",      "#4F46E5", "#EEF2FF"),
    ("media_viagem",      "MEDIA POR VIAGEM",     "moeda",   "#B45309", "#FEF3C7"),
]

_FILTROS = ["Hoje", "Semana", "Mês", "Ano", "Personalizado"]


class Dashboard(ctk.CTkScrollableFrame):

    def __init__(self, master):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])

        self._ff = self.cores["font_family"]
        self._tipo_periodo = "Mês"
        self._mes = datetime.now().strftime("%m")
        self._ano = datetime.now().strftime("%Y")
        self._data_inicio = ""
        self._data_fim = ""
        self._refresh_id = None
        self._geracao = 0

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._carregar_e_montar()

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def _carregar_e_montar(self):
        self._geracao += 1
        gen = self._geracao

        def _tarefa():
            try:
                kpis = dashboard_service.calcular_kpis(
                    self._tipo_periodo, self._mes, self._ano,
                    self._data_inicio, self._data_fim,
                )
                graf_receita = dashboard_service.dados_graficos_receita_mensal(self._ano)
                graf_fretes = dashboard_service.dados_graficos_fretes_mensal(self._ano)
                graf_clientes = dashboard_service.dados_graficos_clientes_lucrativos(self._ano)
                graf_motoristas = dashboard_service.dados_graficos_motoristas_faturamento(self._ano)
                graf_despesas = dashboard_service.dados_graficos_despesas_categoria(
                    self._tipo_periodo, self._mes, self._ano,
                )
                graf_combustivel = dashboard_service.dados_graficos_consumo_combustivel(self._ano)
                graf_comparativo = dashboard_service.dados_graficos_comparativo_mensal(self._ano)

                dados = {
                    "kpis": kpis,
                    "receita": graf_receita,
                    "fretes": graf_fretes,
                    "clientes": graf_clientes,
                    "motoristas": graf_motoristas,
                    "despesas": graf_despesas,
                    "combustivel": graf_combustivel,
                    "comparativo": graf_comparativo,
                }
                if self.winfo_exists():
                    self.after(0, lambda: self._renderizar(dados, gen))
            except Exception as e:
                logger.error(f"Erro ao carregar dashboard: {e}")

        threading.Thread(target=_tarefa, daemon=True).start()

    def _renderizar(self, dados, gen):
        if gen != self._geracao or not self.winfo_exists():
            return

        for w in self.winfo_children():
            w.destroy()

        self._dados = dados
        self._criar_filtros()
        self._criar_kpis(dados["kpis"])
        self._criar_todos_graficos(dados)

        # Agendar auto-refresh
        if self._refresh_id:
            self.after_cancel(self._refresh_id)
        self._refresh_id = self.after(_INTERVALO_REFRESH_MS, self._auto_refresh)

    def _auto_refresh(self):
        if self.winfo_exists():
            self._carregar_e_montar()

    def destroy(self):
        if self._refresh_id:
            self.after_cancel(self._refresh_id)
        super().destroy()

    # ------------------------------------------------------------------
    # Filtros
    # ------------------------------------------------------------------

    def _criar_filtros(self):
        barra = ctk.CTkFrame(self, fg_color="white", corner_radius=16,
                             border_width=1, border_color="#E5E7EB")
        barra.grid(row=0, column=0, columnspan=4, sticky="ew", padx=12, pady=(8, 10))

        ctk.CTkLabel(barra, text="Periodo:", font=(self._ff, 12, "bold"),
                     text_color="#374151").pack(side="left", padx=(16, 8), pady=12)

        self._filtro_vars = {}
        for f in _FILTROS:
            ativo = (f == self._tipo_periodo)
            btn = ctk.CTkButton(
                barra, text=f, width=100, height=36,
                font=(self._ff, 12, "bold"),
                fg_color="#2563EB" if ativo else "#F3F4F6",
                hover_color="#1D4ED8" if ativo else "#E5E7EB",
                text_color="white" if ativo else "#374151",
                command=lambda ft=f: self._selecionar_filtro(ft),
            )
            btn.pack(side="left", padx=3, pady=12)

        # Mes / Ano (visivel para Mes e Ano)
        self._frame_extra = ctk.CTkFrame(barra, fg_color="transparent")
        self._frame_extra.pack(side="left", padx=(12, 4), pady=12)

        self._combo_mes = ctk.CTkComboBox(
            self._frame_extra, width=60, height=36, font=(self._ff, 11),
            values=[f"{m:02d}" for m in range(1, 13)], command=self._on_mes_change,
        )
        self._combo_mes.set(self._mes)
        self._combo_mes.pack(side="left", padx=2)

        self._entry_ano = ctk.CTkEntry(
            self._frame_extra, width=70, height=36, font=(self._ff, 11),
        )
        self._entry_ano.insert(0, self._ano)
        self._entry_ano.pack(side="left", padx=2)

        # Personalizado: data inicio / fim
        self._frame_personalizado = ctk.CTkFrame(barra, fg_color="transparent")
        self._frame_personalizado.pack(side="left", padx=(8, 4), pady=12)

        ctk.CTkLabel(self._frame_personalizado, text="De:", font=(self._ff, 11, "bold"),
                     text_color="#374151").pack(side="left", padx=(0, 2))
        self._entry_di = ctk.CTkEntry(
            self._frame_personalizado, width=100, height=36, font=(self._ff, 11),
            placeholder_text="DD/MM/YYYY",
        )
        self._entry_di.pack(side="left", padx=2)

        ctk.CTkLabel(self._frame_personalizado, text="Ate:", font=(self._ff, 11, "bold"),
                     text_color="#374151").pack(side="left", padx=(6, 2))
        self._entry_df = ctk.CTkEntry(
            self._frame_personalizado, width=100, height=36, font=(self._ff, 11),
            placeholder_text="DD/MM/YYYY",
        )
        self._entry_df.pack(side="left", padx=2)

        if self._data_inicio:
            self._entry_di.insert(0, self._data_inicio)
        if self._data_fim:
            self._entry_df.insert(0, self._data_fim)

        self._atualizar_visibilidade_filtros()

        # Botao atualizar
        ctk.CTkButton(
            barra, text="Atualizar", width=90, height=36,
            font=(self._ff, 12, "bold"), fg_color="#111827", hover_color="#374151",
            command=self._aplicar_filtros,
        ).pack(side="right", padx=12, pady=12)

        # Label ultima atualizacao
        ctk.CTkLabel(
            barra, text=f"Atualizado: {datetime.now().strftime('%H:%M:%S')}",
            font=(self._ff, 10), text_color="#9CA3AF",
        ).pack(side="right", padx=8, pady=12)

    def _selecionar_filtro(self, ft):
        self._tipo_periodo = ft
        self._atualizar_visibilidade_filtros()
        self._aplicar_filtros()

    def _atualizar_visibilidade_filtros(self):
        show_extra = self._tipo_periodo in ("Mês", "Ano")
        show_pers = self._tipo_periodo == "Personalizado"

        if show_extra:
            self._frame_extra.pack(side="left", padx=(12, 4), pady=12)
        else:
            self._frame_extra.pack_forget()

        if show_pers:
            self._frame_personalizado.pack(side="left", padx=(8, 4), pady=12)
        else:
            self._frame_personalizado.pack_forget()

    def _on_mes_change(self, _):
        pass  # Sera lido em _aplicar_filtros

    def _aplicar_filtros(self):
        self._mes = self._combo_mes.get()
        self._ano = self._entry_ano.get().strip() or datetime.now().strftime("%Y")
        self._data_inicio = self._entry_di.get().strip()
        self._data_fim = self._entry_df.get().strip()
        self._carregar_e_montar()

    # ------------------------------------------------------------------
    # KPIs
    # ------------------------------------------------------------------

    def _criar_kpis(self, kpis):
        row_base = 1
        for idx, (chave, titulo, fmt, cor, fundo) in enumerate(_KPI_DEFS):
            row = row_base + idx // 4
            col = idx % 4
            dados = kpis.get(chave, {"valor": 0, "valor_anterior": 0, "crescimento": 0})
            self._criar_card_kpi(titulo, dados, fmt, cor, fundo, row, col)

    def _criar_card_kpi(self, titulo, dados, fmt, cor, fundo, row, col):
        card = ctk.CTkFrame(self, fg_color="white", corner_radius=16,
                            border_width=1, border_color="#E5E7EB")
        card.grid(row=row, column=col, padx=8, pady=6, sticky="nsew")

        # Icone
        icon_frame = ctk.CTkFrame(card, width=48, height=48, fg_color=fundo, corner_radius=12)
        icon_frame.pack(anchor="w", padx=14, pady=(12, 6))
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="", width=48, height=48,
                     font=(self._ff, 11, "bold"), text_color=cor).pack(expand=True)

        # Titulo
        ctk.CTkLabel(card, text=titulo, font=(self._ff, 10, "bold"),
                     text_color="#6B7280").pack(anchor="w", padx=14)

        # Valor
        valor = dados["valor"]
        if fmt == "moeda":
            texto = formatar_moeda(valor)
        elif fmt == "int":
            texto = f"{int(valor):,}".replace(",", ".")
        elif fmt == "float":
            texto = f"{valor:.1f}"
        elif fmt == "km":
            texto = f"{valor:,.0f} km".replace(",", ".")
        else:
            texto = str(valor)

        ctk.CTkLabel(card, text=texto, font=(self._ff, 20, "bold"),
                     text_color="#111827").pack(anchor="w", padx=14, pady=(2, 0))

        # Tendencia
        cresc = dados.get("crescimento", 0)
        if cresc > 0:
            seta = "▲"
            cor_cresc = "#16A34A"
        elif cresc < 0:
            seta = "▼"
            cor_cresc = "#DC2626"
        else:
            seta = "●"
            cor_cresc = "#9CA3AF"

        trend_frame = ctk.CTkFrame(card, fg_color="transparent")
        trend_frame.pack(anchor="w", padx=14, pady=(2, 10))

        ctk.CTkLabel(trend_frame, text=f"{seta} {abs(cresc):.1f}%",
                     font=(self._ff, 11, "bold"), text_color=cor_cresc).pack(side="left")
        ctk.CTkLabel(trend_frame, text=" vs anterior",
                     font=(self._ff, 9), text_color="#9CA3AF").pack(side="left", padx=(4, 0))

        # Barra colorida inferior
        ctk.CTkFrame(card, fg_color=cor, height=3, corner_radius=8).pack(fill="x", side="bottom")

    # ------------------------------------------------------------------
    # Graficos
    # ------------------------------------------------------------------

    def _criar_todos_graficos(self, dados):
        chart_row = 4  # Apos 3 fileiras de KPIs (rows 1-3)

        # Row 4: Receita Mensal + Fretes Mensal
        self._grafico_barras(dados["receita"], "Receita por Mes",
                             "#2563EB", chart_row, 0, 2, y_fmt="moeda_curto")
        self._grafico_barras(dados["fretes"], "Fretes por Mes",
                             "#7C3AED", chart_row, 2, 2, y_fmt="int")

        # Row 5: Clientes Lucrativos + Motoristas Faturamento
        self._grafico_barras_h(dados["clientes"], "Clientes Mais Lucrativos",
                               "#059669", chart_row + 1, 0, 2)
        self._grafico_barras_h(dados["motoristas"], "Motoristas - Maior Faturamento",
                               "#EA580C", chart_row + 1, 2, 2)

        # Row 6: Despesas por Categoria + Consumo Combustivel
        self._grafico_donut(dados["despesas"], "Despesas por Categoria",
                            chart_row + 2, 0, 2)
        self._grafico_linhas_combustivel(dados["combustivel"], "Consumo de Combustivel",
                                         chart_row + 2, 2, 2)

        # Row 7: Comparativo Mensal (full width)
        self._grafico_comparativo(dados["comparativo"], "Comparativo Mensal",
                                  chart_row + 3, 0, 4)

    def _make_chart_frame(self, titulo, row, col, colspan):
        frame = ctk.CTkFrame(self, fg_color="white", corner_radius=16,
                             border_width=1, border_color="#E5E7EB")
        frame.grid(row=row, column=col, columnspan=colspan, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(frame, text=titulo, font=(self._ff, 14, "bold"),
                     text_color="#111827").pack(anchor="w", padx=18, pady=(14, 2))
        return frame

    def _grafico_barras(self, dados, titulo, cor, row, col, colspan, y_fmt="int"):
        frame = self._make_chart_frame(titulo, row, col, colspan)

        valores = dados.get("valores", [])
        labels = dados.get("labels", [])
        if not valores or max(valores) <= 0:
            ctk.CTkLabel(frame, text="Sem dados no periodo.", font=(self._ff, 12),
                         text_color="#9CA3AF").pack(pady=60)
            return

        fig = Figure(figsize=(6, 3.2), dpi=90)
        ax = fig.add_subplot(111)
        bars = ax.bar(range(len(labels)), valores, color=cor, width=0.6,
                      edgecolor="white", linewidth=1)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=8, rotation=0)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=8)
        ax.set_facecolor("#FAFBFC")
        fig.patch.set_facecolor("white")

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 14))

    def _grafico_barras_h(self, dados, titulo, cor, row, col, colspan):
        frame = self._make_chart_frame(titulo, row, col, colspan)

        labels = dados.get("labels", [])
        valores = dados.get("valores", [])
        if not valores or max(valores) <= 0:
            ctk.CTkLabel(frame, text="Sem dados no periodo.", font=(self._ff, 12),
                         text_color="#9CA3AF").pack(pady=60)
            return

        fig = Figure(figsize=(6, 3.2), dpi=90)
        ax = fig.add_subplot(111)

        labels_short = [l[:20] + "..." if len(l) > 20 else l for l in labels]
        bars = ax.barh(range(len(labels_short)), valores, color=cor, height=0.5,
                       edgecolor="white", linewidth=1)
        ax.set_yticks(range(len(labels_short)))
        ax.set_yticklabels(labels_short, fontsize=9)
        ax.grid(axis="x", linestyle="--", alpha=0.3)
        ax.spines[["top", "right", "bottom"]].set_visible(False)
        ax.tick_params(axis="x", labelsize=8)
        ax.set_facecolor("#FAFBFC")
        fig.patch.set_facecolor("white")
        ax.invert_yaxis()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 14))

    def _grafico_donut(self, dados, titulo, row, col, colspan):
        frame = self._make_chart_frame(titulo, row, col, colspan)

        labels = dados.get("labels", [])
        valores = dados.get("valores", [])
        if not valores or sum(valores) <= 0:
            ctk.CTkLabel(frame, text="Sem dados no periodo.", font=(self._ff, 12),
                         text_color="#9CA3AF").pack(pady=60)
            return

        cores_donut = ["#2563EB", "#DC2626", "#16A34A", "#F59E0B", "#7C3AED",
                        "#0891B2", "#EA580C", "#9333EA", "#059669", "#B45309"]

        fig = Figure(figsize=(6, 3.5), dpi=90)
        ax = fig.add_subplot(111)
        wedges, texts, autotexts = ax.pie(
            valores, labels=None, autopct="%1.1f%%",
            colors=cores_donut[:len(valores)],
            startangle=90, pctdistance=0.80,
            wedgeprops={"width": 0.40, "edgecolor": "white", "linewidth": 2},
            textprops={"fontsize": 8, "color": "#374151"},
        )
        ax.text(0, 0, "TOTAL", ha="center", va="center", fontsize=11,
                fontweight="bold", color="#374151")
        fig.patch.set_facecolor("white")

        # Legenda lateral
        legend_frame = ctk.CTkFrame(frame, fg_color="transparent")
        legend_frame.pack(side="right", fill="y", padx=(0, 14), pady=20)
        for i, (lbl, val) in enumerate(zip(labels[:6], valores[:6])):
            row_f = ctk.CTkFrame(legend_frame, fg_color="transparent")
            row_f.pack(fill="x", pady=3)
            ctk.CTkLabel(row_f, text="●", text_color=cores_donut[i % len(cores_donut)],
                         font=(self._ff, 14)).pack(side="left")
            nome = lbl[:15] + ".." if len(lbl) > 15 else lbl
            ctk.CTkLabel(row_f, text=nome, font=(self._ff, 10),
                         text_color="#374151").pack(side="left", padx=4)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left", padx=14, pady=(4, 14))

    def _grafico_linhas_combustivel(self, dados, titulo, row, col, colspan):
        frame = self._make_chart_frame(titulo, row, col, colspan)

        litros = dados.get("litros", [])
        medias = dados.get("medias", [])
        labels = dados.get("labels", [])
        if not litros or max(litros) <= 0:
            ctk.CTkLabel(frame, text="Sem dados no periodo.", font=(self._ff, 12),
                         text_color="#9CA3AF").pack(pady=60)
            return

        fig = Figure(figsize=(6, 3.2), dpi=90)
        ax1 = fig.add_subplot(111)

        ax1.bar(range(len(labels)), litros, color="#2563EB", width=0.5,
                alpha=0.7, label="Litros")
        ax1.set_xticks(range(len(labels)))
        ax1.set_xticklabels(labels, fontsize=8)
        ax1.grid(axis="y", linestyle="--", alpha=0.3)
        ax1.spines[["top", "right", "left"]].set_visible(False)
        ax1.tick_params(axis="y", labelsize=8)
        ax1.set_facecolor("#FAFBFC")

        ax2 = ax1.twinx()
        ax2.plot(range(len(labels)), medias, color="#DC2626", marker="o",
                 linewidth=2, markersize=5, label="Media km/L")
        ax2.spines[["top", "right"]].set_visible(False)
        ax2.tick_params(axis="y", labelsize=8)

        fig.patch.set_facecolor("white")
        fig.legend(loc="upper right", bbox_to_anchor=(0.95, 0.95), fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 14))

    def _grafico_comparativo(self, dados, titulo, row, col, colspan):
        frame = self._make_chart_frame(titulo, row, col, colspan)

        labels = dados.get("labels", [])
        receitas = dados.get("receitas", [])
        despesas = dados.get("despesas", [])
        lucros = dados.get("lucros", [])
        if not receitas or max(receitas + despesas) <= 0:
            ctk.CTkLabel(frame, text="Sem dados no periodo.", font=(self._ff, 12),
                         text_color="#9CA3AF").pack(pady=60)
            return

        fig = Figure(figsize=(12, 3.5), dpi=90)
        ax = fig.add_subplot(111)
        x = range(len(labels))

        ax.plot(x, receitas, color="#16A34A", marker="o", linewidth=2.5,
                markersize=6, label="Receita")
        ax.plot(x, despesas, color="#DC2626", marker="s", linewidth=2.5,
                markersize=6, label="Despesas")
        ax.plot(x, lucros, color="#2563EB", marker="^", linewidth=2.5,
                markersize=6, label="Lucro")

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.3)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="y", labelsize=8)
        ax.set_facecolor("#FAFBFC")
        fig.patch.set_facecolor("white")
        fig.legend(loc="upper left", bbox_to_anchor=(0.02, 0.98), fontsize=9)

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=14, pady=(4, 14))
import customtkinter as ctk
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from utils.helpers import formatar_moeda, formatar_peso
from config.settings import settings
from telas.theme import setup_theme
from services.dashboard_service import dashboard_service


class Dashboard(ctk.CTkScrollableFrame):

    def __init__(self, master):
        # use centralized theme
        cores = setup_theme(settings)
        super().__init__(master, fg_color=cores["fundo"])

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.cores = cores

        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")

        self.carregar_dados()
        self.montar_tela()

    def carregar_dados(self):
        payload = dashboard_service.carregar_dashboard(self.tipo_periodo, self.mes, self.ano)
        self.dados = payload["dados"]
        self.top_destinos = payload["top_destinos"]
        self.ranking_clientes = payload["ranking_clientes"]
        self.extras = payload["extras"]

    def montar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.criar_header()
        self.criar_filtros()
        self.criar_cards()
        self.criar_graficos()
        self.criar_rankings()
        self.criar_rodape()

    def dinheiro(self, valor):
        return formatar_moeda(valor)

    def peso(self, valor):
        return formatar_peso(valor)

    def criar_header(self):
        topo = ctk.CTkFrame(self, fg_color=self.cores["sidebar"], corner_radius=20)
        topo.grid(row=0, column=0, columnspan=4, sticky="ew", padx=12, pady=(10, 18))
        topo.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            topo,
            text=settings.empresa.upper(),
            font=(self.cores["font_family"], 12, "bold"),
            text_color=self.cores["principal"]
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(18, 0))

        ctk.CTkLabel(
            topo,
            text="Dashboard Executivo",
            font=(self.cores["font_family"], 32, "bold"),
            text_color=self.cores["card_text"]
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(4, 2))

        ctk.CTkLabel(
            topo,
            text="Visão estratégica de operações, finanças e logística",
            font=(self.cores["font_family"], 13),
            text_color="#94a3b8"
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(0, 18))

        ctk.CTkLabel(
            topo,
            text=datetime.now().strftime("%d/%m/%Y  •  %H:%M"),
            font=(self.cores["font_family"], 14, "bold"),
            text_color="#ffffff"
        ).grid(row=1, column=1, sticky="e", padx=24)

    def criar_filtros(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["header"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=12, pady=(0, 10))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.combo_periodo = ctk.CTkOptionMenu(frame, values=["Geral", "Mês", "Ano"], height=40, font=(self.cores["font_family"], 11))
        self.combo_periodo.set(self.tipo_periodo)
        self.combo_periodo.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        self.combo_mes = ctk.CTkOptionMenu(frame, values=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], height=40, font=(self.cores["font_family"], 11))
        self.combo_mes.set(self.mes)
        self.combo_mes.grid(row=0, column=1, padx=12, pady=12, sticky="ew")

        self.entry_ano = ctk.CTkEntry(frame, height=40, font=(self.cores["font_family"], 11))
        self.entry_ano.insert(0, self.ano)
        self.entry_ano.grid(row=0, column=2, padx=12, pady=12, sticky="ew")

        ctk.CTkButton(
            frame,
            text="🔄 Atualizar",
            height=40,
            fg_color=self.cores["principal"],
            hover_color=self.cores["hover"],
            font=(self.cores["font_family"], 12, "bold"),
            command=self.atualizar_periodo
        ).grid(row=0, column=3, padx=12, pady=12, sticky="ew")

    def atualizar_periodo(self):
        self.tipo_periodo = self.combo_periodo.get()
        self.mes = self.combo_mes.get()
        self.ano = self.entry_ano.get().strip()

        self.carregar_dados()
        self.montar_tela()

    def card(self, icone, titulo, valor, subtitulo, row, col, cor, fundo):
        card = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        icon_box = ctk.CTkFrame(card, width=56, height=56, fg_color=fundo, corner_radius=14)
        icon_box.pack(anchor="w", padx=18, pady=(16, 8))
        icon_box.pack_propagate(False)

        ctk.CTkLabel(icon_box, text=icone, font=(self.cores["font_family"], 26), text_color=cor).pack(expand=True)

        ctk.CTkLabel(card, text=titulo, font=(self.cores["font_family"], 11, "bold"), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=18)
        ctk.CTkLabel(card, text=str(valor), font=(self.cores["font_family"], 24, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=18, pady=(4, 0))
        ctk.CTkLabel(card, text=subtitulo, font=(self.cores["font_family"], 10), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=18, pady=(4, 14))

        ctk.CTkFrame(card, fg_color=cor, height=3, corner_radius=8).pack(fill="x", side="bottom")

    def criar_cards(self):
        self.card("📦", "NOTAS", self.dados["total_notas"], "Notas importadas", 2, 0, "#7c3aed", "#ede9fe")
        self.card("💰", "VALOR DAS NOTAS", self.dinheiro(self.extras["valor_notas"]), "Mercadorias importadas", 2, 1, "#0f766e", "#ccfbf1")
        self.card("🚚", "FRETE DAS NOTAS", self.dinheiro(self.extras["frete_notas"]), "Frete vindo das notas", 2, 2, "#16a34a", "#dcfce7")
        self.card("🛣️", "FRETE VIAGENS", self.dinheiro(self.dados["frete_total"]), "Frete das viagens criadas", 2, 3, "#2563eb", "#dbeafe")

        self.card("👥", "FUNCIONÁRIOS", self.extras["funcionarios_ativos"], "Funcionários ativos", 3, 0, "#9333ea", "#f3e8ff")
        self.card("💵", "SALÁRIOS ATIVOS", self.dinheiro(self.extras["salarios_ativos"]), "Base mensal cadastrada", 3, 1, "#ea580c", "#ffedd5")
        self.card("📋", "FOLHA DO PERÍODO", self.dinheiro(self.extras["total_folha"]), "Total gerado na folha", 3, 2, "#dc2626", "#fee2e2")
        self.card("⚖️", "PESO TRANSPORTADO", self.peso(self.dados["peso_total"]), "Peso total das viagens", 3, 3, "#0891b2", "#cffafe")

    def criar_graficos(self):
        self.grafico_financeiro()
        self.grafico_status()

    def grafico_financeiro(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=4, column=0, columnspan=2, padx=10, pady=12, sticky="nsew")

        ctk.CTkLabel(frame, text="📊 Resumo Financeiro", font=(self.cores["font_family"], 16, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Comparativo entre notas, fretes e folha", font=(self.cores["font_family"], 11), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=20)

        labels = ["Valor Notas", "Frete Notas", "Frete Viagens", "Folha"]
        valores = [
            self.extras["valor_notas"],
            self.extras["frete_notas"],
            self.dados["frete_total"],
            self.extras["total_folha"]
        ]
        cores = ["#0f766e", "#16a34a", "#2563eb", "#dc2626"]

        if max(valores) <= 0:
            ctk.CTkLabel(frame, text="Sem dados financeiros para exibir.", text_color="#64748b", font=(self.cores["font_family"], 12)).pack(pady=70)
            return

        fig = Figure(figsize=(5.6, 3.6), dpi=100)
        ax = fig.add_subplot(111)

        barras = ax.bar(labels, valores, color=cores, width=0.55, edgecolor="white", linewidth=1.5)
        ax.grid(axis="y", linestyle="--", alpha=0.3, color=self.cores["texto_suave"])
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color(self.cores["muted_border"])
        ax.tick_params(axis="x", labelrotation=12, labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        ax.set_facecolor("#f8fafc")

        for barra, valor in zip(barras, valores):
            ax.text(
                barra.get_x() + barra.get_width() / 2,
                valor,
                self.dinheiro(valor).replace("R$ ", ""),
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color=self.cores["texto"]
            )

        fig.patch.set_facecolor(self.cores["card_bg"])

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=18, pady=15)

    def grafico_status(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=4, column=2, columnspan=2, padx=10, pady=12, sticky="nsew")

        ctk.CTkLabel(frame, text="📈 Status Operacional", font=(self.cores["font_family"], 16, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Notas disponíveis, em viagem e entregues", font=(self.cores["font_family"], 11), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=20)

        valores = [
            self.dados["notas_disponiveis"],
            self.dados["notas_em_viagem"],
            self.dados["notas_entregues"]
        ]

        labels = ["Disponíveis", "Em viagem", "Entregues"]
        cores = ["#16a34a", "#f59e0b", "#2563eb"]

        if sum(valores) <= 0:
            ctk.CTkLabel(frame, text="Sem notas para exibir.", text_color="#64748b", font=(self.cores["font_family"], 12)).pack(pady=70)
            return

        fig = Figure(figsize=(5.0, 3.5), dpi=100)
        ax = fig.add_subplot(111)

        ax.pie(
            valores,
            colors=cores,
            startangle=90,
            autopct="%1.1f%%",
            pctdistance=0.80,
            textprops={"fontsize": 9, "color": "white", "weight": "bold"},
            wedgeprops={"width": 0.40, "edgecolor": "white", "linewidth": 2}
        )

        ax.text(0, 0.05, str(sum(valores)), ha="center", va="center", fontsize=20, fontweight="bold", color="#374151")
        ax.text(0, -0.12, "NOTAS", ha="center", va="center", fontsize=10, color="#64748b")
        ax.axis("equal")
        fig.patch.set_facecolor(self.cores["card_bg"])

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side="left", padx=15, pady=15)

        legenda = ctk.CTkFrame(frame, fg_color="transparent")
        legenda.pack(side="left", fill="both", expand=True, padx=10, pady=20)

        for nome, valor, cor in zip(labels, valores, cores):
            linha = ctk.CTkFrame(legenda, fg_color="transparent")
            linha.pack(fill="x", pady=8)

            ctk.CTkLabel(linha, text="●", text_color=cor, font=(self.cores["font_family"], 20)).pack(side="left")
            ctk.CTkLabel(linha, text=nome, font=(self.cores["font_family"], 12), text_color=self.cores["texto"]).pack(side="left", padx=8)
            ctk.CTkLabel(linha, text=str(valor), font=(self.cores["font_family"], 12, "bold"), text_color=self.cores["texto"]).pack(side="right")

    def criar_rankings(self):
        self.criar_ranking_clientes()
        self.criar_top_destinos()

    def criar_ranking_clientes(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=5, column=0, columnspan=2, padx=10, pady=12, sticky="nsew")

        ctk.CTkLabel(frame, text="🏆 Top Clientes", font=(self.cores["font_family"], 16, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Clientes com maior frete no período", font=(self.cores["font_family"], 11), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=20)

        if not self.ranking_clientes:
            ctk.CTkLabel(frame, text="Nenhum cliente encontrado.", text_color="#64748b", font=(self.cores["font_family"], 12)).pack(pady=35)
            return

        for i, cliente in enumerate(self.ranking_clientes, start=1):
            item = ctk.CTkFrame(frame, fg_color=self.cores["card_bg"], corner_radius=14)
            item.pack(fill="x", padx=20, pady=6)

            ctk.CTkLabel(item, text=f"{i}º", width=42, font=(self.cores["font_family"], 15, "bold"), text_color=self.cores["principal"]).pack(side="left", padx=10, pady=10)

            nome = cliente.get("cliente", "Cliente não informado")
            frete = cliente.get("frete", 0)
            notas = cliente.get("total_notas", 0)

            ctk.CTkLabel(item, text=nome, font=(self.cores["font_family"], 13, "bold"), text_color=self.cores["card_text"], anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(item, text=f"{notas} notas", font=(self.cores["font_family"], 12), text_color=self.cores["texto_suave"]).pack(side="left", padx=10)
            ctk.CTkLabel(item, text=self.dinheiro(frete), font=(self.cores["font_family"], 13, "bold"), text_color="#16a34a").pack(side="right", padx=14)

    def criar_top_destinos(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=5, column=2, columnspan=2, padx=10, pady=12, sticky="nsew")

        ctk.CTkLabel(frame, text="📍 Top Destinos", font=(self.cores["font_family"], 16, "bold"), text_color="#0f172a").pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Destinos com mais notas importadas", font=(self.cores["font_family"], 11), text_color="#64748b").pack(anchor="w", padx=20)

        if not self.top_destinos:
            ctk.CTkLabel(frame, text="Nenhum destino encontrado.", text_color="#64748b", font=(self.cores["font_family"], 12)).pack(pady=35)
            return

        for i, linha in enumerate(self.top_destinos[:4], start=1):
            destino, notas, peso = linha

            item = ctk.CTkFrame(frame, fg_color=self.cores["card_bg"], corner_radius=14)
            item.pack(fill="x", padx=20, pady=6)

            ctk.CTkLabel(item, text=f"{i}º", width=42, font=(self.cores["font_family"], 15, "bold"), text_color=self.cores["principal"]).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(item, text=destino or "-", font=(self.cores["font_family"], 13, "bold"), text_color=self.cores["card_text"], anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(item, text=f"{notas} notas", font=(self.cores["font_family"], 12), text_color=self.cores["texto_suave"]).pack(side="left", padx=10)
            ctk.CTkLabel(item, text=self.peso(peso), font=(self.cores["font_family"], 12, "bold"), text_color="#0891b2").pack(side="right", padx=14)

    def criar_rodape(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["header"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=6, column=0, columnspan=4, padx=10, pady=(12, 25), sticky="ew")

        total = self.dados["total_notas"] or 1
        aproveitamento = (self.dados["notas_entregues"] / total) * 100

        texto = (
            f"Resumo: {self.dados['total_notas']} notas • "
            f"{self.dados['total_viagens']} viagens • "
            f"{aproveitamento:.1f}% entregues • "
            f"Folha: {self.dinheiro(self.extras['total_folha'])}"
        )

        ctk.CTkLabel(
            frame,
            text=texto,
            font=(self.cores["font_family"], 14, "bold"),
            text_color=self.cores["texto"]
        ).pack(side="left", padx=20, pady=16)

        ctk.CTkLabel(
            frame,
            text=f"Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            font=(self.cores["font_family"], 13),
            text_color=self.cores["texto_suave"]
        ).pack(side="right", padx=20)
