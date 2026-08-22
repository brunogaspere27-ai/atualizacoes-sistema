"""
Tela Criar Viagem - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QAbstractItemView, QFrame, QGroupBox, QMessageBox
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
"""

CARD_STYLE = """
QFrame {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px;
}
"""


class TelaCriarViagem(QWidget):
    def __init__(self, cliente_pre_selecionado=None, parent=None):
        super().__init__(parent)
        self.cliente_pre_selecionado = cliente_pre_selecionado
        self.setStyleSheet(ESTILO)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header
        header = QHBoxLayout()
        titulo = QLabel("🚛 Criar Nova Viagem")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()
        layout.addLayout(header)

        # Seleção de caminhão
        grp_caminhao = QGroupBox("🚚 Selecionar Caminhão")
        cam_layout = QHBoxLayout(grp_caminhao)

        self.combo_caminhao = QComboBox()
        self.combo_caminhao.addItems(["Selecione...", "ABC-1234 - Volvo FH 540", "DEF-5678 - Scania R450", "GHI-9012 - Mercedes Actros"])
        cam_layout.addWidget(self.combo_caminhao)

        btn_verificar = QPushButton("Verificar Disponibilidade")
        btn_verificar.setObjectName("secundario")
        cam_layout.addWidget(btn_verificar)
        layout.addWidget(grp_caminhao)

        # Notas disponíveis
        grp_notas = QGroupBox("📋 Notas Disponíveis para Viagem")
        notas_layout = QVBoxLayout(grp_notas)

        self.tabela_notas = QTableWidget()
        self.tabela_notas.setColumnCount(6)
        self.tabela_notas.setHorizontalHeaderLabels([
            "Selecionar", "Nº Nota", "Remetente", "Destinatário", "Peso", "Valor"
        ])
        self.tabela_notas.horizontalHeader().setStretchLastSection(True)
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_notas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_notas.setAlternatingRowColors(True)
        self.tabela_notas.verticalHeader().setVisible(False)
        notas_layout.addWidget(self.tabela_notas)
        layout.addWidget(grp_notas)

        # Resumo
        resumo = QHBoxLayout()
        resumo.setSpacing(16)
        for label_text, valor_text in [
            ("Notas Selecionadas", "0"),
            ("Peso Total", "0 kg"),
            ("Valor Total", "R$ 0,00"),
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

        # Botões
        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secundario")
        botoes.addWidget(btn_cancelar)

        btn_criar = QPushButton("✓ Criar Viagem")
        btn_criar.setObjectName("primario")
        btn_criar.clicked.connect(self._criar_viagem)
        botoes.addWidget(btn_criar)
        layout.addLayout(botoes)

        self._carregar_notas()
        layout.addStretch()

    def _carregar_notas(self):
        self.tabela_notas.setRowCount(0)
        for row_data in [
            ["☐", "NF-001", "Empresa A", "Empresa B", "1.200 kg", "R$ 5.000,00"],
            ["☐", "NF-002", "Empresa C", "Empresa D", "850 kg", "R$ 3.200,00"],
        ]:
            row = self.tabela_notas.rowCount()
            self.tabela_notas.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela_notas.setItem(row, col, item)

    def _criar_viagem(self):
        QMessageBox.information(self, "Sucesso", "Viagem criada com sucesso!")
