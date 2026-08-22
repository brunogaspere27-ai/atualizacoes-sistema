"""
Tela Manutenção - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QDateEdit,
    QMessageBox
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
"""

CARD_STYLE = """
QFrame {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px;
}
"""


class TelaManutencao(QWidget):
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
        titulo = QLabel("🔧 Controle de Manutenções")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        btn_nova = QPushButton("+ Nova Manutenção")
        btn_nova.setObjectName("primario")
        btn_nova.clicked.connect(self._nova_manutencao)
        header.addWidget(btn_nova)
        layout.addLayout(header)

        # KPIs
        kpis = QHBoxLayout()
        kpis.setSpacing(16)
        for label_text, valor_text, color in [
            ("Total Manutenções", "0", "#E6EDF3"),
            ("Custo Total", "R$ 0,00", "#EF4444"),
            ("Pendentes", "0", "#F59E0B"),
            ("Concluídas", "0", "#22C55E"),
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

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(12)

        self.filtro_caminhao = QComboBox()
        self.filtro_caminhao.addItems(["Todos os caminhões", "ABC-1234", "DEF-5678", "GHI-9012"])
        filtros.addWidget(self.filtro_caminhao)

        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Todos os tipos", "Preventiva", "Corretiva", "Revisão", "Pneus"])
        filtros.addWidget(self.filtro_tipo)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Pendente", "Em andamento", "Concluída"])
        filtros.addWidget(self.filtro_status)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("secundario")
        filtros.addWidget(btn_filtrar)
        layout.addLayout(filtros)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "Data", "Caminhão", "Tipo", "Descrição", "Oficina", "Valor", "KM", "Status"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        layout.addStretch()

        self._carregar_dados()

    def _carregar_dados(self):
        self.tabela.setRowCount(0)
        for row_data in [
            ["20/08/2026", "ABC-1234", "Preventiva", "Troca de óleo", "Oficina Central", "R$ 850,00", "45.000", "Concluída"],
        ]:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, col, item)

    def _nova_manutencao(self):
        QMessageBox.information(self, "Nova Manutenção", "Formulário de manutenção será aberto.")
