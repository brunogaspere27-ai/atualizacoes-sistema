"""
Tela Configurações - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QCheckBox, QFrame, QGroupBox,
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
QCheckBox {
    color: #E6EDF3;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #30363D;
    background: #21262D;
}
QCheckBox::indicator:checked {
    background: #D32F2F;
    border-color: #D32F2F;
}
"""


class TelaConfiguracoes(QWidget):
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
        titulo = QLabel("⚙️ Configurações")
        titulo.setObjectName("titulo")
        header.addWidget(titulo)
        header.addStretch()
        layout.addLayout(header)

        # Empresa
        grp_empresa = QGroupBox("🏢 Dados da Empresa")
        emp_layout = QVBoxLayout(grp_empresa)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Razão Social:"))
        self.txt_razao = QLineEdit()
        row1.addWidget(self.txt_razao)
        emp_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("CNPJ:"))
        self.txt_cnpj = QLineEdit()
        row2.addWidget(self.txt_cnpj)
        emp_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Telefone:"))
        self.txt_tel = QLineEdit()
        row3.addWidget(self.txt_tel)
        emp_layout.addLayout(row3)
        layout.addWidget(grp_empresa)

        # Sistema
        grp_sistema = QGroupBox("💻 Configurações do Sistema")
        sys_layout = QVBoxLayout(grp_sistema)

        self.chk_backup = QCheckBox("Backup automático diário")
        self.chk_backup.setChecked(True)
        sys_layout.addWidget(self.chk_backup)

        self.chk_notif = QCheckBox("Notificações de atualização")
        self.chk_notif.setChecked(True)
        sys_layout.addWidget(self.chk_notif)

        self.chk_sync = QCheckBox("Sincronização automática")
        sys_layout.addWidget(self.chk_sync)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Tema:"))
        self.combo_tema = QComboBox()
        self.combo_tema.addItems(["Aurora Dark", "Aurora Light", "Padrão"])
        row4.addWidget(self.combo_tema)
        sys_layout.addLayout(row4)
        layout.addWidget(grp_sistema)

        # Canal de atualização
        grp_update = QGroupBox("⬆️ Atualizações")
        up_layout = QVBoxLayout(grp_update)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Canal:"))
        self.combo_canal = QComboBox()
        self.combo_canal.addItems(["Estável", "Beta", "Desenvolvimento"])
        row5.addWidget(self.combo_canal)
        up_layout.addLayout(row5)
        layout.addWidget(grp_update)

        # Botões
        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secundario")
        botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("💾 Salvar Configurações")
        btn_salvar.setObjectName("primario")
        btn_salvar.clicked.connect(self._salvar)
        botoes.addWidget(btn_salvar)
        layout.addLayout(botoes)
        layout.addStretch()

    def _salvar(self):
        QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
