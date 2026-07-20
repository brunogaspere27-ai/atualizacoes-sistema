"""
SaaS Premium Theme v2.0 - CW Transportadora
Design System inspirado em Linear, Stripe, ClickUp, Vercel, Notion, Framer

Paleta:
- Fundo principal: #0B0B0B
- Fundo cards: #151515
- Bordas: #262626
- Texto primário: #FFFFFF
- Texto secundário: #A1A1AA
- Vermelho CW: #DC2626
- Vermelho CW hover: #EF4444
- Vermelho CW soft: rgba(220, 38, 38, 0.1)
"""

from enum import Enum
from typing import Optional


class AccentColor(Enum):
    """Cores de destaque - apenas vermelho CW e variações."""
    CW = "cw"
    CW_SOFT = "cw_soft"
    CW_HOVER = "cw_hover"
    CW_ACTIVE = "cw_active"


class SaaSTheme:
    """Theme Manager para design SaaS premium."""

    # Cores principais
    COLORS = {
        # Fundos
        'bg_primary': '#0B0B0B',
        'bg_secondary': '#111111',
        'bg_tertiary': '#1A1A1A',
        'bg_surface': '#151515',
        'bg_overlay': 'rgba(255, 255, 255, 0.05)',
        'bg_hover': 'rgba(255, 255, 255, 0.08)',
        'bg_active': 'rgba(255, 255, 255, 0.12)',

        # Cards
        'card_bg': '#151515',
        'card_border': '#262626',
        'card_border_hover': '#3A3A3A',

        # Texto
        'text_primary': '#FFFFFF',
        'text_secondary': '#A1A1AA',
        'text_tertiary': '#71717A',
        'text_disabled': '#525252',
        'text_inverse': '#0B0B0B',

        # Bordas
        'border_default': '#262626',
        'border_strong': '#3A3A3A',
        'border_subtle': '#1F1F1F',

        # Vermelho CW
        'cw': '#DC2626',
        'cw_hover': '#EF4444',
        'cw_active': '#B91C1C',
        'cw_soft': 'rgba(220, 38, 38, 0.1)',
        'cw_softer': 'rgba(220, 38, 38, 0.05)',

        # Status
        'success': '#10B981',
        'success_soft': 'rgba(16, 185, 129, 0.1)',
        'warning': '#F59E0B',
        'warning_soft': 'rgba(245, 158, 11, 0.1)',
        'error': '#EF4444',
        'error_soft': 'rgba(239, 68, 68, 0.1)',
        'info': '#3B82F6',
        'info_soft': 'rgba(59, 130, 246, 0.1)',

        # Gráficos
        'chart_bg': '#0B0B0B',
        'chart_grid': '#262626',
        'chart_text': '#A1A1AA',
        'chart_line': '#DC2626',
    }

    # Tipografia
    FONT_FAMILY = "Inter"
    FONT_FAMILY_QT = "Inter"

    FONT_SIZE_XS = 11
    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 18
    FONT_SIZE_2XL = 24
    FONT_SIZE_3XL = 32
    FONT_SIZE_4XL = 48

    # Espaçamento
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 12
    SPACING_LG = 16
    SPACING_XL = 24
    SPACING_2XL = 32
    SPACING_3XL = 48
    SPACING_4XL = 64

    # Border radius
    RADIUS_SM = 6
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_2XL = 20
    RADIUS_3XL = 24
    RADIUS_FULL = 9999

    # Sombras
    SHADOW_SM = "0 1px 2px rgba(0, 0, 0, 0.3)"
    SHADOW_MD = "0 4px 6px rgba(0, 0, 0, 0.4)"
    SHADOW_LG = "0 10px 15px rgba(0, 0, 0, 0.5)"
    SHADOW_XL = "0 20px 25px rgba(0, 0, 0, 0.6)"
    SHADOW_CW = "0 0 30px rgba(220, 38, 38, 0.3)"

    # Transições
    TRANSITION_FAST = "150ms"
    TRANSITION_NORMAL = "200ms"
    TRANSITION_SLOW = "300ms"

    @classmethod
    def get_color(cls, color_name: str) -> str:
        """Retorna uma cor pelo nome."""
        return cls.COLORS.get(color_name, '#FFFFFF')

    @classmethod
    def get_font(cls, size: int = 14, bold: bool = False) -> QFont:
        """Retorna uma QFont configurada."""
        from PySide6.QtGui import QFont
        weight = QFont.Weight.Bold if bold else QFont.Weight.Normal
        return QFont(cls.FONT_FAMILY_QT, size, weight)

    @classmethod
    def get_stylesheet(cls) -> str:
        """Retorna o stylesheet global."""
        c = cls.COLORS
        t = cls

        return f"""
        /* Global */
        QMainWindow, QDialog {{
            background-color: {c['bg_primary']};
            color: {c['text_primary']};
        }}

        QWidget {{
            background-color: transparent;
            color: {c['text_primary']};
        }}

        /* ScrollBars */
        QScrollBar:vertical {{
            background: {c['bg_secondary']};
            width: 8px;
            margin: 0px;
            border-radius: 4px;
        }}

        QScrollBar::handle:vertical {{
            background: {c['border_default']};
            border-radius: 4px;
            min-height: 40px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {c['border_strong']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            height: 0px;
            background: none;
        }}

        QScrollBar:horizontal {{
            background: {c['bg_secondary']};
            height: 8px;
            margin: 0px;
            border-radius: 4px;
        }}

        QScrollBar::handle:horizontal {{
            background: {c['border_default']};
            border-radius: 4px;
            min-width: 40px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: {c['border_strong']};
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            width: 0px;
            background: none;
        }}

        /* Labels */
        QLabel {{
            color: {c['text_primary']};
            background: transparent;
        }}

        /* Buttons */
        QPushButton {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 10px 20px;
            font-size: {t.FONT_SIZE_MD}px;
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

        /* Primary Button (CW Red) */
        QPushButton[class="primary"] {{
            background-color: {c['cw']};
            color: #FFFFFF;
            border: 1px solid {c['cw']};
        }}

        QPushButton[class="primary"]:hover {{
            background-color: {c['cw_hover']};
            border-color: {c['cw_hover']};
        }}

        QPushButton[class="primary"]:pressed {{
            background-color: {c['cw_active']};
            border-color: {c['cw_active']};
        }}

        /* LineEdit */
        QLineEdit {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 10px 16px;
            font-size: {t.FONT_SIZE_MD}px;
        }}

        QLineEdit:hover {{
            border-color: {c['border_strong']};
        }}

        QLineEdit:focus {{
            border-color: {c['cw']};
            background-color: {c['bg_surface']};
        }}

        QLineEdit:disabled {{
            background-color: {c['bg_secondary']};
            color: {c['text_disabled']};
        }}

        /* ComboBox */
        QComboBox {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 10px 16px;
            font-size: {t.FONT_SIZE_MD}px;
            min-height: 20px;
        }}

        QComboBox:hover {{
            border-color: {c['border_strong']};
        }}

        QComboBox:focus {{
            border-color: {c['cw']};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 30px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {c['text_secondary']};
        }}

        QComboBox QAbstractItemView {{
            background-color: {c['bg_surface']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            selection-background-color: {c['cw_soft']};
            selection-color: {c['cw']};
        }}

        /* CheckBox */
        QCheckBox {{
            color: {c['text_primary']};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {c['border_default']};
            background-color: {c['bg_tertiary']};
            border-radius: 4px;
        }}

        QCheckBox::indicator:hover {{
            border-color: {c['border_strong']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['cw']};
            border-color: {c['cw']};
        }}

        /* Table */
        QTableWidget {{
            background-color: {c['bg_surface']};
            border: 1px solid {c['border_default']};
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

        /* Frame */
        QFrame {{
            background-color: transparent;
            border: none;
        }}

        /* Menu */
        QMenu {{
            background-color: {c['bg_surface']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 16px;
            border-radius: {t.RADIUS_MD}px;
        }}

        QMenu::item:selected {{
            background-color: {c['bg_hover']};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {c['border_default']};
            margin: 4px 8px;
        }}

        /* TabWidget */
        QTabWidget::pane {{
            border: none;
            background-color: transparent;
        }}

        QTabBar::tab {{
            background-color: transparent;
            color: {c['text_secondary']};
            border: none;
            padding: 10px 20px;
            font-size: {t.FONT_SIZE_MD}px;
        }}

        QTabBar::tab:selected {{
            color: {c['text_primary']};
            font-weight: 600;
        }}

        QTabBar::tab:hover {{
            color: {c['text_primary']};
        }}

        /* ProgressBar */
        QProgressBar {{
            background-color: {c['bg_tertiary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_FULL}px;
            height: 8px;
            text-align: center;
        }}

        QProgressBar::chunk {{
            background-color: {c['cw']};
            border-radius: {t.RADIUS_FULL}px;
        }}

        /* Slider */
        QSlider::groove:horizontal {{
            background-color: {c['bg_tertiary']};
            height: 4px;
            border-radius: 2px;
        }}

        QSlider::handle:horizontal {{
            background-color: {c['cw']};
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }}

        QSlider::sub-page:horizontal {{
            background-color: {c['cw']};
            border-radius: 2px;
        }}

        /* SpinBox */
        QSpinBox, QDoubleSpinBox {{
            background-color: {c['bg_tertiary']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            padding: 10px 16px;
            font-size: {t.FONT_SIZE_MD}px;
        }}

        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {c['border_strong']};
        }}

        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {c['cw']};
        }}

        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            border: none;
            background-color: transparent;
            width: 20px;
        }}

        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {c['bg_hover']};
        }}

        /* ToolTip */
        QToolTip {{
            background-color: {c['bg_surface']};
            color: {c['text_primary']};
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_MD}px;
            padding: 8px 12px;
            font-size: {t.FONT_SIZE_SM}px;
        }}

        /* GroupBox */
        QGroupBox {{
            background-color: transparent;
            border: 1px solid {c['border_default']};
            border-radius: {t.RADIUS_LG}px;
            margin-top: 20px;
            padding: 16px;
            font-size: {t.FONT_SIZE_MD}px;
            font-weight: 600;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px;
        }}
        """


# Instância global do tema
saas_theme = SaaSTheme()
