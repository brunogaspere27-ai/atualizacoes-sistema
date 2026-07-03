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
            font=("Segoe UI", 12, "bold"),
            text_color=self.cores["principal"]
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(18, 0))

        ctk.CTkLabel(
            topo,
            text="Dashboard Executivo",
            font=("Segoe UI", 32, "bold"),
            text_color=self.cores["card_text"]
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(4, 2))

        ctk.CTkLabel(
            topo,
            text="Visão estratégica de operações, finanças e logística",
            font=("Segoe UI", 13),
            text_color="#94a3b8"
        ).grid(row=2, column=0, sticky="w", padx=24, pady=(0, 18))

        ctk.CTkLabel(
            topo,
            text=datetime.now().strftime("%d/%m/%Y  •  %H:%M"),
            font=("Segoe UI", 14, "bold"),
            text_color="#ffffff"
        ).grid(row=1, column=1, sticky="e", padx=24)

    def criar_filtros(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["header"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=12, pady=(0, 10))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.combo_periodo = ctk.CTkOptionMenu(frame, values=["Geral", "Mês", "Ano"], height=40, font=("Segoe UI", 11))
        self.combo_periodo.set(self.tipo_periodo)
        self.combo_periodo.grid(row=0, column=0, padx=12, pady=12, sticky="ew")

        self.combo_mes = ctk.CTkOptionMenu(frame, values=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"], height=40, font=("Segoe UI", 11))
        self.combo_mes.set(self.mes)
        self.combo_mes.grid(row=0, column=1, padx=12, pady=12, sticky="ew")

        self.entry_ano = ctk.CTkEntry(frame, height=40, font=("Segoe UI", 11))
        self.entry_ano.insert(0, self.ano)
        self.entry_ano.grid(row=0, column=2, padx=12, pady=12, sticky="ew")

        ctk.CTkButton(
            frame,
            text="🔄 Atualizar",
            height=40,
            fg_color=self.cores["principal"],
            hover_color=self.cores["hover"],
            font=("Segoe UI", 12, "bold"),
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

        ctk.CTkLabel(icon_box, text=icone, font=("Segoe UI", 26), text_color=cor).pack(expand=True)

        ctk.CTkLabel(card, text=titulo, font=("Segoe UI", 11, "bold"), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=18)
        ctk.CTkLabel(card, text=str(valor), font=("Segoe UI", 24, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=18, pady=(4, 0))
        ctk.CTkLabel(card, text=subtitulo, font=("Segoe UI", 10), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=18, pady=(4, 14))

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

        ctk.CTkLabel(frame, text="📊 Resumo Financeiro", font=("Segoe UI", 16, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Comparativo entre notas, fretes e folha", font=("Segoe UI", 11), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=20)

        labels = ["Valor Notas", "Frete Notas", "Frete Viagens", "Folha"]
        valores = [
            self.extras["valor_notas"],
            self.extras["frete_notas"],
            self.dados["frete_total"],
            self.extras["total_folha"]
        ]
        cores = ["#0f766e", "#16a34a", "#2563eb", "#dc2626"]

        if max(valores) <= 0:
            ctk.CTkLabel(frame, text="Sem dados financeiros para exibir.", text_color="#64748b", font=("Segoe UI", 12)).pack(pady=70)
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

        ctk.CTkLabel(frame, text="📈 Status Operacional", font=("Segoe UI", 16, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Notas disponíveis, em viagem e entregues", font=("Segoe UI", 11), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=20)

        valores = [
            self.dados["notas_disponiveis"],
            self.dados["notas_em_viagem"],
            self.dados["notas_entregues"]
        ]

        labels = ["Disponíveis", "Em viagem", "Entregues"]
        cores = ["#16a34a", "#f59e0b", "#2563eb"]

        if sum(valores) <= 0:
            ctk.CTkLabel(frame, text="Sem notas para exibir.", text_color="#64748b", font=("Segoe UI", 12)).pack(pady=70)
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

            ctk.CTkLabel(linha, text="●", text_color=cor, font=("Segoe UI", 20)).pack(side="left")
            ctk.CTkLabel(linha, text=nome, font=("Segoe UI", 12), text_color=self.cores["texto"]).pack(side="left", padx=8)
            ctk.CTkLabel(linha, text=str(valor), font=("Segoe UI", 12, "bold"), text_color=self.cores["texto"]).pack(side="right")

    def criar_rankings(self):
        self.criar_ranking_clientes()
        self.criar_top_destinos()

    def criar_ranking_clientes(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=5, column=0, columnspan=2, padx=10, pady=12, sticky="nsew")

        ctk.CTkLabel(frame, text="🏆 Top Clientes", font=("Segoe UI", 16, "bold"), text_color=self.cores["card_text"]).pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Clientes com maior frete no período", font=("Segoe UI", 11), text_color=self.cores["texto_suave"]).pack(anchor="w", padx=20)

        if not self.ranking_clientes:
            ctk.CTkLabel(frame, text="Nenhum cliente encontrado.", text_color="#64748b", font=("Segoe UI", 12)).pack(pady=35)
            return

        for i, cliente in enumerate(self.ranking_clientes, start=1):
            item = ctk.CTkFrame(frame, fg_color=self.cores["card_bg"], corner_radius=14)
            item.pack(fill="x", padx=20, pady=6)

            ctk.CTkLabel(item, text=f"{i}º", width=42, font=("Segoe UI", 15, "bold"), text_color=self.cores["principal"]).pack(side="left", padx=10, pady=10)

            nome = cliente.get("cliente", "Cliente não informado")
            frete = cliente.get("frete", 0)
            notas = cliente.get("total_notas", 0)

            ctk.CTkLabel(item, text=nome, font=("Segoe UI", 13, "bold"), text_color=self.cores["card_text"], anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(item, text=f"{notas} notas", font=("Segoe UI", 12), text_color=self.cores["texto_suave"]).pack(side="left", padx=10)
            ctk.CTkLabel(item, text=self.dinheiro(frete), font=("Segoe UI", 13, "bold"), text_color="#16a34a").pack(side="right", padx=14)

    def criar_top_destinos(self):
        frame = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        frame.grid(row=5, column=2, columnspan=2, padx=10, pady=12, sticky="nsew")

        ctk.CTkLabel(frame, text="📍 Top Destinos", font=("Segoe UI", 16, "bold"), text_color="#0f172a").pack(anchor="w", padx=20, pady=(16, 2))
        ctk.CTkLabel(frame, text="Destinos com mais notas importadas", font=("Segoe UI", 11), text_color="#64748b").pack(anchor="w", padx=20)

        if not self.top_destinos:
            ctk.CTkLabel(frame, text="Nenhum destino encontrado.", text_color="#64748b", font=("Segoe UI", 12)).pack(pady=35)
            return

        for i, linha in enumerate(self.top_destinos[:4], start=1):
            destino, notas, peso = linha

            item = ctk.CTkFrame(frame, fg_color=self.cores["card_bg"], corner_radius=14)
            item.pack(fill="x", padx=20, pady=6)

            ctk.CTkLabel(item, text=f"{i}º", width=42, font=("Segoe UI", 15, "bold"), text_color=self.cores["principal"]).pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(item, text=destino or "-", font=("Segoe UI", 13, "bold"), text_color=self.cores["card_text"], anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(item, text=f"{notas} notas", font=("Segoe UI", 12), text_color=self.cores["texto_suave"]).pack(side="left", padx=10)
            ctk.CTkLabel(item, text=self.peso(peso), font=("Segoe UI", 12, "bold"), text_color="#0891b2").pack(side="right", padx=14)

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
            font=("Segoe UI", 14, "bold"),
            text_color=self.cores["texto"]
        ).pack(side="left", padx=20, pady=16)

        ctk.CTkLabel(
            frame,
            text=f"Atualizado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            font=("Segoe UI", 13),
            text_color=self.cores["texto_suave"]
        ).pack(side="right", padx=20)
