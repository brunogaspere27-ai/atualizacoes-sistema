"""
Componentes CW UI.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QLineEdit, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.theme.cw_theme import cw_theme


class ButtonVariant:
    PRIMARY = "primary"
    SECONDARY = "secondary"
    GHOST = "ghost"


class ButtonSize:
    SM = "sm"
    MD = "md"
    LG = "lg"


class CWButton(QPushButton):
    """Botão CW."""
    def __init__(self, text, variant=ButtonVariant.PRIMARY, size=ButtonSize.MD, parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self._setup_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _setup_style(self):
        c = cw_theme.colors
        if self.variant == ButtonVariant.PRIMARY:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['primary']};
                    color: #FFFFFF;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{ background-color: {c['primary_hover']}; }}
                QPushButton:pressed {{ background-color: {c['primary_active']}; }}
                QPushButton:disabled {{ background-color: {c['bg_tertiary']}; color: {c['text_disabled']}; }}
            """)
        elif self.variant == ButtonVariant.SECONDARY:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['bg_tertiary']};
                    color: {c['text_primary']};
                    border: 1px solid {c['border_default']};
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{ background-color: {c['bg_overlay']}; }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {c['text_secondary']};
                    border: none;
                    padding: 10px 20px;
                    font-weight: 600;
                    font-size: 13px;
                }}
                QPushButton:hover {{ color: {c['text_primary']}; }}
            """)


class CWCard(QFrame):
    """Card CW."""
    def __init__(self, padding=16, parent=None):
        super().__init__(parent)
        c = cw_theme.colors
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {c['card_bg']};
                border: 1px solid {c['card_border']};
                border-radius: 12px;
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.setSpacing(12)

    def add_widget(self, widget):
        self._layout.addWidget(widget)

    def add_layout(self, layout):
        self._layout.addLayout(layout)

    def add_spacing(self, spacing):
        self._layout.addSpacing(spacing)


class CWInput(QLineEdit):
    """Input CW."""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        c = cw_theme.colors
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c['bg_tertiary']};
                color: {c['text_primary']};
                border: 1px solid {c['border_default']};
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {c['primary']}; }}
        """)


class CWSidebar(QWidget):
    """Sidebar CW."""
    item_clicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(260)
        c = cw_theme.colors
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {c['sidebar_bg']};
                border-right: 1px solid {c['sidebar_border']};
            }}
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(12, 16, 12, 16)
        self._layout.setSpacing(4)
        self._items = {}
        self._active_item = None

    def add_section(self, title, items):
        c = cw_theme.colors
        lbl = QLabel(title.upper())
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {c['text_tertiary']}; background: transparent; padding: 8px 4px;")
        self._layout.addWidget(lbl)

        for item in items:
            btn = QPushButton(f"  {item['label']}")
            btn.setFlat(True)
            btn.setProperty("item_id", item['id'])
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {c['sidebar_text']};
                    border: none;
                    border-radius: 6px;
                    padding: 10px 12px;
                    text-align: left;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background: {c['bg_overlay']};
                    color: {c['text_primary']};
                }}
            """)
            btn.clicked.connect(lambda checked, iid=item['id']: self._on_item_click(iid))
            self._layout.addWidget(btn)
            self._items[item['id']] = btn

        self._layout.addSpacing(8)

    def add_bottom_widget(self, widget):
        self._layout.addStretch()
        self._layout.addWidget(widget)

    def _on_item_click(self, item_id):
        self.set_active_item(item_id)
        self.item_clicked.emit(item_id)

    def set_active_item(self, item_id):
        c = cw_theme.colors
        for iid, btn in self._items.items():
            if iid == item_id:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {c['primary_soft']};
                        color: {c['primary']};
                        border: none;
                        border-radius: 6px;
                        padding: 10px 12px;
                        text-align: left;
                        font-size: 13px;
                        font-weight: 600;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {c['sidebar_text']};
                        border: none;
                        border-radius: 6px;
                        padding: 10px 12px;
                        text-align: left;
                        font-size: 13px;
                    }}
                    QPushButton:hover {{
                        background: {c['bg_overlay']};
                        color: {c['text_primary']};
                    }}
                """)
        self._active_item = item_id


class CWHeader(QFrame):
    """Header CW."""
    profile_requested = Signal()
    settings_requested = Signal()
    search_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        c = cw_theme.colors
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {c['header_bg']};
                border-bottom: 1px solid {c['header_border']};
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)

        self._breadcrumb = QLabel("Principal / Dashboard")
        self._breadcrumb.setFont(QFont("Segoe UI", 11))
        self._breadcrumb.setStyleSheet(f"color: {c['text_secondary']}; background: transparent;")
        layout.addWidget(self._breadcrumb)
        layout.addStretch()

        self._user_label = QLabel("Usuário")
        self._user_label.setFont(QFont("Segoe UI", 11))
        self._user_label.setStyleSheet(f"color: {c['text_primary']}; background: transparent;")
        layout.addWidget(self._user_label)

    def set_user(self, name):
        self._user_label.setText(name)

    def set_breadcrumb(self, section, page):
        self._breadcrumb.setText(f"{section} / {page}")


class PlaceholderScreen(QWidget):
    """Tela placeholder."""
    def __init__(self, title, subtitle, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setFont(QFont("Segoe UI", 14))
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)
