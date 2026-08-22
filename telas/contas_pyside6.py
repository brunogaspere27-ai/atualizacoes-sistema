"""
Tela Contas (Receber/Pagar) - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QTabWidget,
    QDateEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate

ESTILO = """
QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', sans-serif;
}
QLabel#titulo { font-size: 22px; font-weight: 700; }
QLineEdit, QComboBox, QDateEdit {
    background-color: #21262D;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #D32F2F; }
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


class TelaContas(QWidget):
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
        titulo = QLabel("💰 Contas a Receber / Pagar")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        btn_nova = QPushButton("+ Nova Conta")
        btn_nova.setObjectName("primario")
        btn_nova.clicked.connect(self._nova_conta)
        header.addWidget(btn_nova)
        layout.addLayout(header)

        # KPIs
        kpis = QHBoxLayout()
        kpis.setSpacing(16)
        for label_text, valor_text, color in [
            ("A Receber", "R$ 0,00", "#22C55E"),
            ("A Pagar", "R$ 0,00", "#EF4444"),
            ("Saldo", "R$ 0,00", "#0EA5E9"),
            ("Vencidas", "0", "#F59E0B"),
        ]:
            card = QFrame()
            card.setStyleSheet(CARD_STYLE)
            cl = QVBoxLayout(card)
            cl.setSpacing(4)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #9CA3AF; font-size: 12px;")
            cl.addWidget(lbl)
            val = QLabel(valor_text)
            val.setStyleSheet("color: " + color + "; font-size: 20px; font-weight: 700;")
            cl.addWidget(val)
            kpis.addWidget(card)
        layout.addLayout(kpis)

        # Tabs
        tabs = QTabWidget()

        # Receber
        tab_receber = QWidget()
        tr_layout = QVBoxLayout(tab_receber)
        tr_layout.setContentsMargins(16, 16, 16, 16)

        self.tabela_receber = QTableWidget()
        self.tabela_receber.setColumnCount(7)
        self.tabela_receber.setHorizontalHeaderLabels([
            "Descrição", "Cliente", "Valor", "Vencimento", "Status", "Categoria", "Ações"
        ])
        self.tabela_receber.horizontalHeader().setStretchLastSection(True)
        self.tabela_receber.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_receber.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_receber.setAlternatingRowColors(True)
        self.tabela_receber.verticalHeader().setVisible(False)
        tr_layout.addWidget(self.tabela_receber)
        tabs.addTab(tab_receber, "📥 A Receber")

        # Pagar
        tab_pagar = QWidget()
        tp_layout = QVBoxLayout(tab_pagar)
        tp_layout.setContentsMargins(16, 16, 16, 16)

        self.tabela_pagar = QTableWidget()
        self.tabela_pagar.setColumnCount(7)
        self.tabela_pagar.setHorizontalHeaderLabels([
            "Descrição", "Fornecedor", "Valor", "Vencimento", "Status", "Categoria", "Ações"
        ])
        self.tabela_pagar.horizontalHeader().setStretchLastSection(True)
        self.tabela_pagar.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_pagar.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_pagar.setAlternatingRowColors(True)
        self.tabela_pagar.verticalHeader().setVisible(False)
        tp_layout.addWidget(self.tabela_pagar)
        tabs.addTab(tab_pagar, "📤 A Pagar")

        layout.addWidget(tabs)
        layout.addStretch()

        self._carregar_dados()

    def _carregar_dados(self):
        self.tabela_receber.setRowCount(0)
        self.tabela_pagar.setRowCount(0)

    def _nova_conta(self):
        QMessageBox.information(self, "Nova Conta", "Formulário de nova conta será aberto.")
