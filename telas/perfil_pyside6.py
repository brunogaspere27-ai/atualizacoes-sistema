"""
Tela Perfil do Usuário - Padrão CW Moderno
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt

ESTILO = """
QWidget {
    background-color: #0D1117;
    color: #E6EDF3;
    font-family: 'Segoe UI', sans-serif;
}
QLabel#titulo { font-size: 22px; font-weight: 700; }
QLabel#nome_usuario {
    font-size: 20px;
    font-weight: 700;
    color: #E6EDF3;
}
QLabel#email_usuario {
    font-size: 13px;
    color: #9CA3AF;
}
QLineEdit {
    background-color: #21262D;
    color: #E6EDF3;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
}
QLineEdit:focus { border-color: #D32F2F; }
QLineEdit:disabled {
    background-color: #161B22;
    color: #6E7681;
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

AVATAR_STYLE = """
QLabel {
    background-color: #D32F2F;
    color: #FFFFFF;
    border-radius: 40px;
    font-size: 28px;
    font-weight: 700;
}
"""


class TelaPerfil(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(ESTILO)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Card principal
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 16px;
                padding: 32px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)

        # Avatar e nome
        top = QHBoxLayout()
        top.setSpacing(20)

        avatar = QLabel("BG")
        avatar.setFixedSize(80, 80)
        avatar.setStyleSheet(AVATAR_STYLE)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(avatar)

        info = QVBoxLayout()
        info.setSpacing(4)

        nome = QLabel("Bruno Gasper")
        nome.setObjectName("nome_usuario")
        info.addWidget(nome)

        email = QLabel("bruno@cwtransportadora.com")
        email.setObjectName("email_usuario")
        info.addWidget(email)

        perfil = QLabel("👑 Administrador")
        perfil.setStyleSheet("color: #D32F2F; font-size: 13px; font-weight: 600;")
        info.addWidget(perfil)

        top.addLayout(info)
        top.addStretch()
        card_layout.addLayout(top)

        # Dados pessoais
        grp_dados = QGroupBox("👤 Dados Pessoais")
        dados_layout = QVBoxLayout(grp_dados)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Nome Completo:"))
        self.txt_nome = QLineEdit("Bruno Gasper")
        row1.addWidget(self.txt_nome)
        dados_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Email:"))
        self.txt_email = QLineEdit("bruno@cwtransportadora.com")
        row2.addWidget(self.txt_email)
        dados_layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Usuário:"))
        self.txt_user = QLineEdit("bruno")
        self.txt_user.setEnabled(False)
        row3.addWidget(self.txt_user)
        dados_layout.addLayout(row3)
        card_layout.addWidget(grp_dados)

        # Segurança
        grp_seg = QGroupBox("🔒 Segurança")
        seg_layout = QVBoxLayout(grp_seg)

        row4 = QHBoxLayout()
        row4.addWidget(QLabel("Senha Atual:"))
        self.txt_senha_atual = QLineEdit()
        self.txt_senha_atual.setEchoMode(QLineEdit.EchoMode.Password)
        row4.addWidget(self.txt_senha_atual)
        seg_layout.addLayout(row4)

        row5 = QHBoxLayout()
        row5.addWidget(QLabel("Nova Senha:"))
        self.txt_nova_senha = QLineEdit()
        self.txt_nova_senha.setEchoMode(QLineEdit.EchoMode.Password)
        row5.addWidget(self.txt_nova_senha)
        seg_layout.addLayout(row5)

        row6 = QHBoxLayout()
        row6.addWidget(QLabel("Confirmar Senha:"))
        self.txt_conf_senha = QLineEdit()
        self.txt_conf_senha.setEchoMode(QLineEdit.EchoMode.Password)
        row6.addWidget(self.txt_conf_senha)
        seg_layout.addLayout(row6)
        card_layout.addWidget(grp_seg)

        # Botões
        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("secundario")
        botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("💾 Salvar Alterações")
        btn_salvar.setObjectName("primario")
        btn_salvar.clicked.connect(self._salvar)
        botoes.addWidget(btn_salvar)
        card_layout.addLayout(botoes)

        layout.addWidget(card)
        layout.addStretch()

    def _salvar(self):
        QMessageBox.information(self, "Sucesso", "Perfil atualizado com sucesso!")
