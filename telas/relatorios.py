import os
import tempfile
from datetime import datetime

import customtkinter as ctk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm

from utils.helpers import formatar_moeda, formatar_peso
from config.settings import settings
from telas.theme import setup_theme
from services.relatorios_service import relatorios_service


class TelaRelatorios(ctk.CTkFrame):
    def __init__(self, master):
        cores = setup_theme(settings)
        super().__init__(master, fg_color=cores["fundo"])
        self.cores = cores

        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")

        self.criar_layout()
        self.carregar_relatorio()

    def criar_layout(self):
        topo = ctk.CTkFrame(self, fg_color=self.cores["sidebar"], corner_radius=20)
        topo.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(
            topo,
            text="RELATÓRIOS GERENCIAIS",
            font=("Segoe UI", 12, "bold"),
            text_color=self.cores["principal"]
        ).pack(anchor="w", padx=24, pady=(18, 0))

        ctk.CTkLabel(
            topo,
            text="Central de Relatórios",
            font=("Segoe UI", 32, "bold"),
            text_color=self.cores["card_text"]
        ).pack(anchor="w", padx=24)

        ctk.CTkLabel(
            topo,
            text="Resumo completo de notas, fretes, folha, combustível, manutenção, contas e clientes.",
            font=("Segoe UI", 13),
            text_color=self.cores["texto_suave"]
        ).pack(anchor="w", padx=24, pady=(0, 18))

        filtros = ctk.CTkFrame(self, fg_color=self.cores["card_bg"], corner_radius=18, border_width=1, border_color=self.cores["muted_border"])
        filtros.pack(fill="x", padx=25, pady=10)

        self.combo_periodo = ctk.CTkComboBox(
            filtros,
            values=["Geral", "Mês", "Ano"],
            width=120,
            command=lambda e: self.carregar_relatorio()
        )
        self.combo_periodo.set(self.tipo_periodo)
        self.combo_periodo.pack(side="left", padx=12, pady=12)

        self.combo_mes = ctk.CTkComboBox(
            filtros,
            values=[
                "01", "02", "03", "04", "05", "06",
                "07", "08", "09", "10", "11", "12"
            ],
            width=90,
            command=lambda e: self.carregar_relatorio()
        )
        self.combo_mes.set(self.mes)
        self.combo_mes.pack(side="left", padx=8)

        self.entry_ano = ctk.CTkEntry(filtros, width=90, placeholder_text="Ano")
        self.entry_ano.insert(0, self.ano)
        self.entry_ano.pack(side="left", padx=8)
        self.entry_ano.bind("<KeyRelease>", lambda e: self.carregar_relatorio())

        ctk.CTkButton(
            filtros,
            text="Atualizar",
            fg_color=self.cores["sidebar"],
            hover_color=self.cores["hover"],
            command=self.carregar_relatorio
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            filtros,
            text="📄 Gerar PDF",
            fg_color=self.cores["principal"],
            hover_color=self.cores["hover"],
            command=self.gerar_pdf
        ).pack(side="right", padx=12)

        self.frame_resumo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_resumo.pack(fill="x", padx=25, pady=(5, 0))

        self.cards = {}

        nomes_cards = [
            "Receitas",
            "Despesas",
            "Lucro",
            "Valor Notas",
            "Frete Notas",
            "Frete Viagens",
            "A Receber",
            "A Pagar"
        ]

        for nome in nomes_cards:
            self.cards[nome] = self.criar_card_resumo(nome, "R$ 0,00")

        abas = ctk.CTkTabview(self, fg_color=self.cores["card_bg"], corner_radius=18)
        abas.pack(fill="both", expand=True, padx=25, pady=15)

        self.aba_geral = abas.add("Resumo")
        self.aba_clientes = abas.add("Clientes")
        self.aba_viagens = abas.add("Viagens")
        self.aba_custos = abas.add("Custos")
        self.aba_contas = abas.add("Contas")

        self.criar_tabela_resumo()
        self.criar_tabela_clientes()
        self.criar_tabela_viagens()
        self.criar_tabela_custos()
        self.criar_tabela_contas()

    def criar_card_resumo(self, titulo, valor):
        card = ctk.CTkFrame(self.frame_resumo, fg_color=self.cores["header"], corner_radius=16, border_width=1, border_color=self.cores["muted_border"])
        card.pack(side="left", fill="x", expand=True, padx=5, pady=5)

        ctk.CTkLabel(
            card,
            text=titulo,
            font=("Segoe UI", 11),
            text_color=self.cores["texto_suave"]
        ).pack(pady=(10, 0))

        label = ctk.CTkLabel(
            card,
            text=valor,
            font=("Segoe UI", 17, "bold"),
            text_color=self.cores["texto"]
        )
        label.pack(pady=(2, 10))

        return label

    def criar_tabela(self, master, colunas, titulos):
        tabela = ttk.Treeview(master, columns=colunas, show="headings", height=16)

        for col in colunas:
            tabela.heading(col, text=titulos[col])
            tabela.column(col, anchor="center", width=130)

        tabela.pack(fill="both", expand=True, padx=15, pady=15)
        return tabela

    def criar_tabela_resumo(self):
        colunas = ("descricao", "valor")
        titulos = {
            "descricao": "Indicador",
            "valor": "Valor"
        }

        self.tabela_resumo = self.criar_tabela(self.aba_geral, colunas, titulos)
        self.tabela_resumo.column("descricao", width=360)

    def criar_tabela_clientes(self):
        colunas = ("posicao", "cliente", "notas", "valor", "frete", "peso")
        titulos = {
            "posicao": "#",
            "cliente": "Cliente",
            "notas": "Notas",
            "valor": "Valor Notas",
            "frete": "Frete",
            "peso": "Peso"
        }

        self.tabela_clientes = self.criar_tabela(self.aba_clientes, colunas, titulos)
        self.tabela_clientes.column("cliente", width=300)

    def criar_tabela_viagens(self):
        colunas = ("id", "data", "veiculo", "motorista", "status", "peso", "frete", "notas")
        titulos = {
            "id": "ID",
            "data": "Data",
            "veiculo": "Veículo",
            "motorista": "Motorista",
            "status": "Status",
            "peso": "Peso",
            "frete": "Frete",
            "notas": "Notas"
        }

        self.tabela_viagens = self.criar_tabela(self.aba_viagens, colunas, titulos)
        self.tabela_viagens.column("veiculo", width=220)

    def criar_tabela_custos(self):
        colunas = ("tipo", "data", "veiculo", "descricao", "valor", "status")
        titulos = {
            "tipo": "Tipo",
            "data": "Data",
            "veiculo": "Veículo",
            "descricao": "Descrição",
            "valor": "Valor",
            "status": "Status"
        }

        self.tabela_custos = self.criar_tabela(self.aba_custos, colunas, titulos)
        self.tabela_custos.column("descricao", width=300)

    def criar_tabela_contas(self):
        colunas = ("tipo", "descricao", "pessoa", "categoria", "valor", "vencimento", "status")
        titulos = {
            "tipo": "Tipo",
            "descricao": "Descrição",
            "pessoa": "Cliente/Fornecedor",
            "categoria": "Categoria",
            "valor": "Valor",
            "vencimento": "Vencimento",
            "status": "Status"
        }

        self.tabela_contas = self.criar_tabela(self.aba_contas, colunas, titulos)
        self.tabela_contas.column("descricao", width=260)
        self.tabela_contas.column("pessoa", width=230)

    def carregar_relatorio(self):
        self.tipo_periodo = self.combo_periodo.get()
        self.mes = self.combo_mes.get()
        self.ano = self.entry_ano.get().strip()

        payload = relatorios_service.carregar_relatorio(self.tipo_periodo, self.mes, self.ano)
        dados = payload["dados"]
        extras = payload["extras"]
        ranking = payload["ranking"]
        receitas = payload["receitas"]
        despesas = payload["despesas"]
        lucro = payload["lucro"]

        self.cards["Receitas"].configure(text=self.moeda(receitas))
        self.cards["Despesas"].configure(text=self.moeda(despesas))
        self.cards["Lucro"].configure(text=self.moeda(lucro))
        self.cards["Valor Notas"].configure(text=self.moeda(extras["valor_notas"]))
        self.cards["Frete Notas"].configure(text=self.moeda(extras["frete_notas"]))
        self.cards["Frete Viagens"].configure(text=self.moeda(dados["frete_total"]))
        self.cards["A Receber"].configure(text=self.moeda(extras["contas_a_receber"]))
        self.cards["A Pagar"].configure(text=self.moeda(extras["contas_a_pagar"]))

        self.preencher_resumo(dados, extras, receitas, despesas, lucro)
        self.preencher_clientes(ranking)
        self.preencher_viagens()
        self.preencher_custos(extras)
        self.preencher_contas(extras)

    def preencher_resumo(self, dados, extras, receitas, despesas, lucro):
        self.limpar_tabela(self.tabela_resumo)

        linhas = [
            ("Receitas totais", self.moeda(receitas)),
            ("Despesas totais", self.moeda(despesas)),
            ("Lucro estimado", self.moeda(lucro)),
            ("Valor total das notas", self.moeda(extras["valor_notas"])),
            ("Frete total das notas", self.moeda(extras["frete_notas"])),
            ("Frete total das viagens", self.moeda(dados["frete_total"])),
            ("Contas recebidas", self.moeda(extras["contas_recebidas"])),
            ("Contas pagas", self.moeda(extras["contas_pagas"])),
            ("Contas a receber", self.moeda(extras["contas_a_receber"])),
            ("Contas a pagar", self.moeda(extras["contas_a_pagar"])),
            ("Folha de pagamento", self.moeda(extras["folha"])),
            ("Combustível", self.moeda(extras["combustivel"])),
            ("Manutenção", self.moeda(extras["manutencao"])),
            ("Manifestos importados", dados["total_manifestos"]),
            ("Notas importadas", dados["total_notas"]),
            ("Viagens criadas", dados["total_viagens"]),
            ("Peso transportado", self.peso(dados["peso_total"])),
        ]

        for linha in linhas:
            self.tabela_resumo.insert("", "end", values=linha)

    def preencher_clientes(self, ranking):
        self.limpar_tabela(self.tabela_clientes)

        for i, cliente in enumerate(ranking[:30], start=1):
            self.tabela_clientes.insert("", "end", values=(
                i,
                cliente.get("cliente"),
                cliente.get("total_notas"),
                self.moeda(cliente.get("valor_notas")),
                self.moeda(cliente.get("frete")),
                self.peso(cliente.get("peso"))
            ))

    def preencher_viagens(self):
        self.limpar_tabela(self.tabela_viagens)

        viagens = relatorios_service.listar_viagens_periodo(self.tipo_periodo, self.mes, self.ano)

        for v in viagens[:80]:
            viagem_id, data_saida, modelo, placa, motorista, status, peso, frete, notas = v
            veiculo = f"{modelo or ''} {placa or ''}".strip()

            self.tabela_viagens.insert("", "end", values=(
                viagem_id,
                data_saida,
                veiculo,
                motorista or "",
                status or "",
                self.peso(peso),
                self.moeda(frete),
                notas
            ))

    def preencher_custos(self, extras):
        self.limpar_tabela(self.tabela_custos)

        for data, veiculo, posto, valor in extras["abastecimentos"]:
            if self.data_no_periodo(data):
                self.tabela_custos.insert("", "end", values=(
                    "Combustível",
                    data,
                    veiculo or "",
                    posto or "Abastecimento",
                    self.moeda(valor),
                    "Pago"
                ))

        for data, veiculo, descricao, valor, status in extras["manutencoes_lista"]:
            if self.data_no_periodo(data):
                self.tabela_custos.insert("", "end", values=(
                    "Manutenção",
                    data,
                    veiculo or "",
                    descricao or "Manutenção",
                    self.moeda(valor),
                    status or ""
                ))

    def preencher_contas(self, extras):
        self.limpar_tabela(self.tabela_contas)

        for tipo, descricao, pessoa, categoria, valor, vencimento, status in extras["contas_lista"]:
            if self.data_no_periodo(vencimento):
                self.tabela_contas.insert("", "end", values=(
                    tipo or "",
                    descricao or "",
                    pessoa or "",
                    categoria or "",
                    self.moeda(valor),
                    vencimento or "",
                    status or ""
                ))

    def limpar_tabela(self, tabela):
        for item in tabela.get_children():
            tabela.delete(item)

    def data_no_periodo(self, data_texto):
        if self.tipo_periodo == "Geral":
            return True

        if not data_texto:
            return False

        try:
            data_texto = str(data_texto).split(" ")[0]
            data = datetime.strptime(data_texto, "%d/%m/%Y")

            if self.tipo_periodo == "Mês":
                return data.strftime("%m") == self.mes and data.strftime("%Y") == self.ano

            if self.tipo_periodo == "Ano":
                return data.strftime("%Y") == self.ano

        except Exception:
            return False

        return True

    def descricao_periodo(self):
        if self.tipo_periodo == "Mês":
            return f"{self.mes}/{self.ano}"

        if self.tipo_periodo == "Ano":
            return self.ano

        return "Geral"

    def gerar_pdf(self):
        try:
            payload = relatorios_service.carregar_relatorio(self.tipo_periodo, self.mes, self.ano)
            dados = payload["dados"]
            extras = payload["extras"]
            ranking = payload["ranking"][:8]
            receitas = payload["receitas"]
            despesas = payload["despesas"]
            lucro = payload["lucro"]
            margem = (lucro / receitas * 100) if receitas > 0 else 0

            nome_pdf = os.path.join(
                str(settings.reports_dir),
                f"relatorio_premium_cw_{datetime.now().strftime('%d%m%Y_%H%M%S')}.pdf"
            )

            c = canvas.Canvas(nome_pdf, pagesize=A4)
            largura, altura = A4

            azul_escuro = HexColor("#0f172a")
            azul = HexColor("#2563eb")
            verde = HexColor("#16a34a")
            vermelho = HexColor("#dc2626")
            amarelo = HexColor("#f59e0b")
            roxo = HexColor("#7c3aed")
            cinza = HexColor("#64748b")
            fundo = HexColor("#f1f5f9")
            fundo_escuro = HexColor("#e2e8f0")
            branco = HexColor("#ffffff")
            preto = HexColor("#111827")

            def moeda_pdf(valor):
                return f"R$ {float(valor or 0):,.2f}"

            def rodape(pagina):
                c.setFillColor(cinza)
                c.setFont("Helvetica", 7)
                c.drawString(
                    35,
                    28,
                    f"Documento gerado automaticamente pelo Sistema {settings.empresa}."
                )
                c.drawRightString(largura - 35, 28, f"Página {pagina}")

            def cabecalho(titulo, subtitulo):
                c.setFillColor(azul_escuro)
                c.rect(0, altura - 110, largura, 110, fill=True, stroke=False)

                c.setFillColor(self.cores["principal"])
                c.rect(0, altura - 110, largura, 5, fill=True, stroke=False)

                c.setFillColor(branco)
                c.setFont("Helvetica-Bold", 22)
                c.drawString(35, altura - 45, settings.empresa.upper())

                c.setFont("Helvetica", 11)
                c.drawString(35, altura - 65, titulo)

                c.setFont("Helvetica", 9)
                c.drawString(
                    35,
                    altura - 85,
                    f"Período: {self.descricao_periodo()}  •  Emitido em {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
                )

                c.setFont("Helvetica-Bold", 11)
                c.drawRightString(largura - 35, altura - 65, subtitulo)

            def card(x, y, w, h, titulo, valor, cor):
                c.setFillColor(branco)
                c.roundRect(x, y, w, h, 8, fill=True, stroke=False)

                c.setFillColor(cor)
                c.roundRect(x, y, 6, h, 3, fill=True, stroke=False)

                c.setFillColor(cinza)
                c.setFont("Helvetica-Bold", 7)
                c.drawString(x + 15, y + h - 20, titulo)

                c.setFillColor(preto)
                c.setFont("Helvetica-Bold", 12)
                c.drawString(x + 15, y + 16, str(valor))

            def linha_tabela(y, descricao, valor, cor_valor=preto):
                c.setFillColor(fundo)
                c.roundRect(35, y - 12, largura - 70, 27, 6, fill=True, stroke=False)

                c.setFillColor(preto)
                c.setFont("Helvetica", 9)
                c.drawString(50, y, descricao)

                c.setFillColor(cor_valor)
                c.setFont("Helvetica-Bold", 9)
                c.drawRightString(largura - 50, y, str(valor))

            # PÁGINA 1
            pagina = 1
            cabecalho("Relatório Gerencial Premium", "RESUMO EXECUTIVO")

            y = altura - 165

            card(35, y, 125, 58, "RECEITAS", moeda_pdf(receitas), verde)
            card(170, y, 125, 58, "DESPESAS", moeda_pdf(despesas), vermelho)
            card(305, y, 125, 58, "LUCRO ESTIMADO", moeda_pdf(lucro), verde if lucro >= 0 else vermelho)
            card(440, y, 125, 58, "MARGEM", f"{margem:.1f}%", azul)

            y -= 88

            c.setFillColor(preto)
            c.setFont("Helvetica-Bold", 15)
            c.drawString(35, y, "Resumo financeiro")

            y -= 26

            resumo_financeiro = [
                ("Receitas totais", moeda_pdf(receitas), verde),
                ("Despesas totais", moeda_pdf(despesas), vermelho),
                ("Lucro estimado", moeda_pdf(lucro), verde if lucro >= 0 else vermelho),
                ("Frete total das notas", moeda_pdf(extras["frete_notas"]), verde),
                ("Frete total das viagens", moeda_pdf(dados["frete_total"]), roxo),
                ("Contas recebidas", moeda_pdf(extras["contas_recebidas"]), verde),
                ("Contas pagas", moeda_pdf(extras["contas_pagas"]), vermelho),
                ("Contas a receber", moeda_pdf(extras["contas_a_receber"]), azul),
                ("Contas a pagar", moeda_pdf(extras["contas_a_pagar"]), vermelho),
            ]

            for descricao, valor, cor in resumo_financeiro:
                linha_tabela(y, descricao, valor, cor)
                y -= 34

            y -= 8

            c.setFillColor(preto)
            c.setFont("Helvetica-Bold", 15)
            c.drawString(35, y, "Custos operacionais")

            y -= 26

            custos = [
                ("Folha de pagamento", moeda_pdf(extras["folha"]), vermelho),
                ("Combustível", moeda_pdf(extras["combustivel"]), amarelo),
                ("Manutenção", moeda_pdf(extras["manutencao"]), vermelho),
            ]

            for descricao, valor, cor in custos:
                linha_tabela(y, descricao, valor, cor)
                y -= 34

            rodape(pagina)
            c.showPage()

            # PÁGINA 2 - GRÁFICO
            pagina += 1
            cabecalho("Análise Visual Financeira", "GRÁFICOS")

            c.setFillColor(preto)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(35, altura - 140, "Distribuição de receitas e despesas")

            c.setFillColor(cinza)
            c.setFont("Helvetica", 9)
            c.drawString(35, altura - 158, "Gráfico de rosca com as principais entradas e saídas do período.")

            valores_grafico = [
                max(extras["frete_notas"], 0),
                max(dados["frete_total"], 0),
                max(extras["contas_recebidas"], 0),
                max(extras["folha"], 0),
                max(extras["combustivel"], 0),
                max(extras["manutencao"], 0),
                max(extras["contas_pagas"], 0),
            ]

            labels_grafico = [
                "Frete notas",
                "Frete viagens",
                "Contas recebidas",
                "Folha",
                "Combustível",
                "Manutenção",
                "Contas pagas"
            ]

            cores_grafico = [
                "#16a34a",
                "#7c3aed",
                "#2563eb",
                "#dc2626",
                "#f59e0b",
                "#ef4444",
                "#991b1b"
            ]

            if sum(valores_grafico) > 0:
                fig = Figure(figsize=(5.0, 4.0), dpi=170)
                ax = fig.add_subplot(111)

                ax.pie(
                    valores_grafico,
                    colors=cores_grafico,
                    startangle=90,
                    autopct="%1.1f%%",
                    pctdistance=0.78,
                    textprops={
                        "fontsize": 8,
                        "color": "white",
                        "weight": "bold"
                    },
                    wedgeprops={
                        "width": 0.42,
                        "edgecolor": "white",
                        "linewidth": 2
                    }
                )

                ax.text(0, 0.06, "CW", ha="center", va="center", fontsize=18, fontweight="bold")
                ax.text(0, -0.12, "Financeiro", ha="center", va="center", fontsize=9)
                ax.axis("equal")
                fig.patch.set_facecolor("white")

                img_temp = os.path.join(tempfile.gettempdir(), "grafico_financeiro_cw.png")
                fig.savefig(img_temp, bbox_inches="tight", transparent=False)

                c.drawImage(
                    img_temp,
                    40,
                    330,
                    width=245,
                    height=245,
                    preserveAspectRatio=True,
                    mask="auto"
                )

                total_grafico = sum(valores_grafico)
                legenda_x = 315
                legenda_y = 545

                for nome, valor, cor_hex in zip(labels_grafico, valores_grafico, cores_grafico):
                    percentual = (valor / total_grafico * 100) if total_grafico else 0

                    c.setFillColor(HexColor(cor_hex))
                    c.roundRect(legenda_x, legenda_y - 5, 12, 12, 2, fill=True, stroke=False)

                    c.setFillColor(preto)
                    c.setFont("Helvetica-Bold", 9)
                    c.drawString(legenda_x + 20, legenda_y, nome)

                    c.setFillColor(cinza)
                    c.setFont("Helvetica", 8)
                    c.drawString(
                        legenda_x + 20,
                        legenda_y - 13,
                        f"{moeda_pdf(valor)}  •  {percentual:.1f}%"
                    )

                    legenda_y -= 41

                y = 245

                c.setFillColor(preto)
                c.setFont("Helvetica-Bold", 14)
                c.drawString(35, y, "Indicadores principais")

                y -= 28

                indicadores = [
                    ("Valor total das notas", moeda_pdf(extras["valor_notas"])),
                    ("Manifestos importados", dados["total_manifestos"]),
                    ("Notas importadas", dados["total_notas"]),
                    ("Viagens criadas", dados["total_viagens"]),
                    ("Peso transportado", self.peso(dados["peso_total"])),
                ]

                for descricao, valor in indicadores:
                    linha_tabela(y, descricao, valor, azul_escuro)
                    y -= 32

            else:
                c.setFillColor(cinza)
                c.setFont("Helvetica", 11)
                c.drawString(35, 520, "Sem dados financeiros suficientes para gerar gráfico.")

            rodape(pagina)
            c.showPage()

            # PÁGINA 3 - CLIENTES
            pagina += 1
            cabecalho("Ranking Comercial", "TOP CLIENTES")

            y = altura - 140

            c.setFillColor(preto)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(35, y, "Top clientes por frete")

            c.setFillColor(cinza)
            c.setFont("Helvetica", 9)
            c.drawString(35, y - 18, "Clientes com maior participação no frete do período.")

            y -= 48

            if not ranking:
                c.setFillColor(cinza)
                c.setFont("Helvetica", 10)
                c.drawString(35, y, "Nenhum cliente encontrado no período.")
            else:
                for i, cliente in enumerate(ranking, start=1):
                    nome = cliente.get("cliente", "Cliente não informado")
                    notas = cliente.get("total_notas", 0)
                    valor_notas = cliente.get("valor_notas", 0)
                    frete = cliente.get("frete", 0)
                    peso = cliente.get("peso", 0)

                    c.setFillColor(fundo)
                    c.roundRect(35, y - 22, largura - 70, 42, 7, fill=True, stroke=False)

                    c.setFillColor(vermelho)
                    c.setFont("Helvetica-Bold", 13)
                    c.drawString(50, y - 2, f"{i}º")

                    c.setFillColor(preto)
                    c.setFont("Helvetica-Bold", 9)
                    c.drawString(85, y + 6, str(nome)[:48])

                    c.setFillColor(cinza)
                    c.setFont("Helvetica", 8)
                    c.drawString(
                        85,
                        y - 8,
                        f"{notas} notas  •  Valor notas: {moeda_pdf(valor_notas)}  •  Peso: {self.peso(peso)}"
                    )

                    c.setFillColor(verde)
                    c.setFont("Helvetica-Bold", 10)
                    c.drawRightString(largura - 50, y - 1, moeda_pdf(frete))

                    y -= 50

                    if y < 70:
                        rodape(pagina)
                        c.showPage()
                        pagina += 1
                        cabecalho("Ranking Comercial", "TOP CLIENTES")
                        y = altura - 140

            rodape(pagina)
            c.save()

            try:
                os.startfile(nome_pdf)
            except Exception:
                pass  # Alguns ambientes não suportam os.startfile

            messagebox.showinfo(
                "Sucesso",
                f"PDF Premium gerado com sucesso:\n{nome_pdf}"
            )

        except Exception as erro:
            messagebox.showerror("Erro", str(erro))

    def moeda(self, valor):
        return formatar_moeda(valor)

    def peso(self, valor):
        return formatar_peso(valor)     
