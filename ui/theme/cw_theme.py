"""
CW Transportadora Design System v3.0 - Premium Dark Red
Identidade visual profissional para sistema de logística

Inspiração: Industrial precision, Bloomberg terminal meets modern SaaS
Cor principal: #E53935 (Vermelho Premium)
Fundo: #07090c (Dark Navy-Black)
Modo padrão: Dark Premium
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
from typing import Dict
from enum import Enum


class ThemeMode(Enum):
    LIGHT = "light"
    DARK = "dark"


class CWColor(Enum):
    """Paleta de cores CW Transportadora - Premium Dark Red"""

    # Brand Colors
    PRIMARY = "#E53935"        # Vermelho Premium - cor principal
    PRIMARY_DARK = "#C62828"   # Vermelho mais escuro
    PRIMARY_LIGHT = "#EF5350"  # Vermelho mais claro
    PRIMARY_SOFT = "#FFEBEE"   # Vermelho background suave
    
    # Neutral Colors - Superfícies (Dark Premium)
    BG_PRIMARY = "#07090c"        # Dark Navy-Black - canvas principal
    BG_SECONDARY = "#0A0C10"     # Cinza muito escuro - sidebar, cards
    BG_TERTIARY = "#0D0F14"      # Cinza escuro - inputs, hover
    BG_ELEVATED = "#10131A"      # Cinza - cards elevados
    BG_OVERLAY = "#151821"       # Cinza médio - hover states
    BG_SURFACE = "#0A0C10"       # Surface intermediária
    
    # Neutral Colors - Texto (Dark Mode)
    TEXT_PRIMARY = "#FFFFFF"     # Branco - texto principal
    TEXT_SECONDARY = "#A0AEC0"   # Cinza claro - texto secundário
    TEXT_TERTIARY = "#718096"    # Cinza médio - texto terciário
    TEXT_DISABLED = "#4A5568"    # Cinza escuro - desabilitado
    TEXT_INVERTED = "#07090c"    # Dark Navy-Black - texto invertido
    
    # Neutral Colors - Bordas (Dark Mode)
    BORDER_SUBTLE = "#1A202C"    # Cinza muito escuro - borda sutil
    BORDER_DEFAULT = "#2D3748"   # Cinza escuro - borda padrão
    BORDER_STRONG = "#4A5568"    # Cinza médio - borda forte
    BORDER_FOCUS = "#E53935"     # Vermelho Premium - borda foco
    
    # Semantic Colors
    SUCCESS = "#10B981"         # Verde esmeralda
    SUCCESS_SOFT = "#D1FAE5"    # Verde background suave
    WARNING = "#F59E0B"         # Laranja âmbar
    WARNING_SOFT = "#FEF3C7"    # Laranja background suave
    ERROR = "#EF4444"           # Vermelho erro
    ERROR_SOFT = "#FEE2E2"      # Vermelho background suave
    INFO = "#3B82F6"            # Azul info
    INFO_SOFT = "#DBEAFE"       # Azul background suave
    ROSE = "#F43F5E"            # Rose
    ROSE_SOFT = "#FEE2E2"       # Rose background suave
    SKY = "#0EA5E9"             # Sky blue
    SKY_SOFT = "#E0F2FE"        # Sky background suave

    # Aurora Gradient Colors (compatibilidade com tema aurora)
    AURORA = "#E53935"          # Vermelho Premium
    AURORA_START = "#E53935"    # Início do gradiente
    AURORA_END = "#C62828"      # Fim do gradiente
    AURORA_HOVER = "#EF5350"    # Hover
    AURORA_ACTIVE = "#D32F2F"  # Active


class CWTypography:
    """Sistema de tipografia CW - Barlow (display) + JetBrains Mono (dados)"""

    # Font Family
    FONT_FAMILY = "'Barlow', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif"
    FONT_FAMILY_QT = "Barlow"
    FONT_FAMILY_MONO = "'JetBrains Mono', 'Fira Code', Consolas, monospace"
    
    # Font Sizes (escala baseada em 4px)
    FONT_SIZE_XS = 11
    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_2XL = 24
    FONT_SIZE_3XL = 32
    FONT_SIZE_4XL = 48
    FONT_SIZE_5XL = 64
    
    # Font Weights
    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700
    
    # Line Heights
    LINE_HEIGHT_TIGHT = 1.1    # Headings
    LINE_HEIGHT_NORMAL = 1.5   # Body
    LINE_HEIGHT_RELAXED = 1.6  # Long text
    
    # Letter Spacing
    LETTER_SPACING_TIGHT = -0.02
    LETTER_SPACING_NORMAL = -0.01
    LETTER_SPACING_WIDE = 0


class CWSpacing:
    """Sistema de espaçamento CW - Grid 4px"""
    
    XS = 4
    SPACING_XS = 4  # Alias para compatibilidade
    SM = 8
    SPACING_SM = 8  # Alias para compatibilidade
    MD = 12
    SPACING_MD = 12  # Alias para compatibilidade
    LG = 16
    SPACING_LG = 16  # Alias para compatibilidade
    XL = 24
    SPACING_XL = 24  # Alias para compatibilidade
    _2XL = 32
    SPACING_2XL = 32  # Alias para compatibilidade
    _3XL = 48
    _4XL = 64
    _5XL = 96


class CWRadius:
    """Sistema de border radius CW - Profissional"""
    
    XS = 4     # Badges, tags
    SM = 6     # Small inputs
    MD = 8     # Inputs, buttons
    LG = 10    # Cards
    XL = 12    # Dialogs
    _2XL = 16  # Large cards
    FULL = 9999


class CWShadow:
    """Sistema de sombras CW - Sutis e profissionais"""
    
    NONE = "none"
    SM = "0 1px 2px rgba(0, 0, 0, 0.05)"
    MD = "0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -1px rgba(0, 0, 0, 0.04)"
    LG = "0 10px 15px -3px rgba(0, 0, 0, 0.07), 0 4px 6px -2px rgba(0, 0, 0, 0.04)"
    XL = "0 20px 25px -5px rgba(0, 0, 0, 0.07), 0 10px 10px -5px rgba(0, 0, 0, 0.03)"
    
    # Shadow with brand color
    BRAND = "0 4px 12px rgba(211, 47, 47, 0.15)"


class CWTheme:
    """Gerenciador de tema CW Transportadora - Dark Mode Premium"""
    
    def __init__(self, mode: ThemeMode = ThemeMode.DARK):
        self.mode = mode
        self.colors = self._build_colors()
        self.typography = CWTypography
        self.spacing = CWSpacing
        self.radius = CWRadius
        self.shadow = CWShadow
    
    def _build_colors(self) -> Dict[str, str]:
        """Constrói dicionário de cores baseado no modo - Premium Dark Red"""
        return {
            # Brand - Premium Red
            'primary': "#E53935",              # Premium Red - cor principal
            'primary_dark': "#C62828",         # Vermelho mais escuro
            'primary_light': "#EF5350",        # Vermelho mais claro
            'primary_soft': "#2D1A1A",         # Vermelho background suave (dark)
            'brand': "#E53935",                # Alias para primary
            'brand_hover': "#EF5350",          # Brand hover
            'brand_active': "#C62828",         # Brand active
            'brand_glow': "rgba(229, 57, 53, 0.25)",  # Brand glow
            'brand_soft': "#2D1A1A",           # Brand background suave

            # Backgrounds - Premium Dark Palette
            'bg_primary': "#07090c",           # Dark Navy-Black - Background principal
            'bg_secondary': "#0A0C10",        # Background secundário
            'bg_tertiary': "#0D0F14",         # Cards
            'bg_elevated': "#10131A",         # Cards elevados
            'bg_overlay': "#151821",           # Bordas
            'bg_surface': "#0A0C10",          # Surface intermediária
            
            # Sidebar
            'sidebar_bg': "#0A0C10",           # Sidebar background
            'sidebar_gradient_top': "#0A0C10",
            'sidebar_gradient_bottom': "#0A0C10",
            'sidebar_text': "#FFFFFF",
            'sidebar_text_muted': "#718096",
            'sidebar_active': "#E53935",
            'sidebar_active_bg': "#2D1A1A",
            'sidebar_hover': "#10131A",
            'sidebar_border': "#151821",

            # Header
            'header_bg': "#0A0C10",
            'header_border': "#151821",

            # Cards
            'card_bg': "#0D0F14",
            'card_border': "#151821",
            'card_hover': "#10131A",

            # Tables
            'table_header_bg': "#0A0C10",
            'table_header_text': "#A0AEC0",
            'table_row_even': "#07090c",
            'table_row_odd': "#0A0C10",
            'table_row_hover': "#0D0F14",
            'table_row_selected': "#2D1A1A",

            # Text - Premium Dark Hierarchy
            'text_primary': "#FFFFFF",         # Texto principal
            'text_secondary': "#A0AEC0",       # Texto secundário
            'text_tertiary': "#718096",        # Texto terciário
            'text_disabled': "#4A5568",        # Texto desabilitado
            'text_inverted': "#07090c",        # Texto invertido

            # Borders
            'border_subtle': "#151821",        # Borda sutil
            'border_default': "#2D3748",       # Borda padrão
            'border_strong': "#4A5568",        # Borda forte
            'border_focus': "#E53935",         # Borda foco (Premium Red)
            
            # Semantic Colors
            'success': "#10B981",              # Success (Emerald)
            'success_soft': "#1A3D28",         # Success background suave
            'warning': "#F59E0B",              # Warning (Amber)
            'warning_soft': "#3D2E1A",         # Warning background suave
            'error': "#EF4444",                # Danger (Red)
            'error_soft': "#2D1A1A",           # Error background suave
            'info': "#3B82F6",                 # Info (Blue)
            'info_soft': "#1A2D3D",            # Info background suave
            'rose': "#F43F5E",                # Rose
            'rose_soft': "#2D1A1A",            # Rose background suave
            'sky': "#0EA5E9",                 # Sky blue
            'sky_soft': "#1A2D3D",            # Sky background suave
            'violet': "#8B5CF6",              # Violet
            'violet_soft': "#2D1A3D",         # Violet background suave
            'emerald': "#10B981",             # Emerald (same as success)
            'emerald_soft': "#1A3D28",        # Emerald background suave
            'amber': "#F59E0B",               # Amber (same as warning)
            'amber_soft': "#3D2E1A",          # Amber background suave

            # Aurora Gradient Colors (compatibilidade com tema aurora)
            'aurora': "#E53935",               # Vermelho Premium
            'aurora_start': "#E53935",         # Início do gradiente
            'aurora_end': "#C62828",           # Fim do gradiente
            'aurora_hover': "#EF5350",         # Hover
            'aurora_active': "#D32F2F",       # Active
            
            # Chart Colors
            'chart_1': "#E53935",              # Premium Red (Brand)
            'chart_2': "#10B981",              # Emerald Green
            'chart_3': "#3B82F6",              # Blue
            'chart_4': "#F59E0B",              # Amber
            'chart_5': "#8B5CF6",              # Violet
            'chart_6': "#06B6D4",              # Cyan
            'chart_7': "#EC4899",              # Pink
            'chart_8': "#6366F1",              # Indigo
            'chart_bg': "#07090c",
            'chart_grid': "#151821",
            'chart_text': "#A0AEC0",
        }
    
    def get_font(self, size: int, bold: bool = False) -> QFont:
        """Retorna QFont configurado"""
        font = QFont(self.typography.FONT_FAMILY_QT, size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        else:
            font.setWeight(QFont.Weight.Normal)
        return font
    
    def set_mode(self, mode: ThemeMode):
        """Altera o modo do tema"""
        self.mode = mode
        self.colors = self._build_colors()


# Instância global do tema CW - Dark Mode por padrão
cw_theme = CWTheme(mode=ThemeMode.DARK)
