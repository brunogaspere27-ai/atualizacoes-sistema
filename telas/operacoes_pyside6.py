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
from telas.theme_aurora import aurora_theme_manager as theme_manager, AccentColor
from utils.components import ModernButton, ButtonStyle, ModernCard
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
        colors = theme_manager.colors
        tokens = theme_manager.tokens

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
            background-color: {colors['bg_primary']};
            border: none;
        }}
        """)
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {colors['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(
            tokens.SPACING_2XL, tokens.SPACING_2XL,
            tokens.SPACING_2XL, tokens.SPACING_2XL
        )
        content_layout.setSpacing(tokens.SPACING_XL)
        content.setLayout(content_layout)
        scroll.setWidget(content)

        # -- Linha central: formulário (esquerda) + resumo (direita) --------
        row_layout = QHBoxLayout()
        row_layout.setSpacing(tokens.SPACING_LG)
        row_layout.addWidget(self._build_form(), stretch=2)
        row_layout.addWidget(self._build_resumo(), stretch=1)
        content_layout.addLayout(row_layout)

        # -- Tabela de histórico --------------------------------------------
        content_layout.addWidget(self._build_historico())

    # ------------------------------------------------------------------ #
    #  Formulário                                                           #
    # ------------------------------------------------------------------ #

    def _build_form(self) -> ModernCard:
        tokens = theme_manager.tokens

        card = ModernCard(padding=tokens.SPACING_2XL)

        # --- Seção 1: Dados da Transferência ------------------------------
        card.add_widget(self._secao_label("DADOS DA TRANSFERÊNCIA"))

        grid1 = QGridLayout()
        grid1.setContentsMargins(0, 0, 0, 0)
        grid1.setHorizontalSpacing(tokens.SPACING_LG)
        grid1.setVerticalSpacing(tokens.SPACING_MD)
        grid1.setColumnStretch(0, 1)
        grid1.setColumnStretch(1, 1)

        grid1.addWidget(self._campo("data_operacao", "Data da operação"), 0, 0)
        grid1.addWidget(self._campo("nome_caminhao", "Nome do caminhão / carreta"), 0, 1)
        grid1.addWidget(self._campo("placa", "Placa"), 1, 0)
        grid1.addWidget(self._campo("motorista", "Motorista"), 1, 1)

        card.add_layout(grid1)

        # --- Seção 2: Valores da Carga ------------------------------------
        card.add_widget(self._secao_label("VALORES DA CARGA DE SÃO PAULO"))

        grid2 = QGridLayout()
        grid2.setContentsMargins(0, 0, 0, 0)
        grid2.setHorizontalSpacing(tokens.SPACING_LG)
        grid2.setVerticalSpacing(tokens.SPACING_MD)
        grid2.setColumnStretch(0, 1)
        grid2.setColumnStretch(1, 1)

        grid2.addWidget(self._campo("valor_notas", "Valor total das notas da carga SP"), 0, 0)
        grid2.addWidget(self._campo("frete_carreta", "Frete pago à carreta"), 0, 1)
        grid2.addWidget(self._campo("pedagio_carreta", "Pedágio pago à carreta"), 1, 0)
        grid2.addWidget(self._campo("outros_custos", "Outros custos"), 1, 1)

        card.add_layout(grid2)

        # --- Botões -------------------------------------------------------
        btn_row = QHBoxLayout()
        btn_row.setSpacing(tokens.SPACING_MD)

        btn_salvar = ModernButton("💾  SALVAR TRANSFERÊNCIA", ButtonStyle.SUCCESS)
        btn_salvar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_salvar.clicked.connect(self._salvar)
        btn_row.addWidget(btn_salvar)

        btn_limpar = ModernButton("🧹  LIMPAR", ButtonStyle.SECONDARY)
        btn_limpar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_limpar.clicked.connect(self._limpar)
        btn_row.addWidget(btn_limpar)

        card.add_layout(btn_row)

        # Preenche a data actual após criar todos os campos
        self.campos["data_operacao"].setText(datetime.now().strftime("%d/%m/%Y"))

        return card

    def _secao_label(self, texto: str) -> QLabel:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        lbl = QLabel(texto)
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(
            f"color: {colors['violet']}; background: transparent; "
            f"letter-spacing: 1px; padding-top: {tokens.SPACING_MD}px;"
        )
        return lbl

    def _campo(self, nome: str, label_texto: str) -> QWidget:
        """Cria um par label + QLineEdit e o regista em self.campos."""
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(tokens.SPACING_XS)
        container.setLayout(vbox)

        lbl = QLabel(label_texto)
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        vbox.addWidget(lbl)

        entry = QLineEdit()
        entry.setMinimumHeight(42)
        entry.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD))
        entry.setStyleSheet(f"""
        QLineEdit {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1.5px solid {colors['border_subtle']};
            border-radius: {tokens.RADIUS_MD}px;
            padding: {tokens.SPACING_SM}px {tokens.SPACING_MD}px;
        }}
        QLineEdit:hover {{
            border-color: {colors['border_default']};
        }}
        QLineEdit:focus {{
            border: 1.5px solid {colors['violet']};
            background-color: {colors['bg_secondary']};
        }}
        """)
        entry.textChanged.connect(self._atualizar_resumo)
        vbox.addWidget(entry)

        self.campos[nome] = entry
        return container

    # ------------------------------------------------------------------ #
    #  Painel de Resumo                                                     #
    # ------------------------------------------------------------------ #

    def _build_resumo(self) -> ModernCard:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        card = ModernCard(padding=tokens.SPACING_XL)

        titulo = QLabel("📊  RESUMO")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_XL, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        card.add_widget(titulo)

        # Cards de valor (título → cor, chave interna)
        itens = [
            ("Valor das Notas SP",         "valor_notas",    colors["text_primary"]),
            ("Frete Pago à Carreta",        "frete_carreta",  colors["rose"]),
            ("Pedágio Pago",                "pedagio_carreta",colors["amber"]),
            ("Outros Custos",               "outros_custos",  colors["text_secondary"]),
            ("Custo Total Transferência",   "custo_total",    colors["error"]),
            ("Valor Líquido da Carga",      "liquido",        colors["emerald"]),
        ]

        for titulo_item, chave, cor in itens:
            card.add_widget(self._mini_card(titulo_item, chave, cor))

        card.add_widget(self._separador())

        btn = ModernButton("🔄  ATUALIZAR CÁLCULO", ButtonStyle.SECONDARY)
        btn.clicked.connect(self._atualizar_resumo)
        card.add_widget(btn)

        return card

    def _mini_card(self, titulo: str, chave: str, cor: str) -> QFrame:
        """Card de linha exibindo um único valor monetário."""
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        frame = QFrame()
        frame.setObjectName("miniCard")
        frame.setStyleSheet(f"""
        QFrame#miniCard {{
            background-color: {colors['bg_secondary']};
            border: 1px solid {colors['border_subtle']};
            border-radius: {tokens.RADIUS_MD}px;
        }}
        """)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(
            tokens.SPACING_MD, tokens.SPACING_SM,
            tokens.SPACING_MD, tokens.SPACING_SM
        )
        vbox.setSpacing(2)
        frame.setLayout(vbox)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl_titulo.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        vbox.addWidget(lbl_titulo)

        lbl_valor = QLabel("R$ 0,00")
        lbl_valor.setFont(theme_manager.get_font(tokens.FONT_SIZE_LG, bold=True))
        lbl_valor.setStyleSheet(f"color: {cor}; background: transparent;")
        vbox.addWidget(lbl_valor)

        self._resumo_labels[chave] = lbl_valor
        return frame

    def _separador(self) -> QFrame:
        colors = theme_manager.colors
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background-color: {colors['border_subtle']}; border: none;")
        return line

    # ------------------------------------------------------------------ #
    #  Tabela de Histórico                                                  #
    # ------------------------------------------------------------------ #

    def _build_historico(self) -> ModernCard:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        card = ModernCard(padding=tokens.SPACING_XL)

        titulo = QLabel("📋  ÚLTIMAS TRANSFERÊNCIAS SP → CASCAVEL")
        titulo.setFont(theme_manager.get_font(tokens.FONT_SIZE_LG, bold=True))
        titulo.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        card.add_widget(titulo)

        colunas = [
            ("ID",         55),
            ("Data",       100),
            ("Caminhão",   180),
            ("Placa",      100),
            ("Motorista",  150),
            ("Notas SP",   120),
            ("Frete",      120),
            ("Pedágio",    120),
            ("Outros",     110),
            ("Custo",      120),
            ("Líquido",    130),
        ]

        self.tabela = QTableWidget(0, len(colunas))
        self.tabela.setHorizontalHeaderLabels([c[0] for c in colunas])
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setMinimumHeight(220)
        self.tabela.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        header = self.tabela.horizontalHeader()
        for i, (_, largura) in enumerate(colunas):
            header.resizeSection(i, largura)
        header.setStretchLastSection(True)

        self.tabela.setStyleSheet(f"""
        QTableWidget {{
            background-color: {colors['bg_secondary']};
            alternate-background-color: {colors['table_row_odd']};
            gridline-color: {colors['border_subtle']};
            border: 1px solid {colors['border_subtle']};
            border-radius: {tokens.RADIUS_MD}px;
            outline: none;
            font-size: {tokens.FONT_SIZE_MD}px;
        }}
        QTableWidget::item {{
            padding: 8px 12px;
            border: none;
            color: {colors['text_primary']};
        }}
        QTableWidget::item:selected {{
            background-color: {colors['violet_soft']};
            color: {colors['text_primary']};
        }}
        QHeaderView::section {{
            background-color: {colors['table_header_bg']};
            color: {colors['table_header_text']};
            padding: 10px 12px;
            border: none;
            border-bottom: 2px solid {colors['border_default']};
            font-weight: 700;
            font-size: {tokens.FONT_SIZE_SM}px;
        }}
        """)

        card.add_widget(self.tabela)
        return card

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
