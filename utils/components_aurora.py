"""
Aurora Components v1.0 - CW Transportadora
Componentes UI premium com Aurora Design System

Design principles:
- Glassmorphism com bordas ultra-finas
- Gradientes coloridos em vez de cores sólidas
- Sombras coloridas (glow effects)
- Cantos arredondados agressivos
- Animações fluidas
- Micro-interações refinadas
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QPushButton,
    QLabel, QLineEdit, QTextEdit, QComboBox, QScrollArea,
    QSizePolicy, QGridLayout, QSpacerItem, QGraphicsDropShadowEffect,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QProgressBar, QSlider, QCheckBox, QRadioButton
)
from PySide6.QtCore import (
    Qt, Signal, QPropertyAnimation, QEasingCurve, QSize,
    QTimer, QRectF, QParallelAnimationGroup, QPoint
)
from PySide6.QtGui import (
    QFont, QColor, QPainter, QPaintEvent, QPen, QLinearGradient,
    QRadialGradient, QBrush, QPainterPath
)
from typing import Optional, List, Callable
from enum import Enum

from telas.theme_aurora import aurora_theme_manager, ThemeTokens, AccentColor
from utils.icons import get_icon, get_pixmap
from utils.branding import load_official_logo_pixmap


# ===================================================================== Enums
class ButtonStyle(Enum):
    AURORA = "aurora"         # Primary gradient
    OCEAN = "ocean"           # Secondary gradient
    SUNSET = "sunset"         # Warm gradient
    FOREST = "forest"         # Success gradient
    GHOST = "ghost"           # Transparent
    OUTLINE = "outline"       # Border only
    GLASS = "glass"           # Glassmorphism

class ButtonSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"
    XL = "xl"


class CardVariant(Enum):
    DEFAULT = "default"
    GLASS = "glass"
    GLOW = "glow"
    BORDERED = "bordered"


# ===================================================================== AuroraButton - Botões com gradientes
class AuroraButton(QPushButton):
    def __init__(self, text: str, style: ButtonStyle = ButtonStyle.AURORA,
                 icon_name: Optional[str] = None, size: ButtonSize = ButtonSize.MD,
                 parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._style = style
        self._size = size
        self._apply(icon_name)

    def _apply(self, icon_name=None):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        sizes = {
            ButtonSize.SM: (36, 14, 18, t.FONT_SIZE_SM),
            ButtonSize.MD: (44, 18, 24, t.FONT_SIZE_MD),
            ButtonSize.LG: (52, 20, 28, t.FONT_SIZE_LG),
            ButtonSize.XL: (60, 24, 32, t.FONT_SIZE_XL),
        }
        h, px, py, fs = sizes[self._size]
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(h)
        self.setFont(aurora_cw_theme.get_font(fs, bold=True))

        if icon_name:
            self.setIcon(get_icon(icon_name, QSize(24, 24)))
            self.setIconSize(QSize(24, 24))

        # Gradient styles
        gradient_map = {
            ButtonStyle.AURORA: (c['aurora_start'], c['aurora_end'], c['aurora_hover'], c['aurora_active']),
            ButtonStyle.OCEAN: (c['ocean_start'], c['ocean_end'], c['ocean_hover'], c['ocean_active']),
            ButtonStyle.SUNSET: (c['sunset_start'], c['sunset_end'], c['sunset_hover'], c['sunset_active']),
            ButtonStyle.FOREST: (c['forest_start'], c['forest_end'], c['forest_hover'], c['forest_active']),
        }

        if self._style in gradient_map:
            start, end, hover, active = gradient_map[self._style]
            self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {start}, stop:1 {end});
                color: #FFFFFF;
                border: none;
                border-radius: {t.RADIUS_LG}px;
                padding: {py}px {px}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {hover}, stop:1 {end});
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {active}, stop:1 {start});
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background: {c['bg_tertiary']};
                color: {c['text_disabled']};
            }}
            """)
        elif self._style == ButtonStyle.GHOST:
            self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c['text_secondary']};
                border: none;
                border-radius: {t.RADIUS_LG}px;
                padding: {py}px {px}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: {c['bg_overlay']};
                color: {c['text_primary']};
            }}
            QPushButton:pressed {{
                background: {c['bg_tertiary']};
            }}
            """)
        elif self._style == ButtonStyle.OUTLINE:
            self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c['aurora']};
                border: 1.5px solid {c['border_default']};
                border-radius: {t.RADIUS_LG}px;
                padding: {py}px {px}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {c['aurora_soft']};
                border-color: {c['aurora']};
            }}
            QPushButton:pressed {{
                background: {c['aurora']};
                color: #FFFFFF;
            }}
            """)
        elif self._style == ButtonStyle.GLASS:
            self.setStyleSheet(f"""
            QPushButton {{
                background: {c['bg_glass']};
                color: {c['text_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {t.RADIUS_LG}px;
                padding: {py}px {px}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {c['bg_elevated']};
                border-color: {c['border_strong']};
            }}
            QPushButton:pressed {{
                background: {c['bg_overlay']};
            }}
            """)


