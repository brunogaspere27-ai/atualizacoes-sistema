import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.database import criar_banco
from services.financeiro_service import financeiro_service


class TelaContas(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F4F6F8")

        criar_banco()
        self.criar_layout()
        self.carregar_contas()

    def criar_layout(self):
        topo = ctk.CTkFrame(self, fg_color="#0f172a", corner_radius=24)
        topo.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            topo,
            text="FINANCEIRO",
            font=("Arial", 13, "bold"),
            text_color="#93c5fd"
        ).pack(anchor="w", padx=24, pady=(18, 0))

        ctk.CTkLabel(
            topo,
            text="Contas a Pagar e Receber",
            font=("Arial", 34, "bold"),
            text_color="white"
        ).pack(anchor="w", padx=24)

        ctk.CTkLabel(
            topo,
            text="Controle de vencimentos, pagamentos, recebimentos, atrasos e fluxo financeiro.",
            font=("Arial", 14),
            text_color="#cbd5e1"
        ).pack(anchor="w", padx=24, pady=(0, 18))

        filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        filtros.pack(fill="x", padx=25, pady=10)

        self.tipo_periodo = ctk.CTkComboBox(
            filtros,
            values=["Geral", "Mês", "Ano"],
            width=120,
            command=lambda e: self.carregar_contas()
        )
        self.tipo_periodo.set("Geral")
        self.tipo_periodo.pack(side="left", padx=12, pady=12)

        self.mes = ctk.CTkComboBox(
            filtros,
            values=["01", "02", "03", "04", "05", "06",
                    "07", "08", "09", "10", "11", "12"],
            width=90,
            command=lambda e: self.carregar_contas()
        )
        self.mes.set(datetime.now().strftime("%m"))
        self.mes.pack(side="left", padx=8)

        self.ano = ctk.CTkEntry(filtros, width=90, placeholder_text="Ano")
        self.ano.insert(0, datetime.now().strftime("%Y"))
        self.ano.pack(side="left", padx=8)
        self.ano.bind("<KeyRelease>", lambda e: self.carregar_contas())

        self.filtro_tipo = ctk.CTkComboBox(
            filtros,
            values=["Todos", "Pagar", "Receber"],
            width=120,
            command=lambda e: self.carregar_contas()
        )
        self.filtro_tipo.set("Todos")
        self.filtro_tipo.pack(side="left", padx=8)

        self.busca = ctk.CTkEntry(
            filtros,
            width=250,
            placeholder_text="Buscar descrição, pessoa ou categoria..."
        )
        self.busca.pack(side="left", padx=8)
        self.busca.bind("<KeyRelease>", lambda e: self.carregar_contas())

        ctk.CTkButton(
            filtros,
            text="+ Nova Conta",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.abrir_modal_conta
        ).pack(side="right", padx=12)

        self.frame_resumo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_resumo.pack(fill="x", padx=25, pady=(5, 0))

        self.card_receber = self.criar_card_resumo("A receber", "R$ 0,00")
        self.card_pagar = self.criar_card_resumo("A pagar", "R$ 0,00")
        self.card_pago = self.criar_card_resumo("Pago/Recebido", "R$ 0,00")
        self.card_saldo = self.criar_card_resumo("Saldo previsto", "R$ 0,00")

        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=25, pady=12)

        colunas = (
            "id", "tipo", "descricao", "pessoa", "categoria",
            "valor", "vencimento", "pagamento", "status", "observacao"
        )

        self.tabela = ttk.Treeview(card, columns=colunas, show="headings", height=17)

        titulos = {
            "id": "ID",
            "tipo": "Tipo",
            "descricao": "Descrição",
            "pessoa": "Cliente/Fornecedor",
            "categoria": "Categoria",
            "valor": "Valor",
            "vencimento": "Vencimento",
            "pagamento": "Pagamento",
            "status": "Status",
            "observacao": "Observação"
        }

        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, anchor="center", width=120)

        self.tabela.column("id", width=45)
        self.tabela.column("descricao", width=220)
        self.tabela.column("pessoa", width=190)
        self.tabela.column("observacao", width=220)

        self.tabela.pack(fill="both", expand=True, padx=15, pady=15)
        self.tabela.bind("<Double-1>", self.editar_conta)

        rodape = ctk.CTkFrame(card, fg_color="transparent")
        rodape.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            rodape,
            text="Marcar como Pago/Recebido",
            fg_color="#16A34A",
            hover_color="#15803D",
            command=self.marcar_pago
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            rodape,
            text="Excluir",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.excluir_conta
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            rodape,
            text="Atualizar",
            fg_color="#111827",
            hover_color="#374151",
            command=self.carregar_contas
        ).pack(side="right", padx=5)

    def criar_card_resumo(self, titulo, valor):
        card = ctk.CTkFrame(self.frame_resumo, fg_color="white", corner_radius=16)
        card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 12),
            text_color="#6B7280"
        ).pack(pady=(10, 0))

        label = ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 20, "bold"),
            text_color="#111827"
        )
        label.pack(pady=(2, 10))

        return label

    def abrir_modal_conta(self, dados=None):
        janela = ctk.CTkToplevel(self)
        janela.title("Conta")
        janela.geometry("560x720")
        janela.grab_set()

        conta_id = dados[0] if dados else None

        ctk.CTkLabel(
            janela,
            text="Cadastro de Conta",
            font=("Arial", 24, "bold")
        ).pack(pady=(20, 10))

        frame = ctk.CTkFrame(janela, fg_color="white", corner_radius=18)
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        tipo = ctk.CTkComboBox(frame, values=["Pagar", "Receber"], height=40)
        self.criar_label(frame, "Tipo")
        tipo.pack(fill="x", padx=20, pady=(0, 8))
        tipo.set("Pagar")

        descricao = self.criar_campo(frame, "Descrição")
        pessoa = self.criar_campo(frame, "Cliente / Fornecedor")

        categoria = ctk.CTkComboBox(
            frame,
            values=[
                "Frete",
                "Combustível",
                "Manutenção",
                "Folha",
                "Fornecedor",
                "Imposto",
                "Aluguel",
                "Pedágio",
                "Cliente",
                "Outro"
            ],
            height=40
        )
        self.criar_label(frame, "Categoria")
        categoria.pack(fill="x", padx=20, pady=(0, 8))
        categoria.set("Outro")

        valor = self.criar_campo(frame, "Valor")
        vencimento = self.criar_campo(frame, "Vencimento")
        vencimento.insert(0, datetime.now().strftime("%d/%m/%Y"))

        pagamento = self.criar_campo(frame, "Data de pagamento/recebimento")

        status = ctk.CTkComboBox(
            frame,
            values=["Pendente", "Pago", "Recebido", "Atrasado", "Cancelado"],
            height=40
        )
        self.criar_label(frame, "Status")
        status.pack(fill="x", padx=20, pady=(0, 8))
        status.set("Pendente")

        observacao = self.criar_campo(frame, "Observação")

        if dados:
            tipo.set(dados[1] or "Pagar")
            descricao.insert(0, dados[2] or "")
            pessoa.insert(0, dados[3] or "")
            categoria.set(dados[4] or "Outro")
            valor.insert(0, str(dados[5] or "").replace(".", ","))
            vencimento.delete(0, "end")
            vencimento.insert(0, dados[6] or "")
            pagamento.insert(0, dados[7] or "")
            status.set(dados[8] or "Pendente")
            observacao.insert(0, dados[9] or "")

        def salvar():
            if not descricao.get().strip():
                messagebox.showwarning("Atenção", "Informe a descrição.")
                return

            if self.numero(valor.get()) <= 0:
                messagebox.showwarning("Atenção", "Informe o valor.")
                return

            valores = (
                tipo.get(),
                descricao.get().strip(),
                pessoa.get().strip(),
                categoria.get(),
                self.numero(valor.get()),
                vencimento.get().strip(),
                pagamento.get().strip(),
                status.get(),
                observacao.get().strip()
            )

            financeiro_service.salvar_conta(conta_id, valores)

            janela.destroy()
            self.carregar_contas()
            messagebox.showinfo("Sucesso", "Conta salva com sucesso!")

        ctk.CTkButton(
            frame,
            text="Salvar Conta",
            fg_color="#16A34A",
            hover_color="#15803D",
            height=42,
            command=salvar
        ).pack(fill="x", padx=20, pady=18)

    def criar_label(self, frame, texto):
        ctk.CTkLabel(
            frame,
            text=texto,
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(8, 2))

    def criar_campo(self, frame, label):
        self.criar_label(frame, label)

        campo = ctk.CTkEntry(frame, height=40)
        campo.pack(fill="x", padx=20, pady=(0, 8))

        return campo

    def carregar_contas(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        tipo_periodo = self.tipo_periodo.get()
        mes = self.mes.get()
        ano = self.ano.get().strip()
        filtro_tipo = self.filtro_tipo.get()
        busca = self.busca.get().strip()

        dados = financeiro_service.listar_contas(
            tipo_periodo,
            mes,
            ano,
            filtro_tipo,
            busca
        )

        total_receber = 0
        total_pagar = 0
        total_pago = 0

        hoje = datetime.now().date()

        for linha in dados:
            conta_id, tipo, descricao, pessoa, categoria, valor, vencimento, pagamento, status, observacao = linha

            valor = float(valor or 0)
            status_tela = status or "Pendente"

            if status_tela == "Pendente":
                venc_data = self.converter_data(vencimento)
                if venc_data and venc_data < hoje:
                    status_tela = "Atrasado"

            if tipo == "Receber" and status_tela not in ["Recebido", "Cancelado"]:
                total_receber += valor

            if tipo == "Pagar" and status_tela not in ["Pago", "Cancelado"]:
                total_pagar += valor

            if status_tela in ["Pago", "Recebido"]:
                total_pago += valor

            self.tabela.insert("", "end", values=(
                conta_id,
                tipo,
                descricao or "",
                pessoa or "",
                categoria or "",
                self.moeda(valor),
                vencimento or "",
                pagamento or "",
                status_tela,
                observacao or ""
            ))

        saldo = total_receber - total_pagar

        self.card_receber.configure(text=self.moeda(total_receber))
        self.card_pagar.configure(text=self.moeda(total_pagar))
        self.card_pago.configure(text=self.moeda(total_pago))
        self.card_saldo.configure(text=self.moeda(saldo))

    def editar_conta(self, event=None):
        selecionado = self.tabela.selection()

        if not selecionado:
            return

        conta_id = self.tabela.item(selecionado[0], "values")[0]

        dados = financeiro_service.obter_conta(conta_id)

        if dados:
            self.abrir_modal_conta(dados)

    def marcar_pago(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma conta.")
            return

        valores = self.tabela.item(selecionado[0], "values")
        conta_id = valores[0]
        tipo = valores[1]

        novo_status = "Recebido" if tipo == "Receber" else "Pago"
        data_pagamento = datetime.now().strftime("%d/%m/%Y")

        financeiro_service.marcar_pago(conta_id, tipo, data_pagamento)

        self.carregar_contas()

    def excluir_conta(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma conta.")
            return

        conta_id = self.tabela.item(selecionado[0], "values")[0]

        confirmar = messagebox.askyesno(
            "Confirmar",
            "Deseja excluir esta conta?"
        )

        if not confirmar:
            return

        financeiro_service.excluir_conta(conta_id)

        self.carregar_contas()

    def converter_data(self, texto):
        try:
            return datetime.strptime(str(texto), "%d/%m/%Y").date()
        except:
            return None

    def numero(self, valor):
        if not valor:
            return 0.0

        valor = str(valor).replace("R$", "").replace(" ", "").strip()

        if "," in valor:
            valor = valor.replace(".", "").replace(",", ".")

        try:
            return float(valor)
        except:
            return 0.0

    def moeda(self, valor):
        return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
