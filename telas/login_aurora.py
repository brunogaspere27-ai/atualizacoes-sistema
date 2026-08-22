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

from telas.theme_aurora import aurora_cw_theme
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
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing

        # Configurar size policy para expandir e preencher toda a janela
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        # Background preto fosco corporativo
        self.setStyleSheet(f"""
        QWidget {{
            background-color: #0B0B0D;
        }}
        """)

        # Layout principal centralizado
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # Card de login premium - centralizado diretamente no layout
        self._login_card = _PremiumLoginCard()
        root.addStretch(1)
        root.addWidget(self._login_card, 0, Qt.AlignmentFlag.AlignCenter)
        root.addStretch(1)

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
    """Card de login premium corporativo."""

    login_requested = Signal(str, str, bool)
    forgot_password_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        self._password_visible = False

        # Card flutuante com glassmorphism moderno
        self.setStyleSheet(f"""
        QFrame {{
            background: {c['bg_glass']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_2XL}px;
        }}
        QFrame:hover {{
            border-color: {c['border_default']};
        }}
        QLabel {{
            border: none;
            background: transparent;
        }}
        """)

        # Sombra suave premium para efeito de flutuação
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 12)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(32)
        self.setLayout(layout)

        # Logo centralizada - sem tamanho fixo para evitar clipping
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_lbl = QLabel()
        logo_pixmap = load_official_logo_pixmap(180, 81)
        if logo_pixmap is not None:
            logo_lbl.setPixmap(logo_pixmap)
            logo_lbl.setScaledContents(True)
        logo_lbl.setStyleSheet("background: transparent;")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_lbl)

        layout.addWidget(logo_container, 0, Qt.AlignmentFlag.AlignCenter)

        # Nome da empresa
        company_lbl = QLabel("CW TRANSPORTADORA")
        company_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_2XL, bold=True))
        company_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent; letter-spacing: 2px;")
        company_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(company_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        # Subtítulo
        subtitle_lbl = QLabel("Sistema de Gestão Logística")
        subtitle_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_MD))
        subtitle_lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; letter-spacing: 1px;")
        subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(t.SPACING_XL)

        # Campo Usuário
        username_lbl = QLabel("Usuário")
        username_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        username_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        username_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(username_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(t.SPACING_SM)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu usuário")
        self.username_input.setMinimumWidth(380)
        self.username_input.setMinimumHeight(48)
        self.username_input.setMaximumWidth(500)
        self.username_input.setStyleSheet(f"""
        QLineEdit {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 14px 18px;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:hover {{
            background-color: {c['bg_overlay']};
            border-color: {c['border_strong']};
        }}
        QLineEdit:focus {{
            background-color: {c['bg_surface']};
            border: 2px solid {c['aurora']};
        }}
        """)
        layout.addWidget(self.username_input, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(t.SPACING_LG)

        # Campo Senha
        password_lbl = QLabel("Senha")
        password_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM, bold=True))
        password_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        password_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(password_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(t.SPACING_SM)

        password_input_row = QHBoxLayout()
        password_input_row.setContentsMargins(0, 0, 0, 0)
        password_input_row.setSpacing(t.SPACING_SM)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Digite sua senha")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(48)
        self.password_input.setMaximumWidth(500)
        self.password_input.setStyleSheet(f"""
        QLineEdit {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 14px 18px;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:hover {{
            background-color: {c['bg_overlay']};
            border-color: {c['border_strong']};
        }}
        QLineEdit:focus {{
            background-color: {c['bg_surface']};
            border: 2px solid {c['aurora']};
        }}
        """)
        password_input_row.addWidget(self.password_input, 1)

        # Botão mostrar senha minimal
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setFixedSize(48, 48)
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.setIcon(get_icon("eye", QSize(20, 20), "#9A9A9A"))
        self.toggle_password_btn.setIconSize(QSize(20, 20))
        self.toggle_password_btn.setStyleSheet("""
        QPushButton {
            background: #1D1D22;
            border: none;
            border-radius: 12px;
        }
        QPushButton:hover {
            background: #222228;
        }
        """)
        self.toggle_password_btn.clicked.connect(self._toggle_password_visibility)
        password_input_row.addWidget(self.toggle_password_btn)

        # Wrapper widget para o password_input_row
        password_wrapper = QWidget()
        password_wrapper.setLayout(password_input_row)
        password_wrapper.setMinimumWidth(380)
        password_wrapper.setMaximumWidth(500)

        layout.addWidget(password_wrapper, 0, Qt.AlignmentFlag.AlignCenter)

        layout.addSpacing(28)

        # Botão Entrar
        self.login_btn = QPushButton("ENTRAR")
        self.login_btn.setMinimumWidth(380)
        self.login_btn.setMinimumHeight(52)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        self.login_btn.setStyleSheet("""
        QPushButton {
            background: #E53935;
            color: #FFFFFF;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            letter-spacing: 1px;
        }
        QPushButton:hover {
            background: #FF4D4D;
        }
        QPushButton:pressed {
            background: #C62828;
        }
        QPushButton:disabled {
            background: #2C2C31;
            color: #6A6A6A;
        }
        """)

        self.login_btn.clicked.connect(self._on_login)
        layout.addWidget(self.login_btn, 0, Qt.AlignmentFlag.AlignCenter)

        # Error message
        self.error_lbl = QLabel()
        self.error_lbl.setFont(QFont("Segoe UI", 13))
        self.error_lbl.setStyleSheet("""
        QLabel {
            color: #FF5252;
            background: transparent;
            padding: 8px 0px;
        }
        """)
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setVisible(False)
        self.error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_lbl, 0, Qt.AlignmentFlag.AlignCenter)

    def _toggle_password_visibility(self):
        """Alterna visibilidade da senha."""
        self._password_visible = not self._password_visible
        if self._password_visible:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setIcon(get_icon("eye-off", QSize(20, 20), "#9A9A9A"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setIcon(get_icon("eye", QSize(20, 20), "#9A9A9A"))

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        remember = False  # Minimal design - no remember option
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