# ===================================================================== AuroraCard - Cards com glassmorphism
class AuroraCard(QFrame):
    def __init__(self, title: Optional[str] = None, icon_name: Optional[str] = None,
                 variant: CardVariant = CardVariant.DEFAULT, padding: int = None,
                 accent_color: AccentColor = AccentColor.AURORA,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._variant = variant
        self._accent = accent_color
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        pad = padding or t.SPACING_XL

        self.setObjectName("auroraCard")
        
        # Card styles based on variant
        if variant == CardVariant.GLASS:
            self.setStyleSheet(f"""
            QFrame#auroraCard {{
                background: {c['bg_glass']};
                border: 1px solid {c['border_subtle']};
                border-radius: {t.RADIUS_2XL}px;
            }}
            QFrame#auroraCard:hover {{
                border-color: {c['border_default']};
                background: {c['bg_elevated']};
            }}
            """)
        elif variant == CardVariant.GLOW:
            accent = aurora_theme_manager.get_accent(accent_color)
            self.setStyleSheet(f"""
            QFrame#auroraCard {{
                background: {c['card_bg']};
                border: 1px solid {c['border_subtle']};
                border-radius: {t.RADIUS_2XL}px;
            }}
            QFrame#auroraCard:hover {{
                border-color: {accent};
                background: {c['bg_surface']};
            }}
            """)
        elif variant == CardVariant.BORDERED:
            self.setStyleSheet(f"""
            QFrame#auroraCard {{
                background: {c['card_bg']};
                border: 1.5px solid {c['border_default']};
                border-radius: {t.RADIUS_2XL}px;
            }}
            QFrame#auroraCard:hover {{
                border-color: {c['border_strong']};
                background: {c['bg_surface']};
            }}
            """)
        else:  # DEFAULT
            self.setStyleSheet(f"""
            QFrame#auroraCard {{
                background: {c['card_bg']};
                border: 1px solid {c['border_subtle']};
                border-radius: {t.RADIUS_2XL}px;
            }}
            QFrame#auroraCard:hover {{
                border-color: {c['border_default']};
                background: {c['bg_surface']};
            }}
            """)

        layout = QVBoxLayout()
        layout.setContentsMargins(pad, pad, pad, pad)
        layout.setSpacing(t.SPACING_LG)
        self.setLayout(layout)

        if title:
            hdr = QHBoxLayout()
            hdr.setSpacing(t.SPACING_MD)
            if icon_name:
                ico = QLabel()
                accent = aurora_theme_manager.get_accent(accent_color)
                ico.setPixmap(get_pixmap(icon_name, QSize(28, 28), accent))
                hdr.addWidget(ico)
            lbl = QLabel(title)
            lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_LG, bold=True))
            lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
            hdr.addWidget(lbl)
            hdr.addStretch()
            w = QWidget()
            w.setStyleSheet("background: transparent;")
            w.setLayout(hdr)
            layout.addWidget(w)

    def add_widget(self, w): self.layout().addWidget(w)
    def add_layout(self, l): self.layout().addLayout(l)


