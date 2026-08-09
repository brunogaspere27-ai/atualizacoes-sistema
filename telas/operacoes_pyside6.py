"""
Tela Operações CW Transportadora - PySide6
Transferência SP → Cascavel

Migração completa da tela CustomTkinter para PySide6, mantendo toda a
lógica de negócio original:
- Formulário com 8 campos de entrada agrupados em duas seções
- Painel de resumo ao vivo (recalcula enquanto o usuário digita)
- Tabela de histórico de transferências (QTableWidget)
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSizePolicy, QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor

from services.operacoes_service import operacoes_service
from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard, CWInput
from utils.helpers import formatar_moeda, parse_numero


class TelaOperacoes(QWidget):
    """Tela de controle de transferências SP → Cascavel (PySide6)."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Dicionário de QLineEdit indexado por nome de campo
        self.campos: dict[str, QLineEdit] = {}

        # Labels de valor no painel de resumo (atualizadas ao vivo)
        self._resumo_labels: dict[str, QLabel] = {}

        self._setup_ui()
        self._carregar_historico()

    # ------------------------------------------------------------------ #
    #  UI principal                                                         #
    # ------------------------------------------------------------------ #

    def _setup_ui(self):
        c = cw_theme.colors
        t = cw_theme.spacing

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # Scroll que envolve todo o conteúdo
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
        QScrollArea {{
            background-color: {c['bg_primary']};
            border: none;
        }}
        """)
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(t._2XL, t._2XL, t._2XL, t._2XL)
        content_layout.setSpacing(t.XL)
        content.setLayout(content_layout)
        scroll.setWidget(content)

        # -- Linha central: formulário (esquerda) + resumo (direita) --------
        row_layout = QHBoxLayout()
        row_layout.setSpacing(t.LG)
        row_layout.addWidget(self._build_form(), stretch=2)
        row_layout.addWidget(self._build_resumo(), stretch=1)
        content_layout.addLayout(row_layout)

        # -- Tabela de histórico --------------------------------------------
        content_layout.addWidget(self._build_historico())

    # ------------------------------------------------------------------ #
    #  Formulário                                                           #
    # ------------------------------------------------------------------ #

    def _build_form(self) -> CWCard:
        t = cw_theme.spacing

        card = CWCard(padding=t._2XL)

        # --- Seção 1: Dados da Transferência ------------------------------
        card.add_widget(self._secao_label("DADOS DA TRANSFERÊNCIA"))

        grid1 = QGridLayout()
        grid1.setContentsMargins(0, 0, 0, 0)
        grid1.setHorizontalSpacing(t.LG)
        grid1.setVerticalSpacing(t.MD)
        grid1.setColumnStretch(0, 1)
        grid1.setColumnStretch(1, 1)

        grid1.addWidget(self._campo("data_operacao", "Data da operação"), 0, 0)
        grid1.addWidget(self._campo("nome_caminhao", "Nome do caminhão / carreta"), 0, 1)
        grid1.addWidget(self._campo("placa", "Placa"), 1, 0)
        grid1.addWidget(self._campo("motorista", "Motorista"), 1, 1)

        card.add_layout(grid1)

        # --- Seção 2: Valores Financeiros ---------------------------------
        card.add_spacing(t.XL)
        card.add_widget(self._secao_label("VALORES FINANCEIROS"))

        grid2 = QGridLayout()
        grid2.setContentsMargins(0, 0, 0, 0)
        grid2.setHorizontalSpacing(t.LG)
        grid2.setVerticalSpacing(t.MD)
        grid2.setColumnStretch(0, 1)
        grid2.setColumnStretch(1, 1)

        grid2.addWidget(self._campo("valor_frete", "Valor do frete (R$)"), 0, 0)
        grid2.addWidget(self._campo("valor_combustivel", "Combustível (R$)"), 0, 1)
        grid2.addWidget(self._campo("valor_pedagio", "Pedágio (R$)"), 1, 0)
        grid2.addWidget(self._campo("valor_outros", "Outros (R$)"), 1, 1)

        card.add_layout(grid2)

        # --- Botão de ação ------------------------------------------------
        card.add_spacing(t.XL)
        self._btn_salvar = CWButton("Salvar Operação", ButtonVariant.PRIMARY, ButtonSize.MD)
        self._btn_salvar.clicked.connect(self._salvar_operacao)
        card.add_widget(self._btn_salvar)

        # Preenche a data atual após criar todos os campos
        self.campos["data_operacao"].setText(datetime.now().strftime("%d/%m/%Y"))

        return card

    def _secao_label(self, texto: str) -> QLabel:
        c = cw_theme.colors
        t = cw_theme.spacing
        lbl = QLabel(texto)
        lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(
            f"color: {c['primary']}; background: transparent; "
            f"letter-spacing: 1px; padding-top: {t.MD}px;"
        )
        return lbl

    def _campo(self, nome: str, label_texto: str) -> QWidget:
        """Cria um par label + CWInput e o registra em self.campos."""
        c = cw_theme.colors
        t = cw_theme.spacing

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(t.XS)
        container.setLayout(vbox)

        lbl = QLabel(label_texto)
        lbl.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        vbox.addWidget(lbl)

        entry = QLineEdit()
        entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_secondary']};
                border: 1px solid {c['border_default']};
                border-radius: {cw_theme.radius.MD}px;
                padding: 0 {t.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                color: {c['text_primary']};
            }}
            QLineEdit:focus {{
                border: 1px solid {c['border_focus']};
            }}
        """)
        vbox.addWidget(entry)

        self.campos[nome] = entry
        return container

    # ------------------------------------------------------------------ #
    #  Painel de Resumo                                                     #
    # ------------------------------------------------------------------ #

    def _build_resumo(self) -> CWCard:
        c = cw_theme.colors
        t = cw_theme.spacing

        card = CWCard(padding=t.XL)

        titulo = QLabel("RESUMO")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XL, bold=True))
        titulo.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        card.add_widget(titulo)

        # Cards de valor (título → cor, chave interna)
        itens = [
            ("Valor das Notas SP",         "valor_notas",    c["text_primary"]),
            ("Frete Pago à Carreta",        "frete_carreta",  c["primary"]),
            ("Pedágio Pago",                "pedagio_carreta",c["warning"]),
            ("Outros Custos",               "outros_custos",  c["text_secondary"]),
            ("Custo Total Transferência",   "custo_total",    c["error"]),
            ("Valor Líquido da Carga",      "liquido",        c["success"]),
        ]

        for titulo_item, chave, cor in itens:
            card.add_widget(self._mini_card(titulo_item, chave, cor))

        card.add_widget(self._separador())

        btn = CWButton("ATUALIZAR CÁLCULO", ButtonVariant.SECONDARY, ButtonSize.MD)
        btn.clicked.connect(self._atualizar_resumo)
        card.add_widget(btn)

        return card

    def _mini_card(self, titulo: str, chave: str, cor: str) -> QFrame:
        """Card de linha exibindo um único valor monetário."""
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius

        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_elevated']};
                border: 1px solid {c['border_subtle']};
                border-radius: {r.MD}px;
                padding: {t.SM}px;
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(t.SM, t.SM, t.SM, t.SM)
        layout.setSpacing(t.SM)
        frame.setLayout(layout)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XS))
        lbl_titulo.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        layout.addWidget(lbl_titulo)

        layout.addStretch()

        lbl_valor = QLabel("R$ 0,00")
        lbl_valor.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM, bold=True))
        lbl_valor.setStyleSheet(f"color: {cor}; background: transparent;")
        layout.addWidget(lbl_valor)

        self._resumo_labels[chave] = lbl_valor
        return frame

    def _separador(self) -> QFrame:
        c = cw_theme.colors
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setMinimumHeight(1)
        line.setStyleSheet(f"background-color: {c['border_subtle']}; border: none;")
        return line

    # ------------------------------------------------------------------ #
    #  Lógica de negócio                                                    #
    # ------------------------------------------------------------------ #

    def _numero(self, nome: str) -> float:
        """Lê o campo e converte para float tolerando vírgula como decimal."""
        return parse_numero(self.campos[nome].text(), default=0.0)

    def _calcular(self) -> dict:
        valor_notas = self._numero("valor_notas")
        frete       = self._numero("frete_carreta")
        pedagio     = self._numero("pedagio_carreta")
        outros      = self._numero("outros_custos")

        custo_total = frete + pedagio + outros
        liquido     = valor_notas - custo_total

        return {
            "valor_notas":    valor_notas,
            "frete_carreta":  frete,
            "pedagio_carreta": pedagio,
            "outros_custos":  outros,
            "custo_total":    custo_total,
            "liquido":        liquido,
        }

    def _atualizar_resumo(self):
        """Recalcula e atualiza os labels do painel de resumo."""
        colors = theme_manager.colors
        r = self._calcular()

        for chave in ("valor_notas", "frete_carreta", "pedagio_carreta",
                      "outros_custos", "custo_total"):
            lbl = self._resumo_labels.get(chave)
            if lbl:
                lbl.setText(formatar_moeda(r[chave]))

        lbl_liq = self._resumo_labels.get("liquido")
        if lbl_liq:
            lbl_liq.setText(formatar_moeda(r["liquido"]))
            cor = colors["emerald"] if r["liquido"] >= 0 else colors["error"]
            lbl_liq.setStyleSheet(f"color: {cor}; background: transparent;")

    def _salvar(self):
        nome_caminhao = self.campos["nome_caminhao"].text().strip()
        placa         = self.campos["placa"].text().strip()

        if not nome_caminhao:
            QMessageBox.critical(self, "Erro", "Informe o nome do caminhão/carreta.")
            return

        if not placa:
            QMessageBox.critical(self, "Erro", "Informe a placa.")
            return

        r = self._calcular()

        dados = {
            "data_operacao":   self.campos["data_operacao"].text(),
            "nome_caminhao":   nome_caminhao,
            "placa":           placa,
            "motorista":       self.campos["motorista"].text().strip(),
            "valor_notas":     r["valor_notas"],
            "frete_carreta":   r["frete_carreta"],
            "pedagio_carreta": r["pedagio_carreta"],
            "outros_custos":   r["outros_custos"],
            "custo_total":     r["custo_total"],
            "liquido":         r["liquido"],
        }

        operacoes_service.criar_operacao(dados)

        QMessageBox.information(self, "Sucesso", "Transferência salva com sucesso!")

        self._limpar()
        self._carregar_historico()

    def _limpar(self):
        for entry in self.campos.values():
            entry.clear()
        self.campos["data_operacao"].setText(datetime.now().strftime("%d/%m/%Y"))
        self._atualizar_resumo()

    def _carregar_historico(self):
        """Preenche a QTableWidget com os dados do service."""
        self.tabela.setRowCount(0)

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
                liquido,
            ) = linha

            row = self.tabela.rowCount()
            self.tabela.insertRow(row)

            valores = [
                f"#{id_op}",
                str(data) if data else "-",
                str(nome_caminhao) if nome_caminhao else "-",
                str(placa) if placa else "-",
                str(motorista) if motorista else "-",
                formatar_moeda(valor_notas),
                formatar_moeda(frete),
                formatar_moeda(pedagio),
                formatar_moeda(outros),
                formatar_moeda(custo),
                formatar_moeda(liquido),
            ]

            for col, texto in enumerate(valores):
                item = QTableWidgetItem(texto)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter |
                    (Qt.AlignmentFlag.AlignCenter if col == 0
                     else Qt.AlignmentFlag.AlignLeft)
                )
                # Colorir coluna Líquido
                if col == 10:
                    try:
                        colors = theme_manager.colors
                        val = float(liquido)
                        cor = colors["emerald"] if val >= 0 else colors["error"]
                        item.setForeground(QColor(cor))
                    except (TypeError, ValueError):
                        pass
                self.tabela.setItem(row, col, item)
