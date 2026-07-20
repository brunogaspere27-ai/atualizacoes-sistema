"""
SaaS Premium Components v2.0 - CW Transportadora
Componentes inspirados em Linear, Stripe, ClickUp, Vercel, Notion, Framer

Features:
- Cards com cantos 18-20px
- Fundo #151515
- Borda #262626
- Sombras suaves
- Ícones vermelhos CW
- Hover elegante
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QGraphicsDropShadowEffect, QSizePolicy, QScrollArea,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QColor, QFont, QPixmap, QPainter, QPen, QBrush

from telas.theme_saaS import saas_theme, AccentColor
from utils.icons import get_icon, get_pixmap


class SaaSCard(QFrame):
    """Card premium estilo SaaS com cantos 18-20px."""

    def __init__(self, title: str = None, icon_name: str = None,
                 padding: int = None, parent: QWidget = None):
        super().__init__(parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setObjectName("saasCard")
        padding = padding or t.SPACING_XL

        self.setStyleSheet(f"""
        QFrame#saasCard {{
            background-color: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_2XL}px;
        }}
        QFrame#saasCard:hover {{
            border-color: {c['card_border_hover']};
        }}
        """)

        # Glow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(padding, padding, padding, padding)
        layout.setSpacing(t.SPACING_MD)
        self.setLayout(layout)

        # Header com título e ícone
        if title or icon_name:
            header = self._create_header(title, icon_name)
            layout.addWidget(header)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(t.SPACING_MD)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.content_layout)

    def _create_header(self, title: str, icon_name: str) -> QFrame:
        c = saas_theme.COLORS
        t = saas_theme

        header = QFrame()
        header.setStyleSheet("background: transparent;")
        hl = QHBoxLayout()
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(t.SPACING_MD)
        header.setLayout(hl)

        if icon_name:
            icon = QLabel()
            icon.setFixedSize(32, 32)
            icon.setStyleSheet(f"""
            QLabel {{
                background-color: {c['cw_soft']};
                border-radius: 8px;
            }}
            """)
            icon.setPixmap(get_pixmap(icon_name, (16, 16), c['cw']))
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hl.addWidget(icon)

        if title:
            title_lbl = QLabel(title)
            title_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_LG, bold=True))
            title_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
            hl.addWidget(title_lbl)

        hl.addStretch()

        return header

    def add_widget(self, widget: QWidget):
        """Adiciona um widget ao conteúdo do card."""
        self.content_layout.addWidget(widget)

    def add_layout(self, layout):
        """Adiciona um layout ao conteúdo do card."""
        self.content_layout.addLayout(layout)


class SaaSButton(QPushButton):
    """Botão premium estilo SaaS."""

    def __init__(self, text: str, style: str = "default", icon_name: str = None,
                 parent: QWidget = None):
        super().__init__(text, parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setFixedHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(saas_theme.get_font(t.FONT_SIZE_MD))

        if icon_name:
            icon = get_icon(icon_name, c['text_primary'])
            self.setIcon(icon)

        if style == "primary":
            self.setProperty("class", "primary")
            self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['cw']};
                color: #FFFFFF;
                border: 1px solid {c['cw']};
                border-radius: {t.RADIUS_LG}px;
                padding: 0 24px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {c['cw_hover']};
                border-color: {c['cw_hover']};
            }}
            QPushButton:pressed {{
                background-color: {c['cw_active']};
                border-color: {c['cw_active']};
            }}
            QPushButton:disabled {{
                background-color: {c['bg_tertiary']};
                color: {c['text_disabled']};
                border-color: {c['border_default']};
            }}
            """)
        elif style == "ghost":
            self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {c['text_secondary']};
                border: 1px solid transparent;
                border-radius: {t.RADIUS_LG}px;
                padding: 0 24px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                color: {c['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_active']};
            }}
            """)
        else:  # default
            self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_tertiary']};
                color: {c['text_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {t.RADIUS_LG}px;
                padding: 0 24px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {c['bg_hover']};
                border-color: {c['border_strong']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_active']};
            }}
            QPushButton:disabled {{
                background-color: {c['bg_tertiary']};
                color: {c['text_disabled']};
                border-color: {c['border_subtle']};
            }}
            """)


