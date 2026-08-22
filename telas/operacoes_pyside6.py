"""
Tela de Operações - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QGroupBox,
    QDateEdit, QDoubleSpinBox, QSpinBox, QMessageBox,
    QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

ESTILO = """
QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', sans-serif;
}
QLabel {
    color: #E6EDF3;
    background: transparent;
}
QLabel#titulo {
    font-size: 22px;
    font-weight: 700;
}
QLabel#subtitulo {
    font-size: 13px;
    color: #9CA3AF;
}
QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox {
    background-color: #21262D;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    min-height: 18px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #D32F2F;
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
QPushButton#primario:pressed { background-color: #C62828; }
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
QPushButton#perigo {
    background-color: transparent;
    color: #EF4444;
    border: 1px solid #EF4444;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 13px;
}
QPushButton#perigo:hover { background-color: rgba(239, 68, 68, 0.15); }
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
QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #21262D;
}
QTableWidget::item:selected {
    background-color: rgba(211, 47, 47, 0.15);
}
QGroupBox {
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 12px;
    margin-top: 12px;
    padding: 16px;
    font-weight: 600;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 16px;
    padding: 0 8px;
}
QScrollBar:vertical {
    background: #161B22;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #30363D;
    border-radius: 4px;
    min-height: 30px;
}
"""


class TelaOperacoes(QWidget):
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
        titulo = QLabel("📋 Operações de Transporte")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        btn_nova = QPushButton("+ Nova Operação")
        btn_nova.setObjectName("primario")
        btn_nova.clicked.connect(self._nova_operacao)
        header.addWidget(btn_nova)
        layout.addLayout(header)

        # Filtros
        filtros = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout(filtros)
        filtros_layout.setSpacing(12)

        self.filtro_busca = QLineEdit()
        self.filtro_busca.setPlaceholderText("🔍 Buscar por placa, motorista ou cliente...")
        self.filtro_busca.setMinimumWidth(300)
        filtros_layout.addWidget(self.filtro_busca)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos os status", "Pendente", "Em andamento", "Concluído", "Cancelado"])
        filtros_layout.addWidget(self.filtro_status)

        self.filtro_data = QDateEdit()
        self.filtro_data.setCalendarPopup(True)
        self.filtro_data.setDate(QDate.currentDate())
        filtros_layout.addWidget(self.filtro_data)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setObjectName("secundario")
        filtros_layout.addWidget(btn_filtrar)
        layout.addWidget(filtros)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Data", "Caminhão", "Motorista", "Valor Notas", "Frete", "Status", "Ações"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setMinimumHeight(400)
        layout.addWidget(self.tabela)

        # Resumo
        resumo = QHBoxLayout()
        resumo.setSpacing(16)

        for label_text, valor_text in [
            ("Total de Operações", "0"),
            ("Valor em Notas", "R$ 0,00"),
            ("Total de Fretes", "R$ 0,00"),
            ("Líquido", "R$ 0,00"),
        ]:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #161B22;
                    border: 1px solid #30363D;
                    border-radius: 12px;
                    padding: 16px;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(4)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #9CA3AF; font-size: 12px;")
            card_layout.addWidget(lbl)
            val = QLabel(valor_text)
            val.setStyleSheet("color: #E6EDF3; font-size: 20px; font-weight: 700;")
            card_layout.addWidget(val)
            resumo.addWidget(card)

        layout.addLayout(resumo)
        layout.addStretch()

        self._carregar_dados()

    def _carregar_dados(self):
        self.tabela.setRowCount(0)
        # Dados mock - substituir por consulta real
        dados = [
            ["1", "22/08/2026", "ABC-1234", "João Silva", "R$ 15.000,00", "R$ 3.500,00", "Concluído", "👁️ ✏️ 🗑️"],
            ["2", "22/08/2026", "DEF-5678", "Pedro Santos", "R$ 22.000,00", "R$ 4.200,00", "Em andamento", "👁️ ✏️ 🗑️"],
        ]
        for row_data in dados:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, col, item)

    def _nova_operacao(self):
        QMessageBox.information(self, "Nova Operação", "Formulário de nova operação será aberto.")
