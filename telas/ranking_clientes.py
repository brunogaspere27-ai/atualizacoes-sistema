import customtkinter as ctk
from datetime import datetime

from services.ranking_service import ranking_service


class TelaRankingClientes(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")
        self.dados = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self,
            text="🏆 RANKING DE CLIENTES V6",
            font=("Arial", 28, "bold"),
            text_color="#111827"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(0, 18))

        self.criar_filtros()
        self.criar_resumo()
        self.criar_tabela()

        self.carregar_ranking()

    def criar_filtros(self):

        frame = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=16,
            border_width=1,
            border_color="#e5e7eb"
        )
        frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 12))
        frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.combo_periodo = ctk.CTkOptionMenu(
            frame,
            values=["Geral", "Mês", "Ano"],
            height=40,
            fg_color="#111827",
            button_color="#374151",
            button_hover_color="#1f2937"
        )
        self.combo_periodo.grid(row=0, column=0, padx=14, pady=14, sticky="ew")
        self.combo_periodo.set(self.tipo_periodo)

        self.combo_mes = ctk.CTkOptionMenu(
            frame,
            values=["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"],
            height=40,
            fg_color="#b91c1c",
            button_color="#7f1d1d",
            button_hover_color="#450a0a"
        )
        self.combo_mes.grid(row=0, column=1, padx=14, pady=14, sticky="ew")
        self.combo_mes.set(self.mes)

        self.entry_ano = ctk.CTkEntry(
            frame,
            height=40,
            fg_color="#f9fafb",
            border_color="#d1d5db",
            text_color="#111827"
        )
        self.entry_ano.grid(row=0, column=2, padx=14, pady=14, sticky="ew")
        self.entry_ano.insert(0, self.ano)

        ctk.CTkButton(
            frame,
            text="🔄 ATUALIZAR",
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#15803d",
            hover_color="#166534",
            command=self.carregar_ranking
        ).grid(row=0, column=3, padx=14, pady=14, sticky="ew")

    def carregar_ranking(self):

        self.tipo_periodo = self.combo_periodo.get()
        self.mes = self.combo_mes.get()
        self.ano = self.entry_ano.get().strip()

        self.dados = ranking_service.carregar_ranking(
            self.tipo_periodo,
            self.mes,
            self.ano
        )

        self.atualizar_resumo()
        self.atualizar_tabela()

    def criar_resumo(self):

        self.frame_resumo = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=16,
            border_width=1,
            border_color="#e5e7eb"
        )
        self.frame_resumo.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 15))

    def atualizar_resumo(self):

        for widget in self.frame_resumo.winfo_children():
            widget.destroy()

        total_clientes = len(self.dados)
        total_notas = sum(item["total_notas"] for item in self.dados)
        total_frete = sum(item["frete"] for item in self.dados)
        total_peso = sum(item["peso"] for item in self.dados)

        self.frame_resumo.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_resumo("CLIENTES", str(total_clientes), 0, "#111827")
        self.card_resumo("NOTAS", str(total_notas), 1, "#2563eb")
        self.card_resumo("FRETE GERADO", f"R$ {total_frete:,.2f}", 2, "#15803d")
        self.card_resumo("PESO TOTAL", f"{total_peso:,.2f} kg", 3, "#b91c1c")

    def card_resumo(self, titulo, valor, col, cor):

        card = ctk.CTkFrame(
            self.frame_resumo,
            fg_color="#f9fafb",
            corner_radius=14,
            border_width=1,
            border_color="#e5e7eb"
        )
        card.grid(row=0, column=col, padx=10, pady=14, sticky="nsew")

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 11, "bold"),
            text_color="#6b7280"
        ).pack(anchor="w", padx=14, pady=(12, 4))

        ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 20, "bold"),
            text_color=cor
        ).pack(anchor="w", padx=14, pady=(0, 12))

    def criar_tabela(self):

        self.container = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=16,
            border_width=1,
            border_color="#e5e7eb"
        )
        self.container.grid(row=3, column=0, sticky="nsew", padx=10, pady=5)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(1, weight=1)

        topo = ctk.CTkFrame(self.container, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))

        self.titulo_tabela = ctk.CTkLabel(
            topo,
            text="Ranking de Clientes",
            font=("Arial", 17, "bold"),
            text_color="#111827"
        )
        self.titulo_tabela.pack(side="left")

        ctk.CTkLabel(
            topo,
            text="Ordenado por frete gerado",
            font=("Arial", 12),
            text_color="#6b7280"
        ).pack(side="right")

        self.tabela = ctk.CTkScrollableFrame(
            self.container,
            fg_color="#ffffff"
        )
        self.tabela.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

    def atualizar_tabela(self):

        for widget in self.tabela.winfo_children():
            widget.destroy()

        if self.tipo_periodo == "Mês":
            self.titulo_tabela.configure(text=f"Ranking de Clientes - {self.mes}/{self.ano}")
        elif self.tipo_periodo == "Ano":
            self.titulo_tabela.configure(text=f"Ranking de Clientes - Ano {self.ano}")
        else:
            self.titulo_tabela.configure(text="Ranking Geral de Clientes")

        colunas = [
            ("#", 0, 50),
            ("Cliente / Destinatário", 1, 310),
            ("Notas", 2, 90),
            ("Valor Mercadoria", 3, 160),
            ("Frete Gerado", 4, 160),
            ("Peso", 5, 130),
            ("% Médio", 6, 110),
        ]

        for nome, col, largura in colunas:
            self.tabela.grid_columnconfigure(col, minsize=largura)

            ctk.CTkLabel(
                self.tabela,
                text=nome,
                font=("Arial", 12, "bold"),
                text_color="#ffffff",
                fg_color="#b91c1c",
                corner_radius=6
            ).grid(row=0, column=col, padx=4, pady=6, sticky="ew")

        if not self.dados:
            ctk.CTkLabel(
                self.tabela,
                text="Nenhum cliente encontrado para este período.",
                font=("Arial", 15, "bold"),
                text_color="#6b7280"
            ).grid(row=1, column=0, columnspan=7, pady=40)
            return

        for i, item in enumerate(self.dados, start=1):

            cor_linha = "#f9fafb" if i % 2 == 0 else "#ffffff"

            valores = [
                f"{i}º",
                item["cliente"],
                str(item["total_notas"]),
                f"R$ {item['valor_notas']:,.2f}",
                f"R$ {item['frete']:,.2f}",
                f"{item['peso']:,.2f} kg",
                f"{item['percentual_medio']:.2f}%"
            ]

            for col, valor in enumerate(valores):

                cor_texto = "#15803d" if col == 4 else "#374151"

                ctk.CTkLabel(
                    self.tabela,
                    text=valor,
                    font=("Arial", 12, "bold" if col in [0, 2, 3, 4, 5, 6] else "normal"),
                    text_color=cor_texto,
                    fg_color=cor_linha,
                    corner_radius=6
                ).grid(row=i, column=col, padx=4, pady=4, sticky="ew")
