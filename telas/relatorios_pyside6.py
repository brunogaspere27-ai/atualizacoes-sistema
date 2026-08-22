"""
Tela Relatórios - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QGroupBox, QMessageBox
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
    padding: 20px;
}
"""


class TelaRelatorios(QWidget):
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
        titulo = QLabel("📊 Relatórios")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()
        layout.addLayout(header)

        # Grid de relatórios
        grid = QHBoxLayout()
        grid.setSpacing(16)

        relatorios = [
            ("📈", "Faturamento", "Relatório de faturamento por período"),
            ("🚛", "Viagens", "Relatório detalhado de viagens"),
            ("⛽", "Combustível", "Consumo e custos de combustível"),
            ("🔧", "Manutenção", "Custos e histórico de manutenções"),
            ("💰", "Financeiro", "Receitas, despesas e fluxo de caixa"),
            ("📋", "Notas Fiscais", "Relatório de notas e manifestos"),
        ]

        for icon, nome, desc in relatorios:
            card = QFrame()
            card.setStyleSheet(CARD_STYLE)
            card.setMinimumWidth(200)
            cl = QVBoxLayout(card)
            cl.setSpacing(8)

            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 28px;")
            cl.addWidget(icon_lbl)

            nome_lbl = QLabel(nome)
            nome_lbl.setStyleSheet("font-size: 16px; font-weight: 700; color: #E6EDF3;")
            cl.addWidget(nome_lbl)

            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet("font-size: 12px; color: #9CA3AF;")
            desc_lbl.setWordWrap(True)
            cl.addWidget(desc_lbl)

            btn = QPushButton("Gerar Relatório")
            btn.setObjectName("primario")
            btn.clicked.connect(lambda checked, n=nome: self._gerar_relatorio(n))
            cl.addWidget(btn)

            grid.addWidget(card)

        layout.addLayout(grid)
        layout.addStretch()

    def _gerar_relatorio(self, nome):
        QMessageBox.information(self, "Relatório", "Gerando relatório: " + nome)
