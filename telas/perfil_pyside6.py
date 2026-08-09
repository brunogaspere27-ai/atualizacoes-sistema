"""
Tela de Perfil CW Transportadora - PySide6

Gestão de perfil de usuário:
- Visualização e alteração de foto (avatar 96px)
- Alteração de nome completo
- Alteração de senha
- Informações da conta
"""

from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QFileDialog, QMessageBox, QScrollArea,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter, QPainterPath

from ui.theme.cw_theme import cw_theme
from ui.components import CWButton, ButtonVariant, ButtonSize, CWCard
from utils.icons import get_icon, get_pixmap
from services.perfil_service import perfil_service
from services.auth_service import auth_service
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def _fazer_pixmap_circular(caminho: str, tamanho: int) -> Optional[QPixmap]:
    """Recorta uma imagem em círculo."""
    if not caminho:
        return None
    src = QPixmap(caminho)
    if src.isNull():
        return None
    src = src.scaled(
        tamanho, tamanho,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    dst = QPixmap(tamanho, tamanho)
    dst.fill(Qt.GlobalColor.transparent)
    painter = QPainter(dst)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    path = QPainterPath()
    path.addEllipse(0, 0, tamanho, tamanho)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, src)
    painter.end()
    return dst


class TelaPerfil(QWidget):
    """Tela de perfil de usuário."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._usuario = auth_service.usuario_atual or {}
        self._usuario_id = self._usuario.get("id")
        self._setup_ui()
        self._carregar_dados()

    def _setup_ui(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{
            background: transparent; width: 8px; margin: 4px 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {colors['border_default']}; border-radius: 4px; min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {colors['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none; height: 0px;
        }}
        """)

        content = QWidget()
        content.setStyleSheet(f"background: {colors['bg_primary']};")
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL, tokens.SPACING_2XL)
        self._layout.setSpacing(tokens.SPACING_XL)
        content.setLayout(self._layout)
        scroll.setWidget(content)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # === Seção 1: Avatar + Info básica ===
        self._build_avatar_section()

        # === Seção 2: Alterar nome ===
        self._build_nome_section()

        # === Seção 3: Alterar senha ===
        self._build_senha_section()

        # === Seção 4: Informações da conta ===
        self._build_info_section()

    def _build_avatar_section(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        card = ModernCard("Foto de Perfil", icon_name="user_circle", padding=tokens.SPACING_XL)
        layout = card.layout()

        # Avatar + botões
        row = QHBoxLayout()
        row.setSpacing(tokens.SPACING_XL)

        # Avatar circular (96px)
        self._avatar_label = QLabel()
        self._avatar_label.setFixedSize(96, 96)
        self._avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avatar_label.setStyleSheet(f"""
        QLabel {{
            background: {colors['bg_tertiary']};
            border: 2px solid {colors['border_default']};
            border-radius: 48px;
        }}
        """)
        row.addWidget(self._avatar_label)

        # Botões
        btn_col = QVBoxLayout()
        btn_col.setSpacing(tokens.SPACING_SM)

        btn_trocar = ModernButton("Trocar Foto", ButtonStyle.PRIMARY, "camera", parent=self)
        btn_trocar.clicked.connect(self._trocar_foto)
        btn_col.addWidget(btn_trocar)

        btn_remover = ModernButton("Remover Foto", ButtonStyle.GHOST, "trash", parent=self)
        btn_remover.clicked.connect(self._remover_foto)
        btn_col.addWidget(btn_remover)

        btn_col.addStretch()
        row.addLayout(btn_col)
        row.addStretch()

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        container.setLayout(row)
        layout.addWidget(container)

        self._layout.addWidget(card)

    def _build_nome_section(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        card = ModernCard("Nome Completo", icon_name="user_circle", padding=tokens.SPACING_XL)
        layout = card.layout()

        # Label
        lbl = QLabel("Seu nome completo é usado em todo o sistema")
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        lbl.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        layout.addWidget(lbl)

        # Input
        self._entry_nome = QLineEdit()
        self._entry_nome.setPlaceholderText("Digite seu nome completo")
        self._entry_nome.setMinimumHeight(44)
        self._entry_nome.setFont(theme_manager.get_font(tokens.FONT_SIZE_LG))
        self._entry_nome.setStyleSheet(f"""
        QLineEdit {{
            background: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_default']};
            border-radius: {tokens.RADIUS_MD}px;
            padding: 10px 16px;
        }}
        QLineEdit:hover {{ border-color: {colors['border_strong']}; }}
        QLineEdit:focus {{ border: 1px solid {colors['brand']}; background: {colors['bg_secondary']}; }}
        """)
        layout.addWidget(self._entry_nome)

        # Botão salvar
        btn_salvar_nome = ModernButton("Salvar Alterações", ButtonStyle.PRIMARY, parent=self)
        btn_salvar_nome.clicked.connect(self._salvar_nome)
        layout.addWidget(btn_salvar_nome)

        self._layout.addWidget(card)

    def _build_senha_section(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        card = ModernCard("Alterar Senha", icon_name="lock", padding=tokens.SPACING_XL)
        layout = card.layout()

        lbl = QLabel("Use uma senha forte com pelo menos 8 caracteres")
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM))
        lbl.setStyleSheet(f"color: {colors['text_tertiary']}; background: transparent;")
        layout.addWidget(lbl)

        # Senha atual
        lbl_atual = QLabel("Senha Atual")
        lbl_atual.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl_atual.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        layout.addWidget(lbl_atual)

        self._entry_senha_atual = QLineEdit()
        self._entry_senha_atual.setEchoMode(QLineEdit.EchoMode.Password)
        self._entry_senha_atual.setPlaceholderText("Digite sua senha atual")
        self._entry_senha_atual.setMinimumHeight(44)
        self._entry_senha_atual.setStyleSheet(f"""
        QLineEdit {{
            background: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_default']};
            border-radius: {tokens.RADIUS_MD}px;
            padding: 10px 16px;
        }}
        QLineEdit:hover {{ border-color: {colors['border_strong']}; }}
        QLineEdit:focus {{ border: 1px solid {colors['brand']}; background: {colors['bg_secondary']}; }}
        """)
        layout.addWidget(self._entry_senha_atual)

        # Nova senha
        lbl_nova = QLabel("Nova Senha")
        lbl_nova.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl_nova.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        layout.addWidget(lbl_nova)

        self._entry_senha_nova = QLineEdit()
        self._entry_senha_nova.setEchoMode(QLineEdit.EchoMode.Password)
        self._entry_senha_nova.setPlaceholderText("Digite a nova senha")
        self._entry_senha_nova.setMinimumHeight(44)
        self._entry_senha_nova.setStyleSheet(f"""
        QLineEdit {{
            background: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_default']};
            border-radius: {tokens.RADIUS_MD}px;
            padding: 10px 16px;
        }}
        QLineEdit:hover {{ border-color: {colors['border_strong']}; }}
        QLineEdit:focus {{ border: 1px solid {colors['brand']}; background: {colors['bg_secondary']}; }}
        """)
        layout.addWidget(self._entry_senha_nova)

        # Confirmar senha
        lbl_conf = QLabel("Confirmar Nova Senha")
        lbl_conf.setFont(theme_manager.get_font(tokens.FONT_SIZE_SM, bold=True))
        lbl_conf.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        layout.addWidget(lbl_conf)

        self._entry_senha_conf = QLineEdit()
        self._entry_senha_conf.setEchoMode(QLineEdit.EchoMode.Password)
        self._entry_senha_conf.setPlaceholderText("Confirme a nova senha")
        self._entry_senha_conf.setMinimumHeight(44)
        self._entry_senha_conf.setStyleSheet(f"""
        QLineEdit {{
            background: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_default']};
            border-radius: {tokens.RADIUS_MD}px;
            padding: 10px 16px;
        }}
        QLineEdit:hover {{ border-color: {colors['border_strong']}; }}
        QLineEdit:focus {{ border: 1px solid {colors['brand']}; background: {colors['bg_secondary']}; }}
        """)
        layout.addWidget(self._entry_senha_conf)

        # Botão alterar senha
        btn_alterar_senha = ModernButton("Alterar Senha", ButtonStyle.PRIMARY, parent=self)
        btn_alterar_senha.clicked.connect(self._alterar_senha)
        layout.addWidget(btn_alterar_senha)

        self._layout.addWidget(card)

    def _build_info_section(self):
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        card = ModernCard("Informações da Conta", icon_name="info", padding=tokens.SPACING_XL)
        layout = card.layout()

        # Usuário
        self._info_usuario = self._create_info_row("Usuário", "—")
        layout.addWidget(self._info_usuario)

        # Nível de acesso
        self._info_nivel = self._create_info_row("Nível de Acesso", "—")
        layout.addWidget(self._info_nivel)

        # Membro desde
        self._info_criado = self._create_info_row("Membro Desde", "—")
        layout.addWidget(self._info_criado)

        self._layout.addWidget(card)
        self._layout.addStretch()

    def _create_info_row(self, label: str, value: str) -> QWidget:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        row = QWidget()
        row.setStyleSheet("background: transparent;")
        hl = QHBoxLayout()
        hl.setContentsMargins(0, tokens.SPACING_SM, 0, tokens.SPACING_SM)
        row.setLayout(hl)

        lbl = QLabel(label)
        lbl.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD))
        lbl.setStyleSheet(f"color: {colors['text_secondary']}; background: transparent;")
        lbl.setFixedWidth(150)
        hl.addWidget(lbl)

        val = QLabel(value)
        val.setFont(theme_manager.get_font(tokens.FONT_SIZE_MD, bold=True))
        val.setStyleSheet(f"color: {colors['text_primary']}; background: transparent;")
        hl.addWidget(val)
        hl.addStretch()

        self._info_widgets = getattr(self, '_info_widgets', {})
        self._info_widgets[label] = val

        return row

    def _carregar_dados(self):
        """Carrega dados do usuário."""
        if not self._usuario_id:
            return

        info = perfil_service.get_user_info(self._usuario_id)
        if not info:
            return

        # Avatar
        avatar_path = perfil_service.get_avatar_path(self._usuario_id)
        if avatar_path:
            pix = _fazer_pixmap_circular(avatar_path, 96)
            if pix:
                self._avatar_label.setPixmap(pix)
            else:
                self._set_avatar_initials(info["nome_completo"])
        else:
            self._set_avatar_initials(info["nome_completo"])

        # Nome
        self._entry_nome.setText(info["nome_completo"] or "")

        # Info
        if hasattr(self, '_info_widgets'):
            self._info_widgets["Usuário"].setText(info["usuario"] or "—")
            nivel_map = {"mestre": "Mestre", "admin": "Administrador", "operador": "Operador"}
            self._info_widgets["Nível de Acesso"].setText(nivel_map.get(info["nivel"], info["nivel"] or "—"))
            criado = info["criado_em"] or "—"
            if criado != "—" and "T" in criado:
                criado = criado.split("T")[0]
            self._info_widgets["Membro Desde"].setText(criado)

    def _set_avatar_initials(self, nome: str):
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        initials = perfil_service.get_initials(nome)
        color = perfil_service.get_avatar_color(nome)

        self._avatar_label.setText(initials)
        self._avatar_label.setFont(theme_manager.get_font(32, bold=True))
        self._avatar_label.setStyleSheet(f"""
        QLabel {{
            background: {color};
            color: #FFF;
            border: 2px solid {colors['border_default']};
            border-radius: 48px;
        }}
        """)

    def _trocar_foto(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Foto",
            "",
            "Imagens (*.jpg *.jpeg *.png *.bmp)",
        )
        if not file_path or not self._usuario_id:
            return

        if perfil_service.save_avatar(self._usuario_id, file_path):
            # Recarregar avatar
            avatar_path = perfil_service.get_avatar_path(self._usuario_id)
            if avatar_path:
                pix = _fazer_pixmap_circular(avatar_path, 96)
                if pix:
                    self._avatar_label.setPixmap(pix)
            QMessageBox.information(self, "Sucesso", "Foto atualizada com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível salvar a foto.")

    def _remover_foto(self):
        if not self._usuario_id:
            return

        reply = QMessageBox.question(
            self,
            "Confirmar",
            "Deseja realmente remover sua foto de perfil?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        if perfil_service.remove_avatar(self._usuario_id):
            info = perfil_service.get_user_info(self._usuario_id)
            if info:
                self._set_avatar_initials(info["nome_completo"])
            QMessageBox.information(self, "Sucesso", "Foto removida com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível remover a foto.")

    def _salvar_nome(self):
        novo_nome = self._entry_nome.text().strip()
        if not novo_nome or not self._usuario_id:
            return

        if perfil_service.update_nome(self._usuario_id, novo_nome):
            # Atualizar auth_service
            auth_service.usuario_atual["nome_completo"] = novo_nome
            QMessageBox.information(self, "Sucesso", "Nome atualizado com sucesso!")
        else:
            QMessageBox.critical(self, "Erro", "Não foi possível atualizar o nome.")

    def _alterar_senha(self):
        senha_atual = self._entry_senha_atual.text()
        senha_nova = self._entry_senha_nova.text()
        senha_conf = self._entry_senha_conf.text()

        if not senha_atual or not senha_nova or not senha_conf:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos de senha.")
            return

        if senha_nova != senha_conf:
            QMessageBox.warning(self, "Atenção", "As senhas não coincidem.")
            return

        if len(senha_nova) < 8:
            QMessageBox.warning(self, "Atenção", "A nova senha deve ter pelo menos 8 caracteres.")
            return

        try:
            sucesso = auth_service.alterar_senha(self._usuario_id, senha_atual, senha_nova)
            if sucesso:
                QMessageBox.information(self, "Sucesso", "Senha alterada com sucesso!")
                self._entry_senha_atual.clear()
                self._entry_senha_nova.clear()
                self._entry_senha_conf.clear()
            else:
                QMessageBox.critical(self, "Erro", "Senha atual incorreta.")
        except Exception as e:
            logger.error(f"Erro ao alterar senha: {e}")
            QMessageBox.critical(self, "Erro", f"Não foi possível alterar a senha:\n{e}")
