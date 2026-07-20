"""
Operações Aurora v1.0 - CW Transportadora
Tela de operações com Aurora Design System

Features:
- Formulário com glassmorphism
- Painel de resumo ao vivo
- Tabela de histórico premium
- Gradientes e glow effects
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
from telas.theme_aurora import aurora_theme_manager, AccentColor
from utils.components_aurora import (
    AuroraCard, AuroraButton, ButtonStyle, CardVariant,
    AuroraTable, SeparatorLine,
)
from utils.helpers import formatar_moeda, parse_numero


class OperacoesAurora(QWidget):
    """Tela de controle de transferências com Aurora Design System."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Dicionário de QLineEdit indexado por nome de campo
        self.campos: dict[str, QLineEdit] = {}

        # Labels de valor no painel de resumo (atualizadas ao vivo)
        self._resumo_labels: dict[str, QLabel] = {}

        self._setup_ui()
        self._carregar_historico()

    def _setup_ui(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
        QScrollArea {{
            background-color: {c['bg_primary']};
            border: none;
        }}
        QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 2px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 3px; min-height: 40px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['border_strong']}; }}
        """)
        root.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background-color: {c['bg_primary']};")
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(t.SPACING_3XL, t.SPACING_XL, t.SPACING_3XL, t.SPACING_2XL)
        content_layout.setSpacing(t.SPACING_XL)
        content.setLayout(content_layout)
        scroll.setWidget(content)

        # Header
        header = self._create_header()
        content_layout.addWidget(header)

        # Linha: formulário + resumo
        row_layout = QHBoxLayout()
        row_layout.setSpacing(t.SPACING_XL)
        row_layout.addWidget(self._build_form(), stretch=2)
        row_layout.addWidget(self._build_resumo(), stretch=1)
        content_layout.addLayout(row_layout)

        # Tabela de histórico
        content_layout.addWidget(self._build_historico())

    def _create_header(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(t.SPACING_MD)
        header.setLayout(hl)

        title = QLabel("Nova Operação")
        title.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_3XL, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        hl.addWidget(title)

        hl.addStretch()

        subtitle = QLabel("Transferência SP → Cascavel")
        subtitle.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_MD))
        subtitle.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        hl.addWidget(subtitle)

        return header

    def _build_form(self) -> AuroraCard:
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        card = AuroraCard(
            "Dados da Transferência",
            "truck",
            variant=CardVariant.GLOW,
            accent_color=AccentColor.COSMOS,
            padding=t.SPACING_2XL
        )

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(t.SPACING_LG)
        grid.setContentsMargins(0, 0, 0, 0)

        # Campos do formulário
        campos_config = [
            ("data", "Data", "DD/MM/AAAA"),
            ("km_inicial", "KM Inicial", "0"),
            ("km_final", "KM Final", "0"),
            ("litros", "Litros", "0"),
            ("valor_litro", "Valor/Litro", "0,00"),
            ("pedagio", "Pedágio", "0,00"),
            ("outros", "Outros", "0,00"),
            ("valor_frete", "Valor Frete", "0,00"),
        ]

        for idx, (campo, label, placeholder) in enumerate(campos_config):
            row = idx // 2
            col = (idx % 2) * 2

            lbl = QLabel(label)
            lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
            lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            grid.addWidget(lbl, row, col)

            input_field = QLineEdit()
            input_field.setPlaceholderText(placeholder)
            input_field.setFixedHeight(44)
            input_field.setStyleSheet(f"""
            QLineEdit {{
                background: {c['bg_tertiary']};
                color: {c['text_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {t.RADIUS_LG}px;
                padding: 10px 16px;
                font-size: {t.FONT_SIZE_MD}px;
            }}
            QLineEdit:hover {{ border-color: {c['border_strong']}; }}
            QLineEdit:focus {{
                border: 1px solid {c['aurora']};
                background: {c['bg_surface']};
            }}
            """)
            input_field.textChanged.connect(self._atualizar_resumo)
            self.campos[campo] = input_field
            grid.addWidget(input_field, row, col + 1)

        card.add_layout(grid)

        # Botão salvar
        btn_salvar = AuroraButton("Salvar Operação", ButtonStyle.AURORA, "save")
        btn_salvar.setFixedHeight(48)
        btn_salvar.clicked.connect(self._salvar_operacao)
        card.add_widget(btn_salvar)

        return card

    def _build_resumo(self) -> AuroraCard:
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        card = AuroraCard(
            "Resumo",
            "calculator",
            variant=CardVariant.GLOW,
            accent_color=AccentColor.FOREST,
            padding=t.SPACING_2XL
        )

        resumo_layout = QVBoxLayout()
        resumo_layout.setSpacing(t.SPACING_MD)
        resumo_layout.setContentsMargins(0, 0, 0, 0)

        # Itens de resumo
        resumo_items = [
            ("km_percorridos", "KM Percorridos", "0 km"),
            ("custo_combustivel", "Custo Combustível", "R$ 0,00"),
            ("custo_total", "Custo Total", "R$ 0,00"),
            ("lucro", "Lucro", "R$ 0,00"),
        ]

        for key, label, default in resumo_items:
            row = QHBoxLayout()
            row.setSpacing(t.SPACING_SM)

            lbl = QLabel(label)
            lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM))
            lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            row.addWidget(lbl)

            row.addStretch()

            val_lbl = QLabel(default)
            val_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_MD, bold=True))
            val_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
            row.addWidget(val_lbl)

            self._resumo_labels[key] = val_lbl
            resumo_layout.addLayout(row)

        # Separador
        resumo_layout.addWidget(SeparatorLine("horizontal"))

        # Margem
        margem_row = QHBoxLayout()
        margem_row.setSpacing(t.SPACING_SM)

        margem_lbl = QLabel("Margem")
        margem_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        margem_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        margem_row.addWidget(margem_lbl)

        margem_row.addStretch()

        self._margem_lbl = QLabel("0%")
        self._margem_lbl.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_XL, QFont.Weight.Bold))
        self._margem_lbl.setStyleSheet(f"color: {c['forest']}; background: transparent;")
        margem_row.addWidget(self._margem_lbl)

        resumo_layout.addLayout(margem_row)

        card.add_layout(resumo_layout)

        return card

    def _build_historico(self) -> AuroraCard:
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        card = AuroraCard(
            "Histórico de Transferências",
            "history",
            variant=CardVariant.DEFAULT,
            accent_color=AccentColor.OCEAN,
            padding=t.SPACING_2XL
        )

        self.historico_table = AuroraTable()
        self.historico_table.setColumnCount(8)
        self.historico_table.setHorizontalHeaderLabels([
            "Data", "KM Inicial", "KM Final", "Litros",
            "Valor/L", "Pedágio", "Outros", "Frete"
        ])
        self.historico_table.setFixedHeight(300)

        card.add_widget(self.historico_table)

        return card

    def _atualizar_resumo(self):
        """Atualiza o painel de resumo ao vivo."""
        try:
            km_inicial = parse_numero(self.campos["km_inicial"].text()) or 0
            km_final = parse_numero(self.campos["km_final"].text()) or 0
            litros = parse_numero(self.campos["litros"].text()) or 0
            valor_litro = parse_numero(self.campos["valor_litro"].text()) or 0
            pedagio = parse_numero(self.campos["pedagio"].text()) or 0
            outros = parse_numero(self.campos["outros"].text()) or 0
            valor_frete = parse_numero(self.campos["valor_frete"].text()) or 0

            km_percorridos = km_final - km_inicial
            custo_combustivel = litros * valor_litro
            custo_total = custo_combustivel + pedagio + outros
            lucro = valor_frete - custo_total
            margem = (lucro / valor_frete * 100) if valor_frete > 0 else 0

            self._resumo_labels["km_percorridos"].setText(f"{km_percorridos} km")
            self._resumo_labels["custo_combustivel"].setText(formatar_moeda(custo_combustivel))
            self._resumo_labels["custo_total"].setText(formatar_moeda(custo_total))
            self._resumo_labels["lucro"].setText(formatar_moeda(lucro))
            self._margem_lbl.setText(f"{margem:.1f}%")

            # Colorir margem
            c = aurora_theme_manager.colors
            if margem >= 20:
                self._margem_lbl.setStyleSheet(f"color: {c['forest']}; background: transparent;")
            elif margem >= 10:
                self._margem_lbl.setStyleSheet(f"color: {c['aurora']}; background: transparent;")
            else:
                self._margem_lbl.setStyleSheet(f"color: {c['crimson']}; background: transparent;")

        except Exception:
            pass

    def _salvar_operacao(self):
        """Salva a operação no banco."""
        try:
            dados = {
                "data": self.campos["data"].text(),
                "km_inicial": parse_numero(self.campos["km_inicial"].text()) or 0,
                "km_final": parse_numero(self.campos["km_final"].text()) or 0,
                "litros": parse_numero(self.campos["litros"].text()) or 0,
                "valor_litro": parse_numero(self.campos["valor_litro"].text()) or 0,
                "pedagio": parse_numero(self.campos["pedagio"].text()) or 0,
                "outros": parse_numero(self.campos["outros"].text()) or 0,
                "valor_frete": parse_numero(self.campos["valor_frete"].text()) or 0,
            }

            operacoes_service.salvar_operacao(dados)
            QMessageBox.information(self, "Sucesso", "Operação salva com sucesso!")
            self._carregar_historico()

            # Limpar campos
            for campo in self.campos.values():
                campo.clear()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar operação: {e}")

    def _carregar_historico(self):
        """Carrega o histórico de operações."""
        try:
            operacoes = operacoes_service.listar_operacoes()
            self.historico_table.setRowCount(0)

            for idx, op in enumerate(operacoes):
                self.historico_table.insertRow(idx)
                self.historico_table.setItem(idx, 0, QTableWidgetItem(op.get("data", "")))
                self.historico_table.setItem(idx, 1, QTableWidgetItem(str(op.get("km_inicial", 0))))
                self.historico_table.setItem(idx, 2, QTableWidgetItem(str(op.get("km_final", 0))))
                self.historico_table.setItem(idx, 3, QTableWidgetItem(str(op.get("litros", 0))))
                self.historico_table.setItem(idx, 4, QTableWidgetItem(formatar_moeda(op.get("valor_litro", 0))))
                self.historico_table.setItem(idx, 5, QTableWidgetItem(formatar_moeda(op.get("pedagio", 0))))
                self.historico_table.setItem(idx, 6, QTableWidgetItem(formatar_moeda(op.get("outros", 0))))
                self.historico_table.setItem(idx, 7, QTableWidgetItem(formatar_moeda(op.get("valor_frete", 0))))

        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
