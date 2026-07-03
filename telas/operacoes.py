import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import datetime

from services.operacoes_service import operacoes_service


class TelaOperacoes(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.campos = {}

        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="🚛 TRANSFERÊNCIA SÃO PAULO → CASCAVEL",
            font=("Arial", 28, "bold"),
            text_color="#111827"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 18))

        self.form = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=18,
            border_width=1,
            border_color="#e5e7eb"
        )
        self.form.grid(row=1, column=0, sticky="nsew", padx=(10, 8), pady=5)

        self.resumo = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=18,
            border_width=1,
            border_color="#e5e7eb"
        )
        self.resumo.grid(row=1, column=1, sticky="nsew", padx=(8, 10), pady=5)

        self.form.grid_columnconfigure((0, 1), weight=1)

        self.montar_formulario()
        self.montar_resumo()
        self.montar_historico()

    def montar_formulario(self):

        self.criar_secao("DADOS DA TRANSFERÊNCIA", 0)

        self.criar_entry("data_operacao", "Data da operação", 1, 0)
        self.campos["data_operacao"].insert(0, datetime.now().strftime("%d/%m/%Y"))

        self.criar_entry("nome_caminhao", "Nome do caminhão / carreta", 1, 1)
        self.criar_entry("placa", "Placa", 2, 0)
        self.criar_entry("motorista", "Motorista", 2, 1)

        self.criar_secao("VALORES DA CARGA DE SÃO PAULO", 3)

        self.criar_entry("valor_notas", "Valor total das notas da carga SP", 4, 0)
        self.criar_entry("frete_carreta", "Frete pago à carreta", 4, 1)
        self.criar_entry("pedagio_carreta", "Pedágio pago à carreta", 5, 0)
        self.criar_entry("outros_custos", "Outros custos", 5, 1)

        botoes = ctk.CTkFrame(self.form, fg_color="transparent")
        botoes.grid(row=6, column=0, columnspan=2, sticky="ew", padx=18, pady=24)
        botoes.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            botoes,
            text="💾 SALVAR TRANSFERÊNCIA",
            height=46,
            fg_color="#16a34a",
            hover_color="#15803d",
            font=("Arial", 14, "bold"),
            command=self.salvar
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            botoes,
            text="🧹 LIMPAR",
            height=46,
            fg_color="#6b7280",
            hover_color="#4b5563",
            font=("Arial", 14, "bold"),
            command=self.limpar
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def montar_resumo(self):

        ctk.CTkLabel(
            self.resumo,
            text="📊 RESUMO",
            font=("Arial", 20, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=20, pady=(22, 16))

        self.lbl_notas = self.criar_card("Valor das Notas SP", "R$ 0,00", "#111827")
        self.lbl_frete = self.criar_card("Frete Pago à Carreta", "R$ 0,00", "#b91c1c")
        self.lbl_pedagio = self.criar_card("Pedágio Pago", "R$ 0,00", "#ca8a04")
        self.lbl_outros = self.criar_card("Outros Custos", "R$ 0,00", "#6b7280")
        self.lbl_custo_total = self.criar_card("Custo Total Transferência", "R$ 0,00", "#b91c1c")
        self.lbl_liquido = self.criar_card("Valor Líquido da Carga", "R$ 0,00", "#15803d")

        ctk.CTkButton(
            self.resumo,
            text="🔄 ATUALIZAR CÁLCULO",
            height=42,
            fg_color="#111827",
            hover_color="#374151",
            font=("Arial", 13, "bold"),
            command=self.atualizar_resumo
        ).pack(fill="x", padx=20, pady=20)

    def montar_historico(self):

        frame = ctk.CTkFrame(
            self,
            fg_color="#ffffff",
            corner_radius=18,
            border_width=1,
            border_color="#e5e7eb"
        )
        frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(14, 5))

        ctk.CTkLabel(
            frame,
            text="📋 ÚLTIMAS TRANSFERÊNCIAS SP → CASCAVEL",
            font=("Arial", 17, "bold"),
            text_color="#111827"
        ).pack(anchor="w", padx=18, pady=(16, 8))

        colunas = (
            "id", "data", "caminhao", "placa", "motorista",
            "notas", "frete", "pedagio", "outros", "custo", "liquido"
        )

        self.tree = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            height=8
        )

        titulos = {
            "id": "ID",
            "data": "Data",
            "caminhao": "Caminhão",
            "placa": "Placa",
            "motorista": "Motorista",
            "notas": "Notas SP",
            "frete": "Frete",
            "pedagio": "Pedágio",
            "outros": "Outros",
            "custo": "Custo",
            "liquido": "Líquido"
        }

        larguras = {
            "id": 55,
            "data": 100,
            "caminhao": 180,
            "placa": 100,
            "motorista": 150,
            "notas": 110,
            "frete": 110,
            "pedagio": 110,
            "outros": 110,
            "custo": 110,
            "liquido": 120
        }

        for col in colunas:
            self.tree.heading(col, text=titulos[col])
            self.tree.column(col, width=larguras[col], anchor="w")

        self.tree.column("id", anchor="center")

        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 14))

        self.carregar_historico()

    def criar_secao(self, texto, row):

        ctk.CTkLabel(
            self.form,
            text=texto,
            font=("Arial", 14, "bold"),
            text_color="#b91c1c"
        ).grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="w",
            padx=18,
            pady=(20, 6)
        )

    def criar_entry(self, nome, texto, row, col):

        frame = ctk.CTkFrame(self.form, fg_color="transparent")
        frame.grid(row=row, column=col, padx=18, pady=8, sticky="ew")

        ctk.CTkLabel(
            frame,
            text=texto,
            font=("Arial", 12, "bold"),
            text_color="#374151"
        ).pack(anchor="w")

        entry = ctk.CTkEntry(
            frame,
            height=42,
            fg_color="#f9fafb",
            border_color="#d1d5db",
            text_color="#111827"
        )
        entry.pack(fill="x", pady=(5, 0))

        self.campos[nome] = entry
        entry.bind("<KeyRelease>", lambda event: self.atualizar_resumo())

    def criar_card(self, titulo, valor, cor):

        card = ctk.CTkFrame(
            self.resumo,
            fg_color="#f9fafb",
            corner_radius=14,
            border_width=1,
            border_color="#e5e7eb"
        )
        card.pack(fill="x", padx=18, pady=7)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 12, "bold"),
            text_color="#6b7280"
        ).pack(anchor="w", padx=14, pady=(10, 2))

        label = ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 20, "bold"),
            text_color=cor
        )
        label.pack(anchor="w", padx=14, pady=(0, 10))

        return label

    def numero(self, nome):

        try:
            return float(self.campos[nome].get().replace(",", ".") or 0)
        except:
            return 0

    def calcular(self):

        valor_notas = self.numero("valor_notas")
        frete = self.numero("frete_carreta")
        pedagio = self.numero("pedagio_carreta")
        outros = self.numero("outros_custos")

        custo_total = frete + pedagio + outros
        liquido = valor_notas - custo_total

        return {
            "valor_notas": valor_notas,
            "frete_carreta": frete,
            "pedagio_carreta": pedagio,
            "outros_custos": outros,
            "custo_total": custo_total,
            "liquido": liquido
        }

    def atualizar_resumo(self):

        resultado = self.calcular()

        self.lbl_notas.configure(text=f"R$ {resultado['valor_notas']:,.2f}")
        self.lbl_frete.configure(text=f"R$ {resultado['frete_carreta']:,.2f}")
        self.lbl_pedagio.configure(text=f"R$ {resultado['pedagio_carreta']:,.2f}")
        self.lbl_outros.configure(text=f"R$ {resultado['outros_custos']:,.2f}")
        self.lbl_custo_total.configure(text=f"R$ {resultado['custo_total']:,.2f}")

        self.lbl_liquido.configure(
            text=f"R$ {resultado['liquido']:,.2f}",
            text_color="#15803d" if resultado["liquido"] >= 0 else "#b91c1c"
        )

    def salvar(self):

        nome_caminhao = self.campos["nome_caminhao"].get().strip()
        placa = self.campos["placa"].get().strip()

        if not nome_caminhao:
            messagebox.showerror("Erro", "Informe o nome do caminhão/carreta.")
            return

        if not placa:
            messagebox.showerror("Erro", "Informe a placa.")
            return

        resultado = self.calcular()

        dados = {
            "data_operacao": self.campos["data_operacao"].get(),
            "nome_caminhao": nome_caminhao,
            "placa": placa,
            "motorista": self.campos["motorista"].get().strip(),
            "valor_notas": resultado["valor_notas"],
            "frete_carreta": resultado["frete_carreta"],
            "pedagio_carreta": resultado["pedagio_carreta"],
            "outros_custos": resultado["outros_custos"],
            "custo_total": resultado["custo_total"],
            "liquido": resultado["liquido"]
        }

        operacoes_service.criar_operacao(dados)

        messagebox.showinfo("Sucesso", "Transferência salva com sucesso!")

        self.limpar()
        self.carregar_historico()

    def carregar_historico(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        dados = operacoes_service.listar_operacoes()

        for linha in dados:
            (
                id_op,
                data,
                nome_caminhao,
                placa,
                motorista,
                valor_notas,
                frete,
                pedagio,
                outros,
                custo,
                liquido
            ) = linha

            self.tree.insert("", "end", values=(
                f"#{id_op}",
                data,
                nome_caminhao,
                placa,
                motorista or "-",
                f"R$ {valor_notas:,.2f}",
                f"R$ {frete:,.2f}",
                f"R$ {pedagio:,.2f}",
                f"R$ {outros:,.2f}",
                f"R$ {custo:,.2f}",
                f"R$ {liquido:,.2f}"
            ))

    def limpar(self):

        for nome, campo in self.campos.items():
            campo.delete(0, "end")

        self.campos["data_operacao"].insert(0, datetime.now().strftime("%d/%m/%Y"))

        self.atualizar_resumo()
