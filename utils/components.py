"""
Componentes UI Base CW Transportadora v9 - PySide6

Componentes reutilizáveis para interface profissional.
Inspirado em Linear, Notion, VS Code, Stripe Dashboard.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLabel, QLineEdit, QTextEdit, QComboBox, QScrollArea,
    QSizePolicy, QGridLayout, QSpacerItem, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve, QSize,
    QTimer, QRectF, QParallelAnimationGroup
)
from PySide6.QtGui import (
    QFont, QColor, QPainter, QPaintEvent, QPen, QLinearGradient, QPixmap, QPainterPath
)
from typing import Optional, List, Callable
from enum import Enum
import os

from telas.theme_aurora import aurora_theme_manager as theme_manager, ThemeTokens, AccentColor
from utils.icons import get_icon, get_pixmap
from utils.avatar import AvatarWidget
from config.settings import settings


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


# ===================================================================== Enums
class ButtonStyle(Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    GHOST = "ghost"


class ButtonSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"


# ===================================================================== ModernButton
class ModernButton(QPushButton):
    """Botão flat com 3 tamanhos, 6 variantes, transições CSS 150ms."""

    def __init__(self, text: str, style: ButtonStyle = ButtonStyle.PRIMARY,
                 icon_name: Optional[str] = None, size: ButtonSize = ButtonSize.MD,
                 parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._style = style
        self._icon_name = icon_name
        self._size = size
        self._apply()

    def _apply(self):
        c = theme_manager.colors
        t = theme_manager.tokens
        sizes = {
            ButtonSize.SM: (28, 12, 16, t.FONT_SIZE_SM),
            ButtonSize.MD: (36, 14, 20, t.FONT_SIZE_MD),
            ButtonSize.LG: (44, 16, 24, t.FONT_SIZE_LG),
        }
        h, px, py, fs = sizes[self._size]
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(h)
        self.setFont(theme_manager.get_font(fs, bold=True))

        if self._icon_name:
            self.setIcon(get_icon(self._icon_name, QSize(16, 16)))
            self.setIconSize(QSize(16, 16))

        if self._style == ButtonStyle.PRIMARY:
            self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
                color: #FFFFFF;
                border: none;
                border-radius: {t.RADIUS_LG}px;
                padding: {py}px {px}px;
                font-weight: 600;
                letter-spacing: 0.2px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c['aurora_hover']}, stop:1 {c['aurora_end']});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {c['aurora_active']}, stop:1 {c['aurora_start']});
            }}
            QPushButton:disabled {{
                background: {c['bg_tertiary']};
                color: {c['text_disabled']};
            }}
            """)
            return

        style_map = {
            ButtonStyle.SECONDARY: (c["bg_tertiary"], c["bg_overlay"], c["bg_elevated"], c["text_primary"],
                                    f"1px solid {c['border_default']}"),
            ButtonStyle.SUCCESS: (c["success"], "#2EA043", "#258136", "#FFF", "none"),
            ButtonStyle.WARNING: (c["warning"], "#B88217", "#9A6700", "#FFF", "none"),
            ButtonStyle.DANGER: (c["error"], "#DA3633", "#B62324", "#FFF", "none"),
            ButtonStyle.GHOST: ("transparent", c["bg_tertiary"], c["bg_overlay"], c["text_primary"], "none"),
        }
        bg, hover, pressed, fg, border = style_map[self._style]
        self.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg}; color: {fg}; border: {border};
            border-radius: {t.RADIUS_LG}px; padding: {py}px {px}px;
            font-weight: 600; letter-spacing: 0.2px;
        }}
        QPushButton:hover {{ background-color: {hover}; }}
        QPushButton:pressed {{ background-color: {pressed}; }}
        QPushButton:disabled {{ background-color: {c['bg_tertiary']}; color: {c['text_disabled']}; }}
        """)


# ===================================================================== ModernCard
class ModernCard(QFrame):
    """Card com 1px border, 8px radius, hover border shift."""

    def __init__(self, title: Optional[str] = None, icon_name: Optional[str] = None,
                 padding: int = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens
        pad = padding or t.SPACING_LG

        self.setObjectName("mCard")
        self.setStyleSheet(f"""
        QFrame#mCard {{
            background-color: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_XL}px;
            border-top: 2px solid {c['aurora']};
        }}
        QFrame#mCard:hover {{
            border-color: {c['border_strong']};
            background-color: {c['card_hover']};
        }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 28))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(pad, pad, pad, pad)
        layout.setSpacing(t.SPACING_MD)
        self.setLayout(layout)

        if title:
            hdr = QHBoxLayout()
            hdr.setSpacing(t.SPACING_SM)
            if icon_name:
                ico = QLabel()
                ico.setPixmap(get_pixmap(icon_name, QSize(18, 18), c["text_secondary"]))
                hdr.addWidget(ico)
            lbl = QLabel(title)
            lbl.setFont(theme_manager.get_font(t.FONT_SIZE_LG, bold=True))
            lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
            hdr.addWidget(lbl)
            hdr.addStretch()
            container = QWidget()
            container.setStyleSheet("background: transparent;")
            container.setLayout(hdr)
            layout.addWidget(container)

    def add_widget(self, w: QWidget): self.layout().addWidget(w)
    def add_layout(self, l): self.layout().addLayout(l)


