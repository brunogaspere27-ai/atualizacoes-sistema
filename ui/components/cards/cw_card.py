"""
CW Card - Cards profissionais para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Borda sutil (não sombra grande)
- Radius moderado (não exagerado)
- Padding consistente
- Variantes: Default, Elevated, Bordered
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional
from enum import Enum

from ui.components.buttons.cw_button import ButtonVariant, ButtonSize

from ui.theme.cw_theme import cw_theme, CWRadius, CWSpacing


class CardVariant(Enum):
    """Variantes de card CW"""
    DEFAULT = "default"      # Borda sutil
    ELEVATED = "elevated"    # Sombra sutil
    BORDERED = "bordered"    # Borda visível


class CWCard(QFrame):
    """Card profissional CW Transportadora"""
    
    def __init__(
        self,
        title: Optional[str] = None,
        variant: CardVariant = CardVariant.DEFAULT,
        padding: Optional[int] = None,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        
        self._title = title
        self._variant = variant
        self._padding = padding or cw_theme.spacing.XL
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Configura layout do card"""
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(
            self._padding, self._padding,
            self._padding, self._padding
        )
        self.layout.setSpacing(cw_theme.spacing.MD)
        self.setLayout(self.layout)
        
        if self._title:
            self._add_title()
    
    def _add_title(self):
        """Adiciona título ao card"""
        title_label = QLabel(self._title)
        title_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_LG,
            bold=True
        ))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {cw_theme.colors['text_primary']};
                background: transparent;
                padding: 0;
            }}
        """)
        self.layout.addWidget(title_label)
    
    def _apply_style(self):
        """Aplica estilos baseados na variante"""
        c = cw_theme.colors
        r = cw_theme.radius
        
        variant_styles = {
            CardVariant.DEFAULT: self._default_style,
            CardVariant.ELEVATED: self._elevated_style,
            CardVariant.BORDERED: self._bordered_style,
        }
        
        variant_styles[self._variant](c, r)
    
    def _default_style(self, c: dict, r: object):
        """Card padrão - Borda sutil"""
        self.setStyleSheet(f"""
            CWCard {{
                background-color: {c['bg_elevated']};
                border: 1px solid {c['border_subtle']};
                border-radius: {r.LG}px;
            }}
        """)
    
    def _elevated_style(self, c: dict, r: object):
        """Card elevado - Sombra sutil"""
        self.setStyleSheet(f"""
            CWCard {{
                background-color: {c['bg_elevated']};
                border: 1px solid {c['border_subtle']};
                border-radius: {r.LG}px;
            }}
        """)
        # TODO: Adicionar sombra com QGraphicsDropShadowEffect
    
    def _bordered_style(self, c: dict, r: object):
        """Card com borda visível"""
        self.setStyleSheet(f"""
            CWCard {{
                background-color: {c['bg_elevated']};
                border: 1px solid {c['border_default']};
                border-radius: {r.LG}px;
            }}
        """)
    
    def add_widget(self, widget: QWidget):
        """Adiciona widget ao card"""
        self.layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Adiciona layout ao card"""
        self.layout.addLayout(layout)
    
    def add_spacing(self, spacing: int = None):
        """Adiciona espaçamento"""
        sp = spacing or cw_theme.spacing.MD
        self.layout.addSpacing(sp)


class KPICard(CWCard):
    """Card KPI para Dashboard CW Transportadora"""
    
    def __init__(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        trend: Optional[str] = None,
        trend_positive: bool = True,
        parent: Optional[QWidget] = None
    ):
        self._value = value
        self._subtitle = subtitle
        self._trend = trend
        self._trend_positive = trend_positive
        
        super().__init__(title=title, variant=CardVariant.DEFAULT, parent=parent)
        
        self._add_content()
    
    def _add_content(self):
        """Adiciona conteúdo do KPI"""
        c = cw_theme.colors
        
        # Value
        value_label = QLabel(self._value)
        value_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_3XL,
            bold=True
        ))
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {c['text_primary']};
                background: transparent;
                padding: {cw_theme.spacing.SM}px 0;
            }}
        """)
        self.layout.addWidget(value_label)
        
        # Subtitle
        if self._subtitle:
            subtitle_label = QLabel(self._subtitle)
            subtitle_label.setFont(cw_theme.get_font(
                cw_theme.typography.FONT_SIZE_SM
            ))
            subtitle_label.setStyleSheet(f"""
                QLabel {{
                    color: {c['text_secondary']};
                    background: transparent;
                }}
            """)
            self.layout.addWidget(subtitle_label)
        
        # Trend
        if self._trend:
            trend_color = c['success'] if self._trend_positive else c['error']
            trend_label = QLabel(self._trend)
            trend_label.setFont(cw_theme.get_font(
                cw_theme.typography.FONT_SIZE_SM,
                bold=True
            ))
            trend_label.setStyleSheet(f"""
                QLabel {{
                    color: {trend_color};
                    background: transparent;
                }}
            """)
            self.layout.addWidget(trend_label)
