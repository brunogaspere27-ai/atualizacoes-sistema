"""
Login Aurora Premium v2.0 - CW Transportadora
Tela de login premium centralizada com design moderno

Design:
- Card centralizado com fundo #161B22
- Fundo da aplicação #0D1117
- Cor principal #D32F2F
- Animações suaves de entrada
- Botão mostrar senha
- Visual moderno estilo Linear/Stripe
"""

import logging
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QCheckBox, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve, QSize, QRectF,
    QParallelAnimationGroup, QSequentialAnimationGroup, QPoint,
)
from PySide6.QtGui import (
    QColor, QPixmap, QIcon, QPainter, QBrush, QPainterPath,
    QLinearGradient, QRadialGradient, QPen, QFont,
)

from telas.theme_aurora import aurora_theme_manager, AccentColor
from utils.branding import load_official_logo_pixmap
from utils.icons import get_icon, get_pixmap

logger = logging.getLogger(__name__)


class LoginAurora(QWidget):
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
        self._animate_entry()

    def _setup_ui(self):
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens

        self.setWindowTitle("CW Transportadora — Login")
        self.resize(1280, 780)
        self.setMinimumSize(1120, 680)

        # Background sólido premium
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {c['bg_primary']};
        }}
        """)

        # Layout principal centralizado
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # Container centralizado
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Card de login premium
        self._login_card = _PremiumLoginCard()
        center_layout.addWidget(self._login_card, 0, Qt.AlignmentFlag.AlignCenter)

        root.addWidget(center_container, 1)

        # ── Conexões ──
        self._login_card.login_requested.connect(self._on_login_clicked)
        self._login_card.forgot_password_clicked.connect(self._on_forgot_password)

    def _animate_entry(self):
        """Animação suave de entrada do card."""
        self._login_card.setOpacity(0)
        
        opacity_anim = QPropertyAnimation(self._login_card, b"windowOpacity")
        opacity_anim.setDuration(600)
        opacity_anim.setStartValue(0.0)
        opacity_anim.setEndValue(1.0)
        opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        opacity_anim.start()

    def _on_login_clicked(self, username: str, password: str, remember: bool):
        from threading import Thread
        self._login_card.set_loading(True)
        t = Thread(target=self._do_login, args=(username, password, remember), daemon=True)
        t.start()

    def _do_login(self, username: str, password: str, remember: bool):
        try:
            user = self.auth_service.login(username, password)
            if user:
                self._usuario_logado = user
                if remember:
                    self.auth_service.salvar_sessao(user)
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
                self._login_card.show_error("Usuário ou senha incorretos.")
        except Exception as e:
            logger.error(f"Erro no login: {e}")
            self._login_card.show_error(f"Erro: {e}")
        finally:
            self._login_card.set_loading(False)

    def _on_forgot_password(self):
        self._login_card.show_error("Contate o administrador do sistema.")


class _PremiumLoginCard(QFrame):
    """Card de login premium centralizado com design moderno."""

    login_requested = Signal(str, str, bool)
    forgot_password_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        c = aurora_theme_manager.colors
        t = aurora_theme_manager.tokens
        self._password_visible = False

        # Card moderno com sombra suave
        self.setFixedSize(520, 620)
        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_secondary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_2XL}px;
        }}
        """)

        # Adicionar sombra suave
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(0, 0, 0, 0.4))
        shadow.setOffset(0, 12)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_4XL, t.SPACING_4XL, t.SPACING_4XL, t.SPACING_4XL)
        layout.setSpacing(t.SPACING_LG)
        self.setLayout(layout)

        # Logo da CW (centralizado)
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_lbl = QLabel()
        logo_pixmap = load_official_logo_pixmap(160, 72)
        if logo_pixmap is not None:
            logo_lbl.setPixmap(logo_pixmap)
        logo_lbl.setStyleSheet("background: transparent;")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_lbl)

        layout.addWidget(logo_container, 0, Qt.AlignmentFlag.AlignCenter)

        # Nome da empresa (centralizado, melhor contraste)
        company_lbl = QLabel("CW Transportadora")
        company_lbl.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_3XL, QFont.Weight.Bold))
        company_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        company_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        # Subtítulo (melhor contraste e espaçamento)
        subtitle_lbl = QLabel("Sistema Inteligente de Gestão Logística")
        subtitle_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_MD))
        subtitle_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(t.SPACING_2XL)

        # Campo Usuário
        username_lbl = QLabel("Usuário")
        username_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        username_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        layout.addWidget(username_lbl)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu usuário")
        self.username_input.setFixedHeight(52)
        self.username_input.setStyleSheet(f"""
        QLineEdit {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 14px 18px;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:hover {{
            border-color: {c['border_strong']};
            background-color: {c['bg_tertiary']};
        }}
        QLineEdit:focus {{
            border: 2px solid {c['aurora']};
            background-color: {c['bg_tertiary']};
        }}
        """)
        layout.addWidget(self.username_input)

        layout.addSpacing(t.SPACING_LG)

        # Campo Senha com botão mostrar
        password_lbl = QLabel("Senha")
        password_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        password_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        layout.addWidget(password_lbl)

        password_container = QWidget()
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(t.SPACING_SM)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(52)
        self.password_input.setStyleSheet(f"""
        QLineEdit {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 14px 18px;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:hover {{
            border-color: {c['border_strong']};
            background-color: {c['bg_tertiary']};
        }}
        QLineEdit:focus {{
            border: 2px solid {c['aurora']};
            background-color: {c['bg_tertiary']};
        }}
        """)
        password_layout.addWidget(self.password_input, 1)

        # Botão mostrar senha
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setFixedSize(52, 52)
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.setIcon(get_icon("eye", QSize(22, 22), c["text_secondary"]))
        self.toggle_password_btn.setIconSize(QSize(22, 22))
        self.toggle_password_btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: {t.RADIUS_MD}px;
            padding-right: 8px;
        }}
        QPushButton:hover {{
            background: {c['bg_tertiary']};
        }}
        """)
        self.toggle_password_btn.clicked.connect(self._toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_btn)

        layout.addWidget(password_container)

        layout.addSpacing(t.SPACING_MD)

        # Checkbox "Lembrar de mim"
        self.remember_checkbox = QCheckBox("Lembrar de mim")
        self.remember_checkbox.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM))
        self.remember_checkbox.setStyleSheet(f"""
        QCheckBox {{
            color: {c['text_secondary']};
            spacing: 8px;
            background-color: transparent;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {c['border_default']};
            border-radius: 4px;
            background-color: {c['bg_primary']};
        }}
        QCheckBox::indicator:hover {{
            border-color: {c['aurora']};
        }}
        QCheckBox::indicator:checked {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            border-color: {c['aurora']};
        }}
        """)
        layout.addWidget(self.remember_checkbox)

        layout.addSpacing(t.SPACING_LG)

        # Botão Entrar moderno
        self.login_btn = QPushButton("Entrar")
        self.login_btn.setFixedHeight(56)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_LG, QFont.Weight.Bold))
        self.login_btn.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            color: #FFFFFF;
            border: none;
            border-radius: {t.RADIUS_2XL}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_hover']}, stop:1 {c['aurora_end']});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_active']}, stop:1 {c['aurora']});
        }}
        QPushButton:disabled {{
            background: {c['bg_tertiary']};
            color: {c['text_disabled']};
        }}
        """)
        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn)

        # Error message
        self.error_lbl = QLabel()
        self.error_lbl.setFont(aurora_theme_manager.get_font(t.FONT_SIZE_SM))
        self.error_lbl.setStyleSheet(f"""
        QLabel {{
            color: {c['error']};
            background: {c['error_soft']};
            border: 1px solid {c['error']};
            border-radius: {t.RADIUS_MD}px;
            padding: 10px 14px;
        }}
        """)
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setVisible(False)
        layout.addWidget(self.error_lbl)

        layout.addStretch()

    def _toggle_password_visibility(self):
        """Alterna visibilidade da senha."""
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setIcon(get_icon("eye-off", QSize(20, 20), aurora_theme_manager.colors["text_secondary"]))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setIcon(get_icon("eye", QSize(20, 20), aurora_theme_manager.colors["text_secondary"]))

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        remember = self.remember_checkbox.isChecked()
        if username and password:
            self.login_requested.emit(username, password, remember)

    def set_loading(self, loading: bool):
        self.login_btn.setEnabled(not loading)
        self.login_btn.setText("Carregando..." if loading else "Entrar")

    def show_error(self, message: str):
        self.error_lbl.setText(message)
        self.error_lbl.setVisible(True)

    def setOpacity(self, value: float):
        """Define opacidade para animação."""
        self.setWindowOpacity(value)
