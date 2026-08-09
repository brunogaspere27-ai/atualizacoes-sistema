"""
Login SaaS Premium v2.0 - CW Transportadora
Tela de login inspirada em Linear, Stripe, ClickUp, Vercel, Notion, Framer

Features:
- Split screen com branding
- Fundo #0B0B0B
- Logo CW vermelha
- Glassmorphism
- Animações suaves
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QCheckBox, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont

from telas.theme_saaS import saas_theme
from utils.icons import get_icon, get_pixmap

logger = logging.getLogger(__name__)


class LoginSaaS(QWidget):
    login_sucesso = Signal(dict)

    def __init__(self, auth_service=None, auditoria_service=None, parent=None):
        super().__init__(parent)
        if auth_service is None:
            from services.auth_service import auth_service as _auth
            auth_service = _auth
        if auditoria_service is None:
            try:
                from services.auditoria_service import auditoria_service as _aud
                auditoria_service = _aud
            except Exception:
                pass
        self.auth_service = auth_service
        self.auditoria_service = auditoria_service
        self._usuario_logado = None
        self._setup_ui()

    def _setup_ui(self):
        c = saas_theme.COLORS
        t = saas_theme

        self.setWindowTitle("CW Transportadora — Login")
        self.resize(1200, 750)
        self.setMinimumSize(1000, 600)

        # Background
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {c['bg_primary']};
        }}
        """)

        # Layout principal horizontal
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # ── Painel esquerdo (branding) ──
        self._left = _SaaSBrandingPanel()
        root.addWidget(self._left, 1)

        # ── Painel direito (login form) ──
        self._right = _SaaSLoginPanel()
        root.addWidget(self._right, 1)

        # ── Conexões ──
        self._right.login_requested.connect(self._on_login_clicked)
        self._right.forgot_password_clicked.connect(self._on_forgot_password)

    def _on_login_clicked(self, username: str, password: str):
        from threading import Thread
        self._right.set_loading(True)
        t = Thread(target=self._do_login, args=(username, password), daemon=True)
        t.start()

    def _do_login(self, username: str, password: str):
        try:
            user = self.auth_service.login(username, password)
            if user:
                self._usuario_logado = user
                if self.auditoria_service:
                    try:
                        self.auditoria_service.registrar_acao(
                            "LOGIN", f"Login: {user.get('nome', username)}",
                            usuario_id=user.get("id")
                        )
                    except Exception as e:
                        logger.warning(f"Auditoria login falhou: {e}")
                self.login_sucesso.emit(user)
            else:
                self._right.show_error("Usuário ou senha incorretos.")
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            self._right.show_error(f"Erro: {e}")
        finally:
            self._right.set_loading(False)

    def _on_forgot_password(self):
        self._right.show_error("Contate o administrador do sistema.")


class _SaaSBrandingPanel(QFrame):
    """Painel de branding com logo CW vermelha."""

    def __init__(self, parent=None):
        super().__init__(parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_primary']};
            border-right: 1px solid {c['border_default']};
        }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_4XL, t.SPACING_4XL, t.SPACING_4XL, t.SPACING_4XL)
        layout.setSpacing(t.SPACING_XL)
        self.setLayout(layout)

        # Logo CW
        logo = QLabel("CW")
        logo.setFont(QFont(t.FONT_FAMILY_QT, 64, QFont.Weight.Bold))
        logo.setStyleSheet(f"""
        QLabel {{
            color: {c['cw']};
            background: transparent;
            letter-spacing: -4px;
        }}
        """)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(t.SPACING_3XL)

        # Nome da empresa
        company_lbl = QLabel("CW TRANSPORTADORA")
        company_lbl.setFont(QFont(t.FONT_FAMILY_QT, 24, QFont.Weight.Bold))
        company_lbl.setStyleSheet("color: #FFFFFF; background: transparent;")
        company_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company_lbl)

        # Subtítulo
        subtitle_lbl = QLabel("Sistema de Gestão Logística")
        subtitle_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_LG))
        subtitle_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_lbl)

        layout.addStretch()

        # Features
        features = QVBoxLayout()
        features.setSpacing(t.SPACING_MD)
        features.setContentsMargins(0, 0, 0, 0)

        for icon, text in [
            ("shield", "Segurança Avançada"),
            ("truck", "Gestão de Frota"),
            ("chart", "Analytics Premium"),
        ]:
            row = QHBoxLayout()
            row.setSpacing(t.SPACING_SM)
            row.setAlignment(Qt.AlignmentFlag.AlignLeft)

            ico = QLabel()
            ico.setPixmap(get_pixmap(icon, (20, 20), c['cw']))
            row.addWidget(ico)

            lbl = QLabel(text)
            lbl.setFont(saas_theme.get_font(t.FONT_SIZE_MD))
            lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            row.addWidget(lbl)

            features.addLayout(row)

        layout.addLayout(features)

        layout.addSpacing(t.SPACING_2XL)

        # Footer
        footer_lbl = QLabel("© 2026 CW Transportadora")
        footer_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_SM))
        footer_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer_lbl)


