"""
Tela Histórico de Viagens - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QDateEdit
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


class TelaHistorico(QWidget):
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
        titulo = QLabel("📜 Histórico de Viagens")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        btn_exportar = QPushButton("📤 Exportar")
        btn_exportar.setObjectName("secundario")
        header.addWidget(btn_exportar)
        layout.addLayout(header)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(12)

        self.filtro_busca = QLineEdit()
        self.filtro_busca.setPlaceholderText("🔍 Buscar viagem...")
        filtros.addWidget(self.filtro_busca)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos os status", "Concluída", "Em andamento", "Cancelada"])
        filtros.addWidget(self.filtro_status)

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        filtros.addWidget(self.data_inicio)

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        filtros.addWidget(self.data_fim)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("secundario")
        filtros.addWidget(btn_filtrar)
        layout.addLayout(filtros)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Data Saída", "Caminhão", "Motorista", "Notas", "KM", "Status", "Ações"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        # Resumo
        resumo = QHBoxLayout()
        resumo.setSpacing(16)
        for label_text, valor_text in [
            ("Total de Viagens", "0"),
            ("KM Percorridos", "0"),
            ("Média por Viagem", "0 km"),
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
            resumo.addWidget(card)
        layout.addLayout(resumo)
        layout.addStretch()

        self._carregar_dados()

    def _carregar_dados(self):
        self.tabela.setRowCount(0)
        for row_data in [
            ["1", "20/08/2026", "ABC-1234", "João Silva", "12", "1.250", "Concluída", "👁️"],
            ["2", "21/08/2026", "DEF-5678", "Pedro Santos", "8", "980", "Concluída", "👁️"],
        ]:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, col, item)
