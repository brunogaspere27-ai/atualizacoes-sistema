"""
Sistema de Temas CW Transportadora v9 - PySide6 (Qt6)

Design system profissional inspirado em Linear, Notion, VS Code, Stripe Dashboard.
- Tema escuro premium com superfícies em camadas
- Paleta de cores consistente com acentos por categoria
- Tipografia moderna e hierarquia visual clara
- Espaçamentos e bordas refinados
- Chart palette para visualização de dados premium
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFont
from typing import Dict, Literal
from enum import Enum


class ThemeMode(Enum):
    """Modos de tema disponíveis."""
    LIGHT = "light"
    DARK = "dark"


class AccentColor(Enum):
    """Cores de acento por categoria funcional."""
    BRAND = "brand"           # Vermelho CW - marca principal
    EMERALD = "emerald"       # Verde - sucesso, financeiro positivo
    SKY = "sky"               # Azul - informações, viagens
    AMBER = "amber"           # Amarelo - alertas, manutenção
    VIOLET = "violet"         # Vermelho CW - operações
    CYAN = "cyan"             # Ciano - RH, funcionários
    ROSE = "rose"             # Rosa - contas, financeiro negativo


class ThemeTokens:
    """Tokens de design globais — 4px grid system."""

    # Tipografia
    FONT_FAMILY = "'Inter', 'Segoe UI', 'SF Pro Text', 'Helvetica Neue', Arial, sans-serif"
    FONT_FAMILY_QT = "Segoe UI"
    FONT_FAMILY_DISPLAY = "'Inter', 'Segoe UI Semibold', 'Segoe UI', sans-serif"
    FONT_FAMILY_MONO = "'Cascadia Code', 'Consolas', 'Menlo', monospace"

    # Tamanhos de fonte
    FONT_SIZE_XS = 10
    FONT_SIZE_SM = 11
    FONT_SIZE_MD = 13
    FONT_SIZE_LG = 14
    FONT_SIZE_XL = 16
    FONT_SIZE_2XL = 20
    FONT_SIZE_3XL = 24
    FONT_SIZE_4XL = 32

    # Espaçamentos (4px grid)
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 20
    SPACING_2XL = 24
    SPACING_3XL = 32
    SPACING_4XL = 40
    SPACING_5XL = 48
    SPACING_6XL = 64

    # Bordas (refinadas)
    RADIUS_XS = 4
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_2XL = 20
    RADIUS_FULL = 9999

    # Sombras (3 tiers via QGraphicsDropShadowEffect)
    SHADOW_SM_BLUR = 8
    SHADOW_SM_Y = 2
    SHADOW_MD_BLUR = 16
    SHADOW_MD_Y = 4
    SHADOW_LG_BLUR = 32
    SHADOW_LG_Y = 8


class DarkTheme:
    """Tema Escuro Premium — inspirado em Linear/Notion/VS Code."""

    # Superfícies em camadas (profundidade via luminosidade)
    BG_PRIMARY = "#0B0E14"       # canvas base
    BG_SECONDARY = "#11151C"     # painéis, sidebar
    BG_TERTIARY = "#161B24"      # inputs, campos
    BG_ELEVATED = "#1C2230"      # cards elevados, dropdowns
    BG_OVERLAY = "#232B3A"       # hover, overlay

    # Texto (contraste WCAG AA)
    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"
    TEXT_TERTIARY = "#484F58"
    TEXT_DISABLED = "#30363D"
    TEXT_INVERTED = "#0B0E14"

    # Bordas sutis
    BORDER_SUBTLE = "#21262D"
    BORDER_DEFAULT = "#30363D"
    BORDER_STRONG = "#484F58"

    # Marca CW — vermelho vibrante
    BRAND = "#E5484D"
    BRAND_HOVER = "#FF6369"
    BRAND_ACTIVE = "#CC3D42"
    BRAND_SOFT = "#2D1215"
    BRAND_GLOW = "rgba(229, 72, 77, 0.25)"

    # Acentos
    EMERALD = "#3FB950"
    EMERALD_SOFT = "#0D2818"
    SKY = "#58A6FF"
    SKY_SOFT = "#0C2D6B"
    AMBER = "#D29922"
    AMBER_SOFT = "#2A1F0A"
    VIOLET = "#E5484D"
    VIOLET_SOFT = "#2D1215"
    CYAN = "#39C5CF"
    CYAN_SOFT = "#0A2A2E"
    ROSE = "#FB7185"
    ROSE_SOFT = "#2E141C"
    INDIGO = "#818CF8"
    INDIGO_SOFT = "#1A1E3D"

    # Estados
    SUCCESS = "#3FB950"
    SUCCESS_SOFT = "#0D2818"
    WARNING = "#D29922"
    WARNING_SOFT = "#2A1F0A"
    ERROR = "#F85149"
    ERROR_SOFT = "#2D1215"
    INFO = "#58A6FF"
    INFO_SOFT = "#0C2D6B"

    # Sidebar
    SIDEBAR_BG = "#010409"
    SIDEBAR_GRADIENT_TOP = "#010409"
    SIDEBAR_GRADIENT_BOTTOM = "#0B0E14"
    SIDEBAR_TEXT = "#E6EDF3"
    SIDEBAR_TEXT_MUTED = "#484F58"
    SIDEBAR_ACTIVE = "#E5484D"
    SIDEBAR_ACTIVE_BG = "#2D1215"
    SIDEBAR_HOVER = "#161B22"
    SIDEBAR_BORDER = "#21262D"

    # Header/TopBar
    HEADER_BG = "#11151C"
    HEADER_BORDER = "#21262D"

    # Cards
    CARD_BG = "#161B24"
    CARD_BORDER = "#21262D"
    CARD_HOVER = "#1C2230"

    # Tabelas
    TABLE_HEADER_BG = "#11151C"
    TABLE_HEADER_TEXT = "#8B949E"
    TABLE_ROW_EVEN = "#0B0E14"
    TABLE_ROW_ODD = "#11151C"
    TABLE_ROW_HOVER = "#161B24"
    TABLE_ROW_SELECTED = "#2D1215"

    # Chart palette (8 cores harmoniosas)
    CHART_1 = "#58A6FF"   # blue
    CHART_2 = "#3FB950"   # green
    CHART_3 = "#E5484D"   # red/brand
    CHART_4 = "#FB923C"   # ember
    CHART_5 = "#D29922"   # amber
    CHART_6 = "#39C5CF"   # cyan
    CHART_7 = "#FB7185"   # rose
    CHART_8 = "#818CF8"   # indigo

    # Chart surface
    CHART_BG = "#0B0E14"
    CHART_GRID = "#21262D"
    CHART_TEXT = "#8B949E"


class LightTheme:
    """Tema Claro — design limpo e profissional."""

    BG_PRIMARY = "#FFFFFF"
    BG_SECONDARY = "#F6F8FA"
    BG_TERTIARY = "#F0F2F5"
    BG_ELEVATED = "#FFFFFF"
    BG_OVERLAY = "#E8EBF0"

    TEXT_PRIMARY = "#1F2328"
    TEXT_SECONDARY = "#59636E"
    TEXT_TERTIARY = "#8C959F"
    TEXT_DISABLED = "#D1D9E0"
    TEXT_INVERTED = "#FFFFFF"

    BORDER_SUBTLE = "#D1D9E0"
    BORDER_DEFAULT = "#CBCFD3"
    BORDER_STRONG = "#8C959F"

    BRAND = "#CF222E"
    BRAND_HOVER = "#A40E26"
    BRAND_ACTIVE = "#8B0820"
    BRAND_SOFT = "#FFEBE9"
    BRAND_GLOW = "rgba(207, 34, 46, 0.2)"

    EMERALD = "#1A7F37"
    EMERALD_SOFT = "#DAFBE1"
    SKY = "#0969DA"
    SKY_SOFT = "#DDF4FF"
    AMBER = "#9A6700"
    AMBER_SOFT = "#FFF8C5"
    VIOLET = "#CF222E"
    VIOLET_SOFT = "#FFEBE9"
    CYAN = "#0598BC"
    CYAN_SOFT = "#C5F4FA"
    ROSE = "#FF6E8A"
    ROSE_SOFT = "#FFEBE9"
    INDIGO = "#6366F1"
    INDIGO_SOFT = "#EEF2FF"

    SUCCESS = "#1A7F37"
    SUCCESS_SOFT = "#DAFBE1"
    WARNING = "#9A6700"
    WARNING_SOFT = "#FFF8C5"
    ERROR = "#CF222E"
    ERROR_SOFT = "#FFEBE9"
    INFO = "#0969DA"
    INFO_SOFT = "#DDF4FF"

    SIDEBAR_BG = "#F6F8FA"
    SIDEBAR_GRADIENT_TOP = "#F6F8FA"
    SIDEBAR_GRADIENT_BOTTOM = "#FFFFFF"
    SIDEBAR_TEXT = "#1F2328"
    SIDEBAR_TEXT_MUTED = "#8C959F"
    SIDEBAR_ACTIVE = "#CF222E"
    SIDEBAR_ACTIVE_BG = "#FFEBE9"
    SIDEBAR_HOVER = "#E8EBF0"
    SIDEBAR_BORDER = "#D1D9E0"

    HEADER_BG = "#FFFFFF"
    HEADER_BORDER = "#D1D9E0"

    CARD_BG = "#FFFFFF"
    CARD_BORDER = "#D1D9E0"
    CARD_HOVER = "#F6F8FA"

    TABLE_HEADER_BG = "#F6F8FA"
    TABLE_HEADER_TEXT = "#59636E"
    TABLE_ROW_EVEN = "#FFFFFF"
    TABLE_ROW_ODD = "#F6F8FA"
    TABLE_ROW_HOVER = "#F0F2F5"
    TABLE_ROW_SELECTED = "#FFEBE9"

    CHART_1 = "#0969DA"
    CHART_2 = "#1A7F37"
    CHART_3 = "#CF222E"
    CHART_4 = "#FB923C"
    CHART_5 = "#9A6700"
    CHART_6 = "#0598BC"
    CHART_7 = "#FF6E8A"
    CHART_8 = "#6366F1"

    CHART_BG = "#FFFFFF"
    CHART_GRID = "#D1D9E0"
    CHART_TEXT = "#59636E"


class ThemeManager:
    """Gerenciador central de temas."""

    def __init__(self):
        self._current_mode = ThemeMode.DARK
        self._theme = DarkTheme
        self._tokens = ThemeTokens

    def set_mode(self, mode: ThemeMode):
        self._current_mode = mode
        self._theme = LightTheme if mode == ThemeMode.LIGHT else DarkTheme

    def get_mode(self) -> ThemeMode:
        return self._current_mode

    def toggle_mode(self):
        if self._current_mode == ThemeMode.LIGHT:
            self.set_mode(ThemeMode.DARK)
        else:
            self.set_mode(ThemeMode.LIGHT)

    @property
    def colors(self) -> Dict[str, str]:
        theme = self._theme
        return {
            # Superfícies
            "bg_primary": theme.BG_PRIMARY,
            "bg_secondary": theme.BG_SECONDARY,
            "bg_tertiary": theme.BG_TERTIARY,
            "bg_elevated": theme.BG_ELEVATED,
            "bg_overlay": theme.BG_OVERLAY,

            # Texto
            "text_primary": theme.TEXT_PRIMARY,
            "text_secondary": theme.TEXT_SECONDARY,
            "text_tertiary": theme.TEXT_TERTIARY,
            "text_disabled": theme.TEXT_DISABLED,
            "text_inverted": theme.TEXT_INVERTED,

            # Bordas
            "border_subtle": theme.BORDER_SUBTLE,
            "border_default": theme.BORDER_DEFAULT,
            "border_strong": theme.BORDER_STRONG,

            # Marca
            "brand": theme.BRAND,
            "brand_hover": theme.BRAND_HOVER,
            "brand_active": theme.BRAND_ACTIVE,
            "brand_soft": theme.BRAND_SOFT,
            "brand_glow": theme.BRAND_GLOW,

            # Acentos
            "emerald": theme.EMERALD,
            "emerald_soft": theme.EMERALD_SOFT,
            "sky": theme.SKY,
            "sky_soft": theme.SKY_SOFT,
            "amber": theme.AMBER,
            "amber_soft": theme.AMBER_SOFT,
            "violet": theme.VIOLET,
            "violet_soft": theme.VIOLET_SOFT,
            "cyan": theme.CYAN,
            "cyan_soft": theme.CYAN_SOFT,
            "rose": theme.ROSE,
            "rose_soft": theme.ROSE_SOFT,

            # Estados
            "success": theme.SUCCESS,
            "success_soft": theme.SUCCESS_SOFT,
            "warning": theme.WARNING,
            "warning_soft": theme.WARNING_SOFT,
            "error": theme.ERROR,
            "error_soft": theme.ERROR_SOFT,
            "info": theme.INFO,
            "info_soft": theme.INFO_SOFT,

            # Sidebar
            "sidebar_bg": theme.SIDEBAR_BG,
            "sidebar_gradient_top": theme.SIDEBAR_GRADIENT_TOP,
            "sidebar_gradient_bottom": theme.SIDEBAR_GRADIENT_BOTTOM,
            "sidebar_text": theme.SIDEBAR_TEXT,
            "sidebar_text_muted": theme.SIDEBAR_TEXT_MUTED,
            "sidebar_active": theme.SIDEBAR_ACTIVE,
            "sidebar_active_bg": theme.SIDEBAR_ACTIVE_BG,
            "sidebar_hover": theme.SIDEBAR_HOVER,
            "sidebar_border": theme.SIDEBAR_BORDER,

            # Header
            "header_bg": theme.HEADER_BG,
            "header_border": theme.HEADER_BORDER,

            # Cards
            "card_bg": theme.CARD_BG,
            "card_border": theme.CARD_BORDER,
            "card_hover": theme.CARD_HOVER,

            # Tabelas
            "table_header_bg": theme.TABLE_HEADER_BG,
            "table_header_text": theme.TABLE_HEADER_TEXT,
            "table_row_even": theme.TABLE_ROW_EVEN,
            "table_row_odd": theme.TABLE_ROW_ODD,
            "table_row_hover": theme.TABLE_ROW_HOVER,
            "table_row_selected": theme.TABLE_ROW_SELECTED,

            # Charts
            "chart_1": theme.CHART_1,
            "chart_2": theme.CHART_2,
            "chart_3": theme.CHART_3,
            "chart_4": theme.CHART_4,
            "chart_5": theme.CHART_5,
            "chart_6": theme.CHART_6,
            "chart_7": theme.CHART_7,
            "chart_8": theme.CHART_8,
            "chart_bg": theme.CHART_BG,
            "chart_grid": theme.CHART_GRID,
            "chart_text": theme.CHART_TEXT,
        }

    @property
    def tokens(self) -> ThemeTokens:
        return self._tokens

    def get_color(self, color_name: str) -> str:
        return self.colors.get(color_name, "#000000")

    def get_accent(self, accent: AccentColor) -> str:
        accent_map = {
            AccentColor.BRAND: "brand",
            AccentColor.EMERALD: "emerald",
            AccentColor.SKY: "sky",
            AccentColor.AMBER: "amber",
            AccentColor.VIOLET: "violet",
            AccentColor.CYAN: "cyan",
            AccentColor.ROSE: "rose",
        }
        return self.get_color(accent_map.get(accent, "brand"))

    def get_chart_colors(self) -> list:
        """Retorna a paleta de cores para gráficos."""
        c = self.colors
        return [c["chart_1"], c["chart_2"], c["chart_3"], c["chart_4"],
                c["chart_5"], c["chart_6"], c["chart_7"], c["chart_8"]]

    def get_font(self, size: int = ThemeTokens.FONT_SIZE_MD, bold: bool = False, weight: int = None) -> QFont:
        font = QFont(self._cw_theme.spacing.FONT_FAMILY_QT, size)
        if weight is not None:
            try:
                font.setWeight(weight)
            except Exception:
                pass
        if bold:
            font.setBold(True)
        return font

    def get_stylesheet(self) -> str:
        """Stylesheet global — dark premium 2026."""
        c = self.colors
        t = self._tokens

        return f"""
        /* ============================================================
           BASE + TIPOGRAFIA
           ============================================================ */
        * {{
            font-family: {t.FONT_FAMILY};
        }}

        QMainWindow, QDialog {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
        }}

        QWidget {{
            color: {c['text_primary']};
            font-size: {t.FONT_SIZE_MD}px;
        }}

        QLabel {{
            background-color: transparent;
            color: {c['text_primary']};
        }}

        QToolTip {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_MD}px;
            padding: 8px 14px;
            font-size: {t.FONT_SIZE_SM}px;
        }}

        /* ============================================================
           BOTÕES
           ============================================================ */
        QPushButton {{
            background-color: {c['brand']};
            color: #FFFFFF;
            border: none;
            border-radius: {t.RADIUS_MD}px;
            padding: 10px 22px;
            font-weight: 600;
            font-size: {t.FONT_SIZE_MD}px;
            min-height: 20px;
            letter-spacing: 0.2px;
        }}
        QPushButton:hover {{
            background-color: {c['brand_hover']};
        }}
        QPushButton:pressed {{
            background-color: {c['brand_active']};
        }}
        QPushButton:disabled {{
            background-color: {c['bg_tertiary']};
            color: {c['text_disabled']};
        }}
        QPushButton:focus {{
            outline: none;
        }}

        /* ============================================================
           INPUTS
           ============================================================ */
        QLineEdit, QTextEdit, QPlainTextEdit,
        QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QTimeEdit {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: none;
            border-radius: {t.RADIUS_MD}px;
            padding: 10px 14px;
            selection-background-color: {c['brand_soft']};
            selection-color: {c['text_primary']};
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover,
        QSpinBox:hover, QDoubleSpinBox:hover, QDateEdit:hover, QDateTimeEdit:hover {{
            background-color: {c['bg_elevated']};
        }}
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus,
        QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QDateTimeEdit:focus {{
            background-color: {c['bg_elevated']};
        }}
        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: {c['bg_secondary']};
            color: {c['text_disabled']};
        }}
        QLineEdit[echoMode="2"] {{
            lineedit-password-character: 8226;
        }}

        /* ============================================================
           COMBOBOX
           ============================================================ */
        QComboBox {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: none;
            border-radius: {t.RADIUS_MD}px;
            padding: 8px 14px;
            min-height: 26px;
        }}
        QComboBox:hover {{ background-color: {c['bg_elevated']}; }}
        QComboBox:focus {{ background-color: {c['bg_elevated']}; }}
        QComboBox::drop-down {{
            border: none;
            width: 32px;
            subcontrol-position: center right;
        }}
        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {c['text_secondary']};
            margin-right: 12px;
        }}
        QComboBox::down-arrow:on {{
            border-top-color: {c['brand']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: none;
            border-radius: {t.RADIUS_MD}px;
            selection-background-color: {c['brand_soft']};
            selection-color: {c['text_primary']};
            padding: 6px;
            outline: none;
        }}
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: {t.RADIUS_SM}px;
            min-height: 22px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {c['bg_overlay']};
        }}

        /* ============================================================
           CHECKBOX / RADIO
           ============================================================ */
        QCheckBox, QRadioButton {{
            color: {c['text_secondary']};
            spacing: 10px;
            background-color: transparent;
            font-size: {t.FONT_SIZE_MD}px;
            padding: 2px 0;
        }}
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px; height: 18px;
            border: 1.5px solid {c['border_default']};
            background-color: {c['bg_tertiary']};
        }}
        QCheckBox::indicator {{ border-radius: {t.RADIUS_XS}px; }}
        QRadioButton::indicator {{ border-radius: 9px; }}
        QCheckBox::indicator:hover, QRadioButton::indicator:hover {{
            border-color: {c['brand']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {c['brand']};
            border-color: {c['brand']};
            image: none;
        }}
        QRadioButton::indicator:checked {{
            background-color: {c['brand']};
            border-color: {c['brand']};
        }}

        /* ============================================================
           TABELAS
           ============================================================ */
        QTableView, QTableWidget, QTreeView, QListView {{
            background-color: {c['bg_primary']};
            alternate-background-color: {c['table_row_odd']};
            gridline-color: transparent;
            border: none;
            border-radius: {t.RADIUS_LG}px;
            selection-background-color: {c['table_row_selected']};
            selection-color: {c['text_primary']};
            outline: none;
            font-size: {t.FONT_SIZE_MD}px;
        }}
        QTableView::item, QTableWidget::item, QTreeView::item, QListView::item {{
            padding: 12px 16px;
            border: none;
        }}
        QTableView::item:hover, QTableWidget::item:hover,
        QTreeView::item:hover, QListView::item:hover {{
            background-color: {c['table_row_hover']};
        }}
        QTableView::item:selected, QTableWidget::item:selected,
        QTreeView::item:selected, QListView::item:selected {{
            background-color: {c['table_row_selected']};
            color: {c['text_primary']};
            font-weight: 600;
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
            font-weight: 600;
            font-size: {t.FONT_SIZE_SM}px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        QHeaderView::section:first {{ border-top-left-radius: {t.RADIUS_LG}px; }}
        QHeaderView::section:last  {{ border-top-right-radius: {t.RADIUS_LG}px; }}

        /* ============================================================
           SCROLLBARS (6px, rounded, transparent track)
           ============================================================ */
        QScrollBar:vertical {{
            background-color: transparent;
            width: 8px;
            margin: 4px 2px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {c['border_default']};
            border-radius: 4px;
            min-height: 40px;
        }}
        QScrollBar::handle:vertical:hover {{ background-color: {c['border_strong']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none; border: none; height: 0px;
        }}
        QScrollBar:horizontal {{
            background-color: transparent;
            height: 8px;
            margin: 2px 4px;
        }}
        QScrollBar::handle:horizontal {{
            background-color: {c['border_default']};
            border-radius: 4px;
            min-width: 40px;
        }}
        QScrollBar::handle:horizontal:hover {{ background-color: {c['border_strong']}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none; border: none; width: 0px;
        }}

        /* ============================================================
           MENUS + MESSAGEBOX
           ============================================================ */
        QMenu {{
            background-color: {c['bg_elevated']};
            color: {c['text_primary']};
            border: none;
            border-radius: {t.RADIUS_MD}px;
            padding: 6px;
        }}
        QMenu::item {{
            padding: 8px 22px;
            border-radius: {t.RADIUS_SM}px;
            min-width: 160px;
        }}
        QMenu::item:selected {{
            background-color: {c['bg_overlay']};
            color: {c['text_primary']};
        }}
        QMenu::separator {{
            height: 1px;
            background-color: {c['border_subtle']};
            margin: 4px 8px;
        }}

        QMessageBox {{
            background-color: {c['bg_elevated']};
        }}
        QMessageBox QLabel {{
            color: {c['text_primary']};
            background-color: transparent;
            font-size: {t.FONT_SIZE_MD}px;
            padding: 8px 4px;
        }}
        QMessageBox QPushButton {{
            min-width: 90px;
            padding: 8px 18px;
        }}

        /* ============================================================
           TABS (underline style)
           ============================================================ */
        QTabWidget::pane {{
            border: none;
            border-radius: {t.RADIUS_MD}px;
            background-color: {c['bg_elevated']};
            top: -1px;
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {c['text_tertiary']};
            padding: 12px 24px;
            border: none;
            border-bottom: 2px solid transparent;
            font-weight: 600;
            font-size: {t.FONT_SIZE_MD}px;
            letter-spacing: 0.2px;
        }}
        QTabBar::tab:selected {{
            color: {c['text_primary']};
            border-bottom: 2px solid {c['brand']};
        }}
        QTabBar::tab:hover:!selected {{
            color: {c['text_secondary']};
            border-bottom: 2px solid {c['border_default']};
        }}

        /* ============================================================
           GROUPBOX / FRAMES
           ============================================================ */
        QGroupBox {{
            border: none;
            border-radius: {t.RADIUS_LG}px;
            margin-top: 16px;
            padding: 16px;
            color: {c['text_primary']};
            font-weight: 600;
            background-color: {c['bg_elevated']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 14px;
            padding: 0 8px;
            color: {c['text_secondary']};
            background-color: {c['bg_primary']};
            font-size: {t.FONT_SIZE_SM}px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* ============================================================
           PROGRESS BAR
           ============================================================ */
        QProgressBar {{
            background-color: {c['bg_tertiary']};
            border: none;
            border-radius: 4px;
            text-align: center;
            color: {c['text_primary']};
            font-weight: 600;
            height: 6px;
        }}
        QProgressBar::chunk {{
            background-color: {c['brand']};
            border-radius: 4px;
        }}

        /* ============================================================
           SPLITTER
           ============================================================ */
        QSplitter::handle {{
            background-color: {c['border_subtle']};
        }}
        QSplitter::handle:horizontal {{ width: 1px; }}
        QSplitter::handle:vertical   {{ height: 1px; }}

        /* ============================================================
           DIALOGS
           ============================================================ */
        QDialog {{
            background-color: {c['bg_primary']};
        }}
        QDialog > QFrame {{
            background-color: transparent;
        }}
        QDialog QPushButton {{
            min-width: 100px;
            padding: 10px 20px;
        }}

        /* ============================================================
           STATUS BAR
           ============================================================ */
        QStatusBar {{
            background-color: {c['bg_secondary']};
            color: {c['text_secondary']};
            border: none;
            padding: 4px 12px;
            font-size: {t.FONT_SIZE_SM}px;
        }}
        QStatusBar::item {{
            border: none;
        }}

        /* ============================================================
           SLIDER
           ============================================================ */
        QSlider::groove:horizontal {{
            height: 4px;
            background: {c['bg_tertiary']};
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {c['brand']};
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {c['brand_hover']};
        }}
        QSlider::sub-page:horizontal {{
            background: {c['brand']};
            border-radius: 2px;
        }}
        """

    def apply_to_app(self, app):
        """Aplica o tema à aplicação Qt."""
        app.setStyleSheet(self.get_stylesheet())


# Instância global do gerenciador de temas
theme_manager = ThemeManager()


def setup_theme(settings) -> Dict[str, str]:
    """
    Configura o tema baseado nas configurações do sistema.
    Retorna um dict de cores para uso nos componentes.
    """
    tema_config = settings.configuracoes.get("tema", "Premium Escuro")

    if tema_config == "Claro":
        theme_manager.set_mode(ThemeMode.LIGHT)
    else:
        theme_manager.set_mode(ThemeMode.DARK)

    colors = cw_theme.colors

    # Aliases para compatibilidade com código existente
    return {
        "fundo": cw_theme.colors["bg_primary"],
        "sidebar": cw_theme.colors["sidebar_bg"],
        "sidebar_card": cw_theme.colors["bg_elevated"],
        "header": cw_theme.colors["header_bg"],
        "header_bg": cw_theme.colors["header_bg"],
        "header_tag": cw_theme.colors["brand"],
        "header_title": cw_theme.colors["text_primary"],
        "header_subtitle": cw_theme.colors["text_secondary"],
        "principal": cw_theme.colors["brand"],
        "hover": cw_theme.colors["brand_hover"],
        "texto": cw_theme.colors["text_primary"],
        "texto_suave": cw_theme.colors["text_secondary"],
        "card_bg": cw_theme.colors["card_bg"],
        "card_text": cw_theme.colors["text_primary"],
        "muted_border": cw_theme.colors["border_subtle"],
        "surface_alt": cw_theme.colors["bg_tertiary"],
        "accent": cw_theme.colors["brand"],
        "divider": cw_theme.colors["border_default"],
        "shadow": "#000000",
        "font_family": cw_theme.spacing.FONT_FAMILY,

        # Cores de acento
        "brand": cw_theme.colors["brand"],
        "brand_soft": cw_theme.colors["brand_soft"],
        "emerald": cw_theme.colors["emerald"],
        "emerald_soft": cw_theme.colors["emerald_soft"],
        "sky": cw_theme.colors["sky"],
        "sky_soft": cw_theme.colors["sky_soft"],
        "amber": cw_theme.colors["amber"],
        "amber_soft": cw_theme.colors["amber_soft"],
        "violet": cw_theme.colors["violet"],
        "violet_soft": cw_theme.colors["violet_soft"],
        "cyan": cw_theme.colors["cyan"],
        "cyan_soft": cw_theme.colors["cyan_soft"],
        "rose": cw_theme.colors["rose"],
        "rose_soft": cw_theme.colors["rose_soft"],
        "success": cw_theme.colors["success"],
        "warning": cw_theme.colors["warning"],
        "error": cw_theme.colors["error"],
        "info": cw_theme.colors["info"],

        # Charts
        "chart_bg": cw_theme.colors["chart_bg"],
        "chart_grid": cw_theme.colors["chart_grid"],
        "chart_text": cw_theme.colors["chart_text"],
    }
