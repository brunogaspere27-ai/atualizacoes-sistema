"""
Tela Funcionários - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QTabWidget,
    QMessageBox
)
from PySide6.QtCore import Qt

ESTILO = """
QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', sans-serif;
}
QLabel#titulo { font-size: 22px; font-weight: 700; }
QLineEdit, QComboBox {
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


class TelaFuncionarios(QWidget):
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
        titulo = QLabel("👥 Funcionários")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        btn_novo = QPushButton("+ Novo Funcionário")
        btn_novo.setObjectName("primario")
        btn_novo.clicked.connect(self._novo_funcionario)
        header.addWidget(btn_novo)
        layout.addLayout(header)

        # KPIs
        kpis = QHBoxLayout()
        kpis.setSpacing(16)
        for label_text, valor_text in [
            ("Total Funcionários", "0"),
            ("Ativos", "0"),
            ("Folha Mensal", "R$ 0,00"),
        ]:
            card = QFrame()
            card.setStyleSheet(CARD_STYLE)
            cl = QVBoxLayout(card)
            cl.setSpacing(4)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #9CA3AF; font-size: 12px;")
            cl.addWidget(lbl)
            val = QLabel(valor_text)
            val.setStyleSheet("color: #E6EDF3; font-size: 20px; font-weight: 700;")
            cl.addWidget(val)
            kpis.addWidget(card)
        layout.addLayout(kpis)

        # Tabs
        tabs = QTabWidget()

        # Funcionários
        tab_func = QWidget()
        tf_layout = QVBoxLayout(tab_func)
        tf_layout.setContentsMargins(16, 16, 16, 16)

        filtros = QHBoxLayout()
        self.filtro_busca = QLineEdit()
        self.filtro_busca.setPlaceholderText("🔍 Buscar funcionário...")
        filtros.addWidget(self.filtro_busca)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Ativo", "Inativo"])
        filtros.addWidget(self.filtro_status)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("secundario")
        filtros.addWidget(btn_filtrar)
        tf_layout.addLayout(filtros)

        self.tabela_func = QTableWidget()
        self.tabela_func.setColumnCount(7)
        self.tabela_func.setHorizontalHeaderLabels([
            "Nome", "CPF", "Cargo", "Salário", "Admissão", "Status", "Ações"
        ])
        self.tabela_func.horizontalHeader().setStretchLastSection(True)
        self.tabela_func.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_func.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_func.setAlternatingRowColors(True)
        self.tabela_func.verticalHeader().setVisible(False)
        tf_layout.addWidget(self.tabela_func)
        tabs.addTab(tab_func, "👥 Funcionários")

        # Folha
        tab_folha = QWidget()
        tfolha_layout = QVBoxLayout(tab_folha)
        tfolha_layout.setContentsMargins(16, 16, 16, 16)

        self.tabela_folha = QTableWidget()
        self.tabela_folha.setColumnCount(6)
        self.tabela_folha.setHorizontalHeaderLabels([
            "Funcionário", "Salário Base", "Horas Extras", "Adicionais", "Descontos", "Líquido"
        ])
        self.tabela_folha.horizontalHeader().setStretchLastSection(True)
        self.tabela_folha.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_folha.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_folha.setAlternatingRowColors(True)
        self.tabela_folha.verticalHeader().setVisible(False)
        tfolha_layout.addWidget(self.tabela_folha)
        tabs.addTab(tab_folha, "💵 Folha de Pagamento")

        layout.addWidget(tabs)
        layout.addStretch()

        self._carregar_dados()

    def _carregar_dados(self):
        self.tabela_func.setRowCount(0)
        self.tabela_folha.setRowCount(0)

    def _novo_funcionario(self):
        QMessageBox.information(self, "Novo Funcionário", "Formulário será aberto.")
