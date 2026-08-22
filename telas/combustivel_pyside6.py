"""
Tela Combustível - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QDoubleSpinBox,
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
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox {
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


class TelaCombustivel(QWidget):
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
        titulo = QLabel("⛽ Controle de Combustível")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        btn_novo = QPushButton("+ Novo Abastecimento")
        btn_novo.setObjectName("primario")
        btn_novo.clicked.connect(self._novo_abastecimento)
        header.addWidget(btn_novo)
        layout.addLayout(header)

        # KPIs
        kpis = QHBoxLayout()
        kpis.setSpacing(16)
        for label_text, valor_text, color in [
            ("Total Litros", "0 L", "#0EA5E9"),
            ("Custo Total", "R$ 0,00", "#EF4444"),
            ("KM Rodados", "0", "#22C55E"),
            ("Média KM/L", "0,0", "#F59E0B"),
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

        self.filtro_data = QDateEdit()
        self.filtro_data.setCalendarPopup(True)
        self.filtro_data.setDate(QDate.currentDate())
        filtros.addWidget(self.filtro_data)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("secundario")
        filtros.addWidget(btn_filtrar)
        layout.addLayout(filtros)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "Data", "Caminhão", "Posto", "Litros", "Valor/L", "Total", "KM Atual", "Ações"
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
            ["22/08/2026", "ABC-1234", "Posto Shell", "200,0", "R$ 6,50", "R$ 1.300,00", "45.230", "✏️ 🗑️"],
        ]:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, col, item)

    def _novo_abastecimento(self):
        QMessageBox.information(self, "Novo Abastecimento", "Formulário de abastecimento será aberto.")
