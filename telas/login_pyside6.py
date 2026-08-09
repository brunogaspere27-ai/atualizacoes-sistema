"""
Tela de Login CW Transportadora - PySide6

Design premium minimalista:
- Fundo com gradiente suave
- Card centralizado (420px, 8px radius, 1px border)
- Logo CW circular (64px) no topo do card
- Inputs modernos com label
- Botão primário full-width
- Thread de autenticação usa Signal para retornar à UI thread (thread-safe)
"""

from typing import Optional
import os
import threading

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFrame, QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer, QSize
from PySide6.QtGui import QColor, QPixmap, QIcon, QPainter, QBrush, QPainterPath

from config.settings import settings
from services.auth_service import (
    auth_service,
    ContaBloqueadaError,
    ContaInativaError,
    CredenciaisInvalidasError,
)
from services.auditoria_service import auditoria_service, ACAO_LOGIN, ACAO_LOGIN_FALHOU
from ui.theme.cw_theme import cw_theme
from utils.logger import get_logger

logger = get_logger(__name__)


def _fazer_pixmap_circular(caminho: str, tamanho: int) -> Optional[QPixmap]:
    """Recorta uma imagem em círculo. Retorna None se não conseguir carregar."""
    if not caminho or not os.path.exists(caminho):
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


