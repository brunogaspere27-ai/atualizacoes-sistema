"""
Tela de Login CW Transportadora - PySide6
Layout premium inspirado na referência:
- Painel esquerdo com imagem, overlay escuro e identidade CW
- Painel direito preto, sem card
- Formulário centralizado verticalmente
- Logo/brand maior
- Inputs modernos
- Ícone de mostrar/ocultar senha
- Autenticação em thread + Signals para UI thread
"""

from typing import Optional
import os
import threading

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPixmap, QPainter

from config.settings import settings
from services.auth_service import (
    auth_service,
    ContaBloqueadaError,
    ContaInativaError,
    CredenciaisInvalidasError,
)
from services.auditoria_service import (
    auditoria_service,
    ACAO_LOGIN,
    ACAO_LOGIN_FALHOU,
)
from utils.logger import get_logger


logger = get_logger(__name__)


# ============================================================================
# DESIGN SYSTEM
# ============================================================================

_BG_LEFT = "#0B1018"
_BG_RIGHT = "#080B11"

_SURFACE = "#111722"
_SURFACE_HOVER = "#151C29"

_BORDER = "#242D3D"
_BORDER_FOCUS = "#E51C23"

_WHITE = "#FFFFFF"
_TEXT = "#E7ECF3"
_TEXT_SECONDARY = "#94A3B8"
_TEXT_MUTED = "#64748B"

_RED = "#E51C23"
_RED_HOVER = "#F52A31"
_RED_PRESSED = "#C9161D"

_ERROR_BG = "#2A1115"
_ERROR_BORDER = "#7F1D1D"
_ERROR_TEXT = "#F87171"


# ============================================================================
# HERO / PAINEL ESQUERDO
# ============================================================================