# ===================================================================== ModernInput
class ModernInput(QLineEdit):
    """Input padronizado com estilo consistente em toda a aplicação."""

    def __init__(self, placeholder: str = "", label: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._placeholder = placeholder
        self._label = label
        self._has_error = False
        self._apply_style()

    def _apply_style(self):
        c = theme_manager.colors
        t = theme_manager.tokens
        border = c["error"] if self._has_error else c["border_subtle"]
        focus_border = c["error"] if self._has_error else c["brand"]
        self.setPlaceholderText(self._placeholder)
        self.setMinimumHeight(44)
        self.setFont(theme_manager.get_font(t.FONT_SIZE_MD))
        self.setStyleSheet(f"""
        QLineEdit {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1.5px solid {border};
            border-radius: {t.RADIUS_LG}px;
            padding: {t.SPACING_SM}px {t.SPACING_MD}px;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:focus {{
            border-color: {focus_border};
            background-color: {c['bg_elevated']};
        }}
        QLineEdit:hover {{ border-color: {c['border_default']}; }}
        QLineEdit:disabled {{
            background-color: {c['bg_secondary']};
            color: {c['text_disabled']};
            border-color: {c['border_subtle']};
        }}
        """)

    def set_error(self, has_error: bool):
        self._has_error = has_error
        self._apply_style()


# ===================================================================== ModernTable
class ModernTable(QTableWidget):
    """Tabela com estilo consistente do tema Aurora."""

    def __init__(self, parent=None, columns: int = 0):
        super().__init__(parent)
        if columns > 0:
            self.setColumnCount(columns)
        c = theme_manager.colors
        t = theme_manager.tokens

        self.setStyleSheet(f"""
        QTableWidget {{
            background-color: {c['bg_secondary']};
            alternate-background-color: {c['bg_primary']};
            gridline-color: {c['border_subtle']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_MD}px;
            font-size: {t.FONT_SIZE_MD}px;
            selection-background-color: {c['brand']};
            selection-color: #FFFFFF;
        }}
        QTableWidget::item {{
            padding: 8px 12px;
            border: none;
            color: {c['text_primary']};
        }}
        QTableWidget::item:selected {{
            background-color: {c['brand_soft']};
            color: {c['text_primary']};
        }}
        QTableWidget::item:hover {{ background-color: {c['bg_overlay']}; }}
        QHeaderView::section {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            padding: 10px 12px;
            border: none;
            border-bottom: 2px solid {c['border_default']};
            font-weight: 700;
            font-size: {t.FONT_SIZE_SM}px;
        }}
        QHeaderView::section:hover {{ background-color: {c['bg_overlay']}; }}
        QScrollBar:vertical {{
            background-color: {c['bg_secondary']};
            width: 10px;
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {c['border_default']};
            border-radius: 5px;
        }}
        QScrollBar::handle:vertical:hover {{ background-color: {c['text_tertiary']}; }}
        """)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)


