"""Modern Button Component - CW Transportadora
Botões com múltiplas variantes e sizes
"""

from enum import Enum
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import Qt, QSize

from ui.theme.cw_theme import cw_theme


class ButtonVariant(Enum):
    """Variantes de botão."""
    PRIMARY = "primary"        # Vermelho CW
    SECONDARY = "secondary"    # Cinza
    DANGER = "danger"         # Vermelho de erro
    SUCCESS = "success"       # Verde
    WARNING = "warning"       # Laranja
    GHOST = "ghost"           # Transparente com borda
    LINK = "link"            # Apenas texto


class ButtonSize(Enum):
    """Tamanhos de botão."""
    XS = 24     # Micro
    SM = 32     # Pequeno
    MD = 40     # Médio (default)
    LG = 48     # Grande
    XL = 56     # Extra grande


class CWButton(QPushButton):
    """
    Botão moderno com Design System CW
    Suporta múltiplas variantes, tamanhos e ícones
    """
    
    def __init__(
        self,
        text: str = "",
        variant: ButtonVariant = ButtonVariant.PRIMARY,
        size: ButtonSize = ButtonSize.MD,
        icon: str = None,
        parent=None
    ):
        super().__init__(text, parent)
        self.variant = variant
        self.size = size
        self.icon_name = icon
        
        self._setup_style()
        self._setup_size()
    
    def _setup_size(self):
        """Configura tamanho do botão."""
        height = self.size.value
        
        # Calcular padding horizontal baseado no tamanho
        padding_h = 16 if self.size in [ButtonSize.XS, ButtonSize.SM] else 24
        
        font_size = {
            ButtonSize.XS: 10,
            ButtonSize.SM: 11,
            ButtonSize.MD: 13,
            ButtonSize.LG: 14,
            ButtonSize.XL: 16,
        }.get(self.size, 13)
        
        font = QFont(cw_theme.typography.FONT_FAMILY_QT, font_size)
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)
        
        self.setMinimumHeight(height)
        self.setMinimumWidth(height * 2 if self.text() else height)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _setup_style(self):
        """Aplica styling baseado na variante."""
        if self.variant == ButtonVariant.PRIMARY:
            stylesheet = self._get_primary_style()
        elif self.variant == ButtonVariant.SECONDARY:
            stylesheet = self._get_secondary_style()
        elif self.variant == ButtonVariant.DANGER:
            stylesheet = self._get_danger_style()
        elif self.variant == ButtonVariant.SUCCESS:
            stylesheet = self._get_success_style()
        elif self.variant == ButtonVariant.WARNING:
            stylesheet = self._get_warning_style()
        elif self.variant == ButtonVariant.GHOST:
            stylesheet = self._get_ghost_style()
        elif self.variant == ButtonVariant.LINK:
            stylesheet = self._get_link_style()
        else:
            stylesheet = self._get_primary_style()
        
        self.setStyleSheet(stylesheet)
    
    def _get_primary_style(self) -> str:
        """Estilo PRIMARY: Vermelho CW"""
        return f"""
            QPushButton {{
                background-color: {cw_theme.colors['primary']};
                color: #FFFFFF;
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 0px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {cw_theme.colors['brand_hover']};
            }}
            QPushButton:pressed {{
                background-color: {cw_theme.colors['brand_active']};
            }}
            QPushButton:disabled {{
                background-color: {cw_theme.colors['text_disabled']};
                color: {cw_theme.colors['text_tertiary']};
            }}
        """
    
    def _get_secondary_style(self) -> str:
        """Estilo SECONDARY: Cinza"""
        return f"""
            QPushButton {{
                background-color: {cw_theme.colors['bg_secondary']};
                color: {cw_theme.colors['text_primary']};
                border: 1px solid {cw_theme.colors['border_default']};
                border-radius: {cw_theme.radius.MD}px;
                padding: 0px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {cw_theme.colors['bg_tertiary']};
            }}
            QPushButton:pressed {{
                background-color: {cw_theme.colors['bg_overlay']};
            }}
            QPushButton:disabled {{
                color: {cw_theme.colors['text_disabled']};
            }}
        """
    
    def _get_danger_style(self) -> str:
        """Estilo DANGER: Vermelho de erro"""
        return f"""
            QPushButton {{
                background-color: {cw_theme.colors['error']};
                color: #FFFFFF;
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 0px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #DC2626;
            }}
            QPushButton:pressed {{
                background-color: #991B1B;
            }}
            QPushButton:disabled {{
                background-color: {cw_theme.colors['text_disabled']};
            }}
        """
    
    def _get_success_style(self) -> str:
        """Estilo SUCCESS: Verde"""
        return f"""
            QPushButton {{
                background-color: {cw_theme.colors['success']};
                color: #FFFFFF;
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 0px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #16A34A;
            }}
            QPushButton:pressed {{
                background-color: #15803D;
            }}
            QPushButton:disabled {{
                background-color: {cw_theme.colors['text_disabled']};
            }}
        """
    
    def _get_warning_style(self) -> str:
        """Estilo WARNING: Laranja"""
        return f"""
            QPushButton {{
                background-color: {cw_theme.colors['warning']};
                color: #FFFFFF;
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: 0px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #D97706;
            }}
            QPushButton:pressed {{
                background-color: #92400E;
            }}
            QPushButton:disabled {{
                background-color: {cw_theme.colors['text_disabled']};
            }}
        """
    
    def _get_ghost_style(self) -> str:
        """Estilo GHOST: Transparente com borda"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {cw_theme.colors['text_primary']};
                border: 1px solid {cw_theme.colors['border_default']};
                border-radius: {cw_theme.radius.MD}px;
                padding: 0px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {cw_theme.colors['bg_secondary']};
                border: 1px solid {cw_theme.colors['border_strong']};
            }}
            QPushButton:pressed {{
                background-color: {cw_theme.colors['bg_tertiary']};
            }}
            QPushButton:disabled {{
                color: {cw_theme.colors['text_disabled']};
                border: 1px solid {cw_theme.colors['border_subtle']};
            }}
        """
    
    def _get_link_style(self) -> str:
        """Estilo LINK: Apenas texto"""
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {cw_theme.colors['primary']};
                border: none;
                padding: 0px;
                font-weight: 500;
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {cw_theme.colors['brand_hover']};
            }}
            QPushButton:pressed {{
                color: {cw_theme.colors['brand_active']};
            }}
            QPushButton:disabled {{
                color: {cw_theme.colors['text_disabled']};
            }}
        """
