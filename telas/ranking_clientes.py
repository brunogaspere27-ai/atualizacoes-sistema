"""
Tela de Ranking de Clientes - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QAbstractItemView, QFrame, QTabWidget
)
from PySide6.QtCore import Qt

ESTILO = """
QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', sans-serif;
}
QLabel#titulo { font-size: 22px; font-weight: 700; }
QComboBox {
    background-color: #21262D;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}
QPushButton#primario {
    background-color: #D32F2F;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton#primario:hover { background-color: #E53935; }
QPushButton#secundario {
    background-color: #21262D;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton#secundario:hover { background-color: #30363D; }
QTableWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    gridline-color: #21262D;
}
QHeaderView::section {
    background-color: #161B22;
    color: #9CA3AF;
    padding: 10px;
    border: none;
    font-weight: 600;
    font-size: 12px;
}
QTableWidget::item { padding: 10px; border-bottom: 1px solid #21262D; }
QTableWidget::item:selected { background-color: rgba(211, 47, 47, 0.15); }
QTabWidget::pane { border: 1px solid #30363D; border-radius: 8px; background: #161B22; }
QTabBar::tab {
    background: #21262D;
    color: #9CA3AF;
    padding: 10px 20px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
}
QTabBar::tab:selected { background: #D32F2F; color: #FFFFFF; }
"""

CARD_STYLE = """
QFrame {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px;
}
"""


class TelaRankingClientes(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(ESTILO)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        titulo = QLabel("📊 Ranking de Clientes")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Faturamento", "Volume", "Frequência", "Ticket Médio"])
        header.addWidget(self.combo_tipo)

        self.combo_mes = QComboBox()
        self.combo_mes.addItems(["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                                  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        header.addWidget(self.combo_mes)

        btn_exportar = QPushButton("📤 Exportar")
        btn_exportar.setObjectName("secundario")
        header.addWidget(btn_exportar)
        layout.addLayout(header)

        # Top 3 Podium
        podium = QHBoxLayout()
        podium.setSpacing(16)
        for pos, (cliente, valor, cor) in enumerate([
            ("2º Lugar", "R$ 85.000", "#C0C0C0"),
            ("1º Lugar", "R$ 120.000", "#FFD700"),
            ("3º Lugar", "R$ 62.000", "#CD7F32"),
        ]):
            card = QFrame()
            card.setStyleSheet(CARD_STYLE)
            cl = QVBoxLayout(card)
            cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            pos_lbl = QLabel("🥇" if pos == 1 else "🥈" if pos == 0 else "🥉")
            pos_lbl.setStyleSheet("font-size: 32px; color: " + cor + ";")
            pos_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(pos_lbl)
            nome = QLabel(cliente)
            nome.setStyleSheet("font-size: 14px; font-weight: 600; color: #E6EDF3;")
            nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(nome)
            val = QLabel(valor)
            val.setStyleSheet("font-size: 18px; font-weight: 700; color: " + cor + ";")
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(val)
            podium.addWidget(card)
        layout.addLayout(podium)

        # Tabela completa
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Posição", "Cliente", "Faturamento", "Volume", "Fretes", "Ticket Médio"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        self._carregar_dados()
        layout.addStretch()

    def _carregar_dados(self):
        self.tabela.setRowCount(0)
        for i, row_data in enumerate([
            ["1", "Cliente A Ltda", "R$ 120.000,00", "450t", "32", "R$ 3.750,00"],
            ["2", "Cliente B S/A", "R$ 85.000,00", "320t", "28", "R$ 3.035,00"],
            ["3", "Cliente C ME", "R$ 62.000,00", "210t", "19", "R$ 3.263,00"],
        ]):
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 0 and i < 3:
                    item.setForeground(Qt.GlobalColor.yellow if i == 0 else Qt.GlobalColor.lightGray if i == 1 else Qt.GlobalColor.darkYellow)
                self.tabela.setItem(row, col, item)