class TelaLogin(QWidget):
    """Tela de login premium em PySide6 - design minimalista.

    Thread-safety:
        A autenticação roda em threading.Thread para não travar a UI.
        Usamos Signals para retornar resultados à UI thread de forma segura.
    """

    # Sinal público: emitido quando o login é aprovado (conectado pelo App)
    login_sucesso = Signal(dict)

    # Sinais internos — usados para cruzar a barreira thread → UI thread
    _auth_sucesso  = Signal(dict)   # payload: dados do usuário
    _auth_erro     = Signal(str)    # payload: mensagem de erro para o usuário

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._autenticando = False
        self._senha_visivel = False

        # Conectar sinais internos aos handlers na UI thread
        self._auth_sucesso.connect(self._on_auth_sucesso)
        self._auth_erro.connect(self._on_auth_erro)

        self._setup_ui()

    # ---------------------------------------------------------------- Setup
    def _setup_ui(self):
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius

        # Fundo do widget inteiro com gradiente suave
        self.setObjectName("loginPage")
        self.setStyleSheet(f"""
        QWidget#loginPage {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['bg_primary']},
                stop:0.5 {c['bg_secondary']},
                stop:1 {c['bg_primary']});
        }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Centralizar completamente (horizontal e vertical)
        outer = QHBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addStretch()
        
        inner = QVBoxLayout()
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)
        inner.addStretch()
        inner.addWidget(self._build_card(), alignment=Qt.AlignmentFlag.AlignCenter)
        inner.addStretch()
        
        outer.addLayout(inner)
        outer.addStretch()
        root.addLayout(outer)

    def _build_card(self) -> QFrame:
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius

        card = QFrame()
        card.setObjectName("loginCard")
        card.setMinimumWidth(420)
        card.setStyleSheet(f"""
        QFrame#loginCard {{
            background-color: {c['bg_elevated']};
            border: 1px solid {c['border_subtle']};
            border-radius: {r.LG}px;
        }}
        """)

        # Sombra sutil
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 36, 40, 32)
        layout.setSpacing(16)

        # Logo CW circular (64px)
        logo_row = QHBoxLayout()
        logo_row.addStretch()

        logo_circle = QFrame()
        logo_circle.setFixedSize(64, 64)
        logo_circle.setStyleSheet(f"""
        QFrame {{
            background: {c['primary']};
            border-radius: 32px;
        }}
        """)
        circle_layout = QVBoxLayout(logo_circle)
        circle_layout.setContentsMargins(0, 0, 0, 0)

        logo_label = QLabel()
        logo_label.setFixedSize(64, 64)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = str(settings.resource_path("assets/logo_cw.jpg"))
        pix = _fazer_pixmap_circular(logo_path, 64)
        if pix is not None:
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("CW")
            logo_label.setStyleSheet(f"""
            QLabel {{
                background: {c['primary']};
                color: white;
                border-radius: 32px;
                font-size: 20px;
                font-weight: 800;
            }}
            """)
        circle_layout.addWidget(logo_label)
        logo_row.addWidget(logo_circle)
        logo_row.addStretch()
        layout.addLayout(logo_row)

        # Título
        titulo = QLabel("CW Transportadora")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet(f"""
        QLabel {{
            color: {c['text_primary']};
            font-size: {cw_theme.typography.FONT_SIZE_3XL}px;
            font-weight: 700;
            background: transparent;
            padding-top: 4px;
        }}
        """)
        layout.addWidget(titulo)

        subtitulo = QLabel("Sistema de Gestão Logística • V8")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitulo.setStyleSheet(f"""
        QLabel {{
            color: {c['text_tertiary']};
            font-size: {cw_theme.typography.FONT_SIZE_SM}px;
            background: transparent;
            letter-spacing: 1.5px;
            padding-bottom: 8px;
        }}
        """)
        layout.addWidget(subtitulo)

        # Banner de erro (oculto no início)
        self.label_erro = QLabel("")
        self.label_erro.setWordWrap(True)
        self.label_erro.setStyleSheet(f"""
        QLabel {{
            background-color: {c['error_soft']};
            color: {c['error']};
            border: 1px solid {c['error']};
            border-radius: {r.MD}px;
            padding: 10px 14px;
            font-size: {cw_theme.typography.FONT_SIZE_MD}px;
        }}
        """)
        self.label_erro.hide()
        layout.addWidget(self.label_erro)

        # Usuário
        layout.addWidget(self._field_label("USUÁRIO"))
        self.entry_usuario = self._modern_input("Digite seu usuário")
        layout.addWidget(self.entry_usuario)

        # Senha
        layout.addWidget(self._field_label("SENHA"))
        layout.addWidget(self._senha_row())

        # Lembrar
        self.check_lembrar = QCheckBox("Manter-me conectado")
        self.check_lembrar.setStyleSheet(f"""
        QCheckBox {{
            color: {c['text_secondary']};
            background: transparent;
            font-size: {cw_theme.typography.FONT_SIZE_MD}px;
            padding: 4px 2px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border-radius: {r.XS}px;
            border: 1.5px solid {c['border_default']};
            background-color: {c['bg_tertiary']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {c['primary']};
            border-color: {c['primary']};
        }}
        """)
        layout.addWidget(self.check_lembrar)

        # Botão entrar (full-width)
        self.btn_entrar = QPushButton("ENTRAR NO SISTEMA")
        self.btn_entrar.setMinimumHeight(48)
        self.btn_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_entrar.setStyleSheet(f"""
        QPushButton {{
            background-color: {colors['brand']};
            color: white;
            border: none;
            border-radius: {tokens.RADIUS_MD}px;
            font-size: {tokens.FONT_SIZE_LG}px;
            font-weight: 700;
            letter-spacing: 1.2px;
        }}
        QPushButton:hover {{
            background-color: {colors['brand_hover']};
        }}
        QPushButton:pressed {{
            background-color: {colors['brand_active']};
        }}
        QPushButton:disabled {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_disabled']};
        }}
        """)
        self.btn_entrar.clicked.connect(self._tentar_login)
        layout.addWidget(self.btn_entrar)

        # Loading
        self.label_loading = QLabel("")
        self.label_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_loading.setStyleSheet(f"""
        QLabel {{
            color: {colors['text_tertiary']};
            background: transparent;
            padding-top: 8px;
            font-size: {tokens.FONT_SIZE_SM}px;
        }}
        """)
        layout.addWidget(self.label_loading)

        layout.addStretch()

        # Rodapé
        rodape = QLabel("Versão 8.0  •  © CW Transportadora")
        rodape.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rodape.setStyleSheet(f"""
        QLabel {{
            color: {colors['text_tertiary']};
            background: transparent;
            padding-top: 12px;
            font-size: {tokens.FONT_SIZE_XS}px;
        }}
        """)
        layout.addWidget(rodape)

        # Enter dispara login
        self.entry_usuario.returnPressed.connect(self._tentar_login)
        self.entry_senha.returnPressed.connect(self._tentar_login)

        return card

    # ---------------------------------------------------------------- Helpers
    def _field_label(self, texto: str) -> QLabel:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        lbl = QLabel(texto)
        lbl.setStyleSheet(f"""
        QLabel {{
            color: {colors['text_secondary']};
            background-color: transparent;
            padding-bottom: 4px;
            font-size: {tokens.FONT_SIZE_XS}px;
            font-weight: 700;
            letter-spacing: 1.5px;
        }}
        """)
        return lbl

    def _modern_input(self, placeholder: str) -> QLineEdit:
        colors = theme_manager.colors
        tokens = theme_manager.tokens
        ed = QLineEdit()
        ed.setPlaceholderText(placeholder)
        ed.setMinimumHeight(48)
        ed.setFont(theme_manager.get_font(tokens.FONT_SIZE_LG))
        ed.setStyleSheet(f"""
        QLineEdit {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_primary']};
            border: 1px solid {colors['border_default']};
            border-radius: {tokens.RADIUS_MD}px;
            padding: 12px 16px;
            selection-background-color: {colors['brand_soft']};
        }}
        QLineEdit:hover {{
            border-color: {colors['border_strong']};
        }}
        QLineEdit:focus {{
            border: 1px solid {colors['brand']};
            background-color: {colors['bg_secondary']};
        }}
        """)
        return ed

    def _senha_row(self) -> QWidget:
        colors = theme_manager.colors
        tokens = theme_manager.tokens

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        self.entry_senha = self._modern_input("Digite sua senha")
        self.entry_senha.setEchoMode(QLineEdit.EchoMode.Password)
        h.addWidget(self.entry_senha)

        self.btn_toggle_senha = QPushButton("Mostrar")
        self.btn_toggle_senha.setFixedWidth(80)
        self.btn_toggle_senha.setMinimumHeight(48)
        self.btn_toggle_senha.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_senha.setStyleSheet(f"""
        QPushButton {{
            background-color: {colors['bg_tertiary']};
            color: {colors['text_secondary']};
            border: 1px solid {colors['border_default']};
            border-radius: {tokens.RADIUS_MD}px;
            font-size: {tokens.FONT_SIZE_SM}px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: {colors['bg_overlay']};
            color: {colors['text_primary']};
            border-color: {colors['border_strong']};
        }}
        """)
        self.btn_toggle_senha.clicked.connect(self._toggle_senha)
        h.addWidget(self.btn_toggle_senha)

        return container

    # ---------------------------------------------------------------- Ações
    def _toggle_senha(self):
        self._senha_visivel = not self._senha_visivel
        if self._senha_visivel:
            self.entry_senha.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_senha.setText("Ocultar")
        else:
            self.entry_senha.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_senha.setText("Mostrar")

    def _tentar_login(self):
        if self._autenticando:
            return

        usuario = self.entry_usuario.text().strip()
        senha = self.entry_senha.text()

        if not usuario or not senha:
            self._mostrar_erro("Preencha usuário e senha para continuar.")
            return

        self._autenticando = True
        self.label_erro.hide()
        self.label_loading.setText("Autenticando, aguarde...")
        self.btn_entrar.setEnabled(False)
        self.btn_entrar.setText("ENTRANDO...")

        def tarefa():
            """Roda em thread de background — NÃO tocar em widgets daqui.

            Resultados são entregues via Signal, que o Qt enfileira na UI thread.
            """
            try:
                dados = auth_service.login(usuario, senha)

                # Auditoria também em background (I/O SQLite, não bloqueia a UI)
                try:
                    auditoria_service.registrar(
                        ACAO_LOGIN, modulo="auth",
                        registro_afetado=dados["usuario"],
                        detalhes="Login bem-sucedido",
                        usuario_id=dados["id"],
                        usuario_nome=dados["nome_completo"],
                    )
                except Exception as e_audit:
                    logger.warning(f"Falha ao registrar auditoria de login: {e_audit}")

                if self.check_lembrar.isChecked():
                    try:
                        auth_service.salvar_sessao(dados)
                    except Exception as e_sess:
                        logger.warning(f"Falha ao salvar sessão: {e_sess}")

                # Emitir Signal — Qt entrega na UI thread automaticamente
                self._auth_sucesso.emit(dados)

            except ContaBloqueadaError as erro:
                try:
                    auditoria_service.registrar(
                        ACAO_LOGIN_FALHOU, modulo="auth",
                        registro_afetado=usuario, detalhes="Conta bloqueada",
                    )
                except Exception:
                    pass
                self._auth_erro.emit(str(erro))

            except ContaInativaError as erro:
                self._auth_erro.emit(str(erro))

            except CredenciaisInvalidasError as erro:
                try:
                    auditoria_service.registrar(
                        ACAO_LOGIN_FALHOU, modulo="auth",
                        registro_afetado=usuario, detalhes="Credenciais inválidas",
                    )
                except Exception:
                    pass
                self._auth_erro.emit(str(erro))

            except Exception as erro:
                logger.error(f"Erro inesperado no login: {erro}", exc_info=True)
                self._auth_erro.emit("Erro interno ao autenticar. Tente novamente.")

        threading.Thread(target=tarefa, daemon=True).start()

    # --------- Handlers na UI thread (chamados via Signal) ----------

    def _on_auth_sucesso(self, dados: dict):
        """Chamado na UI thread quando a autenticação é aprovada."""
        self._resetar_estado()
        self.login_sucesso.emit(dados)

    def _on_auth_erro(self, mensagem: str):
        """Chamado na UI thread quando a autenticação falha."""
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
        self.btn_entrar.setText("ENTRAR NO SISTEMA")
        self.label_loading.setText("")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            return
        super().keyPressEvent(event)
