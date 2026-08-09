"""
CW Empty State - Estados vazios profissionais para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Mensagem principal e secundária
- Ícone ilustrativo
- Botão de ação opcional
- Layout centralizado
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional

from ui.theme.cw_theme import cw_theme, CWSpacing
from ui.components.buttons.cw_button import CWButton, ButtonVariant, ButtonSize


class CWEmptyState(QWidget):
    """Empty state profissional CW Transportadora"""
    
    def __init__(
        self,
        title: str,
        description: str,
        icon: str = "📭",
        action_text: Optional[str] = None,
        action_callback: Optional[callable] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._title = title
        self._description = description
        self._icon = icon
        self._action_text = action_text
        self._action_callback = action_callback
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Configura layout do empty state"""
        c = cw_theme.colors
        t = cw_theme.spacing
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(
            t._3XL, t._3XL,
            t._3XL, t._3XL
        )
        self.layout.setSpacing(t.LG)
        self.setLayout(self.layout)
        
        # Icon
        icon_label = QLabel(self._icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(cw_theme.get_font(64))
        icon_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_tertiary']};
                background: transparent;
            }}
        """)
        self.layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self._title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_XL,
            bold=True
        ))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                background: transparent;
            }}
        """)
        self.layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(self._description)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_MD
        ))
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_secondary']};
                background: transparent;
            }}
        """)
        desc_label.setWordWrap(True)
        self.layout.addWidget(desc_label)
        
        # Action button
        if self._action_text and self._action_callback:
            button_container = QWidget()
            button_layout = QHBoxLayout()
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_layout.addStretch()
            button_container.setLayout(button_layout)
            
            action_btn = CWButton(
                self._action_text,
                ButtonVariant.PRIMARY,
                ButtonSize.MD
            )
            action_btn.clicked.connect(self._action_callback)
            button_layout.addWidget(action_btn)
            button_layout.addStretch()
            
            self.layout.addWidget(button_container)
        
        self.layout.addStretch()
    
    def _apply_style(self):
        """Aplica estilos"""
        c = cw_theme.colors
        
        self.setStyleSheet(f"""
            CWEmptyState {{
                background-color: {c['bg_primary']};
                border-radius: {cw_theme.radius.LG}px;
            }}
        """)