# ===================================================================== ModernComboBox
class ModernComboBox(QComboBox):
    """ComboBox padronizado com estilo consistente em toda a aplicação."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens

        self.setMinimumHeight(42)
        self.setStyleSheet(f"""
        QComboBox {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1.5px solid {c['border_subtle']};
            border-radius: {t.RADIUS_MD}px;
            padding: {t.SPACING_SM}px {t.SPACING_MD}px;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QComboBox:hover {{ border-color: {c['border_default']}; }}
        QComboBox:focus {{
            border-color: {c['brand']};
            background-color: {c['bg_elevated']};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c['text_secondary']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_MD}px;
            selection-background-color: {c['brand_soft']};
            selection-color: {c['text_primary']};
            padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: {t.RADIUS_SM}px;
        }}
        QComboBox QAbstractItemView::item:hover {{ background-color: {c['bg_overlay']}; }}
        QComboBox:disabled {{
            background-color: {c['bg_secondary']};
            color: {c['text_disabled']};
            border-color: {c['border_subtle']};
        }}
        """)


# ===================================================================== ModernSidebar
class ModernSidebar(QFrame):
    """Sidebar 240px/64px collapsível com animação suave."""

    navigation_requested = Signal(str)
    collapse_toggled = Signal(bool)  # True = collapsed

    EXPANDED_W = 240
    COLLAPSED_W = 64

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._menu_items: List[dict] = []
        self._active_item: Optional[str] = None
        self._collapsed = False
        self._bottom_widgets: List[QWidget] = []
        self._setup()

    def _setup(self):
        c = theme_manager.colors
        t = theme_manager.tokens
        self.setFixedWidth(self.EXPANDED_W)
        self.setObjectName("sidebar")
        self.setStyleSheet(f"""
        QFrame#sidebar {{
            background-color: {c['sidebar_bg']};
            border-right: 1px solid {c['sidebar_border']};
        }}
        """)

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self.setLayout(self._main_layout)

        # Header: logo oficial (circular como no login)
        self._header = QFrame()
        self._header.setMinimumHeight(72)
        self._header.setStyleSheet(f"""
        QFrame {{ background: transparent; border-bottom: 1px solid {c['sidebar_border']}; }}
        """)
        hl = QHBoxLayout()
        hl.setContentsMargins(20, 0, 20, 0)
        hl.setSpacing(12)
        self._header.setLayout(hl)

        # Logo circular oficial (igual ao login)
        self._logo = QLabel()
        self._logo.setFixedSize(40, 40)
        self._logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = str(settings.resource_path("assets/logo_cw.jpg"))
        pix = _fazer_pixmap_circular(logo_path, 40)
        if pix is not None:
            self._logo.setPixmap(pix)
        else:
            self._logo.setText("CW")
            self._logo.setFont(theme_manager.get_font(t.FONT_SIZE_LG, bold=True))
            self._logo.setStyleSheet(f"""
            QLabel {{ background: {c['brand']}; color: #FFF; border-radius: 20px; }}
            """)
        hl.addWidget(self._logo)

        # Brand name com estilo premium
        self._brand_label = QLabel("CW Transportadora")
        self._brand_label.setFont(theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        self._brand_label.setStyleSheet(f"""
        color: {c['sidebar_text']}; background: transparent; 
        letter-spacing: 0.3px; font-weight: 600;
        """)
        hl.addWidget(self._brand_label)
        hl.addStretch()

        # Collapse toggle button
        self._toggle_btn = QPushButton()
        self._toggle_btn.setFixedSize(32, 32)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setIcon(get_icon("menu", QSize(18, 18), c["sidebar_text_muted"]))
        self._toggle_btn.setIconSize(QSize(18, 18))
        self._toggle_btn.setStyleSheet(f"""
        QPushButton {{ background: transparent; border: none; border-radius: 8px; }}
        QPushButton:hover {{ background: {c['sidebar_hover']}; }}
        """)
        self._toggle_btn.clicked.connect(self.toggle_collapse)
        hl.addWidget(self._toggle_btn)

        self._main_layout.addWidget(self._header)

        # User card area
        self._user_card_container = QWidget()
        self._user_card_container.setStyleSheet("background: transparent;")
        self._user_card_layout = QVBoxLayout()
        self._user_card_layout.setContentsMargins(0, 0, 0, 0)
        self._user_card_layout.setSpacing(0)
        self._user_card_container.setLayout(self._user_card_layout)
        self._main_layout.addWidget(self._user_card_container)

        # Scroll area for menu
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 6px; margin: 4px 1px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 3px; min-height: 30px; }}
        QScrollBar::handle:vertical:hover {{ background: {c['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0; }}
        """)

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet("background: transparent;")
        self._scroll_layout = QVBoxLayout()
        self._scroll_layout.setContentsMargins(8, 8, 8, 8)
        self._scroll_layout.setSpacing(2)
        self._scroll_content.setLayout(self._scroll_layout)
        scroll.setWidget(self._scroll_content)
        self._main_layout.addWidget(scroll, 1)

        # Bottom area
        self._bottom_container = QWidget()
        self._bottom_container.setStyleSheet("background: transparent;")
        self._bottom_layout = QVBoxLayout()
        self._bottom_layout.setContentsMargins(8, 4, 8, 8)
        self._bottom_layout.setSpacing(4)
        self._bottom_container.setLayout(self._bottom_layout)
        self._main_layout.addWidget(self._bottom_container)

    def add_user_card(self, name: str, role: str, usuario_id: Optional[int] = None):
        """Avatar com foto real + nome + cargo no topo."""
        c = theme_manager.colors
        t = theme_manager.tokens
        card = QFrame()
        card.setObjectName("userCard")
        card.setStyleSheet(f"""
        QFrame#userCard {{
            background: transparent;
            border-bottom: 1px solid {c['sidebar_border']};
        }}
        """)
        card.setFixedHeight(56)
        hl = QHBoxLayout()
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(10)
        card.setLayout(hl)

        # AvatarWidget - mostra foto real se existir, senão iniciais
        self._avatar_widget = AvatarWidget(usuario_id=usuario_id, nome=name, tamanho=32, parent=self)
        hl.addWidget(self._avatar_widget)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(0)
        self._user_name_label = QLabel(name)
        self._user_name_label.setFont(theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        self._user_name_label.setStyleSheet(f"color: {c['sidebar_text']}; background: transparent;")
        info.addWidget(self._user_name_label)
        self._user_role_label = QLabel(role)
        self._user_role_label.setFont(theme_manager.get_font(t.FONT_SIZE_XS))
        self._user_role_label.setStyleSheet(f"color: {c['sidebar_text_muted']}; background: transparent;")
        info.addWidget(self._user_role_label)
        hl.addLayout(info)
        hl.addStretch()

        self._user_card = card
        self._user_card_layout.addWidget(card)

    def add_section(self, title: str):
        c = theme_manager.colors
        t = theme_manager.tokens
        if self._scroll_layout.count() > 0:
            self._scroll_layout.addSpacing(12)
        lbl = QLabel(title.upper())
        lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        lbl.setObjectName("sectionLabel")
        lbl.setStyleSheet(f"""
        QLabel {{
            color: {c['sidebar_text_muted']}; padding: 6px 10px 2px;
            background: transparent; letter-spacing: 1.5px;
        }}
        """)
        self._section_labels.append(lbl) if hasattr(self, '_section_labels') else None
        self._scroll_layout.addWidget(lbl)

    def add_menu_item(self, name: str, label: str, icon_name: str,
                      accent_color: AccentColor = AccentColor.AURORA):
        c = theme_manager.colors
        t = theme_manager.tokens
        accent = theme_manager.get_accent(accent_color)

        row = QFrame()
        row.setMinimumHeight(36)
        row.setStyleSheet("QFrame { background: transparent; border: none; }")
        rl = QHBoxLayout()
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        row.setLayout(rl)

        # Active indicator bar
        indicator = QLabel()
        indicator.setFixedWidth(3)
        indicator.setStyleSheet("background: transparent; border-radius: 2px;")
        rl.addWidget(indicator)

        btn = QPushButton("  " + label)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(36)
        btn.setIcon(get_icon(icon_name, color=c["sidebar_text"]))
        btn.setIconSize(QSize(18, 18))
        btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent; color: {c['sidebar_text']};
            border: none; border-radius: {t.RADIUS_MD}px;
            padding: 6px 10px; text-align: left;
            font-size: {t.FONT_SIZE_MD}px; font-weight: 500;
        }}
        QPushButton:hover {{ background: {c['sidebar_hover']}; }}
        """)
        btn._cw_name = name
        btn._cw_accent = accent
        btn._cw_indicator = indicator
        btn._cw_icon_name = icon_name
        btn._cw_label = label
        btn.clicked.connect(lambda: self._on_click(name))
        rl.addWidget(btn, 1)

        self._menu_items.append({"name": name, "button": btn, "row": row, "indicator": indicator})
        self._scroll_layout.addWidget(row)

    def _on_click(self, name: str):
        self._active_item = name
        self._update_active()
        self.navigation_requested.emit(name)

    def _update_active(self):
        c = theme_manager.colors
        t = theme_manager.tokens
        for item in self._menu_items:
            btn = item["button"]
            ind = item["indicator"]
            accent = btn._cw_accent
            icon_name = btn._cw_icon_name
            if item["name"] == self._active_item:
                ind.setStyleSheet(f"background: {accent}; border-radius: 2px; margin: 4px 0;")
                btn.setStyleSheet(f"""
                QPushButton {{
                    background: {c['sidebar_active_bg']}; color: {c['text_primary']};
                    border: none; border-radius: {t.RADIUS_MD}px;
                    padding: 6px 10px; text-align: left;
                    font-size: {t.FONT_SIZE_MD}px; font-weight: 700;
                }}
                """)
                btn.setIcon(get_icon(icon_name, color=accent))
            else:
                ind.setStyleSheet("background: transparent;")
                btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; color: {c['sidebar_text']};
                    border: none; border-radius: {t.RADIUS_MD}px;
                    padding: 6px 10px; text-align: left;
                    font-size: {t.FONT_SIZE_MD}px; font-weight: 500;
                }}
                QPushButton:hover {{ background: {c['sidebar_hover']}; }}
                """)
                btn.setIcon(get_icon(icon_name, color=c["sidebar_text"]))

    def set_active_item(self, name: str):
        self._active_item = name
        self._update_active()

    def add_spacer(self): self._scroll_layout.addStretch()

    def add_bottom_widget(self, widget: QWidget):
        self._bottom_layout.addWidget(widget)

    def toggle_collapse(self):
        self._collapsed = not self._collapsed
        target_w = self.COLLAPSED_W if self._collapsed else self.EXPANDED_W
        anim = QPropertyAnimation(self, b"minimumWidth")
        anim.setDuration(200)
        anim.setStartValue(self.width())
        anim.setEndValue(target_w)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()
        self._anim = anim  # prevent GC

        # Show/hide text elements
        show = not self._collapsed
        self._brand_label.setVisible(show)
        if hasattr(self, '_user_name_label'):
            self._user_name_label.setVisible(show)
        if hasattr(self, '_user_role_label'):
            self._user_role_label.setVisible(show)
        for item in self._menu_items:
            btn = item["button"]
            if show:
                btn.setText("  " + btn._cw_label)
            else:
                btn.setText("")
        # Section labels
        for i in range(self._scroll_layout.count()):
            w = self._scroll_layout.itemAt(i).widget()
            if w and w.objectName() == "sectionLabel":
                w.setVisible(show)

        self.collapse_toggled.emit(self._collapsed)


