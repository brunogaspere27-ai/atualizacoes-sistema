"""
CW Button - Botões profissionais para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Cores sólidas (sem gradientes)
- Hover e press states refinados
- Sizes consistentes
- Variants: Primary, Secondary, Ghost, Danger, Success
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont
from enum import Enum
from typing import Optional

from ui.theme.cw_theme import cw_theme, CWColor, CWRadius, CWSpacing


class ButtonVariant(Enum):
    """Variantes de botão CW"""
    PRIMARY = "primary"      # Vermelho CW - ação principal
    SECONDARY = "secondary"  # Cinza neutro - ação secundária
    GHOST = "ghost"          # Transparente - ação discreta
    DANGER = "danger"        # Vermelho erro - ação destrutiva
    SUCCESS = "success"      # Verde - ação de sucesso


class ButtonSize(Enum):
    """Tamanhos de botão CW"""
    SM = "sm"    # 32px altura
    MD = "md"    # 40px altura
    LG = "lg"    # 48px altura


class CWButton(QPushButton):
    """Botão profissional CW Transportadora"""
    
    def __init__(
        self,
        text: str,
        variant: ButtonVariant = ButtonVariant.PRIMARY,
        size: ButtonSize = ButtonSize.MD,
        icon: Optional[str] = None,
        disabled: bool = False,
        parent: Optional[object] = None
    ):
        super().__init__(text, parent)
        
        self._variant = variant
        self._size = size
        self._icon_name = icon
        
        self._apply_style()
        self._apply_icon()
        
        if disabled:
            self.setEnabled(False)
    
    def _apply_style(self):
        """Aplica estilos baseados na variante e tamanho"""
        c = cw_theme.colors
        t = cw_theme.spacing
        r = cw_theme.radius
        
        # Size configurations
        sizes = {
            ButtonSize.SM: (32, t.SM, t.LG, cw_theme.typography.FONT_SIZE_SM),
            ButtonSize.MD: (40, t.LG, t.XL, cw_theme.typography.FONT_SIZE_MD),
            ButtonSize.LG: (48, t.XL, t._2XL, cw_theme.typography.FONT_SIZE_LG),
        }
        height, px, py, font_size = sizes[self._size]
        
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(cw_theme.get_font(font_size, bold=True))
        
        # Variant styles
        variant_styles = {
            ButtonVariant.PRIMARY: self._primary_style,
            ButtonVariant.SECONDARY: self._secondary_style,
            ButtonVariant.GHOST: self._ghost_style,
            ButtonVariant.DANGER: self._danger_style,
            ButtonVariant.SUCCESS: self._success_style,
        }
        
        variant_styles[self._variant](c, t, r, px, py)
    
    def _primary_style(self, c: dict, t: object, r: object, px: int, py: int):
        """Botão primário - Vermelho CW"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['primary']};
                color: {c['text_inverted']};
                border: none;
                border-radius: {r.MD}px;
                padding: {py}px {px}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {c['primary_dark']};
            }}
            QPushButton:pressed {{
                background-color: {c['primary_dark']};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background-color: {c['bg_tertiary']};
                color: {c['text_disabled']};
                cursor: not-allowed;
            }}
        """)
    
    def _secondary_style(self, c: dict, t: object, r: object, px: int, py: int):
        """Botão secundário - Cinza neutro"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['bg_tertiary']};
                color: {c['text_primary']};
                border: 1px solid {c['border_default']};
                border-radius: {r.MD}px;
                padding: {py}px {px}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {c['bg_overlay']};
                border-color: {c['border_strong']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_overlay']};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background-color: {c['bg_secondary']};
                color: {c['text_disabled']};
                border-color: {c['border_subtle']};
                cursor: not-allowed;
            }}
        """)
    
    def _ghost_style(self, c: dict, t: object, r: object, px: int, py: int):
        """Botão ghost - Transparente"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {c['text_secondary']};
                border: none;
                border-radius: {r.MD}px;
                padding: {py}px {px}px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {c['bg_tertiary']};
                color: {c['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {c['bg_overlay']};
            }}
            QPushButton:disabled {{
                color: {c['text_disabled']};
                cursor: not-allowed;
            }}
        """)
    
    def _danger_style(self, c: dict, t: object, r: object, px: int, py: int):
        """Botão danger - Vermelho erro"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['error']};
                color: {c['text_inverted']};
                border: none;
                border-radius: {r.MD}px;
                padding: {py}px {px}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:pressed {{
                background-color: #B91C1C;
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background-color: {c['bg_tertiary']};
                color: {c['text_disabled']};
                cursor: not-allowed;
            }}
        """)
    
    def _success_style(self, c: dict, t: object, r: object, px: int, py: int):
        """Botão success - Verde"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {c['success']};
                color: {c['text_inverted']};
                border: none;
                border-radius: {r.MD}px;
                padding: {py}px {px}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
            QPushButton:pressed {{
                background-color: #047857;
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background-color: {c['bg_tertiary']};
                color: {c['text_disabled']};
                cursor: not-allowed;
            }}
        """)
    
    def _apply_icon(self):
        """Aplica ícone se fornecido"""
        if self._icon_name:
            # TODO: Implementar sistema de ícones
            pass
