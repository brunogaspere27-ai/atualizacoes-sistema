"""
CW Badge - Badges profissionais para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Status badges com cores sutis
- Tamanhos consistentes
- Variantes: Default, Success, Warning, Error, Info
- Radius moderado
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Optional
from enum import Enum

from ui.theme.cw_theme import cw_theme, CWRadius, CWSpacing


class BadgeVariant(Enum):
    """Variantes de badge CW"""
    DEFAULT = "default"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


class CWBadge(QLabel):
    """Badge profissional CW Transportadora"""
    
    def __init__(
        self,
        text: str,
        variant: BadgeVariant = BadgeVariant.DEFAULT,
        parent: Optional[object] = None
    ):
        super().__init__(text, parent)
        
        self._variant = variant
        
        self._apply_style()
    
    def _apply_style(self):
        """Aplica estilos baseados na variante"""
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius
        
        # Variant configurations
        variant_config = {
            BadgeVariant.DEFAULT: {
                'bg': c['bg_tertiary'],
                'text': c['text_secondary'],
                'border': c['border_default']
            },
            BadgeVariant.SUCCESS: {
                'bg': c['success_soft'],
                'text': c['success'],
                'border': c['success']
            },
            BadgeVariant.WARNING: {
                'bg': c['warning_soft'],
                'text': c['warning'],
                'border': c['warning']
            },
            BadgeVariant.ERROR: {
                'bg': c['error_soft'],
                'text': c['error'],
                'border': c['error']
            },
            BadgeVariant.INFO: {
                'bg': c['info_soft'],
                'text': c['info'],
                'border': c['info']
            }
        }
        
        config = variant_config[self._variant]
        
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {config['bg']};
                color: {config['text']};
                border: 1px solid {config['border']};
                border-radius: {r.SM}px;
                padding: {t.XS}px {t.SM}px;
                font-size: {cw_theme.typography.FONT_SIZE_XS}px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
        """)
        
        self.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_XS,
            bold=True
        ))
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