class SaaSSidebar(QFrame):
    """Sidebar premium estilo SaaS com fundo #0B0B0B."""

    navigation_requested = Signal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setFixedWidth(280)
        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_primary']};
            border-right: 1px solid {c['border_default']};
        }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_LG, t.SPACING_XL, t.SPACING_LG, t.SPACING_LG)
        layout.setSpacing(t.SPACING_MD)
        self.setLayout(layout)

        # Logo CW
        self._create_logo()
        layout.addSpacing(t.SPACING_2XL)

        # Menu
        self.menu_container = QVBoxLayout()
        self.menu_container.setSpacing(t.SPACING_SM)
        self.menu_container.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.menu_container)

        layout.addStretch()

        # User card
        self._create_user_card()

    def _create_logo(self):
        c = saas_theme.COLORS
        t = saas_theme

        logo = QLabel("CW")
        logo.setFont(QFont(t.FONT_FAMILY_QT, 32, QFont.Weight.Bold))
        logo.setStyleSheet(f"""
        QLabel {{
            color: {c['cw']};
            background: transparent;
            letter-spacing: -2px;
        }}
        """)
        self.layout().addWidget(logo)

    def add_menu_item(self, name: str, label: str, icon_name: str):
        """Adiciona um item ao menu."""
        c = saas_theme.COLORS
        t = saas_theme

        btn = QPushButton(label)
        btn.setFixedHeight(40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(saas_theme.get_font(t.FONT_SIZE_MD))
        btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            color: {c['text_secondary']};
            border: none;
            border-radius: {t.RADIUS_LG}px;
            padding: 0 16px;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {c['bg_hover']};
            color: {c['text_primary']};
        }}
        """)
        btn.clicked.connect(lambda: self._on_item_clicked(name, btn))
        self.menu_container.addWidget(btn)

    def _on_item_clicked(self, name: str, btn: QPushButton):
        """Handle item click."""
        self._clear_active()
        btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {c['cw_soft']};
            color: {c['cw']};
            border: none;
            border-radius: {t.RADIUS_LG}px;
            padding: 0 16px;
            text-align: left;
            font-weight: 600;
        }}
        """)
        self.navigation_requested.emit(name)

    def _clear_active(self):
        """Remove active state from all items."""
        c = saas_theme.COLORS
        t = saas_theme

        for i in range(self.menu_container.count()):
            item = self.menu_container.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QPushButton):
                    widget.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {c['text_secondary']};
                        border: none;
                        border-radius: {t.RADIUS_LG}px;
                        padding: 0 16px;
                        text-align: left;
                    }}
                    QPushButton:hover {{
                        background-color: {c['bg_hover']};
                        color: {c['text_primary']};
                    }}
                    """)

    def _create_user_card(self):
        c = saas_theme.COLORS
        t = saas_theme

        user_card = QFrame()
        user_card.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_surface']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 12px;
        }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(t.SPACING_MD)
        user_card.setLayout(layout)

        # Avatar
        avatar = QLabel()
        avatar.setFixedSize(36, 36)
        avatar.setStyleSheet(f"""
        QLabel {{
            background-color: {c['cw']};
            border-radius: 18px;
        }}
        """)
        avatar.setText("U")
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setFont(saas_theme.get_font(t.FONT_SIZE_MD, bold=True))
        avatar.setStyleSheet(f"""
        QLabel {{
            background-color: {c['cw']};
            color: #FFFFFF;
            border-radius: 18px;
        }}
        """)
        layout.addWidget(avatar)

        # User info
        info = QVBoxLayout()
        info.setSpacing(2)
        info.setContentsMargins(0, 0, 0, 0)

        name = QLabel("Usuário")
        name.setFont(saas_theme.get_font(t.FONT_SIZE_SM, bold=True))
        name.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        info.addWidget(name)

        role = QLabel("Administrador")
        role.setFont(saas_theme.get_font(t.FONT_SIZE_XS))
        role.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent;")
        info.addWidget(role)

        layout.addLayout(info)

        self.layout().addWidget(user_card)


class SaaSTopBar(QFrame):
    """Topbar premium estilo SaaS."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setFixedHeight(64)
        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['bg_primary']};
            border-bottom: 1px solid {c['border_default']};
        }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(t.SPACING_XL, 0, t.SPACING_XL, 0)
        layout.setSpacing(t.SPACING_LG)
        self.setLayout(layout)

        # Search
        search = QLineEdit()
        search.setPlaceholderText("Buscar...")
        search.setFixedWidth(320)
        search.setFixedHeight(40)
        search.setStyleSheet(f"""
        QLineEdit {{
            background-color: {c['bg_surface']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 0 16px;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:hover {{
            border-color: {c['border_strong']};
        }}
        QLineEdit:focus {{
            border-color: {c['cw']};
        }}
        """)
        layout.addWidget(search)

        layout.addStretch()

        # Right side
        right = QHBoxLayout()
        right.setSpacing(t.SPACING_MD)

        # Notifications
        notif_btn = QPushButton()
        notif_btn.setFixedSize(40, 40)
        notif_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: {t.RADIUS_LG}px;
        }}
        QPushButton:hover {{
            background-color: {c['bg_hover']};
        }}
        """)
        notif_btn.setIcon(get_icon("bell", c['text_secondary']))
        right.addWidget(notif_btn)

        # Avatar
        avatar = QPushButton()
        avatar.setFixedSize(40, 40)
        avatar.setStyleSheet(f"""
        QPushButton {{
            background-color: {c['cw']};
            border: none;
            border-radius: 20px;
        }}
        QPushButton:hover {{
            background-color: {c['cw_hover']};
        }}
        """)
        avatar.setText("U")
        avatar.setFont(saas_theme.get_font(t.FONT_SIZE_MD, bold=True))
        avatar.setStyleSheet(f"""
        QPushButton {{
            background-color: {c['cw']};
            color: #FFFFFF;
            border: none;
            border-radius: 20px;
        }}
        QPushButton:hover {{
            background-color: {c['cw_hover']};
        }}
        """)
        right.addWidget(avatar)

        layout.addLayout(right)


class SaaSKPICard(QFrame):
    """KPI Card premium estilo SaaS."""

    def __init__(self, title: str, value: str, trend: str = "",
                 icon_name: str = None, parent: QWidget = None):
        super().__init__(parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setStyleSheet(f"""
        QFrame {{
            background-color: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_2XL}px;
        }}
        QFrame:hover {{
            border-color: {c['card_border_hover']};
        }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(t.SPACING_XL, t.SPACING_XL, t.SPACING_XL, t.SPACING_XL)
        layout.setSpacing(t.SPACING_SM)
        self.setLayout(layout)

        # Header
        header = QHBoxLayout()
        header.setSpacing(t.SPACING_SM)

        if icon_name:
            icon = QLabel()
            icon.setFixedSize(32, 32)
            icon.setStyleSheet(f"""
            QLabel {{
                background-color: {c['cw_soft']};
                border-radius: 8px;
            }}
            """)
            icon.setPixmap(get_pixmap(icon_name, (16, 16), c['cw']))
            icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.addWidget(icon)

        title_lbl = QLabel(title)
        title_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_SM))
        title_lbl.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        header.addWidget(title_lbl)

        header.addStretch()
        layout.addLayout(header)

        # Value
        value_lbl = QLabel(value)
        value_lbl.setFont(QFont(t.FONT_FAMILY_QT, t.FONT_SIZE_3XL, QFont.Weight.Bold))
        value_lbl.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        layout.addWidget(value_lbl)

        # Trend
        if trend:
            trend_lbl = QLabel(trend)
            trend_lbl.setFont(saas_theme.get_font(t.FONT_SIZE_SM))
            if "+" in trend:
                trend_lbl.setStyleSheet(f"color: {c['success']}; background: transparent;")
            else:
                trend_lbl.setStyleSheet(f"color: {c['error']}; background: transparent;")
            layout.addWidget(trend_lbl)