# ===================================================================== TopBar
class TopBar(QFrame):
    """Barra superior 48px: breadcrumb + search + bell + avatar dropdown."""

    profile_requested = Signal()
    settings_requested = Signal()
    password_requested = Signal()
    logout_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens
        self.setMinimumHeight(48)
        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_secondary']};
            border-bottom: 1px solid {c['header_border']};
        }}
        """)

        hl = QHBoxLayout()
        hl.setContentsMargins(t.SPACING_XL, 0, t.SPACING_LG, 0)
        hl.setSpacing(t.SPACING_MD)
        self.setLayout(hl)

        # Breadcrumb
        self._breadcrumb = QLabel("")
        self._breadcrumb.setFont(theme_manager.get_font(t.FONT_SIZE_SM))
        self._breadcrumb.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        hl.addWidget(self._breadcrumb)
        hl.addStretch()

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar...")
        self._search.setFixedWidth(200)
        self._search.setFixedHeight(32)
        self._search.setStyleSheet(f"""
        QLineEdit {{
            background: {c['bg_tertiary']}; color: {c['text_primary']};
            border: 1px solid {c['border_subtle']}; border-radius: {t.RADIUS_MD}px;
            padding: 4px 12px; font-size: {t.FONT_SIZE_SM}px;
        }}
        QLineEdit:focus {{ border-color: {c['brand']}; }}
        """)
        hl.addWidget(self._search)

        # Bell
        bell_btn = QPushButton()
        bell_btn.setFixedSize(32, 32)
        bell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bell_btn.setIcon(get_icon("bell", QSize(18, 18), c["text_secondary"]))
        bell_btn.setIconSize(QSize(18, 18))
        bell_btn.setStyleSheet(f"""
        QPushButton {{ background: transparent; border: none; border-radius: 6px; }}
        QPushButton:hover {{ background: {c['bg_tertiary']}; }}
        """)
        hl.addWidget(bell_btn)

        # Avatar button (opens dropdown)
        self._avatar_btn = QPushButton()
        self._avatar_btn.setFixedSize(32, 32)
        self._avatar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._avatar_btn.setText("U")
        self._avatar_btn.setFont(theme_manager.get_font(t.FONT_SIZE_SM, bold=True))
        self._avatar_btn.setStyleSheet(f"""
        QPushButton {{
            background: {c['brand']}; color: #FFF; border: none; border-radius: 16px;
        }}
        QPushButton:hover {{ background: {c['brand_hover']}; }}
        """)
        hl.addWidget(self._avatar_btn)

        # Name label
        self._name_label = QLabel("")
        self._name_label.setFont(theme_manager.get_font(t.FONT_SIZE_SM))
        self._name_label.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        hl.addWidget(self._name_label)

        # Dropdown menu
        self._menu = QFrame()
        self._menu.setFixedWidth(200)
        self._menu.setStyleSheet(f"""
        QFrame {{
            background: {c['bg_elevated']}; border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_MD}px;
        }}
        """)
        ml = QVBoxLayout()
        ml.setContentsMargins(4, 4, 4, 4)
        ml.setSpacing(2)
        self._menu.setLayout(ml)
        self._menu.setVisible(False)

        menu_items = [
            ("Meu Perfil", "user", self.profile_requested),
            ("Configurações", "settings", self.settings_requested),
            ("Alterar Senha", "lock", self.password_requested),
        ]
        for text, icon, sig in menu_items:
            btn = QPushButton(f"  {text}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(36)
            btn.setIcon(get_icon(icon, QSize(16, 16), c["text_secondary"]))
            btn.setIconSize(QSize(16, 16))
            btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {c['text_primary']};
                border: none; border-radius: {t.RADIUS_SM}px;
                padding: 6px 12px; text-align: left; font-size: {t.FONT_SIZE_SM}px;
            }}
            QPushButton:hover {{ background: {c['bg_overlay']}; }}
            """)
            btn.clicked.connect(lambda: self._menu.setVisible(False))
            btn.clicked.connect(sig.emit)
            ml.addWidget(btn)

        # Separator
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {c['border_subtle']}; border: none;")
        ml.addWidget(sep)

        # Logout
        logout_btn = QPushButton("  Sair")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setFixedHeight(36)
        logout_btn.setIcon(get_icon("logout", QSize(16, 16), c["error"]))
        logout_btn.setIconSize(QSize(16, 16))
        logout_btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent; color: {c['error']};
            border: none; border-radius: {t.RADIUS_SM}px;
            padding: 6px 12px; text-align: left; font-size: {t.FONT_SIZE_SM}px;
        }}
        QPushButton:hover {{ background: {c['error_soft']}; }}
        """)
        logout_btn.clicked.connect(lambda: self._menu.setVisible(False))
        logout_btn.clicked.connect(self.logout_requested.emit)
        ml.addWidget(logout_btn)

        self._avatar_btn.clicked.connect(self._toggle_menu)

    def _toggle_menu(self):
        if self._menu.isVisible():
            self._menu.setVisible(False)
        else:
            # Position below avatar button
            pos = self._avatar_btn.mapToGlobal(self._avatar_btn.rect().bottomLeft())
            pos.setY(pos.y() + 4)
            pos.setX(pos.x() - self._menu.width() + self._avatar_btn.width())
            self._menu.move(pos)
            self._menu.raise_()
            self._menu.setVisible(True)

    def set_breadcrumb(self, section: str, page: str):
        c = theme_manager.colors
        self._breadcrumb.setText(f'{section}  /  {page}')

    def set_user_info(self, name: str, avatar_letter: str = "U"):
        self._name_label.setText(name)
        self._avatar_btn.setText(avatar_letter)


# ===================================================================== ModernInput
class ModernInput(QLineEdit):
    """Input com label, borda 1px, focus glow, error state."""

    def __init__(self, placeholder: str = "", label: str = "", parent: Optional[QWidget] = None):
        super().__init__()
        c = theme_manager.colors
        t = theme_manager.tokens
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(40)
        self.setFont(theme_manager.get_font(t.FONT_SIZE_MD))
        self.setStyleSheet(f"""
        QLineEdit {{
            background: {c['bg_tertiary']}; color: {c['text_primary']};
            border: 1px solid {c['border_default']}; border-radius: {t.RADIUS_MD}px;
            padding: 8px 14px;
        }}
        QLineEdit:hover {{ border-color: {c['border_strong']}; }}
        QLineEdit:focus {{ border: 1px solid {c['brand']}; background: {c['bg_secondary']}; }}
        QLineEdit:disabled {{ background: {c['bg_secondary']}; color: {c['text_disabled']}; }}
        """)

    def set_error(self, has_error: bool):
        c = theme_manager.colors
        t = theme_manager.tokens
        if has_error:
            self.setStyleSheet(f"""
            QLineEdit {{
                background: {c['bg_tertiary']}; color: {c['text_primary']};
                border: 1px solid {c['error']}; border-radius: {t.RADIUS_MD}px; padding: 8px 14px;
            }}
            """)
        else:
            self.__init__()


# ===================================================================== ModernComboBox
class ModernComboBox(QComboBox):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens
        self.setMinimumHeight(40)
        self.setFont(theme_manager.get_font(t.FONT_SIZE_MD))
        self.setStyleSheet(f"""
        QComboBox {{
            background: {c['bg_tertiary']}; color: {c['text_primary']};
            border: 1px solid {c['border_default']}; border-radius: {t.RADIUS_MD}px;
            padding: 8px 14px;
        }}
        QComboBox:hover {{ border-color: {c['border_strong']}; }}
        QComboBox:focus {{ border: 1px solid {c['brand']}; }}
        QComboBox::drop-down {{ border: none; width: 30px; }}
        QComboBox::down-arrow {{
            image: none; border-left: 5px solid transparent;
            border-right: 5px solid transparent; border-top: 5px solid {c['text_secondary']};
        }}
        QComboBox QAbstractItemView {{
            background: {c['bg_elevated']}; border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_MD}px; selection-background-color: {c['brand_soft']};
            selection-color: {c['text_primary']}; padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{ padding: 6px 10px; border-radius: 4px; }}
        QComboBox QAbstractItemView::item:hover {{ background: {c['bg_overlay']}; }}
        """)


# ===================================================================== KPICard (Stripe Style V3)
class KPICard(QFrame):
    """KPI premium estilo Stripe: ícone discreto, valor enorme, sparkline."""

    def __init__(self, label: str, value: str = "—", trend: str = "",
                 icon_name: str = "", accent: AccentColor = AccentColor.AURORA,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._label_text = label
        self._value_text = value
        self._accent = accent
        self._build(label, value, trend, icon_name)

    def _build(self, label, value, trend, icon_name):
        c = theme_manager.colors
        t = theme_manager.tokens
        accent = theme_manager.get_accent(self._accent)

        self.setObjectName("kpiCard")
        self.setMinimumHeight(120)

        # Background clean sem gradiente
        self.setStyleSheet(f"""
        QFrame#kpiCard {{
            background: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_LG}px;
        }}
        QFrame#kpiCard:hover {{
            border-color: {c['border_strong']};
            background: {c['card_hover']};
        }}
        """)

        # Sombra muito sutil
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 4))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_LG, t.SPACING_MD, t.SPACING_LG, t.SPACING_MD)
        layout.setSpacing(t.SPACING_XS)
        self.setLayout(layout)

        # Header: ícone pequeno + título
        header = QHBoxLayout()
        header.setSpacing(t.SPACING_SM)

        # Ícone pequeno em círculo discreto
        icon_container = QFrame()
        icon_container.setFixedSize(32, 32)
        icon_container.setStyleSheet(f"""
        QFrame {{
            background: {c['bg_tertiary']};
            border: 1px solid {c['border_subtle']};
            border-radius: 16px;
        }}
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon_name:
            icon_label.setPixmap(get_pixmap(icon_name, QSize(16, 16), c["text_secondary"]))
        else:
            icon_label.setText("📊")
            icon_label.setFont(theme_manager.get_font(14))
        icon_layout.addWidget(icon_label)
        header.addWidget(icon_container)

        # Título pequeno
        title = QLabel(label)
        title.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        title.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; letter-spacing: 0.5px;")
        header.addWidget(title)
        header.addStretch()

        layout.addLayout(header)

        # Valor ENORME
        val = QLabel(value)
        val.setFont(theme_manager.get_font(t.FONT_SIZE_4XL, bold=True))
        val.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        layout.addWidget(val)
        self._value_label = val

        # Trend + Sparkline
        bottom = QHBoxLayout()
        bottom.setSpacing(t.SPACING_MD)

        # Trend badge discreto
        if trend:
            is_positive = "↑" in trend or "+" in trend or trend.startswith("+")
            arrow = "↑" if is_positive else "↓"
            arrow_color = c["success"] if is_positive else c["error"]

            trend_label = QLabel(f"{arrow} {trend}")
            trend_label.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
            trend_label.setStyleSheet(f"""
            QLabel {{
                color: {arrow_color};
                background: {arrow_color}15;
                padding: 4px 8px;
                border-radius: 4px;
            }}
            """)
            bottom.addWidget(trend_label)
        else:
            bottom.addStretch()

        # Sparkline real (pontos conectados)
        sparkline = QFrame()
        sparkline.setMinimumHeight(24)
        sparkline.setStyleSheet("background: transparent;")
        sparkline_layout = QHBoxLayout(sparkline)
        sparkline_layout.setContentsMargins(0, 0, 0, 0)
        sparkline_layout.setSpacing(2)

        # Criar pontos do sparkline
        import random
        spark_points = [random.randint(2, 20) for _ in range(12)]
        for i, height in enumerate(spark_points):
            point = QFrame()
            point.setFixedWidth(3)
            point.setFixedHeight(height)
            point.setStyleSheet(f"""
            QFrame {{
                background: {accent}40;
                border-radius: 1px;
            }}
            """)
            sparkline_layout.addWidget(point)

        bottom.addWidget(sparkline, 1)
        layout.addLayout(bottom)

    def set_value(self, value: str):
        self._value_text = value
        if hasattr(self, '_value_label'):
            self._value_label.setText(value)

    def set_trend(self, trend: str, positive: Optional[bool] = None):
        """Atualiza o texto de tendência (ex.: '12,5% vs mês anterior')."""
        pass


