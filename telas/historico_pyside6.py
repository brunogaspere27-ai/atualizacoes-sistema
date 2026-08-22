"""
Tela Histórico de Viagens - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QHeaderView, QAbstractItemView, QFrame, QDateEdit,
    QDialog, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, QDate

from utils.database.viagens import listar_viagens, listar_notas_da_viagem, apagar_viagem

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


class DialogoNotasViagem(QDialog):
    def __init__(self, viagem_id, parent=None):
        super().__init__(parent)
        self.viagem_id = viagem_id
        self.setWindowTitle(f"Notas da Viagem #{viagem_id}")
        self.setMinimumSize(900, 500)
        self.setStyleSheet(ESTILO)
        self._setup_ui()
        self._carregar_notas()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        titulo = QLabel(f"📋 Notas da Viagem #{self.viagem_id}")
        titulo.setObjectName("titulo")
        layout.addWidget(titulo)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "CT-e/Chave", "Remetente", "Destinatário", "Origem", "Destino", "Frete", "Peso", "Status"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        btn_ok = QPushButton("Fechar")
        btn_ok.setObjectName("secundario")
        btn_ok.clicked.connect(self.accept)
        layout.addWidget(btn_ok)

    def _carregar_notas(self):
        self.tabela.setRowCount(0)
        notas = listar_notas_da_viagem(self.viagem_id)
        
        for nota in notas:
            # (id, numero_cte, remetente, destinatario, origem, destino, valor_frete, peso, status)
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            valores = [
                str(nota[0]),
                str(nota[1] or "-"),
                str(nota[2] or "-"),
                str(nota[3] or "-"),
                str(nota[4] or "-"),
                str(nota[5] or "-"),
                f"R$ {float(nota[6] or 0):,.2f}",
                f"{float(nota[7] or 0):,.2f} kg",
                str(nota[8] or "-")
            ]
            
            for col, value in enumerate(valores):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, col, item)


class TelaHistorico(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(ESTILO)
        self._setup_ui()
        self._carregar_dados()

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
        layout.addLayout(header)

        # Filtros
        filtros = QHBoxLayout()
        filtros.setSpacing(12)

        self.filtro_busca = QLineEdit()
        self.filtro_busca.setPlaceholderText("🔍 Buscar viagem...")
        filtros.addWidget(self.filtro_busca)

        self.filtro_status = QComboBox()
        self.filtro_status.addItems(["Todos os status", "Em viagem", "Finalizada", "Cancelada"])
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
        btn_filtrar.clicked.connect(self._carregar_dados)
        filtros.addWidget(btn_filtrar)
        layout.addLayout(filtros)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Data Saída", "Caminhão", "Motorista", "Notas", "KM", "Status", "Ações"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setAlternatingRowColors(True)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setColumnWidth(0, 60)
        self.tabela.setColumnWidth(4, 80)
        self.tabela.setColumnWidth(7, 120)
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
            val.setObjectName(f"resumo_{label_text.lower().replace(' ', '_')}")
            val.setStyleSheet("color: #E6EDF3; font-size: 20px; font-weight: 700;")
            cl.addWidget(val)
            resumo.addWidget(card)
        layout.addLayout(resumo)
        layout.addStretch()

    def _carregar_dados(self):
        self.tabela.setRowCount(0)
        viagens = listar_viagens()
        
        total_viagens = 0
        total_km = 0
        
        for v in viagens:
            # (id, data_saida, modelo, placa, motorista, status, peso_total, frete_total, total_notas)
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            
            valores = [
                str(v[0]),
                str(v[1] or "-"),
                f"{v[2] or '-'} ({v[3] or '-'})",
                str(v[4] or "-"),
                str(v[8] or 0),  # total_notas
                "-",  # KM não tem na query atual
                str(v[5] or "-"),
            ]
            
            for col, value in enumerate(valores):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.tabela.setItem(row, col, item)
            
            # Botão de ações
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(6)
            
            btn_ver = QPushButton("👁️ Ver")
            btn_ver.setObjectName("secundario")
            btn_ver.setStyleSheet("""
                QPushButton {
                    background-color: #21262D;
                    color: #58A6FF;
                    border: 1px solid #30363D;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-size: 12px;
                }
                QPushButton:hover { background-color: #30363D; }
            """)
            btn_ver.clicked.connect(lambda checked, vid=v[0]: self._ver_notas(vid))
            
            btn_apagar = QPushButton("�️")
            btn_apagar.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #F85149;
                    border: none;
                    padding: 4px 8px;
                    font-size: 12px;
                }
            """)
            btn_apagar.clicked.connect(lambda checked, vid=v[0]: self._apagar_viagem(vid))
            
            btn_layout.addWidget(btn_ver)
            btn_layout.addWidget(btn_apagar)
            btn_layout.addStretch()
            
            self.tabela.setCellWidget(row, 7, btn_container)
            
            total_viagens += 1
        
        # Atualizar resumo
        self._atualizar_resumo("total_de_viagens", str(total_viagens))
        self._atualizar_resumo("km_percorridos", "0")
        self._atualizar_resumo("media_por_viagem", "0 km")

    def _ver_notas(self, viagem_id):
        dialogo = DialogoNotasViagem(viagem_id, self)
        dialogo.exec()

    def _apagar_viagem(self, viagem_id):
        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"Deseja apagar a viagem #{viagem_id}?\nAs notas voltarão a ficar disponíveis.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                apagar_viagem(viagem_id)
                self._carregar_dados()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao apagar viagem:\n{str(e)}")

    def _atualizar_resumo(self, chave, valor):
        widget = self.findChild(QLabel, f"resumo_{chave}")
        if widget:
            widget.setText(valor)
