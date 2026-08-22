"""
Tela Relatórios Gerenciais - CW Transportadora - PySide6 Premium Dark Red
Central de relatórios com abas: Resumo, Clientes, Viagens, Custos, Contas.
Design System CW - Premium Dark Industrial
"""

from __future__ import annotations

import os
import tempfile
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QFrame, QMessageBox, QAbstractItemView, QScrollArea,
    QTabWidget,
)
from PySide6.QtCore import Qt, QTimer

from services.relatorios_service import relatorios_service
from config.settings import settings
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWTable
from utils.helpers import formatar_moeda, formatar_peso
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaRelatorios(QWidget):
    """Tela de relatórios gerenciais em PySide6."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tipo_periodo = "Geral"
        self.mes = datetime.now().strftime("%m")
        self.ano = datetime.now().strftime("%Y")
        self._setup_ui()
        self._carregar_relatorio()

    def _setup_ui(self):
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: {c['bg_primary']}; border: none; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; margin: 4px 2px; }}
            QScrollBar::handle:vertical {{ background: {c['border_subtle']}; border-radius: 4px; min-height: 40px; }}
            QScrollBar::handle:vertical:hover {{ background: {c['border_default']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0px; }}
        """)
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_primary']};")
        cl = QVBoxLayout()
        cl.setContentsMargins(t._2XL, t._2XL, t._2XL, t._2XL)
        cl.setSpacing(t.XL)
        content.setLayout(cl)
        scroll.setWidget(content)

        # Filtros
        filtros = CWCard("Filtros", padding=t.LG)
        fr = QHBoxLayout()
        fr.setSpacing(t.MD)

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems(["Geral", "Mês", "Ano"])
        self.combo_periodo.setCurrentText(self.tipo_periodo)
        self.combo_periodo.setMinimumHeight(40)
        self.combo_periodo.setMinimumWidth(110)
        self.combo_periodo.setStyleSheet(f"""
            QComboBox {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: {t.SM}px {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {c['text_primary']};
            }}
            QComboBox:hover {{ border-color: {c['border_strong']}; }}
            QComboBox::drop-down {{ border: none; width: 30px; }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {c['text_secondary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                selection-background-color: {c['primary_soft']};
                selection-color: {c['primary']};
            }}
        """)
        self.combo_periodo.currentTextChanged.connect(lambda: self._carregar_relatorio())
        fr.addWidget(self.combo_periodo)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        self.combo_mes.setCurrentText(self.mes)
        self.combo_mes.setMinimumHeight(40)
        self.combo_mes.setMinimumWidth(80)
        self.combo_mes.setStyleSheet(self.combo_periodo.styleSheet())
        self.combo_mes.currentTextChanged.connect(lambda: self._carregar_relatorio())
        fr.addWidget(self.combo_mes)

        self.entry_ano = QLineEdit(self.ano)
        self.entry_ano.setFixedWidth(80)
        self.entry_ano.setMinimumHeight(40)
        self.entry_ano.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: 0 {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {c['text_primary']};
            }}
            QLineEdit:focus {{ border: 1px solid {c['border_focus']}; }}
        """)
        self.entry_ano.textChanged.connect(lambda: self._carregar_relatorio())
        fr.addWidget(self.entry_ano)

        btn_atualizar = CWButton("Atualizar", ButtonVariant.SECONDARY, ButtonSize.MD)
        btn_atualizar.clicked.connect(self._carregar_relatorio)
        fr.addWidget(btn_atualizar)

        fr.addStretch()

        btn_pdf = CWButton("Gerar PDF", ButtonVariant.PRIMARY, ButtonSize.MD)
        btn_pdf.clicked.connect(self._gerar_pdf)
        fr.addWidget(btn_pdf)

        filtros.add_layout(fr)
        cl.addWidget(filtros)

        # Cards resumo - KPI style
        resumo_layout = QHBoxLayout()
        resumo_layout.setSpacing(t.MD)

        self._cards = {}
        nomes = ["Receitas", "Despesas", "Lucro", "Valor Notas", "Frete Notas", "Frete Viagens", "A Receber", "A Pagar"]
        for nome in nomes:
            kpi_card = QFrame()
            kpi_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {c['bg_elevated']};
                    border: 1px solid {c['border_subtle']};
                    border-radius: {r.LG}px;
                }}
            """)
            kpi_layout = QVBoxLayout()
            kpi_layout.setContentsMargins(t.MD, t.SM, t.MD, t.SM)
            kpi_layout.setSpacing(t.XS)
            kpi_card.setLayout(kpi_layout)

            t_label = QLabel(nome)
            t_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            t_label.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            kpi_layout.addWidget(t_label)

            v_label = QLabel("R$ 0,00")
            v_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_LG, bold=True))
            v_label.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
            kpi_layout.addWidget(v_label)

            self._cards[nome] = v_label
            resumo_layout.addWidget(kpi_card)

        cl.addLayout(resumo_layout)

        # Abas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid {c['border_subtle']}; border-radius: {r.LG}px; background: {c['bg_secondary']}; }}
            QTabBar::tab {{ background: {c['bg_tertiary']}; color: {c['text_secondary']}; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; font-weight: 600; }}
            QTabBar::tab:selected {{ background: {c['bg_secondary']}; color: {c['text_primary']}; }}
        """)

        self.tabela_resumo = self._criar_tabela_abas(["Indicador", "Valor"], [360, 200])
        self.tabela_clientes = self._criar_tabela_abas(["#", "Cliente", "Notas", "Valor Notas", "Frete", "Peso"], [40, 300, 70, 130, 130, 130])
        self.tabela_viagens = self._criar_tabela_abas(["ID", "Data", "Veículo", "Motorista", "Status", "Peso", "Frete", "Notas"], [50, 100, 220, 140, 90, 110, 120, 70])
        self.tabela_custos = self._criar_tabela_abas(["Tipo", "Data", "Veículo", "Descrição", "Valor", "Status"], [100, 100, 160, 300, 120, 90])
        self.tabela_contas = self._criar_tabela_abas(["Tipo", "Descrição", "Cliente/Forn.", "Categoria", "Valor", "Vencimento", "Status"], [70, 260, 230, 110, 110, 110, 90])

        self.tabs.addTab(self._wrap_table(self.tabela_resumo), "Resumo")
        self.tabs.addTab(self._wrap_table(self.tabela_clientes), "Clientes")
        self.tabs.addTab(self._wrap_table(self.tabela_viagens), "Viagens")
        self.tabs.addTab(self._wrap_table(self.tabela_custos), "Custos")
        self.tabs.addTab(self._wrap_table(self.tabela_contas), "Contas")

        cl.addWidget(self.tabs)

    def _criar_tabela_abas(self, colunas: list, larguras: list) -> CWTable:
        tabela = CWTable(colunas)
        tabela.setMinimumHeight(350)

        h = tabela.horizontalHeader()
        for i, w in enumerate(larguras):
            h.resizeSection(i, w)
        h.setStretchLastSection(True)
        return tabela

    def _wrap_table(self, tabela: QTableWidget) -> QWidget:
        w = QWidget()
        l = QVBoxLayout()
        l.setContentsMargins(8, 8, 8, 8)
        l.addWidget(tabela)
        w.setLayout(l)
        return w

    def _carregar_relatorio(self):
        self.tipo_periodo = self.combo_periodo.currentText()
        self.mes = self.combo_mes.currentText()
        self.ano = self.entry_ano.text().strip()

        def tarefa():
            try:
                payload = relatorios_service.carregar_relatorio(self.tipo_periodo, self.mes, self.ano)
                QTimer.singleShot(0, lambda: self._aplicar_dados(payload))
            except Exception as e:
                logger.error(f"Erro ao carregar relatório: {e}")

        threading.Thread(target=tarefa, daemon=True).start()

    def _aplicar_dados(self, payload):
        dados = payload["dados"]
        extras = payload["extras"]
        ranking = payload["ranking"]
        receitas = payload["receitas"]
        despesas = payload["despesas"]
        lucro = payload["lucro"]

        self._cards["Receitas"].setText(self.moeda(receitas))
        self._cards["Despesas"].setText(self.moeda(despesas))
        self._cards["Lucro"].setText(self.moeda(lucro))
        self._cards["Valor Notas"].setText(self.moeda(extras["valor_notas"]))
        self._cards["Frete Notas"].setText(self.moeda(extras["frete_notas"]))
        self._cards["Frete Viagens"].setText(self.moeda(dados["frete_total"]))
        self._cards["A Receber"].setText(self.moeda(extras["contas_a_receber"]))
        self._cards["A Pagar"].setText(self.moeda(extras["contas_a_pagar"]))

        self._preencher_resumo(dados, extras, receitas, despesas, lucro)
        self._preencher_clientes(ranking)
        self._preencher_viagens()
        self._preencher_custos(extras)
        self._preencher_contas(extras)

    def _limpar_tabela(self, tabela: QTableWidget):
        tabela.setRowCount(0)

    def _add_row(self, tabela: QTableWidget, valores: list):
        row = tabela.rowCount()
        tabela.insertRow(row)
        for col, texto in enumerate(valores):
            item = QTableWidgetItem(str(texto))
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            tabela.setItem(row, col, item)

    def _preencher_resumo(self, dados, extras, receitas, despesas, lucro):
        self._limpar_tabela(self.tabela_resumo)
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
            ("Manifestos importados", str(dados["total_manifestos"])),
            ("Notas importadas", str(dados["total_notas"])),
            ("Viagens criadas", str(dados["total_viagens"])),
            ("Peso transportado", self.peso(dados["peso_total"])),
        ]
        for linha in linhas:
            self._add_row(self.tabela_resumo, linha)

    def _preencher_clientes(self, ranking):
        self._limpar_tabela(self.tabela_clientes)
        for i, cliente in enumerate(ranking[:30], start=1):
            self._add_row(self.tabela_clientes, [
                i, cliente.get("cliente"), cliente.get("total_notas"),
                self.moeda(cliente.get("valor_notas")),
                self.moeda(cliente.get("frete")),
                self.peso(cliente.get("peso")),
            ])

    def _preencher_viagens(self):
        self._limpar_tabela(self.tabela_viagens)
        viagens = relatorios_service.listar_viagens_periodo(self.tipo_periodo, self.mes, self.ano)
        for v in viagens[:80]:
            viagem_id, data_saida, modelo, placa, motorista, status, peso, frete, notas = v
            veiculo = f"{modelo or ''} {placa or ''}".strip()
            self._add_row(self.tabela_viagens, [
                viagem_id, data_saida, veiculo, motorista or "",
                status or "", self.peso(peso), self.moeda(frete), notas,
            ])

    def _preencher_custos(self, extras):
        self._limpar_tabela(self.tabela_custos)
        for data, veiculo, posto, valor in extras["abastecimentos"]:
            if self._data_no_periodo(data):
                self._add_row(self.tabela_custos, [
                    "Combustível", data, veiculo or "", posto or "Abastecimento",
                    self.moeda(valor), "Pago",
                ])
        for data, veiculo, descricao, valor, status in extras["manutencoes_lista"]:
            if self._data_no_periodo(data):
                self._add_row(self.tabela_custos, [
                    "Manutenção", data, veiculo or "", descricao or "Manutenção",
                    self.moeda(valor), status or "",
                ])

    def _preencher_contas(self, extras):
        self._limpar_tabela(self.tabela_contas)
        for tipo, descricao, pessoa, categoria, valor, vencimento, status in extras["contas_lista"]:
            if self._data_no_periodo(vencimento):
                self._add_row(self.tabela_contas, [
                    tipo or "", descricao or "", pessoa or "", categoria or "",
                    self.moeda(valor), vencimento or "", status or "",
                ])

    def _data_no_periodo(self, data_texto) -> bool:
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

    def _gerar_pdf(self):
        try:
            payload = relatorios_service.carregar_relatorio(self.tipo_periodo, self.mes, self.ano)
            dados = payload["dados"]
            extras = payload["extras"]
            ranking = payload["ranking"][:8]
            receitas = payload["receitas"]
            despesas = payload["despesas"]
            lucro = payload["lucro"]
            margem = (lucro / receitas * 100) if receitas > 0 else 0

            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.colors import HexColor
            from matplotlib.figure import Figure

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
            branco = HexColor("#ffffff")
            preto = HexColor("#111827")

            def moeda_pdf(valor):
                return f"R$ {float(valor or 0):,.2f}"

            def rodape(pagina):
                c.setFillColor(cinza)
                c.setFont("Helvetica", 7)
                c.drawString(35, 28, f"Documento gerado automaticamente pelo Sistema {settings.empresa}.")
                c.drawRightString(largura - 35, 28, f"Página {pagina}")

            def cabecalho(titulo, subtitulo):
                c.setFillColor(azul_escuro)
                c.rect(0, altura - 110, largura, 110, fill=True, stroke=False)
                c.setFillColor(azul)
                c.rect(0, altura - 110, largura, 5, fill=True, stroke=False)
                c.setFillColor(branco)
                c.setFont("Helvetica-Bold", 22)
                c.drawString(35, altura - 45, settings.empresa.upper())
                c.setFont("Helvetica", 11)
                c.drawString(35, altura - 65, titulo)
                c.setFont("Helvetica", 9)
                periodo_desc = self._descricao_periodo()
                c.drawString(35, altura - 85, f"Período: {periodo_desc}  •  Emitido em {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
                c.setFont("Helvetica-Bold", 11)
                c.drawRightString(largura - 35, altura - 65, subtitulo)

            def card_pdf(x, y, w, h, titulo, valor, cor):
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

            card_pdf(35, y, 125, 58, "RECEITAS", moeda_pdf(receitas), verde)
            card_pdf(170, y, 125, 58, "DESPESAS", moeda_pdf(despesas), vermelho)
            card_pdf(305, y, 125, 58, "LUCRO ESTIMADO", moeda_pdf(lucro), verde if lucro >= 0 else vermelho)
            card_pdf(440, y, 125, 58, "MARGEM", f"{margem:.1f}%", azul)

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
                max(extras["frete_notas"], 0), max(dados["frete_total"], 0),
                max(extras["contas_recebidas"], 0), max(extras["folha"], 0),
                max(extras["combustivel"], 0), max(extras["manutencao"], 0),
                max(extras["contas_pagas"], 0),
            ]
            labels_grafico = ["Frete notas", "Frete viagens", "Contas recebidas", "Folha", "Combustível", "Manutenção", "Contas pagas"]
            cores_grafico = ["#16a34a", "#7c3aed", "#2563eb", "#dc2626", "#f59e0b", "#ef4444", "#991b1b"]

            if sum(valores_grafico) > 0:
                fig = Figure(figsize=(5.0, 4.0), dpi=170)
                ax = fig.add_subplot(111)
                ax.pie(
                    valores_grafico, colors=cores_grafico, startangle=90,
                    autopct="%1.1f%%", pctdistance=0.78,
                    textprops={"fontsize": 8, "color": "white", "weight": "bold"},
                    wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2},
                )
                ax.text(0, 0.06, "CW", ha="center", va="center", fontsize=18, fontweight="bold")
                ax.text(0, -0.12, "Financeiro", ha="center", va="center", fontsize=9)
                ax.axis("equal")
                fig.patch.set_facecolor("white")

                img_temp = os.path.join(tempfile.gettempdir(), "grafico_financeiro_cw.png")
                fig.savefig(img_temp, bbox_inches="tight", transparent=False)
                c.drawImage(img_temp, 40, 330, width=245, height=245, preserveAspectRatio=True, mask="auto")

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
                    c.drawString(legenda_x + 20, legenda_y - 13, f"{moeda_pdf(valor)}  •  {percentual:.1f}%")
                    legenda_y -= 41

                y = 245
                c.setFillColor(preto)
                c.setFont("Helvetica-Bold", 14)
                c.drawString(35, y, "Indicadores principais")
                y -= 28

                indicadores = [
                    ("Valor total das notas", moeda_pdf(extras["valor_notas"])),
                    ("Manifestos importados", str(dados["total_manifestos"])),
                    ("Notas importadas", str(dados["total_notas"])),
                    ("Viagens criadas", str(dados["total_viagens"])),
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
                    c.drawString(85, y - 8, f"{notas} notas  •  Valor notas: {moeda_pdf(valor_notas)}  •  Peso: {self.peso(peso)}")
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
                pass

            QMessageBox.information(self, "Sucesso", f"PDF Premium gerado com sucesso:\n{nome_pdf}")

        except Exception as erro:
            QMessageBox.critical(self, "Erro", str(erro))

    def _descricao_periodo(self) -> str:
        if self.tipo_periodo == "Mês":
            return f"{self.mes}/{self.ano}"
        if self.tipo_periodo == "Ano":
            return self.ano
        return "Geral"

    def moeda(self, valor) -> str:
        return formatar_moeda(valor)

    def peso(self, valor) -> str:
        return formatar_peso(valor)
