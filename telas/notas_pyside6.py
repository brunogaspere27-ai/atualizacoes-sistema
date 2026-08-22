"""
Tela de Notas/Manifestos - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QTabWidget,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt

ESTILO = """
QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', sans-serif;
}
QLabel#titulo { font-size: 22px; font-weight: 700; }
QLabel#subtitulo { font-size: 13px; color: #9CA3AF; }
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
QTabBar::tab:hover:!selected { background: #30363D; color: #E6EDF3; }
"""

CARD_STYLE = """
QFrame {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 16px;
}
"""


class TelaNotas(QWidget):
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
        titulo = QLabel("📄 Notas Fiscais & Manifestos")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()

        btn_importar = QPushButton("📥 Importar XML")
        btn_importar.setObjectName("primario")
        btn_importar.clicked.connect(self._importar_xml)
        header.addWidget(btn_importar)
        layout.addLayout(header)

        # Tabs
        tabs = QTabWidget()

        # Tab Manifestos
        tab_manifestos = QWidget()
        m_layout = QVBoxLayout(tab_manifestos)
        m_layout.setContentsMargins(16, 16, 16, 16)

        filtros = QHBoxLayout()
        self.filtro_busca = QLineEdit()
        self.filtro_busca.setPlaceholderText("🔍 Buscar manifesto...")
        filtros.addWidget(self.filtro_busca)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos", "Aberto", "Em viagem", "Entregue"])
        filtros.addWidget(self.filtro_status)

        btn_filtro = QPushButton("Filtrar")
        btn_filtro.setObjectName("secundario")
        filtros.addWidget(btn_filtro)
        m_layout.addLayout(filtros)

        self.tabela_manifestos = QTableWidget()
        self.tabela_manifestos.setColumnCount(7)
        self.tabela_manifestos.setHorizontalHeaderLabels([
            "Nº Manifesto", "Transportadora", "Data", "Qtd Notas", "Valor Total", "Status", "Ações"
        ])
        self.tabela_manifestos.horizontalHeader().setStretchLastSection(True)
        self.tabela_manifestos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_manifestos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_manifestos.setAlternatingRowColors(True)
        self.tabela_manifestos.verticalHeader().setVisible(False)
        m_layout.addWidget(self.tabela_manifestos)
        tabs.addTab(tab_manifestos, "📋 Manifestos")

        # Tab Notas
        tab_notas = QWidget()
        n_layout = QVBoxLayout(tab_notas)
        n_layout.setContentsMargins(16, 16, 16, 16)

        self.tabela_notas = QTableWidget()
        self.tabela_notas.setColumnCount(8)
        self.tabela_notas.setHorizontalHeaderLabels([
            "Nº Nota", "Chave Acesso", "Remetente", "Destinatário", "Valor", "Peso", "Volumes", "Status"
        ])
        self.tabela_notas.horizontalHeader().setStretchLastSection(True)
        self.tabela_notas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_notas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_notas.setAlternatingRowColors(True)
        self.tabela_notas.verticalHeader().setVisible(False)
        n_layout.addWidget(self.tabela_notas)
        tabs.addTab(tab_notas, "🧾 Notas Fiscais")

        layout.addWidget(tabs)

        # Resumo
        resumo = QHBoxLayout()
        resumo.setSpacing(16)
        for label_text, valor_text, color in [
            ("Manifestos", "0", "#E6EDF3"),
            ("Notas Importadas", "0", "#E6EDF3"),
            ("Valor Total", "R$ 0,00", "#22C55E"),
            ("Pendências", "0", "#F59E0B"),
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
            resumo.addWidget(card)
        layout.addLayout(resumo)
        layout.addStretch()

        self._carregar_dados()

    def _carregar_dados(self):
        self.tabela_manifestos.setRowCount(0)
        for row_data in [
            ["MNF-001", "CW Transportes", "22/08/2026", "12", "R$ 45.000,00", "Aberto", "👁️ ✏️ 🗑️"],
        ]:
            row = self.tabela_manifestos.rowCount()
            self.tabela_manifestos.insertRow(row)
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela_manifestos.setItem(row, col, item)

    def _importar_xml(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self, 
            "Importar Manifesto", 
            "", 
            "Todos os arquivos (*.*);;XML (*.xml);;TXT (*.txt);;CSV (*.csv);;PDF (*.pdf)"
        )
        if arquivo:
            QMessageBox.information(self, "Importar", "Arquivo selecionado: " + arquivo)
