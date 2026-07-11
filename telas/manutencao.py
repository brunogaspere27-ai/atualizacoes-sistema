import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime
from services.frota_service import frota_service
from config.settings import settings
from telas.theme import setup_theme, criar_header


class TelaManutencao(ctk.CTkFrame):
    def __init__(self, master):
        self.cores = setup_theme(settings)
        super().__init__(master, fg_color=self.cores["fundo"])

        self.criar_layout()
        self.carregar_manutencoes()

    def criar_layout(self):
        ff = self.cores["font_family"]
        criar_header(
            self,
            tag="MANUTENÇÃO DA FROTA",
            titulo="Manutenções",
            subtitulo="Controle de revisões, oficinas, custos e próximos vencimentos por KM.",
            cores=self.cores,
        )

        filtros = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        filtros.pack(fill="x", padx=25, pady=10)

        self.tipo_periodo = ctk.CTkComboBox(
            filtros,
            values=["Geral", "Mês", "Ano"],
            width=120,
            command=lambda e: self.carregar_manutencoes()
        )
        self.tipo_periodo.set("Geral")
        self.tipo_periodo.pack(side="left", padx=12, pady=12)

        self.mes = ctk.CTkComboBox(
            filtros,
            values=["01", "02", "03", "04", "05", "06",
                    "07", "08", "09", "10", "11", "12"],
            width=90,
            command=lambda e: self.carregar_manutencoes()
        )
        self.mes.set(datetime.now().strftime("%m"))
        self.mes.pack(side="left", padx=8)

        self.ano = ctk.CTkEntry(filtros, width=90, placeholder_text="Ano")
        self.ano.insert(0, datetime.now().strftime("%Y"))
        self.ano.pack(side="left", padx=8)
        self.ano.bind("<KeyRelease>", lambda e: self.carregar_manutencoes())

        self.busca = ctk.CTkEntry(
            filtros,
            width=260,
            placeholder_text="Buscar veículo, oficina ou tipo..."
        )
        self.busca.pack(side="left", padx=8)
        self.busca.bind("<KeyRelease>", lambda e: self.carregar_manutencoes())

        ctk.CTkButton(
            filtros,
            text="+ Nova Manutenção",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.abrir_modal_manutencao
        ).pack(side="right", padx=12)

        self.frame_resumo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_resumo.pack(fill="x", padx=25, pady=(5, 0))

        self.card_qtd = self.criar_card_resumo("Manutenções", "0")
        self.card_gasto = self.criar_card_resumo("Gasto total", "R$ 0,00")
        self.card_pendentes = self.criar_card_resumo("Pendentes", "0")
        self.card_pagas = self.criar_card_resumo("Pagas", "0")

        card = ctk.CTkFrame(self, fg_color="white", corner_radius=18)
        card.pack(fill="both", expand=True, padx=25, pady=12)

        colunas = (
            "id", "data", "veiculo", "km", "tipo", "oficina",
            "valor", "prox_revisao", "status", "descricao"
        )

        self.tabela = ttk.Treeview(card, columns=colunas, show="headings", height=17)

        titulos = {
            "id": "ID",
            "data": "Data",
            "veiculo": "Veículo",
            "km": "KM Atual",
            "tipo": "Tipo",
            "oficina": "Oficina",
            "valor": "Valor",
            "prox_revisao": "Próx. Revisão",
            "status": "Status",
            "descricao": "Descrição"
        }

        for col in colunas:
            self.tabela.heading(col, text=titulos[col])
            self.tabela.column(col, anchor="center", width=110)

        self.tabela.column("id", width=45)
        self.tabela.column("veiculo", width=170)
        self.tabela.column("descricao", width=220)
        self.tabela.column("oficina", width=150)

        self.tabela.pack(fill="both", expand=True, padx=15, pady=15)
        self.tabela.bind("<Double-1>", self.editar_manutencao)

        rodape = ctk.CTkFrame(card, fg_color="transparent")
        rodape.pack(fill="x", padx=15, pady=(0, 15))

        ctk.CTkButton(
            rodape,
            text="Excluir",
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self.excluir_manutencao
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            rodape,
            text="Atualizar",
            fg_color="#111827",
            hover_color="#374151",
            command=self.carregar_manutencoes
        ).pack(side="right", padx=5)

    def criar_card_resumo(self, titulo, valor):
        card = ctk.CTkFrame(self.frame_resumo, fg_color="white", corner_radius=16)
        card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=(self.cores["font_family"], 12),
            text_color="#6B7280"
        ).pack(pady=(10, 0))

        label = ctk.CTkLabel(
            card,
            text=valor,
            font=(self.cores["font_family"], 20, "bold"),
            text_color="#111827"
        )
        label.pack(pady=(2, 10))

        return label

    def abrir_modal_manutencao(self, dados=None):
        janela = ctk.CTkToplevel(self)
        janela.title("Manutenção")
        janela.geometry("580x760")
        janela.grab_set()

        manutencao_id = dados[0] if dados else None

        ctk.CTkLabel(
            janela,
            text="Cadastro de Manutenção",
            font=(self.cores["font_family"], 24, "bold")
        ).pack(pady=(20, 10))

        frame = ctk.CTkFrame(janela, fg_color="white", corner_radius=18)
        frame.pack(fill="both", expand=True, padx=20, pady=15)

        veiculos = self.buscar_veiculos()

        data = self.criar_campo(frame, "Data")
        data.insert(0, datetime.now().strftime("%d/%m/%Y"))

        ctk.CTkLabel(
            frame,
            text="Veículo",
            font=(self.cores["font_family"], 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(8, 2))

        linha_veiculo = ctk.CTkFrame(frame, fg_color="transparent")
        linha_veiculo.pack(fill="x", padx=20, pady=(0, 8))

        veiculo = ctk.CTkComboBox(
            linha_veiculo,
            values=veiculos,
            height=40
        )
        veiculo.pack(side="left", fill="x", expand=True)

        def adicionar_veiculo():
            novo = ctk.CTkInputDialog(
                text="Digite o nome do novo veículo:",
                title="Novo veículo"
            ).get_input()

            if novo and novo.strip():
                novo = novo.strip()

                if novo not in veiculos:
                    veiculos.append(novo)

                veiculo.configure(values=veiculos)
                veiculo.set(novo)

        ctk.CTkButton(
            linha_veiculo,
            text="+",
            width=42,
            height=40,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=adicionar_veiculo
        ).pack(side="right", padx=(8, 0))

        if veiculos:
            veiculo.set(veiculos[0])

        km_atual = self.criar_campo(frame, "KM atual")

        tipo = ctk.CTkComboBox(
            frame,
            values=[
                "Preventiva",
                "Corretiva",
                "Troca de óleo",
                "Pneus",
                "Freios",
                "Suspensão",
                "Elétrica",
                "Motor",
                "Revisão geral",
                "Outro"
            ],
            height=40
        )

        ctk.CTkLabel(
            frame,
            text="Tipo de manutenção",
            font=(self.cores["font_family"], 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(8, 2))
        tipo.pack(fill="x", padx=20, pady=(0, 8))
        tipo.set("Preventiva")

        descricao = self.criar_campo(frame, "Descrição")
        oficina = self.criar_campo(frame, "Oficina / Fornecedor")
        valor = self.criar_campo(frame, "Valor")
        proxima_revisao = self.criar_campo(frame, "Próxima revisão em KM")

        status = ctk.CTkComboBox(
            frame,
            values=["Pendente", "Pago", "Agendado", "Cancelado"],
            height=40
        )

        ctk.CTkLabel(
            frame,
            text="Status",
            font=(self.cores["font_family"], 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(8, 2))
        status.pack(fill="x", padx=20, pady=(0, 8))
        status.set("Pendente")

        observacao = self.criar_campo(frame, "Observação")

        if dados:
            data.delete(0, "end")
            data.insert(0, dados[1] or "")
            veiculo.set(dados[2] or "")
            km_atual.insert(0, str(dados[3] or "").replace(".", ","))
            tipo.set(dados[4] or "Preventiva")
            descricao.insert(0, dados[5] or "")
            oficina.insert(0, dados[6] or "")
            valor.insert(0, str(dados[7] or "").replace(".", ","))
            proxima_revisao.insert(0, str(dados[8] or "").replace(".", ","))
            status.set(dados[9] or "Pendente")
            observacao.insert(0, dados[10] or "")

        def salvar():
            if not data.get().strip():
                messagebox.showwarning("Atenção", "Informe a data.")
                return

            if not veiculo.get().strip():
                messagebox.showwarning("Atenção", "Informe o veículo.")
                return

            valores = (
                data.get().strip(),
                veiculo.get().strip(),
                self.numero(km_atual.get()),
                tipo.get(),
                descricao.get().strip(),
                oficina.get().strip(),
                self.numero(valor.get()),
                self.numero(proxima_revisao.get()),
                status.get(),
                observacao.get().strip()
            )

            frota_service.salvar_manutencao(manutencao_id, valores)

            janela.destroy()
            self.carregar_manutencoes()
            messagebox.showinfo("Sucesso", "Manutenção salva com sucesso!")

        ctk.CTkButton(
            frame,
            text="Salvar Manutenção",
            fg_color="#16A34A",
            hover_color="#15803D",
            height=42,
            command=salvar
        ).pack(fill="x", padx=20, pady=18)

    def criar_campo(self, frame, label):
        ctk.CTkLabel(
            frame,
            text=label,
            font=(self.cores["font_family"], 13, "bold"),
            text_color="#374151"
        ).pack(anchor="w", padx=20, pady=(8, 2))

        campo = ctk.CTkEntry(frame, height=40)
        campo.pack(fill="x", padx=20, pady=(0, 8))

        return campo

    def carregar_manutencoes(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        tipo_periodo = self.tipo_periodo.get()
        mes = self.mes.get()
        ano = self.ano.get().strip()
        busca = self.busca.get().strip()

        dados = frota_service.listar_manutencoes(tipo_periodo, mes, ano, busca)

        total_gasto = 0
        pendentes = 0
        pagas = 0

        for linha in dados:
            valor = float(linha[7] or 0)
            status = linha[9] or "Pendente"

            total_gasto += valor

            if status == "Pago":
                pagas += 1
            elif status == "Pendente":
                pendentes += 1

            self.tabela.insert("", "end", values=(
                linha[0],
                linha[1],
                linha[2] or "",
                self.formatar_numero(linha[3]),
                linha[4] or "",
                linha[6] or "",
                self.moeda(linha[7]),
                self.formatar_numero(linha[8]),
                status,
                linha[5] or ""
            ))

        self.card_qtd.configure(text=str(len(dados)))
        self.card_gasto.configure(text=self.moeda(total_gasto))
        self.card_pendentes.configure(text=str(pendentes))
        self.card_pagas.configure(text=str(pagas))

    def editar_manutencao(self, event=None):
        selecionado = self.tabela.selection()

        if not selecionado:
            return

        manutencao_id = self.tabela.item(selecionado[0], "values")[0]

        dados = frota_service.obter_manutencao(manutencao_id)

        if dados:
            self.abrir_modal_manutencao(dados)

    def excluir_manutencao(self):
        selecionado = self.tabela.selection()

        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma manutenção.")
            return

        manutencao_id = self.tabela.item(selecionado[0], "values")[0]

        confirmar = messagebox.askyesno(
            "Confirmar",
            "Deseja excluir esta manutenção?"
        )

        if not confirmar:
            return

        frota_service.excluir_manutencao(manutencao_id)

        self.carregar_manutencoes()

    def buscar_veiculos(self):
        return frota_service.listar_veiculos_disponiveis("manutencoes")

    def numero(self, valor: str) -> float:
        """Converte string para float tratando separadores BR."""
        from utils.helpers import parse_numero
        return parse_numero(str(valor).replace("R$", "").strip())

    def moeda(self, valor) -> str:
        from utils.helpers import formatar_moeda
        return formatar_moeda(valor)

    def formatar_numero(self, valor) -> str:
        v = float(valor or 0)
        return str(int(v)) if v == int(v) else f"{v:.2f}".replace(".", ",")
