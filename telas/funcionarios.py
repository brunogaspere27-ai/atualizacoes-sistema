import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.database import criar_banco
from services.funcionarios_service import funcionarios_service


class TelaFuncionarios(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#F4F6F8")

        self.modo_tela = "funcionarios"

        criar_banco()
        self.criar_layout_principal()

    def limpar_tela(self):
        for widget in self.winfo_children():
            widget.destroy()

    # =========================
    # TELA FUNCIONÁRIOS
    # =========================

    def criar_layout_principal(self):
        self.modo_tela = "funcionarios"
        self.limpar_tela()

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(
            topo,
            text="Funcionários",
            font=("Arial", 28, "bold"),
            text_color="#111827"
        ).pack(side="left")

        ctk.CTkButton(
            topo,
            text="Ver Folha do Mês",
            fg_color="#16A34A",
            hover_color="#15803D",
            height=40,
            command=self.criar_layout_folha_mes
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            topo,
            text="+ Criar Funcionário",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=40,
            command=self.abrir_modal_funcionario
        ).pack(side="right", padx=5)

        filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        filtros.pack(fill="x", padx=25, pady=10)

        self.busca_funcionario = ctk.CTkEntry(
            filtros,
            placeholder_text="Buscar funcionário...",
            width=300,
            height=38
        )
        self.busca_funcionario.pack(side="left", padx=12, pady=12)
        self.busca_funcionario.bind("<KeyRelease>", lambda e: self.carregar_funcionarios())

        ctk.CTkButton(
            filtros,
            text="Atualizar",
            fg_color="#111827",
            hover_color="#374151",
            command=self.carregar_funcionarios
        ).pack(side="left", padx=8)

        card = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        colunas = (
            "id",
            "nome",
            "cargo",
            "telefone",
            "admissao",
            "salario",
            "vale",
            "status"
        )

        self.tabela_funcionarios = ttk.Treeview(card, columns=colunas, show="headings", height=16)

        titulos = {
            "id": "ID",
            "nome": "Funcionário",
            "cargo": "Cargo",
            "telefone": "Telefone",
            "admissao": "Admissão",
            "salario": "Salário",
            "vale": "Vale Refeição",
            "status": "Status"
        }

        for col in colunas:
            self.tabela_funcionarios.heading(col, text=titulos[col])
            self.tabela_funcionarios.column(col, anchor="center", width=120)

        self.tabela_funcionarios.column("id", width=50)
        self.tabela_funcionarios.column("nome", width=230)
        self.tabela_funcionarios.column("cargo", width=160)

        self.tabela_funcionarios.pack(fill="both", expand=True, padx=15, pady=15)
        self.tabela_funcionarios.bind("<Double-1>", lambda e: self.editar_cadastro_selecionado())

        rodape = ctk.CTkFrame(card, fg_color="transparent")
        rodape.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            rodape,
            text="Editar Cadastro",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.editar_cadastro_selecionado
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            rodape,
            text="Excluir",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.excluir_funcionario
        ).pack(side="right", padx=5)

        self.carregar_funcionarios()

    def carregar_funcionarios(self):
        for item in self.tabela_funcionarios.get_children():
            self.tabela_funcionarios.delete(item)

        busca = self.busca_funcionario.get().strip()

        dados = funcionarios_service.listar_funcionarios(busca)

        for linha in dados:
            self.tabela_funcionarios.insert("", "end", values=(
                linha[0],
                linha[1],
                linha[2] or "",
                linha[3] or "",
                linha[4] or "",
                self.formatar_moeda(linha[5]),
                self.formatar_moeda(linha[6]),
                linha[7] or "Ativo"
            ))

    # =========================
    # TELA FOLHA DO MÊS
    # =========================

    def criar_layout_folha_mes(self):
        self.modo_tela = "folha"
        self.limpar_tela()

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkButton(
            topo,
            text="← Voltar",
            fg_color="#6B7280",
            hover_color="#4B5563",
            height=38,
            width=100,
            command=self.criar_layout_principal
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            topo,
            text="Folha do Mês",
            font=("Arial", 28, "bold"),
            text_color="#111827"
        ).pack(side="left")

        filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        filtros.pack(fill="x", padx=25, pady=10)

        self.mes_folha = ctk.CTkComboBox(
            filtros,
            values=[
                "01", "02", "03", "04", "05", "06",
                "07", "08", "09", "10", "11", "12"
            ],
            width=90,
            command=lambda e: self.carregar_folha_mes()
        )
        self.mes_folha.set(datetime.now().strftime("%m"))
        self.mes_folha.pack(side="left", padx=12, pady=12)

        self.ano_folha = ctk.CTkEntry(filtros, width=100, placeholder_text="Ano")
        self.ano_folha.insert(0, datetime.now().strftime("%Y"))
        self.ano_folha.pack(side="left", padx=8)
        self.ano_folha.bind("<KeyRelease>", lambda e: self.carregar_folha_mes())

        self.busca_folha = ctk.CTkEntry(
            filtros,
            placeholder_text="Buscar na folha...",
            width=230,
            height=38
        )
        self.busca_folha.pack(side="left", padx=8)
        self.busca_folha.bind("<KeyRelease>", lambda e: self.carregar_folha_mes())

        ctk.CTkButton(
            filtros,
            text="Gerar / Atualizar Folha do Mês",
            fg_color="#16A34A",
            hover_color="#15803D",
            height=38,
            command=self.gerar_folha_todos
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            filtros,
            text="Atualizar",
            fg_color="#111827",
            hover_color="#374151",
            height=38,
            command=self.carregar_folha_mes
        ).pack(side="left", padx=8)

        self.card_resumo = ctk.CTkFrame(self, fg_color="transparent")
        self.card_resumo.pack(fill="x", padx=25, pady=(5, 0))

        self.label_total_funcionarios = self.criar_card_resumo("Funcionários na folha", "0")
        self.label_total_horas = self.criar_card_resumo("Horas extras", "0")
        self.label_total_hora_extra = self.criar_card_resumo("Total hora extra", "R$ 0,00")
        self.label_total_folha = self.criar_card_resumo("Total folha", "R$ 0,00")

        card = ctk.CTkFrame(self, fg_color="white", corner_radius=16)
        card.pack(fill="both", expand=True, padx=25, pady=10)

        colunas = (
            "id",
            "nome",
            "cargo",
            "salario",
            "vale",
            "qtd_horas",
            "valor_hora",
            "total_hora_extra",
            "outros",
            "total",
            "status"
        )

        self.tabela_folha = ttk.Treeview(card, columns=colunas, show="headings", height=16)

        titulos = {
            "id": "ID",
            "nome": "Funcionário",
            "cargo": "Cargo",
            "salario": "Salário",
            "vale": "Vale",
            "qtd_horas": "Horas",
            "valor_hora": "Valor Hora",
            "total_hora_extra": "Total H. Extra",
            "outros": "Outros",
            "total": "Total Folha",
            "status": "Status"
        }

        for col in colunas:
            self.tabela_folha.heading(col, text=titulos[col])
            self.tabela_folha.column(col, anchor="center", width=110)

        self.tabela_folha.column("id", width=50)
        self.tabela_folha.column("nome", width=210)
        self.tabela_folha.column("cargo", width=150)
        self.tabela_folha.column("total_hora_extra", width=130)

        self.tabela_folha.pack(fill="both", expand=True, padx=15, pady=15)
        self.tabela_folha.bind("<Double-1>", self.abrir_modal_hora_extra)

        rodape = ctk.CTkFrame(card, fg_color="transparent")
        rodape.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            rodape,
            text="Lançar Hora Extra",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.abrir_modal_hora_extra
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            rodape,
            text="Remover da Folha",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.remover_da_folha
        ).pack(side="right", padx=5)

        self.carregar_folha_mes()

    def criar_card_resumo(self, titulo, valor):
        card = ctk.CTkFrame(self.card_resumo, fg_color="white", corner_radius=14)
        card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 13),
            text_color="#6B7280"
        ).pack(pady=(10, 0))

        label_valor = ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 20, "bold"),
            text_color="#111827"
        )
        label_valor.pack(pady=(2, 10))

        return label_valor

    def carregar_folha_mes(self):
        for item in self.tabela_folha.get_children():
            self.tabela_folha.delete(item)

        mes = self.mes_folha.get()
        ano = self.ano_folha.get().strip()
        busca = self.busca_folha.get().strip()

        if not ano:
            return

        dados = funcionarios_service.listar_folha_mes(mes, ano, busca)

        total_funcionarios = len(dados)
        total_horas = 0
        total_hora_extra = 0
        total_folha = 0

        for linha in dados:
            total_horas += float(linha[5] or 0)
            total_hora_extra += float(linha[7] or 0)
            total_folha += float(linha[9] or 0)

            self.tabela_folha.insert("", "end", values=(
                linha[0],
                linha[1],
                linha[2] or "",
                self.formatar_moeda(linha[3]),
                self.formatar_moeda(linha[4]),
                self.formatar_numero(linha[5]),
                self.formatar_moeda(linha[6]),
                self.formatar_moeda(linha[7]),
                self.formatar_moeda(linha[8]),
                self.formatar_moeda(linha[9]),
                linha[10] or "Ativo"
            ))

        self.label_total_funcionarios.configure(text=str(total_funcionarios))
        self.label_total_horas.configure(text=self.formatar_numero(total_horas))
        self.label_total_hora_extra.configure(text=self.formatar_moeda(total_hora_extra))
        self.label_total_folha.configure(text=self.formatar_moeda(total_folha))

    def gerar_folha_todos(self):
        mes = self.mes_folha.get()
        ano = self.ano_folha.get().strip()

        if not ano:
            messagebox.showwarning("Atenção", "Informe o ano.")
            return

        confirmar = messagebox.askyesno(
            "Gerar folha",
            f"Deseja gerar/atualizar a folha de todos os funcionários ativos para {mes}/{ano}?"
        )

        if not confirmar:
            return

        funcionarios = funcionarios_service.listar_funcionarios_ativos()

        if not funcionarios:
            messagebox.showwarning("Atenção", "Nenhum funcionário ativo encontrado.")
            return
        total_gerados = funcionarios_service.gerar_folha_todos(mes, ano)

        self.carregar_folha_mes()

        messagebox.showinfo(
            "Sucesso",
            f"Folha de {total_gerados} funcionários gerada para {mes}/{ano}."
        )

    def abrir_modal_hora_extra(self, event=None):
        selecionado = self.tabela_folha.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um funcionário da folha.")
            return

        valores = self.tabela_folha.item(selecionado[0], "values")
        funcionario_id = valores[0]
        nome_funcionario = valores[1]

        mes = self.mes_folha.get()
        ano = self.ano_folha.get().strip()

        folha = funcionarios_service.obter_folha_funcionario(funcionario_id, mes, ano)

        if not folha:
            messagebox.showwarning(
                "Atenção",
                "Esse funcionário ainda não está na folha. Clique em Gerar/Atualizar Folha do Mês."
            )
            return

        salario = folha[1] or 0
        vale = folha[2] or 0
        qtd_atual = folha[3] or ""
        valor_hora_atual = folha[4] or ""
        outros_atual = folha[6] or ""

        janela = ctk.CTkToplevel(self)
        janela.title("Hora Extra")
        janela.geometry("480x540")
        janela.grab_set()

        ctk.CTkLabel(
            janela,
            text=f"Folha de {nome_funcionario}",
            font=("Arial", 22, "bold")
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            janela,
            text=f"Referência: {mes}/{ano}",
            font=("Arial", 14),
            text_color="#6B7280"
        ).pack(pady=(0, 15))

        frame = ctk.CTkFrame(janela, fg_color="white", corner_radius=16)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            frame,
            text="Quantidade de horas extras",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(20, 2))

        entrada_qtd = ctk.CTkEntry(frame, placeholder_text="Ex: 10", height=40)
        entrada_qtd.pack(fill="x", padx=20, pady=(0, 10))

        if qtd_atual not in ("", None, 0):
            entrada_qtd.insert(0, str(qtd_atual).replace(".", ","))

        ctk.CTkLabel(
            frame,
            text="Valor de cada hora extra",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(5, 2))

        entrada_valor_hora = ctk.CTkEntry(frame, placeholder_text="Ex: 25,00", height=40)
        entrada_valor_hora.pack(fill="x", padx=20, pady=(0, 10))

        if valor_hora_atual not in ("", None, 0):
            entrada_valor_hora.insert(0, str(valor_hora_atual).replace(".", ","))

        ctk.CTkLabel(
            frame,
            text="Outros adicionais ou descontos",
            font=("Arial", 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(5, 2))

        entrada_outros = ctk.CTkEntry(frame, placeholder_text="Ex: 100,00 ou -50,00", height=40)
        entrada_outros.pack(fill="x", padx=20, pady=(0, 10))

        if outros_atual not in ("", None, 0):
            entrada_outros.insert(0, str(outros_atual).replace(".", ","))

        label_total = ctk.CTkLabel(
            frame,
            text="",
            font=("Arial", 17, "bold"),
            text_color="#111827"
        )
        label_total.pack(pady=15)

        def atualizar_total(event=None):
            qtd = self.moeda_para_float(entrada_qtd.get())
            valor_hora = self.moeda_para_float(entrada_valor_hora.get())
            outros = self.moeda_para_float(entrada_outros.get())

            total_hora_extra = qtd * valor_hora
            total = float(salario or 0) + float(vale or 0) + total_hora_extra + outros

            label_total.configure(
                text=(
                    f"Hora extra: {self.formatar_moeda(total_hora_extra)}\n"
                    f"Total da folha: {self.formatar_moeda(total)}"
                )
            )

        entrada_qtd.bind("<KeyRelease>", atualizar_total)
        entrada_valor_hora.bind("<KeyRelease>", atualizar_total)
        entrada_outros.bind("<KeyRelease>", atualizar_total)

        atualizar_total()

        def salvar():
            qtd = self.moeda_para_float(entrada_qtd.get())
            valor_hora = self.moeda_para_float(entrada_valor_hora.get())
            outros = self.moeda_para_float(entrada_outros.get())

            salario_float = float(salario or 0)
            vale_float = float(vale or 0)
            total_hora_extra = qtd * valor_hora
            total = salario_float + vale_float + total_hora_extra + outros

            funcionarios_service.salvar_hora_extra(
                funcionario_id,
                mes,
                ano,
                qtd,
                valor_hora,
                outros
            )

            janela.destroy()
            self.carregar_folha_mes()

            messagebox.showinfo("Sucesso", "Lançamento salvo na folha!")

        ctk.CTkButton(
            frame,
            text="Salvar na Folha",
            fg_color="#16A34A",
            hover_color="#15803D",
            height=42,
            command=salvar
        ).pack(fill="x", padx=20, pady=15)

    def remover_da_folha(self):
        selecionado = self.tabela_folha.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um funcionário da folha.")
            return

        valores = self.tabela_folha.item(selecionado[0], "values")
        funcionario_id = valores[0]
        nome = valores[1]

        mes = self.mes_folha.get()
        ano = self.ano_folha.get().strip()

        confirmar = messagebox.askyesno(
            "Remover da folha",
            f"Deseja remover {nome} da folha {mes}/{ano}?"
        )

        if not confirmar:
            return

        funcionarios_service.remover_da_folha(funcionario_id, mes, ano)

        self.carregar_folha_mes()

    # =========================
    # CADASTRO FUNCIONÁRIO
    # =========================

    def abrir_modal_funcionario(self, funcionario=None):
        janela = ctk.CTkToplevel(self)
        janela.title("Funcionário")
        janela.geometry("520x520")
        janela.grab_set()

        funcionario_id = funcionario[0] if funcionario else None

        ctk.CTkLabel(
            janela,
            text="Cadastro de Funcionário",
            font=("Arial", 24, "bold")
        ).pack(pady=(20, 10))

        frame = ctk.CTkFrame(janela, fg_color="white", corner_radius=16)
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        nome = ctk.CTkEntry(frame, placeholder_text="Nome do funcionário", height=40)
        cargo = ctk.CTkEntry(frame, placeholder_text="Cargo", height=40)
        telefone = ctk.CTkEntry(frame, placeholder_text="Telefone", height=40)
        data_admissao = ctk.CTkEntry(frame, placeholder_text="Data admissão", height=40)
        salario = ctk.CTkEntry(frame, placeholder_text="Salário", height=40)
        vale = ctk.CTkEntry(frame, placeholder_text="Vale refeição", height=40)

        status = ctk.CTkComboBox(frame, values=["Ativo", "Inativo"], height=40)
        status.set("Ativo")

        campos = [nome, cargo, telefone, data_admissao, salario, vale, status]

        for campo in campos:
            campo.pack(fill="x", padx=20, pady=8)

        if funcionario:
            nome.insert(0, funcionario[1] or "")
            cargo.insert(0, funcionario[2] or "")
            telefone.insert(0, funcionario[3] or "")
            data_admissao.insert(0, funcionario[4] or "")
            salario.insert(0, str(funcionario[5] or "").replace(".", ","))
            vale.insert(0, str(funcionario[6] or "").replace(".", ","))
            status.set(funcionario[7] or "Ativo")

        def salvar():
            if not nome.get().strip():
                messagebox.showwarning("Atenção", "Informe o nome do funcionário.")
                return

            dados = (
                nome.get().strip(),
                cargo.get().strip(),
                telefone.get().strip(),
                data_admissao.get().strip(),
                self.moeda_para_float(salario.get()),
                self.moeda_para_float(vale.get()),
                status.get()
            )

            funcionarios_service.salvar_funcionario(funcionario_id, dados)

            janela.destroy()

            if self.modo_tela == "funcionarios":
                self.carregar_funcionarios()
            else:
                self.carregar_folha_mes()

            messagebox.showinfo("Sucesso", "Funcionário salvo com sucesso!")

        ctk.CTkButton(
            frame,
            text="Salvar",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            height=42,
            command=salvar
        ).pack(fill="x", padx=20, pady=15)

    def editar_cadastro_selecionado(self):
        selecionado = self.tabela_funcionarios.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um funcionário.")
            return

        valores = self.tabela_funcionarios.item(selecionado[0], "values")
        funcionario_id = valores[0]

        funcionario = funcionarios_service.obter_funcionario(funcionario_id)

        if funcionario:
            self.abrir_modal_funcionario(funcionario)

    def excluir_funcionario(self):
        selecionado = self.tabela_funcionarios.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione um funcionário.")
            return

        valores = self.tabela_funcionarios.item(selecionado[0], "values")
        funcionario_id = valores[0]
        nome = valores[1]

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Deseja excluir {nome}?"
        )

        if not confirmar:
            return

        funcionarios_service.excluir_funcionario(funcionario_id)

        self.carregar_funcionarios()

    # =========================
    # UTILITÁRIOS
    # =========================

    def moeda_para_float(self, valor):
        if not valor:
            return 0.0

        valor = str(valor).strip()
        valor = valor.replace("R$", "")
        valor = valor.replace(" ", "")

        if "," in valor:
            valor = valor.replace(".", "").replace(",", ".")

        try:
            return float(valor)
        except ValueError:
            return 0.0

    def formatar_moeda(self, valor):
        return f"R$ {float(valor or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def formatar_numero(self, valor):
        valor = float(valor or 0)

        if valor.is_integer():
            return str(int(valor))

        return str(valor).replace(".", ",")