# ===================================================================== AuroraSidebar - Sidebar minimalista com gradientes
class AuroraSidebar(QFrame):
    navigation_requested = Signal(str)
    collapse_toggled = Signal(bool)

    EXPANDED_W = 240
    COLLAPSED_W = 64

    def __init__(self, parent=None):
        super().__init__(parent)
        self._menu_items = []
        self._active_item = None
        self._collapsed = False
        self._setup()

    def _setup(self):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        self.setFixedWidth(self.EXPANDED_W)
        self.setObjectName("auroraSidebar")
        self.setStyleSheet(f"""
        QFrame#auroraSidebar {{
            background: {c['sidebar_bg']};
            border-right: 1px solid {c['sidebar_border']};
        }}
        """)

        self._main_layout = QVBoxLayout()
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(0)
        self.setLayout(self._main_layout)

        # Logo header premium com a marca oficial
        self._header = QFrame()
        self._header.setMinimumHeight(88)
        self._header.setStyleSheet(f"""
        QFrame {{
            background: {c['sidebar_bg']};
            border-bottom: 1px solid {c['sidebar_border']};
        }}
        """)
        hl = QHBoxLayout()
        hl.setContentsMargins(18, 12, 18, 12)
        hl.setSpacing(12)
        self._header.setLayout(hl)

        # Logo oficial da CW
        self._logo = QLabel()
        self._logo.setFixedSize(132, 56)
        self._logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._logo.setStyleSheet(f"""
        QLabel {{
            background: transparent;
            border: none;
        }}
        """)
        logo_pixmap = load_official_logo_pixmap(132, 56)
        if logo_pixmap is not None:
            self._logo.setPixmap(logo_pixmap)
        
        hl.addWidget(self._logo)

        hl.addStretch()

        self._toggle_btn = QPushButton()
        self._toggle_btn.setFixedSize(32, 32)
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setIcon(get_icon("menu", QSize(24, 24), c["text_tertiary"]))
        self._toggle_btn.setIconSize(QSize(24, 24))
        self._toggle_btn.setStyleSheet(f"""
        QPushButton {{ background: transparent; border: none; border-radius: 8px; }}
        QPushButton:hover {{ background: {c['sidebar_hover']}; }}
        """)
        self._toggle_btn.clicked.connect(self.toggle_collapse)
        hl.addWidget(self._toggle_btn)

        self._main_layout.addWidget(self._header)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{ background: transparent; width: 4px; }}
        QScrollBar::handle:vertical {{ background: {c['border_default']}; border-radius: 2px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; height: 0; }}
        """)

        self._scroll_content = QWidget()
        self._scroll_content.setStyleSheet("background: transparent;")
        self._scroll_layout = QVBoxLayout()
        self._scroll_layout.setContentsMargins(12, 16, 12, 16)
        self._scroll_layout.setSpacing(2)
        self._scroll_content.setLayout(self._scroll_layout)
        scroll.setWidget(self._scroll_content)
        self._main_layout.addWidget(scroll, 1)

        # Bottom container
        self._bottom_container = QWidget()
        self._bottom_container.setStyleSheet("background: transparent;")
        self._bottom_layout = QVBoxLayout()
        self._bottom_layout.setContentsMargins(12, 0, 12, 16)
        self._bottom_layout.setSpacing(8)
        self._bottom_container.setLayout(self._bottom_layout)
        self._main_layout.addWidget(self._bottom_container)

    def add_user_card(self, name: str, role: str, avatar_letter: str = "U",
                      usuario_id: int = None, status: str = "online"):
        from utils.avatar import AvatarWidget, avatar_bus
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing

        sep = QFrame()
        sep.setMinimumHeight(1)
        sep.setStyleSheet(f"background: {c['border_subtle']}; border: none;")
        self._bottom_layout.addWidget(sep)

        card = QFrame()
        card.setMinimumHeight(72)
        card.setStyleSheet(f"""
        QFrame {{
            background: transparent;
            border-radius: {t.RADIUS_XL}px;
        }}
        QFrame:hover {{ background: {c['sidebar_hover']}; }}
        """)
        hl = QHBoxLayout()
        hl.setContentsMargins(16, 0, 16, 0)
        hl.setSpacing(16)
        card.setLayout(hl)

        # Avatar (aumentado)
        avatar_frame = QFrame()
        avatar_frame.setFixedSize(48, 48)
        avatar_frame.setStyleSheet("background: transparent;")
        self._sidebar_avatar = AvatarWidget(usuario_id=usuario_id, nome=name, tamanho=44)
        av_layout = QVBoxLayout()
        av_layout.setContentsMargins(2, 2, 2, 2)
        av_layout.addWidget(self._sidebar_avatar)
        avatar_frame.setLayout(av_layout)

        # Status dot
        status_colors = {"online": "#10B981", "ausente": "#F59E0B",
                         "ocupado": "#EF4444", "offline": "#6B7280"}
        self._sidebar_status_dot = QLabel()
        self._sidebar_status_dot.setFixedSize(14, 14)
        sc = status_colors.get(status, "#10B981")
        self._sidebar_status_dot.setStyleSheet(
            f"background: {sc}; border-radius: 7px; border: 2px solid {c['sidebar_bg']};"
        )
        self._sidebar_status_dot.setParent(card)
        hl.addWidget(avatar_frame)

        info = QVBoxLayout()
        info.setContentsMargins(0, 0, 0, 0)
        info.setSpacing(4)
        self._user_name_label = QLabel(name)
        self._user_name_label.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_MD, bold=True))
        self._user_name_label.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        info.addWidget(self._user_name_label)

        status_text = {"online": "Online", "ausente": "Ausente",
                       "ocupado": "Ocupado", "offline": "Offline"}
        self._user_role_label = QLabel(f"{status_text.get(status, 'Online')}  ·  {role}")
        self._user_role_label.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM))
        self._user_role_label.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        info.addWidget(self._user_role_label)
        hl.addLayout(info)
        hl.addStretch()

        self._bottom_layout.addWidget(card)

        # Position dot
        QTimer.singleShot(50, lambda: self._sidebar_status_dot.move(34, 34) if self._sidebar_status_dot else None)

    def add_section(self, title: str):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        if self._scroll_layout.count() > 0:
            self._scroll_layout.addSpacing(20)
        lbl = QLabel(title.upper())
        lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_XS, bold=True))
        lbl.setObjectName("sectionLabel")
        lbl.setStyleSheet(f"""
        QLabel {{
            color: {c['sidebar_text_muted']};
            padding: 4px 16px 4px;
            background: transparent;
            letter-spacing: 2px;
            font-size: 10px;
        }}
        """)
        self._scroll_layout.addWidget(lbl)

    def add_menu_item(self, name: str, label: str, icon_name: str,
                      accent_color: AccentColor = AccentColor.AURORA,
                      badge: str = "", shortcut: str = ""):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        accent = aurora_theme_manager.get_accent(accent_color)

        row = QFrame()
        row.setMinimumHeight(48)
        row.setStyleSheet("QFrame { background: transparent; }")
        rl = QHBoxLayout()
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        row.setLayout(rl)

        # Active indicator pill elegante estilo Linear (indicador vermelho)
        indicator = QLabel()
        indicator.setFixedWidth(3)
        indicator.setStyleSheet("background: transparent; border-radius: 2px;")
        rl.addWidget(indicator)

        btn = QPushButton("  " + label)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(48)
        btn.setIcon(get_icon(icon_name, color=c["sidebar_text"]))
        btn.setIconSize(QSize(24, 24))
        btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            color: {c['sidebar_text']};
            border: none;
            border-radius: {t.RADIUS_LG}px;
            padding: 12px 16px;
            text-align: left;
            font-size: {t.FONT_SIZE_MD}px;
            font-weight: 500;
            letter-spacing: -0.01em;
        }}
        QPushButton:hover {{
            background: {c['sidebar_hover']};
            color: {c['text_primary']};
        }}
        """)
        btn._cw_name = name
        btn._cw_accent = accent
        btn._cw_indicator = indicator
        btn._cw_icon_name = icon_name
        btn._cw_label = label
        btn._cw_accent_color = accent_color
        btn.clicked.connect(lambda: self._on_click(name))
        rl.addWidget(btn, 1)

        # Keyboard hint elegante
        if shortcut:
            hint = QLabel(shortcut)
            hint.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_XS))
            hint.setStyleSheet(f"""
                color: {c['text_tertiary']};
                background: {c['bg_tertiary']};
                border: 1px solid {c['border_subtle']};
                border-radius: 4px;
                padding: 2px 6px;
                letter-spacing: -0.01em;
            """)
            rl.addWidget(hint)
            rl.addSpacing(8)

        # Badge elegante estilo Linear
        self._badge_labels = getattr(self, '_badge_labels', {})
        if badge:
            badge_lbl = QLabel(str(badge))
            badge_lbl.setFixedSize(24, 20)
            badge_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_XS, bold=True))
            badge_lbl.setStyleSheet(f"""
            QLabel {{
                background: {accent}20;
                color: {accent};
                border: 1px solid {accent}40;
                border-radius: 10px;
                font-size: 10px;
                letter-spacing: -0.01em;
            }}
            """)
            rl.addWidget(badge_lbl)
            rl.addSpacing(8)
            self._badge_labels[name] = badge_lbl

        self._menu_items.append({"name": name, "button": btn, "row": row, "indicator": indicator, "accent_color": accent_color})
        self._scroll_layout.addWidget(row)

    def update_badge(self, name: str, value: str):
        self._badge_labels = getattr(self, '_badge_labels', {})
        lbl = self._badge_labels.get(name)
        if lbl:
            if value and value != "0":
                lbl.setText(str(value))
                lbl.setVisible(True)
            else:
                lbl.setVisible(False)

    def _on_click(self, name: str):
        self._active_item = name
        self._update_active()
        self.navigation_requested.emit(name)

    def _update_active(self):
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        for item in self._menu_items:
            btn = item["button"]
            ind = item["indicator"]
            accent = btn._cw_accent
            accent_color = item["accent_color"]
            icon_name = btn._cw_icon_name
            if item["name"] == self._active_item:
                # Active indicator pill elegante estilo Linear com cor vermelho CW
                ind.setStyleSheet(f"""
                background: {c['aurora']};
                border-radius: 2px;
                margin: 14px 0;
                """)
                btn.setStyleSheet(f"""
                QPushButton {{
                    background: {c['sidebar_active_bg']};
                    color: {c['aurora']};
                    border: none;
                    border-radius: {t.RADIUS_LG}px;
                    padding: 12px 16px;
                    text-align: left;
                    font-size: {t.FONT_SIZE_MD}px;
                    font-weight: 600;
                    letter-spacing: -0.01em;
                }}
                """)
                btn.setIcon(get_icon(icon_name, color=c["aurora"]))
            else:
                ind.setStyleSheet("background: transparent;")
                btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {c['sidebar_text']};
                    border: none;
                    border-radius: {t.RADIUS_LG}px;
                    padding: 12px 16px;
                    text-align: left;
                    font-size: {t.FONT_SIZE_MD}px;
                    font-weight: 500;
                    letter-spacing: -0.01em;
                }}
                QPushButton:hover {{
                    background: {c['sidebar_hover']};
                    color: {c['text_primary']};
                }}
                """)
                btn.setIcon(get_icon(icon_name, color=c["sidebar_text"]))

    def set_active_item(self, name: str):
        self._active_item = name
        self._update_active()

    def add_spacer(self): self._scroll_layout.addStretch()

    def add_bottom_widget(self, w): self._bottom_layout.addWidget(w)

    def toggle_collapse(self):
        self._collapsed = not self._collapsed
        target_w = self.COLLAPSED_W if self._collapsed else self.EXPANDED_W
        anim = QPropertyAnimation(self, b"minimumWidth")
        anim.setDuration(250)
        anim.setStartValue(self.width())
        anim.setEndValue(target_w)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._anim = anim

        show = not self._collapsed
        if hasattr(self, '_user_name_label'):
            self._user_name_label.setVisible(show)
        if hasattr(self, '_user_role_label'):
            self._user_role_label.setVisible(show)
        for item in self._menu_items:
            btn = item["button"]
            btn.setText("  " + btn._cw_label if show else "")
        for i in range(self._scroll_layout.count()):
            w = self._scroll_layout.itemAt(i).widget()
            if w and w.objectName() == "sectionLabel":
                w.setVisible(show)
        self.collapse_toggled.emit(self._collapsed)


# ===================================================================== AuroraTopBar - TopBar premium
class AuroraTopBar(QFrame):
    profile_requested = Signal()
    settings_requested = Signal()
    password_requested = Signal()
    logout_requested = Signal()
    search_requested = Signal(str)
    new_operation_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._usuario_id = None
        self._usuario_nome = ""
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        self.setMinimumHeight(56)  # Linear usa 56px para mais compact
        self.setObjectName("auroraTopBar")
        self.setStyleSheet(f"""
        QFrame#auroraTopBar {{
            background: {c['header_bg']};
            border-bottom: 1px solid {c['header_border']};
        }}
        """)

        hl = QHBoxLayout()
        hl.setContentsMargins(t.SPACING_XL, 0, t.SPACING_XL, 0)
        hl.setSpacing(t.SPACING_LG)
        self.setLayout(hl)

        # Breadcrumb elegante estilo Linear
        self._breadcrumb = QLabel("")
        self._breadcrumb.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_SM))
        self._breadcrumb.setStyleSheet(f"""
            color: {c['text_tertiary']};
            background: transparent;
            letter-spacing: -0.01em;
        """)
        hl.addWidget(self._breadcrumb)
        hl.addStretch()

        # Search bar refinada estilo Linear (maior)
        search_container = QFrame()
        search_container.setMinimumHeight(40)
        search_container.setMinimumWidth(320)
        search_container.setStyleSheet(f"""
        QFrame {{
            background: {c['bg_tertiary']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_LG}px;
        }}
        QFrame:hover {{ border-color: {c['border_default']}; }}
        QFrame:focus-within {{ border-color: {c['aurora']}; }}
        """)
        sl = QHBoxLayout()
        sl.setContentsMargins(14, 0, 14, 0)
        sl.setSpacing(10)
        search_container.setLayout(sl)

        search_icon = QLabel()
        search_icon.setPixmap(get_pixmap("search", QSize(24, 24), c["text_tertiary"]))
        search_icon.setStyleSheet("background: transparent;")
        sl.addWidget(search_icon)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar operações, clientes...")
        self._search.setFrame(False)
        self._search.setClearButtonEnabled(True)
        self._search.setToolTip("Digite o que deseja encontrar")
        self._search.setStyleSheet(f"""
        QLineEdit {{
            background: transparent;
            color: {c['text_primary']};
            border: none;
            font-size: {t.FONT_SIZE_MD}px;
            letter-spacing: -0.01em;
        }}
        QLineEdit::placeholder {{ color: {c['text_tertiary']}; }}
        """)
        sl.addWidget(self._search, 1)
        # Conectar tanto ao Enter quanto ao textChanged para busca dinâmica
        self._search.returnPressed.connect(
            lambda: self.search_requested.emit(self._search.text().strip())
        )
        self._search.textChanged.connect(self._on_search_changed)

        hint = QLabel("⌘K")
        hint.setStyleSheet(f"""
        QLabel {{
            background: {c['bg_overlay']};
            color: {c['text_tertiary']};
            border-radius: {t.RADIUS_SM}px;
            padding: 4px 8px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: -0.01em;
        }}
        """)
        sl.addWidget(hint)
        hl.addWidget(search_container)

        hl.addSpacing(12)

        # Botão Nova Operação útil
        add_btn = QPushButton("+ Nova Operação")
        add_btn.setMinimumHeight(40)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_SM, QFont.Weight.Bold))
        add_btn.setStyleSheet(f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_start']}, stop:1 {c['aurora_end']});
            color: #FFFFFF;
            border: none;
            border-radius: {t.RADIUS_LG}px;
            font-size: {t.FONT_SIZE_SM}px;
            font-weight: 600;
            padding: 0 16px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_hover']}, stop:1 {c['aurora_end']});
        }}
        QPushButton:pressed {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {c['aurora_active']}, stop:1 {c['aurora']});
        }}
        """)
        hl.addWidget(add_btn)
        add_btn.clicked.connect(self.new_operation_requested.emit)

        hl.addSpacing(8)

        # Sino com notification badge elegante
        bell_container = QFrame()
        bell_container.setFixedSize(36, 36)
        bell_container.setStyleSheet("background: transparent;")
        bell_layout = QVBoxLayout()
        bell_layout.setContentsMargins(0, 0, 0, 0)
        bell_container.setLayout(bell_layout)

        self._bell_btn = QPushButton()
        self._bell_btn.setFixedSize(36, 36)
        self._bell_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bell_btn.setIcon(get_icon("bell", QSize(24, 24), c["text_secondary"]))
        self._bell_btn.setIconSize(QSize(24, 24))
        self._bell_btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent;
            border: none;
            border-radius: 8px;
        }}
        QPushButton:hover {{ background: {c['bg_tertiary']}; }}
        """)
        bell_layout.addWidget(self._bell_btn)

        # Notification badge elegante
        notification_badge = QLabel()
        notification_badge.setFixedSize(8, 8)
        notification_badge.setStyleSheet(f"""
            background: {c['crimson']};
            border-radius: 4px;
            border: 2px solid {c['header_bg']};
        """)
        notification_badge.move(24, 6)
        notification_badge.setParent(bell_container)
        notification_badge.raise_()
        
        hl.addWidget(bell_container)

        hl.addSpacing(4)

        # Separador subtle
        sep = QFrame()
        sep.setFixedSize(1, 24)
        sep.setStyleSheet(f"background: {c['border_subtle']};")
        hl.addWidget(sep)

        hl.addSpacing(8)

        # Avatar com subtle status dot
        from utils.avatar import AvatarWidget, avatar_bus
        self._avatar_container = QFrame()
        self._avatar_container.setFixedSize(36, 36)
        self._avatar_container.setStyleSheet("background: transparent; border-radius: 10px;")
        self._avatar_container.setCursor(Qt.CursorShape.PointingHandCursor)
        avl = QVBoxLayout()
        avl.setContentsMargins(1, 1, 1, 1)
        self._avatar_container.setLayout(avl)
        self._avatar_w = AvatarWidget(usuario_id=None, nome="U", tamanho=34)
        avl.addWidget(self._avatar_w)
        self._avatar_container.mousePressEvent = lambda e: self._toggle_menu()
        hl.addWidget(self._avatar_container)

        # Status dot subtle estilo Linear
        self._status_dot = QLabel()
        self._status_dot.setFixedSize(10, 10)
        self._status_dot.setStyleSheet(f"background: #10B981; border-radius: 5px; border: 2px solid {c['header_bg']};")
        self._status_dot.setParent(self)
        self._status_dot.raise_()

        # Dropdown menu premium
        self._menu = QFrame()
        self._menu.setFixedWidth(240)
        self._menu.setObjectName("topbarMenu")
        self._menu.setStyleSheet(f"""
        QFrame#topbarMenu {{
            background: {c['bg_elevated']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_2XL}px;
        }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 100))
        self._menu.setGraphicsEffect(shadow)

        ml = QVBoxLayout()
        ml.setContentsMargins(8, 8, 8, 8)
        ml.setSpacing(2)
        self._menu.setLayout(ml)
        self._menu.setVisible(False)

        for text, icon, sig in [
            ("Meu Perfil", "user", self.profile_requested),
            ("Configurações", "settings", self.settings_requested),
            ("Alterar Senha", "lock", self.password_requested),
        ]:
            btn = QPushButton(f"  {text}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(42)
            btn.setIcon(get_icon(icon, QSize(24, 24), c["text_tertiary"]))
            btn.setIconSize(QSize(24, 24))
            btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {c['text_primary']};
                border: none; border-radius: {t.RADIUS_MD}px;
                padding: 8px 14px; text-align: left; font-size: {t.FONT_SIZE_SM}px;
            }}
            QPushButton:hover {{ background: {c['bg_overlay']}; }}
            """)
            btn.clicked.connect(lambda: self._menu.setVisible(False))
            btn.clicked.connect(sig.emit)
            ml.addWidget(btn)

        sep2 = QFrame()
        sep2.setMinimumHeight(1)
        sep2.setStyleSheet(f"background: {c['border_subtle']}; margin: 4px 10px;")
        ml.addWidget(sep2)

        logout_btn = QPushButton("  Sair do sistema")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.setMinimumHeight(42)
        logout_btn.setIcon(get_icon("logout", QSize(24, 24), c["crimson"]))
        logout_btn.setIconSize(QSize(24, 24))
        logout_btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent; color: {c['crimson']};
            border: none; border-radius: {t.RADIUS_MD}px;
            padding: 8px 14px; text-align: left; font-size: {t.FONT_SIZE_SM}px;
        }}
        QPushButton:hover {{ background: {c['crimson_soft']}; }}
        """)
        logout_btn.clicked.connect(lambda: self._menu.setVisible(False))
        logout_btn.clicked.connect(self.logout_requested.emit)
        ml.addWidget(logout_btn)

    def _toggle_menu(self):
        if self._menu.isVisible():
            self._menu.setVisible(False)
        else:
            pos = self._avatar_container.mapToGlobal(self._avatar_container.rect().bottomLeft())
            pos.setY(pos.y() + 8)
            pos.setX(pos.x() - self._menu.width() + self._avatar_container.width() + 100)
            self._menu.move(pos)
        self._avatar_w.update_user(usuario_id, name)
        try:
            avatar_bus.avatar_updated.disconnect(self._on_avatar_updated)
        except Exception:
            pass
        avatar_bus.avatar_updated.connect(self._on_avatar_updated)

    def _on_avatar_updated(self, uid: int):
        if uid == self._usuario_id:
            self._avatar_w.update_user(uid, self._usuario_nome)

    def _on_search_changed(self, text: str):
        """Handler para busca dinâmica em tempo real."""
        if len(text.strip()) >= 2:
            self.search_requested.emit(text.strip())

    def set_user_info(self, nome: str, avatar_letter: str, usuario_id: int = None):
        """Define informações do usuário."""
        self._usuario_nome = nome
        self._usuario_id = usuario_id

    def set_breadcrumb(self, section: str, page: str):
        """Define o breadcrumb estilo Linear."""
        self._breadcrumb.setText(f"{section} / {page}")

    def update_status_dot(self, status: str):
        colors = {"online": "#10B981", "ausente": "#F59E0B",
                  "ocupado": "#EF4444", "offline": "#6B7280"}
        cor = colors.get(status, "#10B981")
        c = aurora_cw_theme.colors
        self._status_dot.setStyleSheet(
            f"background: {cor}; border-radius: 6px; border: 2px solid {c['header_bg']};"
        )

    def resizeEvent(self, event):
        if hasattr(self, '_status_dot'):
            self._status_dot.move(self.width() - 50, 23)
        super().resizeEvent(event)