# ===================================================================== Badge (Premium Style)
class Badge(QLabel):
    """Badge premium estilo Linear/Attio para status e categorias."""

    def __init__(self, text: str, variant: str = "default", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._variant = variant
        self._setup()

    def _setup(self):
        c = theme_manager.colors
        t = theme_manager.tokens

        variant_colors = {
            "default": (c["text_primary"], c["bg_tertiary"]),
            "success": (c["success"], c["success_soft"]),
            "warning": (c["warning"], c["warning_soft"]),
            "error": (c["error"], c["error_soft"]),
            "info": (c["info"], c["info_soft"]),
            "brand": (c["brand"], c["brand_soft"]),
        }

        fg, bg = variant_colors.get(self._variant, variant_colors["default"])

        self.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        self.setStyleSheet(f"""
        QLabel {{
            background-color: {bg};
            color: {fg};
            border-radius: {t.RADIUS_SM}px;
            padding: 4px 10px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}
        """)


# ===================================================================== Chip (Premium Style)
class Chip(QFrame):
    """Chip premium estilo Linear para seleções e filtros."""

    def __init__(self, text: str, selected: bool = False, closable: bool = False,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._text = text
        self._selected = selected
        self._closable = closable
        self._setup()

    def _setup(self):
        c = theme_manager.colors
        t = theme_manager.tokens

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()

        layout = QHBoxLayout()
        layout.setContentsMargins(t.SPACING_SM, t.SPACING_XS, t.SPACING_SM, t.SPACING_XS)
        layout.setSpacing(t.SPACING_XS)
        self.setLayout(layout)

        label = QLabel(self._text)
        label.setFont(theme_manager.get_font(t.FONT_SIZE_SM))
        label.setStyleSheet("background: transparent;")
        layout.addWidget(label)

        if self._closable:
            close_btn = QPushButton("×")
            close_btn.setFixedSize(16, 16)
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none; color: {c['text_secondary']};
                font-size: 14px; font-weight: bold;
            }}
            QPushButton:hover {{ color: {c['text_primary']}; }}
            """)
            layout.addWidget(close_btn)

    def _update_style(self):
        c = theme_manager.colors
        t = theme_manager.tokens

        if self._selected:
            self.setStyleSheet(f"""
            QFrame {{
                background-color: {c['brand']};
                border: 1px solid {c['brand']};
                border-radius: {t.RADIUS_MD}px;
            }}
            """)
        else:
            self.setStyleSheet(f"""
            QFrame {{
                background-color: {c['bg_tertiary']};
                border: 1px solid {c['border_default']};
                border-radius: {t.RADIUS_MD}px;
            }}
            QFrame:hover {{
                border-color: {c['border_strong']};
                background-color: {c['bg_overlay']};
            }}
            """)

    def set_selected(self, selected: bool):
        self._selected = selected
        self._update_style()

    def mousePressEvent(self, event):
        self.set_selected(not self._selected)
        super().mousePressEvent(event)


# ===================================================================== ProgressBar (Premium Style)
class ProgressBar(QFrame):
    """Barra de progresso premium estilo Linear."""

    def __init__(self, value: float = 0, max_value: float = 100,
                 color: str = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._value = value
        self._max_value = max_value
        self._color = color
        self._setup()

    def _setup(self):
        c = theme_manager.colors
        t = theme_manager.tokens
        bar_color = self._color or c["brand"]

        self.setMinimumHeight(8)
        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_tertiary']};
            border-radius: 4px;
        }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self._progress_bar = QFrame()
        self._update_progress()
        layout.addWidget(self._progress_bar)

    def _update_progress(self):
        c = theme_manager.colors
        bar_color = self._color or c["brand"]
        percentage = min(100, max(0, (self._value / self._max_value) * 100)) if self._max_value > 0 else 0

        self._progress_bar.setStyleSheet(f"""
        QFrame {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {bar_color}, stop:1 {bar_color}80);
            border-radius: 4px;
        }}
        """)
        self._progress_bar.setFixedWidth(int(self.width() * (percentage / 100)) if self.width() > 0 else 0)

    def set_value(self, value: float):
        self._value = value
        self._update_progress()

    def resizeEvent(self, event):
        self._update_progress()
        super().resizeEvent(event)


# ===================================================================== SummaryCard
class SummaryCard(QFrame):
    """Card resumo compacto com borda accent no topo."""

    def __init__(self, label: str, value: str = "—",
                 accent: AccentColor = AccentColor.AURORA, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens
        accent_color = theme_manager.get_accent(accent)
        self.setObjectName("summaryCard")
        self.setStyleSheet(f"""
        QFrame#summaryCard {{
            background: {c['card_bg']}; border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_LG}px; border-top: 3px solid {accent_color};
        }}
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_LG, t.SPACING_MD, t.SPACING_LG, t.SPACING_LG)
        layout.setSpacing(4)
        self.setLayout(layout)

        lbl = QLabel(label.upper())
        lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; letter-spacing: 1px;")
        layout.addWidget(lbl)

        self._value_lbl = QLabel(value)
        self._value_lbl.setFont(theme_manager.get_font(t.FONT_SIZE_2XL, bold=True))
        self._value_lbl.setStyleSheet(f"color: {accent_color}; background: transparent;")
        layout.addWidget(self._value_lbl)

    def set_value(self, value: str):
        if hasattr(self, "_value_lbl"):
            self._value_lbl.setText(value)