class SaaSTable(QTableWidget):
    """Tabela premium estilo SaaS."""

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        c = saas_theme.COLORS
        t = saas_theme

        self.setStyleSheet(f"""
        QTableWidget {{
            background-color: {c['card_bg']};
            border: 1px solid {c['card_border']};
            border-radius: {t.RADIUS_XL}px;
            gridline-color: {c['border_subtle']};
            selection-background-color: {c['cw_soft']};
            selection-color: {c['cw']};
        }}
        QTableWidget::item {{
            padding: 12px 16px;
            border-bottom: 1px solid {c['border_subtle']};
        }}
        QTableWidget::item:hover {{
            background-color: {c['bg_hover']};
        }}
        QTableWidget::item:selected {{
            background-color: {c['cw_soft']};
        }}
        QHeaderView::section {{
            background-color: {c['bg_tertiary']};
            color: {c['text_secondary']};
            border: none;
            border-bottom: 1px solid {c['border_default']};
            padding: 12px 16px;
            font-size: {t.FONT_SIZE_SM}px;
            font-weight: 600;
        }}
        QTableWidget QTableCornerButton::section {{
            background-color: {c['bg_tertiary']};
            border: none;
        }}
        """)

        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

        vertical_header = self.verticalHeader()
        vertical_header.setVisible(False)