# ===================================================================== AuroraKPICard - KPI Card premium estilo Attio/Linear
class AuroraKPICard(QFrame):
    def __init__(self, title: str, value: str, change: str = None,
                 icon_name: str = None, accent_color: AccentColor = AccentColor.AURORA,
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        self._accent = accent_color
        self._sparkline_data = []

        self.setObjectName("kpiCard")
        accent = aurora_theme_manager.get_accent(accent_color)
        soft = aurora_theme_manager.get_color(accent_color.value + '_soft')

        # Premium card styling limpo e moderno - sem bordas grossas
        self.setStyleSheet(f"""
        QFrame#kpiCard {{
            background: {c['card_bg']};
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_XL}px;
        }}
        QFrame#kpiCard:hover {{
            border-color: {c['border_default']};
            background: {c['card_hover']};
        }}
        """)

        # Sombra premium mais sofisticada
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(20)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 60))
        self.setGraphicsEffect(self._shadow)

        # Enable hover events
        self.setMouseTracking(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        self.setLayout(layout)

        # Header com icon e title refinados
        hdr = QHBoxLayout()
        hdr.setSpacing(16)

        if icon_name:
            ico_container = QLabel()
            ico_container.setMinimumSize(48, 48)
            ico_container.setMaximumSize(48, 48)
            ico_container.setStyleSheet(f"""
            QLabel {{
                background: {accent}26;
                border-radius: 24px;
                border: none;
            }}
            """)
            ico_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

            ico = QLabel()
            ico.setMinimumSize(26, 26)
            ico.setMaximumSize(26, 26)
            ico.setPixmap(get_pixmap(icon_name, QSize(26, 26), accent))
            ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ico.setStyleSheet("background: transparent;")

            ico_layout = QVBoxLayout()
            ico_layout.setContentsMargins(0, 0, 0, 0)
            ico_layout.addWidget(ico)
            ico_container.setLayout(ico_layout)
            hdr.addWidget(ico_container)

            # Guardar referência para hover effect
            self._icon_container = ico_container
            self._icon_base_color = accent

        title_lbl = QLabel(title)
        title_lbl.setFont(aurora_cw_theme.get_font(14, bold=True))
        title_lbl.setStyleSheet(f"""
            color: {c['text_secondary']};
            background: transparent;
            letter-spacing: 0.02em;
            font-weight: 600;
        """)
        hdr.addWidget(title_lbl)
        hdr.addStretch()

        layout.addLayout(hdr)

        # Value com tipografia premium
        value_lbl = QLabel(value)
        value_lbl.setFont(QFont(t.FONT_FAMILY_QT, 36, QFont.Weight.Bold))
        value_lbl.setStyleSheet(f"""
            color: {c['text_primary']};
            background: transparent;
            letter-spacing: -0.03em;
            line-height: 1.0;
        """)
        layout.addWidget(value_lbl)
        self._value_label = value_lbl

        # Change indicator elegante
        self._change_row = None
        self._change_icon_label = None
        self._change_label = None
        self._change_badge = None
        if change:
            change_row = QHBoxLayout()
            change_row.setSpacing(8)
            
            is_positive = change.startswith('+')
            change_color = c['forest'] if is_positive else c['crimson']
            change_icon = "trending_up" if is_positive else "trending_down"
            
            # Badge elegante para change
            # IMPORTANTE: não usar QLabel como container de layout (gera glitch/artefatos e sizeHint ruim).
            change_badge = QFrame()
            change_badge.setObjectName("kpiChangeBadge")
            change_badge.setStyleSheet(f"""
            QFrame#kpiChangeBadge {{
                background: {change_color}15;
                border: 1px solid {change_color}40;
                border-radius: 10px;
            }}
            """)

            badge_layout = QHBoxLayout(change_badge)
            badge_layout.setContentsMargins(10, 6, 10, 6)
            badge_layout.setSpacing(6)

            change_ico = QLabel()
            change_ico.setFixedSize(18, 18)
            change_ico.setPixmap(get_pixmap(change_icon, QSize(18, 18), change_color))
            change_ico.setStyleSheet("background: transparent;")

            change_lbl = QLabel(change)
            change_lbl.setFont(aurora_cw_theme.get_font(13, bold=True))
            change_lbl.setStyleSheet(f"color: {change_color}; background: transparent;")

            badge_layout.addWidget(change_ico)
            badge_layout.addWidget(change_lbl)
            
            change_row.addWidget(change_badge)
            change_row.addStretch()
            layout.addLayout(change_row)
            self._change_row = change_row
            self._change_icon_label = change_ico
            self._change_label = change_lbl
            self._change_badge = change_badge

        # Sparkline real (não placeholder)
        self._sparkline_widget = _PremiumSparkline(accent_color)
        self._sparkline_widget.setMinimumHeight(56)
        layout.addWidget(self._sparkline_widget)

    def set_value(self, value: str):
        self._value_label.setText(value)

    def set_change(self, change: str):
        c = aurora_cw_theme.colors
        is_positive = change.startswith('+')
        change_color = c['forest'] if is_positive else c['crimson']
        change_icon = "trending_up" if is_positive else "trending_down"

        if self._change_label is None or self._change_badge is None or self._change_icon_label is None:
            change_row = QHBoxLayout()
            change_row.setSpacing(8)
            
            # Badge elegante para change (QFrame container)
            change_badge = QFrame()
            change_badge.setObjectName("kpiChangeBadge")
            change_badge.setStyleSheet(f"""
            QFrame#kpiChangeBadge {{
                background: {change_color}15;
                border: 1px solid {change_color}40;
                border-radius: 10px;
            }}
            """)

            badge_layout = QHBoxLayout(change_badge)
            badge_layout.setContentsMargins(10, 6, 10, 6)
            badge_layout.setSpacing(6)

            change_ico = QLabel()
            change_ico.setFixedSize(18, 18)
            change_lbl = QLabel()
            change_lbl.setFont(aurora_cw_theme.get_font(13, bold=True))
            
            badge_layout.addWidget(change_ico)
            badge_layout.addWidget(change_lbl)
            
            change_row.addWidget(change_badge)
            change_row.addStretch()
            self.layout().insertLayout(2, change_row)
            self._change_row = change_row
            self._change_icon_label = change_ico
            self._change_label = change_lbl
            self._change_badge = change_badge

        self._change_icon_label.setPixmap(get_pixmap(change_icon, QSize(18, 18), change_color))
        self._change_icon_label.setStyleSheet("background: transparent;")
        self._change_label.setText(change)
        self._change_label.setStyleSheet(f"color: {change_color}; background: transparent;")

    def set_sparkline_data(self, data: list):
        """Define os dados do sparkline."""
        self._sparkline_data = data
        self._sparkline_widget.set_data(data)

    def enterEvent(self, event):
        """Hover enter - eleva sombra e ilumina ícone."""
        if hasattr(self, '_shadow'):
            self._shadow.setBlurRadius(30)
            self._shadow.setOffset(0, 6)
            self._shadow.setColor(QColor(0, 0, 0, 80))
        if hasattr(self, '_icon_container'):
            self._icon_container.setStyleSheet(f"""
            QLabel {{
                background: {self._icon_base_color}40;
                border-radius: 24px;
                border: none;
            }}
            """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Hover leave - restaura sombra e ícone."""
        if hasattr(self, '_shadow'):
            self._shadow.setBlurRadius(20)
            self._shadow.setOffset(0, 4)
            self._shadow.setColor(QColor(0, 0, 0, 60))
        if hasattr(self, '_icon_container'):
            self._icon_container.setStyleSheet(f"""
            QLabel {{
                background: {self._icon_base_color}26;
                border-radius: 24px;
                border: none;
            }}
            """)
        super().leaveEvent(event)


# ===================================================================== _PremiumSparkline - Sparkline real estilo Linear
class _PremiumSparkline(QWidget):
    """Sparkline premium com gradient fill e smooth curves."""
    
    def __init__(self, accent_color: AccentColor = AccentColor.AURORA, parent=None):
        super().__init__(parent)
        self._data = []
        self._accent_color = accent_color
        self._hover_index = -1
        self.setMouseTracking(True)
        
    def set_data(self, data: list):
        self._data = data
        self.update()
        
    def mouseMoveEvent(self, event):
        """Track hover position para tooltip."""
        if not self._data:
            return
        width = self.width()
        if width > 0:
            index = int((event.position().x() / width) * len(self._data))
            self._hover_index = max(0, min(index, len(self._data) - 1))
            self.update()
            
    def leaveEvent(self, event):
        self._hover_index = -1
        self.update()
        
    def paintEvent(self, event):
        if not self._data or len(self._data) < 2:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        c = aurora_cw_theme.colors
        accent = aurora_theme_manager.get_accent(self._accent_color)
        soft = aurora_theme_manager.get_color(self._accent_color.value + '_soft')
        
        width = self.width()
        height = self.height()
        
        # Normalizar dados
        min_val = min(self._data)
        max_val = max(self._data)
        range_val = max_val - min_val if max_val != min_val else 1
        
        points = []
        for i, val in enumerate(self._data):
            x = (i / (len(self._data) - 1)) * width
            y = height - ((val - min_val) / range_val) * (height - 20) - 10
            points.append(QPoint(int(x), int(y)))
        
        # Gradient fill
        gradient = QLinearGradient(0, 0, 0, height)
        gradient.setColorAt(0, QColor(accent + "40"))
        gradient.setColorAt(1, QColor(accent + "00"))
        
        path = QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        path.lineTo(width, height)
        path.lineTo(0, height)
        path.closeSubpath()
        
        painter.fillPath(path, QBrush(gradient))
        
        # Stroke line
        pen = QPen(QColor(accent))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        line_path = QPainterPath()
        line_path.moveTo(points[0])
        for point in points[1:]:
            line_path.lineTo(point)
        painter.drawPath(line_path)
        
        # Hover indicator
        if self._hover_index >= 0 and self._hover_index < len(points):
            hover_point = points[self._hover_index]
            
            # Vertical line
            hover_pen = QPen(QColor(accent + "80"))
            hover_pen.setWidth(1)
            hover_pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(hover_pen)
            painter.drawLine(hover_point.x(), 0, hover_point.x(), height)
            
            # Dot
            painter.setBrush(QBrush(QColor(accent)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(hover_point, 4, 4)


# ===================================================================== AuroraTable - Tabela premium estilo Linear
class AuroraTable(QTableWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing

        self.setStyleSheet(f"""
        QTableWidget {{
            background-color: {c['bg_primary']};
            alternate-background-color: {c['table_row_odd']};
            gridline-color: transparent;
            border: 1px solid {c['border_subtle']};
            border-radius: {t.RADIUS_XL}px;
            selection-background-color: {c['table_row_selected']};
            selection-color: {c['text_primary']};
            outline: none;
        }}
        QTableWidget::item {{
            padding: 14px 16px;
            border: none;
            border-bottom: 1px solid {c['border_subtle']};
        }}
        QTableWidget::item:hover {{
            background-color: {c['table_row_hover']};
        }}
        QTableWidget::item:selected {{
            background-color: {c['table_row_selected']};
            color: {c['text_primary']};
            font-weight: 500;
        }}
        QHeaderView {{
            background-color: {c['table_header_bg']};
            border: none;
        }}
        QHeaderView::section {{
            background-color: {c['table_header_bg']};
            color: {c['table_header_text']};
            padding: 12px 16px;
            border: none;
            border-bottom: 1px solid {c['border_default']};
            border-right: 1px solid {c['border_subtle']};
            font-weight: 600;
            font-size: {t.FONT_SIZE_SM}px;
            letter-spacing: -0.01em;
        }}
        QHeaderView::section:first {{
            border-top-left-radius: {t.RADIUS_XL}px;
        }}
        QHeaderView::section:last {{
            border-top-right-radius: {t.RADIUS_XL}px;
            border-right: none;
        }}
        QHeaderView::section:hover {{
            background-color: {c['bg_tertiary']};
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 6px;
            margin: 4px 2px;
        }}
        QScrollBar::handle:vertical {{
            background: {c['border_default']};
            border-radius: 3px;
            min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {c['border_strong']};
        }}
        """)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(140)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)


# ===================================================================== AuroraProgressBar - Progress bar com gradient
class AuroraProgressBar(QProgressBar):
    def __init__(self, accent_color: AccentColor = AccentColor.AURORA, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        self._accent = accent_color

        start = aurora_theme_manager.get_color(accent_color.value + '_start')
        end = aurora_theme_manager.get_color(accent_color.value + '_end')

        self.setStyleSheet(f"""
        QProgressBar {{
            background: {c['bg_tertiary']};
            border: none;
            border-radius: 8px;
            text-align: center;
            color: {c['text_primary']};
            height: 10px;
        }}
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {start}, stop:1 {end});
            border-radius: 8px;
        }}
        """)


# ===================================================================== SeparatorLine
class SeparatorLine(QFrame):
    def __init__(self, orientation: str = "horizontal", parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        if orientation == "horizontal":
            self.setMinimumHeight(1)
            self.setStyleSheet(f"background: {c['border_subtle']}; border: none;")
        else:
            self.setMinimumWidth(1)
            self.setStyleSheet(f"background: {c['border_subtle']}; border: none;")


# ===================================================================== PlaceholderScreen
class PlaceholderScreen(QFrame):
    def __init__(self, title: str, subtitle: str = "", icon_name: str = "sparkles",
                 accent: AccentColor = AccentColor.AURORA, parent: Optional[QWidget] = None):
        super().__init__(parent)
        c = aurora_cw_theme.colors
        t = aurora_cw_theme.spacing
        accent_color = aurora_theme_manager.get_accent(accent)

        self.setStyleSheet(f"""
        QFrame {{
            background: {c['bg_primary']};
        }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(t.SPACING_XL)
        self.setLayout(layout)

        layout.addStretch()

        # Icon
        icon = QLabel()
        icon.setFixedSize(80, 80)
        icon.setStyleSheet(f"""
        QLabel {{
            background: {aurora_theme_manager.get_color(accent.value + '_soft')};
            border-radius: 24px;
        }}
        """)
        icon.setPixmap(get_pixmap(icon_name, QSize(40, 40), accent_color))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_container = QWidget()
        ic_layout = QVBoxLayout()
        ic_layout.setContentsMargins(0, 0, 0, 0)
        ic_layout.addWidget(icon)
        ic_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.setLayout(ic_layout)
        layout.addWidget(icon_container)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_2XL, bold=True))
        title_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_container = QWidget()
        tc_layout = QVBoxLayout()
        tc_layout.setContentsMargins(0, 0, 0, 0)
        tc_layout.addWidget(title_lbl)
        tc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_container.setLayout(tc_layout)
        layout.addWidget(title_container)

        # Subtitle
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setFont(aurora_cw_theme.get_font(t.FONT_SIZE_MD))
            sub_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
            sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub_lbl.setWordWrap(True)

            sub_container = QWidget()
            sc_layout = QVBoxLayout()
            sc_layout.setContentsMargins(0, 0, 0, 0)
            sc_layout.addWidget(sub_lbl)
            sc_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub_container.setLayout(sc_layout)
            layout.addWidget(sub_container)

        layout.addStretch()