class _SaaSLoginPanel(QFrame):
    """Painel de login com estilo SaaS premium."""

    login_requested = Signal(str, str)
    forgot_password_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_primary']};
        }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        # Card centralizado
        card = QFrame()
        card.setFixedWidth(420)
        card.setStyleSheet(f"""
        QFrame {{
            background-color: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_2XL}px;
        }}
        """)

        # Glow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(t.SPACING_3XL, t.SPACING_3XL, t.SPACING_3XL, t.SPACING_3XL)
        card_layout.setSpacing(t.SPACING_XL)
        card.setLayout(card_layout)

        # Header
        header = QVBoxLayout()
        header.setSpacing(t.SPACING_SM)
        header.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel("Bem-vindo de volta")
        title_lbl.setFont(QFont(t.FONT_FAMILY_QT, 28, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        header.addWidget(title_lbl)

        subtitle_lbl = QLabel("Faça login para acessar o sistema")
        subtitle_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_MD))
        subtitle_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        header.addWidget(subtitle_lbl)

        card_layout.addLayout(header)

        card_layout.addSpacing(t.SPACING_XL)

        # Username input
        username_lbl = QLabel("Usuário")
        username_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_SM, bold=True))
        username_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        card_layout.addWidget(username_lbl)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu usuário")
        self.username_input.setMinimumHeight(48)
        card_layout.addWidget(self.username_input)

        card_layout.addSpacing(t.SPACING_MD)

        # Password input
        password_lbl = QLabel("Senha")
        password_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_SM, bold=True))
        password_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        card_layout.addWidget(password_lbl)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        card_layout.addWidget(self.password_input)

        # Lembrar senha
        remember_row = QHBoxLayout()
        remember_row.setSpacing(t.SPACING_SM)

        self.remember_cb = QCheckBox("Lembrar-me")
        remember_row.addWidget(self.remember_cb)
        remember_row.addStretch()

        forgot_btn = QPushButton("Esqueceu a senha?")
        forgot_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            color: {c['cw']};
            border: none;
            font-size: {t.FONT_SIZE_SM}px;
            font-weight: 500;
        }}
        QPushButton:hover {{ text-decoration: underline; }}
        """)
        forgot_btn.clicked.connect(self.forgot_password_clicked.emit)
        remember_row.addWidget(forgot_btn)

        card_layout.addLayout(remember_row)

        card_layout.addSpacing(t.SPACING_LG)

        # Login button
        self.login_btn = QPushButton("Entrar")
        self.login_btn.setMinimumHeight(52)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_LG, QFont.Weight.Bold))
        self.login_btn.setProperty("class", "primary")
        self.login_btn.clicked.connect(self._on_login)
        card_layout.addWidget(self.login_btn)

        # Error message
        self.error_lbl = QLabel()
        self.error_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_SM))
        self.error_lbl.setStyleSheet(f"""
        QLabel {{
            color: {c['error']};
            background: {c['error_soft']};
            border: 1px solid {c['error']};
            border-radius: {t.RADIUS_MD}px;
            padding: 12px 16px;
        }}
        """)
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setVisible(False)
        card_layout.addWidget(self.error_lbl)

        card_layout.addStretch()

        # Centralizar card
        card_container = QWidget()
        card_container.setStyleSheet("background: transparent;")
        card_layout_center = QVBoxLayout()
        card_layout_center.setContentsMargins(0, 0, 0, 0)
        card_layout_center.addWidget(card, 0, Qt.AlignmentFlag.AlignCenter)
        card_container.setLayout(card_layout_center)

        layout.addWidget(card_container, 1)

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if username and password:
            self.login_requested.emit(username, password)

    def set_loading(self, loading: bool):
        self.login_btn.setEnabled(not loading)
        self.login_btn.setText("Carregando..." if loading else "Entrar")

    def show_error(self, message: str):
        self.error_lbl.setText(message)
        self.error_lbl.setVisible(True)