class _HeroPanel(QWidget):
    """
    Painel visual esquerdo.

    A imagem ocupa todo o painel e recebe um overlay escuro para manter
    o texto legível. A largura é proporcional à janela, em vez de fixa.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setMinimumWidth(460)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self._bg: Optional[QPixmap] = None

        # O projeto atual já utiliza este recurso como imagem principal.
        try:
            image_path = str(settings.resource_path("assets/logo_cw.login.jpg"))
            if os.path.exists(image_path):
                pix = QPixmap(image_path)
                if not pix.isNull():
                    self._bg = pix
        except Exception as exc:
            logger.warning(f"Não foi possível carregar imagem do login: {exc}")

        self._setup_content()

    def _setup_content(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(62, 56, 62, 52)
        layout.setSpacing(0)

        # ------------------------------------------------------------------
        # Marca no topo
        # ------------------------------------------------------------------

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(0, 0, 0, 0)
        brand_row.setSpacing(12)

        logo = QFrame()
        logo.setFixedSize(48, 48)
        logo.setStyleSheet(f"""
            QFrame {{
                background-color: {_RED};
                border-radius: 8px;
            }}
        """)

        logo_layout = QVBoxLayout(logo)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        logo_text = QLabel("CW")
        logo_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_text.setStyleSheet("""
            QLabel {
                color: white;
                background: transparent;
                font-size: 16px;
                font-weight: 900;
            }
        """)
        logo_layout.addWidget(logo_text)

        logo_shadow = QGraphicsDropShadowEffect(self)
        logo_shadow.setBlurRadius(22)
        logo_shadow.setOffset(0, 5)
        logo_shadow.setColor(QColor(229, 28, 35, 145))
        logo.setGraphicsEffect(logo_shadow)

        brand_row.addWidget(logo, 0, Qt.AlignmentFlag.AlignVCenter)

        brand = QLabel("CW Transportadora")
        brand.setStyleSheet(f"""
            QLabel {{
                color: {_WHITE};
                background: transparent;
                font-size: 24px;
                font-weight: 800;
            }}
        """)
        brand_row.addWidget(brand, 0, Qt.AlignmentFlag.AlignVCenter)
        brand_row.addStretch()

        layout.addLayout(brand_row)

        # Espaço flexível: mantém o conteúdo inferior na parte de baixo.
        layout.addStretch(1)

        # ------------------------------------------------------------------
        # Texto principal
        # ------------------------------------------------------------------

        title = QLabel("Sistema de Gestão Logística")
        title.setWordWrap(True)
        title.setStyleSheet(f"""
            QLabel {{
                color: {_WHITE};
                background: transparent;
                font-size: 38px;
                font-weight: 800;
                line-height: 1.1;
            }}
        """)
        layout.addWidget(title)

        subtitle = QLabel(
            "Controle operacional completo: de notas fiscais e viagens "
            "à frotas e fluxos financeiros em uma única central de inteligência."
        )
        subtitle.setWordWrap(True)
        subtitle.setContentsMargins(0, 14, 0, 0)
        subtitle.setMaximumWidth(610)
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {_TEXT_SECONDARY};
                background: transparent;
                font-size: 15px;
                font-weight: 500;
                line-height: 1.45;
            }}
        """)
        layout.addWidget(subtitle)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        rect = self.rect()

        if self._bg:
            scaled = self._bg.scaled(
                rect.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )

            x = max(0, (scaled.width() - rect.width()) // 2)
            y = max(0, (scaled.height() - rect.height()) // 2)

            painter.drawPixmap(
                0, 0,
                scaled,
                x, y,
                rect.width(), rect.height(),
            )
        else:
            painter.fillRect(rect, QColor(_BG_LEFT))

        # Overlay principal: escurece a foto sem escondê-la.
        painter.fillRect(rect, QColor(5, 8, 13, 158))

        # Pequeno reforço escuro na parte inferior para destacar o texto.
        bottom_gradient = QColor(5, 8, 13, 75)
        painter.fillRect(
            0,
            int(rect.height() * 0.62),
            rect.width(),
            int(rect.height() * 0.38),
            bottom_gradient,
        )

        painter.end()


# ============================================================================
# TELA DE LOGIN
# ============================================================================

class TelaLogin(QWidget):
    login_sucesso = Signal(dict)

    # Sinais para voltar da thread de autenticação para a UI thread.
    _auth_sucesso = Signal(dict)
    _auth_erro = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._autenticando = False
        self._senha_visivel = False

        self._auth_sucesso.connect(self._on_auth_sucesso)
        self._auth_erro.connect(self._on_auth_erro)

        self._setup_ui()

    # ------------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------------

    def _setup_ui(self):
        self.setObjectName("loginPage")
        self.setStyleSheet(f"""
            QWidget#loginPage {{
                background: {_BG_RIGHT};
            }}
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # O painel esquerdo cresce proporcionalmente.
        hero = _HeroPanel(self)
        root.addWidget(hero, 48)

        # Painel direito.
        form_panel = self._build_form_panel()
        root.addWidget(form_panel, 52)

    def _build_form_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("loginFormPanel")
        panel.setStyleSheet(f"""
            QWidget#loginFormPanel {{
                background: {_BG_RIGHT};
            }}
        """)

        panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        outer = QVBoxLayout(panel)
        outer.setContentsMargins(48, 0, 48, 0)
        outer.setSpacing(0)

        # Centralização vertical.
        outer.addStretch(1)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addStretch()

        row.addWidget(
            self._build_form(),
            0,
            Qt.AlignmentFlag.AlignCenter,
        )

        row.addStretch()
        outer.addLayout(row)

        outer.addStretch(1)

        # Rodapé.
        footer = QLabel("Versão v6.0.21  |  CW Transportadora S/A")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"""
            QLabel {{
                color: {_TEXT_MUTED};
                background: transparent;
                font-size: 11px;
                padding-bottom: 28px;
            }}
        """)
        outer.addWidget(footer)

        return panel

    def _build_form(self) -> QWidget:
        form = QWidget()
        form.setFixedWidth(400)
        form.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(form)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ------------------------------------------------------------------
        # Cabeçalho
        # ------------------------------------------------------------------

        title = QLabel("Acessar Central")
        title.setStyleSheet(f"""
            QLabel {{
                color: {_WHITE};
                background: transparent;
                font-size: 32px;
                font-weight: 800;
            }}
        """)
        layout.addWidget(title)

        subtitle = QLabel("Insira suas credenciais corporativas")
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {_TEXT_SECONDARY};
                background: transparent;
                font-size: 13px;
                font-weight: 500;
                padding-top: 7px;
                padding-bottom: 32px;
            }}
        """)
        layout.addWidget(subtitle)

        # ------------------------------------------------------------------
        # Erro
        # ------------------------------------------------------------------

        self.label_erro = QLabel("")
        self.label_erro.setWordWrap(True)
        self.label_erro.setContentsMargins(12, 9, 12, 9)
        self.label_erro.setStyleSheet(f"""
            QLabel {{
                background: {_ERROR_BG};
                color: {_ERROR_TEXT};
                border: 1px solid {_ERROR_BORDER};
                border-radius: 7px;
                font-size: 12px;
            }}
        """)
        self.label_erro.hide()
        layout.addWidget(self.label_erro)

        if self.label_erro.isVisible():
            layout.addSpacing(16)

        # ------------------------------------------------------------------
        # Usuário
        # ------------------------------------------------------------------

        layout.addWidget(self._field_label("Usuário"))

        self.entry_usuario = self._input(
            "operacoes@cwtransportes.com.br"
        )
        layout.addWidget(self.entry_usuario)

        layout.addSpacing(20)

        # ------------------------------------------------------------------
        # Senha
        # ------------------------------------------------------------------

        layout.addWidget(self._field_label("Senha"))
        layout.addWidget(self._senha_row())

        layout.addSpacing(18)

        # ------------------------------------------------------------------
        # Lembrar / Esqueci
        # ------------------------------------------------------------------

        options = QHBoxLayout()
        options.setContentsMargins(0, 0, 0, 0)
        options.setSpacing(8)

        self.check_lembrar = QCheckBox("Lembrar de mim")
        self.check_lembrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_lembrar.setStyleSheet(f"""
            QCheckBox {{
                color: {_TEXT_SECONDARY};
                background: transparent;
                font-size: 13px;
                spacing: 8px;
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid {_BORDER};
                background: {_SURFACE};
            }}

            QCheckBox::indicator:hover {{
                border-color: {_TEXT_MUTED};
            }}

            QCheckBox::indicator:checked {{
                background: {_RED};
                border: 1px solid {_RED};
            }}
        """)
        options.addWidget(self.check_lembrar)

        options.addStretch()

        btn_esqueci = QPushButton("Esqueci minha senha")
        btn_esqueci.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_esqueci.setStyleSheet(f"""
            QPushButton {{
                color: {_RED};
                background: transparent;
                border: none;
                padding: 0;
                font-size: 13px;
                font-weight: 700;
            }}

            QPushButton:hover {{
                color: {_RED_HOVER};
            }}

            QPushButton:pressed {{
                color: {_RED_PRESSED};
            }}
        """)
        options.addWidget(btn_esqueci)

        layout.addLayout(options)

        layout.addSpacing(30)

        # ------------------------------------------------------------------
        # Entrar
        # ------------------------------------------------------------------

        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setMinimumHeight(49)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.setStyleSheet(f"""
            QPushButton {{
                background-color: {_RED};
                color: {_WHITE};
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 800;
            }}

            QPushButton:hover {{
                background-color: {_RED_HOVER};
            }}

            QPushButton:pressed {{
                background-color: {_RED_PRESSED};
            }}

            QPushButton:disabled {{
                background-color: {_BORDER};
                color: {_TEXT_MUTED};
            }}
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(229, 28, 35, 62))
        self.btn_entrar.setGraphicsEffect(shadow)

        self.btn_entrar.clicked.connect(self._tentar_login)
        layout.addWidget(self.btn_entrar)

        # Loading.
        self.label_loading = QLabel("")
        self.label_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_loading.setStyleSheet(f"""
            QLabel {{
                color: {_TEXT_MUTED};
                background: transparent;
                font-size: 12px;
                padding-top: 9px;
            }}
        """)
        layout.addWidget(self.label_loading)

        # Enter.
        self.entry_usuario.returnPressed.connect(self._tentar_login)

        return form

    # ------------------------------------------------------------------------
    # Helpers visuais
    # ------------------------------------------------------------------------

    def _field_label(self, texto: str) -> QLabel:
        label = QLabel(texto)
        label.setStyleSheet(f"""
            QLabel {{
                color: {_TEXT_SECONDARY};
                background: transparent;
                font-size: 12px;
                font-weight: 700;
                padding-bottom: 7px;
            }}
        """)
        return label

    def _input(self, placeholder: str) -> QLineEdit:
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setMinimumHeight(47)
        edit.setStyleSheet(f"""
            QLineEdit {{
                background: {_SURFACE};
                color: {_TEXT};
                border: 1px solid {_BORDER};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                selection-background-color: {_RED};
            }}

            QLineEdit:hover {{
                background: {_SURFACE_HOVER};
                border-color: #303B4E;
            }}

            QLineEdit:focus {{
                background: {_SURFACE_HOVER};
                border: 1px solid {_RED};
            }}

            QLineEdit::placeholder {{
                color: {_TEXT_SECONDARY};
            }}
        """)
        return edit

    def _senha_row(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.entry_senha = self._input("••••••••••••")
        self.entry_senha.setEchoMode(QLineEdit.EchoMode.Password)

        # O campo ocupa todo o espaço; o botão fica integrado visualmente.
        self.entry_senha.setStyleSheet(
            self.entry_senha.styleSheet().replace(
                "border-radius: 8px;",
                "border-radius: 8px 0 0 8px;"
            )
        )
        layout.addWidget(self.entry_senha)

        self.btn_toggle = QPushButton("◉")
        self.btn_toggle.setFixedSize(47, 47)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setToolTip("Mostrar senha")
        self.btn_toggle.setStyleSheet(f"""
            QPushButton {{
                background: {_SURFACE};
                color: {_TEXT_MUTED};
                border: 1px solid {_BORDER};
                border-left: none;
                border-radius: 0 8px 8px 0;
                font-size: 17px;
            }}

            QPushButton:hover {{
                background: {_SURFACE_HOVER};
                color: {_TEXT_SECONDARY};
            }}

            QPushButton:pressed {{
                color: {_WHITE};
            }}
        """)
        self.btn_toggle.clicked.connect(self._toggle_senha)

        layout.addWidget(self.btn_toggle)

        self.entry_senha.returnPressed.connect(self._tentar_login)

        return container

    # ------------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------------

    def _toggle_senha(self):
        self._senha_visivel = not self._senha_visivel

        if self._senha_visivel:
            self.entry_senha.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle.setText("◌")
            self.btn_toggle.setToolTip("Ocultar senha")
        else:
            self.entry_senha.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle.setText("◉")
            self.btn_toggle.setToolTip("Mostrar senha")

    def _tentar_login(self):
        if self._autenticando:
            return

        usuario = self.entry_usuario.text().strip()
        senha = self.entry_senha.text()

        if not usuario or not senha:
            self._mostrar_erro(
                "Preencha usuário e senha para continuar."
            )
            return

        self._autenticando = True
        self.label_erro.hide()
        self.label_loading.setText("Autenticando, aguarde...")
        self.btn_entrar.setEnabled(False)
        self.btn_entrar.setText("Entrando...")

        def tarefa():
            try:
                dados = auth_service.login(usuario, senha)

                # Auditoria ocorre em background para não bloquear a UI.
                try:
                    auditoria_service.registrar(
                        ACAO_LOGIN,
                        modulo="auth",
                        registro_afetado=dados["usuario"],
                        detalhes="Login bem-sucedido",
                        usuario_id=dados["id"],
                        usuario_nome=dados["nome_completo"],
                    )
                except Exception as exc:
                    logger.warning(
                        f"Auditoria de login falhou: {exc}"
                    )

                # Salvar sessão somente se o usuário marcou a opção.
                try:
                    if self.check_lembrar.isChecked():
                        auth_service.salvar_sessao(dados)
                except Exception as exc:
                    logger.warning(
                        f"Falha ao salvar sessão: {exc}"
                    )

                self._auth_sucesso.emit(dados)

            except ContaBloqueadaError as exc:
                try:
                    auditoria_service.registrar(
                        ACAO_LOGIN_FALHOU,
                        modulo="auth",
                        registro_afetado=usuario,
                        detalhes="Conta bloqueada",
                    )
                except Exception:
                    pass

                self._auth_erro.emit(str(exc))

            except ContaInativaError as exc:
                self._auth_erro.emit(str(exc))

            except CredenciaisInvalidasError as exc:
                try:
                    auditoria_service.registrar(
                        ACAO_LOGIN_FALHOU,
                        modulo="auth",
                        registro_afetado=usuario,
                        detalhes="Credenciais inválidas",
                    )
                except Exception:
                    pass

                self._auth_erro.emit(str(exc))

            except Exception as exc:
                logger.error(
                    f"Erro inesperado no login: {exc}",
                    exc_info=True,
                )
                self._auth_erro.emit(
                    "Erro interno ao autenticar. Tente novamente."
                )

        threading.Thread(
            target=tarefa,
            daemon=True,
        ).start()

    # ------------------------------------------------------------------------
    # Handlers UI thread
    # ------------------------------------------------------------------------

    def _on_auth_sucesso(self, dados: dict):
        self._resetar_estado()
        self.login_sucesso.emit(dados)

    def _on_auth_erro(self, mensagem: str):
        self._resetar_estado()
        self._mostrar_erro(mensagem)

    def _mostrar_erro(self, mensagem: str):
        self.label_erro.setText("⚠  " + mensagem)
        self.label_erro.show()

        self.label_loading.setText("")
        self.entry_senha.clear()
        self.entry_senha.setFocus()

    def _resetar_estado(self):
        self._autenticando = False
        self.btn_entrar.setEnabled(True)
        self.btn_entrar.setText("Entrar")
        self.label_loading.setText("")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