# ===================================================================== StatusBadge
class StatusBadge(QFrame):
    """Badge pill com dot indicador."""

    def __init__(self, text: str, status: str = "info", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._text = text
        self._status = status
        self._build()

    def _build(self):
        c = theme_manager.colors
        t = theme_manager.tokens
        sc = {
            "info": (c["info"], c["info_soft"]),
            "success": (c["success"], c["success_soft"]),
            "warning": (c["warning"], c["warning_soft"]),
            "error": (c["error"], c["error_soft"]),
        }
        tc, bg = sc.get(self._status, sc["info"])
        hl = QHBoxLayout()
        hl.setContentsMargins(10, 4, 10, 4)
        hl.setSpacing(6)
        self.setLayout(hl)
        dot = QLabel()
        dot.setFixedSize(6, 6)
        dot.setStyleSheet(f"background: {tc}; border-radius: 3px;")
        hl.addWidget(dot)
        lbl = QLabel(self._text)
        lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        lbl.setStyleSheet(f"color: {tc}; background: transparent;")
        hl.addWidget(lbl)
        self.setStyleSheet(f"QFrame {{ background: {bg}; border-radius: {t.RADIUS_FULL}px; }}")

    def setText(self, text: str):
        self._text = text
        for c in self.findChildren(QLabel):
            if c.text() != "" and c.text() != self._text:
                c.setText(text)
                break

    def set_status(self, status: str):
        self._status = status
        self._build()


# ===================================================================== SeparatorLine
class SeparatorLine(QFrame):
    def __init__(self, orientation: str = "horizontal", parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        b = c["border_subtle"]
        if orientation == "horizontal":
            self.setMinimumHeight(1)
            self.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 transparent, stop:0.15 {b}, stop:0.85 {b}, stop:1 transparent); border: none; }}
            """)
        else:
            self.setMinimumWidth(1)
            self.setStyleSheet(f"""
            QFrame {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 transparent, stop:0.15 {b}, stop:0.85 {b}, stop:1 transparent); border: none; }}
            """)


# ===================================================================== LoadingOverlay
class LoadingOverlay(QWidget):
    def __init__(self, parent: Optional[QWidget] = None, message: str = "Carregando..."):
        super().__init__(parent)
        self._message = message
        self._angle = 0
        self._opacity = 0.0
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 160);")
        self.setVisible(False)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._fade_timer = QTimer(self)
        self._fade_timer.timeout.connect(self._fade_step)

    def show_loading(self, message: str = None):
        if message: self._message = message
        self._opacity = 0.0
        self._angle = 0
        self.setVisible(True)
        self.raise_()
        self._timer.start(30)
        self._fade_timer.start(16)

    def hide_loading(self):
        self._timer.stop()
        self._fade_timer.stop()
        self.setVisible(False)

    def _fade_step(self):
        self._opacity = min(1.0, self._opacity + 0.08)
        if self._opacity >= 1.0: self._fade_timer.stop()
        self.update()

    def _animate(self):
        self._angle = (self._angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(0, 0, 0, int(160 * self._opacity)))
        cx, cy = self.width() // 2, self.height() // 2
        # Track
        pen = QPen(QColor(255, 255, 255, int(40 * self._opacity)))
        pen.setWidth(3)
        p.setPen(pen)
        r = 28
        p.drawEllipse(cx - r, cy - r - 20, r * 2, r * 2)
        # Arc
        c = theme_manager.colors
        brand = QColor(c["brand"])
        brand.setAlpha(int(255 * self._opacity))
        pen = QPen(brand)
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(cx - r, cy - r - 20, r * 2, r * 2, int(self._angle * 16), 120 * 16)
        # Text
        t = theme_manager.tokens
        p.setFont(theme_manager.get_font(t.FONT_SIZE_LG, bold=True))
        p.setPen(QColor(255, 255, 255, int(230 * self._opacity)))
        p.drawText(QRectF(cx - 150, cy + 20, 300, 40), Qt.AlignmentFlag.AlignCenter, self._message)
        p.end()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent(): self.setGeometry(self.parent().rect())


# ===================================================================== ToastNotification
class ToastNotification(QFrame):
    _instances: list = []

    def __init__(self, message: str, toast_type: str = "info",
                 duration: int = 3500, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._message = message
        self._toast_type = toast_type
        self._duration = duration
        ToastNotification._instances.append(self)
        self._build()
        self._show()

    def _build(self):
        c = theme_manager.colors
        t = theme_manager.tokens
        cfg = {
            "info": (c["info"], c["info_soft"], "i"),
            "success": (c["success"], c["success_soft"], "✓"),
            "warning": (c["warning"], c["warning_soft"], "!"),
            "error": (c["error"], c["error_soft"], "x"),
        }
        accent, bg, icon_char = cfg.get(self._toast_type, cfg["info"])
        self.setFixedWidth(360)
        self.setObjectName("toast")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setYOffset(6)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        hl = QHBoxLayout()
        hl.setContentsMargins(t.SPACING_LG, t.SPACING_MD, t.SPACING_LG, t.SPACING_MD)
        hl.setSpacing(t.SPACING_MD)
        self.setLayout(hl)

        # Icon circle
        ico = QFrame()
        ico.setFixedSize(28, 28)
        ico.setStyleSheet(f"background: {accent}; border-radius: 14px;")
        ico_l = QVBoxLayout()
        ico_l.setContentsMargins(0, 0, 0, 0)
        ico.setLayout(ico_l)
        lbl = QLabel(icon_char)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setFont(theme_manager.get_font(t.FONT_SIZE_XS, bold=True))
        lbl.setStyleSheet("color: #FFF; background: transparent;")
        ico_l.addWidget(lbl)
        hl.addWidget(ico)

        msg = QLabel(self._message)
        msg.setFont(theme_manager.get_font(t.FONT_SIZE_SM))
        msg.setWordWrap(True)
        msg.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        hl.addWidget(msg, 1)

        self.setStyleSheet(f"""
        QFrame#toast {{
            background: {c['card_bg']}; border: 1px solid {c['card_border']};
            border-left: 3px solid {accent}; border-radius: {t.RADIUS_LG}px;
        }}
        """)

    def _show(self):
        self.setVisible(True)
        self.raise_()
        if self.parent():
            base_y = 16 + (len(ToastNotification._instances) - 1) * 64
            self.move(self.parent().width() - self.width() - 16, base_y)
        QTimer.singleShot(self._duration, self._dismiss)

    def _dismiss(self):
        if self in ToastNotification._instances:
            ToastNotification._instances.remove(self)
        self.deleteLater()

    @staticmethod
    def show_toast(message: str, toast_type: str = "info",
                   parent: Optional[QWidget] = None, duration: int = 3500):
        return ToastNotification(message, toast_type, duration, parent)


# ===================================================================== PlaceholderScreen
class PlaceholderScreen(QWidget):
    def __init__(self, title: str, subtitle: str = "", icon_name: str = "settings",
                 accent: AccentColor = AccentColor.AURORA, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = theme_manager.colors
        t = theme_manager.tokens
        ac = theme_manager.get_accent(accent)
        ac_soft = theme_manager.get_color(f"{accent.value}_soft")

        root = QVBoxLayout()
        root.setContentsMargins(t.SPACING_2XL, t.SPACING_2XL, t.SPACING_2XL, t.SPACING_2XL)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(root)

        card = QFrame()
        card.setStyleSheet(f"""
        QFrame {{
            background: {c['card_bg']}; border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_XL}px;
        }}
        """)
        card.setMinimumSize(480, 320)
        cl = QVBoxLayout()
        cl.setContentsMargins(t.SPACING_3XL, t.SPACING_3XL, t.SPACING_3XL, t.SPACING_3XL)
        cl.setSpacing(t.SPACING_LG)
        cl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setLayout(cl)

        # Icon
        ico_wrap = QFrame()
        ico_wrap.setFixedSize(80, 80)
        ico_wrap.setStyleSheet(f"background: {ac_soft}; border-radius: 40px; border: 1px solid {ac};")
        ico_l = QVBoxLayout()
        ico_l.setContentsMargins(0, 0, 0, 0)
        ico_wrap.setLayout(ico_l)
        ico_lbl = QLabel()
        ico_lbl.setPixmap(get_pixmap(icon_name, QSize(40, 40), ac))
        ico_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ico_l.addWidget(ico_lbl)
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(ico_wrap)
        row.addStretch()
        cl.addLayout(row)

        tl = QLabel(title)
        tl.setFont(theme_manager.get_font(t.FONT_SIZE_3XL, bold=True))
        tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        cl.addWidget(tl)

        if subtitle:
            sl = QLabel(subtitle)
            sl.setFont(theme_manager.get_font(t.FONT_SIZE_LG))
            sl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.setWordWrap(True)
            sl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            cl.addWidget(sl)

        root.addWidget(card)
