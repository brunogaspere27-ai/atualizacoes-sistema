"""
Tela de histórico de versões do CW Transportadora — PySide6.

Exibe versão instalada, botão de verificação de atualização e lista
paginada de releases anteriores obtidos via update_service.
"""

from __future__ import annotations

import threading

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from services.update_service import update_service
from ui.theme.cw_theme import cw_theme
from utils.logger import get_logger

logger = get_logger(__name__)


class TelaHistoricoVersoes(QWidget):
    """Tela com histórico de versões do sistema."""

    # Sinais internos para cruzar thread → UI thread
    _dados_prontos = Signal(str, str, str, list)   # versao, data, nome, historico
    _dados_erro = Signal(str)
    _verificacao_pronta = Signal(dict)
    _verificacao_erro = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._dados_prontos.connect(self._on_dados_prontos)
        self._dados_erro.connect(self._on_dados_erro)
        self._verificacao_pronta.connect(self._on_verificacao_pronta)
        self._verificacao_erro.connect(self._on_verificacao_erro)

        self._setup_ui()
        self._carregar_dados()

    # ---------------------------------------------------------------- setup
    def _setup_ui(self) -> None:
        colors = cw_theme.colors
        tokens = cw_theme.spacing

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ──────────────────────────────────────────────────────────
        header = QFrame()
        header.setStyleSheet(f"""
        QFrame {{
            background-color: {cw_theme.colors['sidebar_bg']};
            border: none;
        }}
        """)
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(
            cw_theme.spacing.SPACING_2XL, cw_theme.spacing.SPACING_LG,
            cw_theme.spacing.SPACING_2XL, cw_theme.spacing.SPACING_LG,
        )
        header_layout.setSpacing(cw_theme.spacing.SPACING_XS)

        titulo = QLabel("HISTÓRICO DE VERSÕES")
        titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_2XL, bold=True))
        titulo.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: transparent;")
        header_layout.addWidget(titulo)

        subtitulo = QLabel("Informações de atualizações e releases do sistema")
        subtitulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        subtitulo.setStyleSheet(f"color: {cw_theme.colors['text_secondary']}; background: transparent;")
        header_layout.addWidget(subtitulo)

        root.addWidget(header)

        # ── Área rolável ─────────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(f"""
        QScrollArea {{
            background-color: {cw_theme.colors['bg_primary']};
            border: none;
        }}
        """)

        self._content = QWidget()
        self._content.setStyleSheet(f"background-color: {cw_theme.colors['bg_primary']};")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(
            cw_theme.spacing.SPACING_2XL, cw_theme.spacing.SPACING_XL,
            cw_theme.spacing.SPACING_2XL, cw_theme.spacing.SPACING_XL,
        )
        self._content_layout.setSpacing(cw_theme.spacing.SPACING_MD)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(self._content)
        root.addWidget(scroll, stretch=1)

        # ── Card versão atual ────────────────────────────────────────────────
        self._card_versao = self._make_card()
        card_layout = QVBoxLayout(self._card_versao)
        card_layout.setContentsMargins(
            cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_LG,
            cw_theme.spacing.SPACING_XL, cw_theme.spacing.SPACING_LG,
        )
        card_layout.setSpacing(cw_theme.spacing.SPACING_SM)

        self._lbl_versao = QLabel("Versão instalada: carregando…")
        self._lbl_versao.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_LG, bold=True))
        self._lbl_versao.setStyleSheet(
            f"color: {cw_theme.colors['text_primary']}; background: transparent;"
        )
        card_layout.addWidget(self._lbl_versao)

        self._lbl_data = QLabel("")
        self._lbl_data.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        self._lbl_data.setStyleSheet(
            f"color: {cw_theme.colors['text_secondary']}; background: transparent;"
        )
        card_layout.addWidget(self._lbl_data)

        # Linha botão + status
        btn_row = QHBoxLayout()
        btn_row.setSpacing(cw_theme.spacing.SPACING_MD)

        self._btn_verificar = QPushButton("Verificar Atualizações")
        self._btn_verificar.setMinimumHeight(40)
        self._btn_verificar.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_verificar.setStyleSheet(f"""
        QPushButton {{
            background-color: {cw_theme.colors['info']};
            color: #FFFFFF;
            border: none;
            border-radius: {cw_theme.radius.MD}px;
            padding: 0 20px;
            font-weight: 700;
            font-size: {cw_theme.typography.FONT_SIZE_MD}px;
        }}
        QPushButton:hover  {{ background-color: {cw_theme.colors['info']}; }}
        QPushButton:pressed {{ background-color: {cw_theme.colors['brand']}; }}
        QPushButton:disabled {{
            background-color: {cw_theme.colors['bg_tertiary']};
            color: {cw_theme.colors['text_disabled']};
        }}
        """)
        self._btn_verificar.clicked.connect(self._verificar_agora)
        btn_row.addWidget(self._btn_verificar)

        self._lbl_status = QLabel("")
        self._lbl_status.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        self._lbl_status.setStyleSheet(
            f"color: {cw_theme.colors['text_secondary']}; background: transparent;"
        )
        btn_row.addWidget(self._lbl_status)
        btn_row.addStretch()

        card_layout.addLayout(btn_row)
        self._content_layout.addWidget(self._card_versao)

        # Loading placeholder
        self._lbl_loading = QLabel("Carregando histórico…")
        self._lbl_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_loading.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD))
        self._lbl_loading.setStyleSheet(
            f"color: {cw_theme.colors['text_secondary']}; background: transparent;"
        )
        self._lbl_loading.setMinimumHeight(60)
        self._content_layout.addWidget(self._lbl_loading)

    # ---------------------------------------------------------------- helpers
    def _make_card(self) -> QFrame:
        colors = cw_theme.colors
        tokens = cw_theme.spacing
        card = QFrame()
        card.setStyleSheet(f"""
        QFrame {{
            background-color: {cw_theme.colors['card_bg']};
            border: 1px solid {cw_theme.colors['card_border']};
            border-radius: {cw_theme.radius.LG}px;
        }}
        """)
        return card

    # ---------------------------------------------------------------- carregamento
    def _carregar_dados(self) -> None:
        def _tarefa() -> None:
            try:
                info = update_service.obter_versao_instalada()
                versao = info.get("versao", "0.0.0")
                data = info.get("data", "")
                nome = info.get("nome", "CW Transportadora")
                historico = update_service.obter_historico_versoes(limit=20)
                self._dados_prontos.emit(versao, data, nome, historico)
            except Exception as exc:
                logger.error(f"Erro ao carregar histórico: {exc}")
                self._dados_erro.emit(str(exc))

        threading.Thread(target=_tarefa, daemon=True).start()

    # ---- handlers UI thread
    def _on_dados_prontos(self, versao: str, data: str, nome: str, historico: list) -> None:
        colors = cw_theme.colors
        tokens = cw_theme.spacing

        self._lbl_versao.setText(f"{nome}  v{versao}")
        self._lbl_data.setText(f"Data da versão: {data or 'N/A'}")

        self._lbl_loading.deleteLater()

        # Título seção histórico
        lbl_titulo = QLabel("Releases anteriores")
        lbl_titulo.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_LG, bold=True))
        lbl_titulo.setStyleSheet(
            f"color: {cw_theme.colors['text_primary']}; background: transparent;"
        )
        self._content_layout.addWidget(lbl_titulo)

        if not historico:
            vazio = QLabel("Nenhum release encontrado.")
            vazio.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            vazio.setStyleSheet(
                f"color: {cw_theme.colors['text_secondary']}; background: transparent;"
            )
            self._content_layout.addWidget(vazio)
            return

        for release in historico:
            self._content_layout.addWidget(self._criar_item_release(release))

        self._content_layout.addStretch()

    def _on_dados_erro(self, erro: str) -> None:
        colors = cw_theme.colors
        self._lbl_loading.setText(f"Erro ao carregar histórico: {erro}")
        self._lbl_loading.setStyleSheet(
            f"color: {cw_theme.colors['error']}; background: transparent;"
        )

    # ---------------------------------------------------------------- item release
    def _criar_item_release(self, release: dict) -> QFrame:
        colors = cw_theme.colors
        tokens = cw_theme.spacing

        versao = release.get("versao", "?")
        data = release.get("data", "")
        notas = release.get("notas", "")
        prerelease = release.get("prerelease", False)

        card = self._make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(
            cw_theme.spacing.SPACING_LG, cw_theme.spacing.SPACING_MD,
            cw_theme.spacing.SPACING_LG, cw_theme.spacing.SPACING_MD,
        )
        layout.setSpacing(cw_theme.spacing.SPACING_SM)

        # Linha superior: versão + tag + data
        top_row = QHBoxLayout()
        top_row.setSpacing(cw_theme.spacing.SPACING_SM)

        lbl_versao = QLabel(f"v{versao}")
        lbl_versao.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_MD, bold=True))
        lbl_versao.setStyleSheet(
            f"color: {cw_theme.colors['text_primary']}; background: transparent;"
        )
        top_row.addWidget(lbl_versao)

        tag_cor = cw_theme.colors["amber"] if prerelease else cw_theme.colors["emerald"]
        tag_texto = "BETA" if prerelease else "STABLE"
        lbl_tag = QLabel(tag_texto)
        lbl_tag.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_XS, bold=True))
        lbl_tag.setStyleSheet(f"""
        QLabel {{
            color: {tag_cor};
            background: transparent;
            padding: 1px 6px;
            border: 1px solid {tag_cor};
            border-radius: 4px;
        }}
        """)
        top_row.addWidget(lbl_tag)
        top_row.addStretch()

        if data:
            lbl_data = QLabel(data)
            lbl_data.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            lbl_data.setStyleSheet(
                f"color: {cw_theme.colors['text_secondary']}; background: transparent;"
            )
            top_row.addWidget(lbl_data)

        layout.addLayout(top_row)

        # Notas da versão
        if notas:
            preview = notas[:300] + ("…" if len(notas) > 300 else "")
            lbl_notas = QLabel(preview)
            lbl_notas.setWordWrap(True)
            lbl_notas.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            lbl_notas.setStyleSheet(
                f"color: {cw_theme.colors['text_secondary']}; background: transparent;"
            )
            layout.addWidget(lbl_notas)

        return card

    # ---------------------------------------------------------------- verificar
    def _verificar_agora(self) -> None:
        colors = cw_theme.colors
        self._btn_verificar.setEnabled(False)
        self._lbl_status.setText("Verificando…")
        self._lbl_status.setStyleSheet(
            f"color: {cw_theme.colors['warning']}; background: transparent;"
        )

        def _tarefa() -> None:
            try:
                resultado = update_service.check_for_updates(channel="stable")
                self._verificacao_pronta.emit(resultado)
            except Exception as exc:
                self._verificacao_erro.emit(str(exc))

        threading.Thread(target=_tarefa, daemon=True).start()

    def _on_verificacao_pronta(self, resultado: dict) -> None:
        colors = cw_theme.colors
        self._btn_verificar.setEnabled(True)

        if resultado.get("error"):
            self._lbl_status.setText(f"Erro: {resultado['error']}")
            self._lbl_status.setStyleSheet(
                f"color: {cw_theme.colors['error']}; background: transparent;"
            )
            return

        if resultado.get("has_update"):
            nova = resultado.get("latest_version", "")
            self._lbl_status.setText(f"Nova versão disponível: {nova}")
            self._lbl_status.setStyleSheet(
                f"color: {cw_theme.colors['success']}; background: transparent;"
            )
        else:
            self._lbl_status.setText("Sistema atualizado!")
            self._lbl_status.setStyleSheet(
                f"color: {cw_theme.colors['success']}; background: transparent;"
            )

    def _on_verificacao_erro(self, erro: str) -> None:
        colors = cw_theme.colors
        self._btn_verificar.setEnabled(True)
        self._lbl_status.setText(f"Erro: {erro}")
        self._lbl_status.setStyleSheet(
            f"color: {cw_theme.colors['error']}; background: transparent;"
        )
