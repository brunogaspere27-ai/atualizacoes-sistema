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

from services.notas_service import notas_service
from utils.database.notas import listar_notas

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
        self._manifesto_selecionado_id = None
        self._setup_ui()
        self._carregar_manifestos()
        self._carregar_notas()

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

        btn_importar = QPushButton("📥 Importar TXT")
        btn_importar.setObjectName("primario")
        btn_importar.clicked.connect(self._importar_txt)
        header.addWidget(btn_importar)

        btn_exportar = QPushButton("📤 Exportar XML")
        btn_exportar.setObjectName("secundario")
        btn_exportar.clicked.connect(self._exportar_xml)
        header.addWidget(btn_exportar)
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
        btn_filtro.clicked.connect(self._carregar_manifestos)
        filtros.addWidget(btn_filtro)
        m_layout.addLayout(filtros)

        self.tabela_manifestos = QTableWidget()
        self.tabela_manifestos.setColumnCount(7)
        self.tabela_manifestos.setHorizontalHeaderLabels([
            "ID", "Arquivo", "Importado em", "Qtd Notas", "Valor Total", "Frete Total", "Ações"
        ])
        self.tabela_manifestos.horizontalHeader().setStretchLastSection(True)
        self.tabela_manifestos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela_manifestos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_manifestos.setAlternatingRowColors(True)
        self.tabela_manifestos.verticalHeader().setVisible(False)
        self.tabela_manifestos.itemSelectionChanged.connect(self._on_manifesto_selecionado)
        m_layout.addWidget(self.tabela_manifestos)
        tabs.addTab(tab_manifestos, "📋 Manifestos")

        # Tab Notas
        tab_notas = QWidget()
        n_layout = QVBoxLayout(tab_notas)
        n_layout.setContentsMargins(16, 16, 16, 16)

        self.tabela_notas = QTableWidget()
        self.tabela_notas.setColumnCount(10)
        self.tabela_notas.setHorizontalHeaderLabels([
            "ID", "Chave/CT-e", "Remetente", "Destinatário", "Origem", "Destino", "Valor", "Frete", "Peso", "Status"
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
            val.setObjectName(f"resumo_{label_text.lower().replace(' ', '_')}")
            val.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: 700;")
            cl.addWidget(val)
            resumo.addWidget(card)
        layout.addLayout(resumo)
        layout.addStretch()

    def _carregar_manifestos(self):
        self.tabela_manifestos.setRowCount(0)
        manifestos = notas_service.listar_manifestos()
        
        total_notas = 0
        total_valor = 0
        total_pendencias = 0
        
        for row_data in manifestos:
            # row_data: (id, nome_arquivo, data_importacao, total_notas, valor_total, frete_total, peso_total)
            row = self.tabela_manifestos.rowCount()
            self.tabela_manifestos.insertRow(row)
            
            valores = [
                str(row_data[0]),
                str(row_data[1]),
                str(row_data[2]),
                str(row_data[3]),
                f"R$ {float(row_data[4] or 0):,.2f}",
                f"R$ {float(row_data[5] or 0):,.2f}",
                "👁️ 🗑️"
            ]
            
            for col, value in enumerate(valores):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela_manifestos.setItem(row, col, item)
            
            total_notas += int(row_data[3] or 0)
            total_valor += float(row_data[4] or 0)
            if int(row_data[3] or 0) == 0:
                total_pendencias += 1
        
        # Atualizar resumo
        self._atualizar_resumo("manifestos", str(len(manifestos)))
        self._atualizar_resumo("notas_importadas", str(total_notas))
        self._atualizar_resumo("valor_total", f"R$ {total_valor:,.2f}")
        self._atualizar_resumo("pendencias", str(total_pendencias))

    def _carregar_notas(self):
        self.tabela_notas.setRowCount(0)
        notas = listar_notas()
        
        for nota in notas:
            # (id, chave_nfe, numero_cte, remetente, destinatario, origem, destino, valor_frete, peso, status)
            row = self.tabela_notas.rowCount()
            self.tabela_notas.insertRow(row)
            
            valores = [
                str(nota[0]),
                str(nota[2] or nota[1] or "-"),
                str(nota[3] or "-"),
                str(nota[4] or "-"),
                str(nota[5] or "-"),
                str(nota[6] or "-"),
                f"R$ {float(nota[7] or 0):,.2f}",
                f"R$ {float(nota[8] or 0):,.2f}",
                f"{float(nota[9] or 0):,.2f} kg",
                str(nota[10] or "-")
            ]
            
            for col, value in enumerate(valores):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela_notas.setItem(row, col, item)

    def _on_manifesto_selecionado(self):
        selected = self.tabela_manifestos.selectedItems()
        if selected:
            row = selected[0].row()
            self._manifesto_selecionado_id = int(self.tabela_manifestos.item(row, 0).text())

    def _importar_txt(self):
        arquivo, _ = QFileDialog.getOpenFileName(
            self, 
            "Importar Manifesto", 
            "", 
            "Arquivos TXT (*.txt);;Todos os arquivos (*.*)"
        )
        if not arquivo:
            return
        
        try:
            resultado = notas_service.importar_manifesto(arquivo)
            QMessageBox.information(
                self, 
                "Importação Concluída",
                f"Arquivo: {resultado['arquivo']}\n"
                f"Notas encontradas: {resultado['encontradas']}\n"
                f"Notas salvas: {resultado['salvas']}\n"
                f"Duplicadas: {resultado['duplicadas']}"
            )
            self._carregar_manifestos()
            self._carregar_notas()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar:\n{str(e)}")

    def _exportar_xml(self):
        if not self._manifesto_selecionado_id:
            QMessageBox.warning(self, "Atenção", "Selecione um manifesto na aba 'Manifestos' para exportar.")
            return
        
        arquivo, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Manifesto XML",
            f"manifesto_{self._manifesto_selecionado_id}.xml",
            "XML (*.xml)"
        )
        if not arquivo:
            return
        
        # Garantir extensão .xml
        if not arquivo.lower().endswith('.xml'):
            arquivo += '.xml'
        
        try:
            sucesso = notas_service.exportar_manifesto_xml(self._manifesto_selecionado_id, arquivo)
            if sucesso:
                QMessageBox.information(self, "Sucesso", f"Manifesto exportado para:\n{arquivo}")
            else:
                QMessageBox.warning(self, "Atenção", "Manifesto vazio ou não encontrado.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")

    def _atualizar_resumo(self, chave, valor):
        widget = self.findChild(QLabel, f"resumo_{chave}")
        if widget:
            widget.setText(valor)
