"""Modern Card Component - CW Transportadora
Cards reutilizáveis com Dark Mode e Design System CW
"""

from enum import Enum
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QFont, QColor, QIcon
from PySide6.QtCore import Qt

from ui.theme.cw_theme import cw_theme


class CardVariant(Enum):
    """Variantes de cards."""
    DEFAULT = "default"      # Card padrão
    ELEVATED = "elevated"    # Card com mais profundidade
    OUTLINED = "outlined"    # Card apenas com borda
    FLAT = "flat"           # Card sem borda ou sombra


class CWCard(QWidget):
    """
    Card moderno com suporte a:
    - Variantes (default, elevated, outlined, flat)
    - Cabeçalho customizável
    - Conteúdo flexível
    - Dark Mode automático
    - Espaçamento consistente
    """
    
    def __init__(
        self,
        title: Optional[str] = None,
        variant: CardVariant = CardVariant.DEFAULT,
        parent=None
    ):
        super().__init__(parent)
        self.title = title
        self.variant = variant
        self.content_widgets = []
        
        # Layout principal
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(
            cw_theme.spacing.LG,
            cw_theme.spacing.LG,
            cw_theme.spacing.LG,
            cw_theme.spacing.LG
        )
        self.main_layout.setSpacing(cw_theme.spacing.MD)
        self.setLayout(self.main_layout)
        
        # Adicionar título se fornecido
        if title:
            self._create_header()
        
        # Container para conteúdo
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(cw_theme.spacing.MD)
        self.main_layout.addLayout(self.content_layout)
        
        self._apply_style()
    
    def _create_header(self):
        """Cria cabeçalho do card com título."""
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(cw_theme.spacing.MD)
        
        title_label = QLabel(self.title)
        title_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_LG, bold=True))
        title_label.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: transparent;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        self.main_layout.addLayout(header_layout)
        
        # Adicionar separador sutil
        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"background-color: {cw_theme.colors['border_subtle']};")
        self.main_layout.addWidget(separator)
    
    def _apply_style(self):
        """Aplica styling baseado na variante e tema."""
        if self.variant == CardVariant.DEFAULT:
            stylesheet = f"""
                QWidget {{
                    background-color: {cw_theme.colors['card_bg']};
                    border: 1px solid {cw_theme.colors['card_border']};
                    border-radius: {cw_theme.radius.LG}px;
                }}
            """
        elif self.variant == CardVariant.ELEVATED:
            stylesheet = f"""
                QWidget {{
                    background-color: {cw_theme.colors['bg_elevated']};
                    border: 1px solid {cw_theme.colors['border_subtle']};
                    border-radius: {cw_theme.radius.LG}px;
                }}
            """
        elif self.variant == CardVariant.OUTLINED:
            stylesheet = f"""
                QWidget {{
                    background-color: transparent;
                    border: 2px solid {cw_theme.colors['border_default']};
                    border-radius: {cw_theme.radius.LG}px;
                }}
            """
        elif self.variant == CardVariant.FLAT:
            stylesheet = f"""
                QWidget {{
                    background-color: {cw_theme.colors['bg_secondary']};
                    border: none;
                    border-radius: {cw_theme.radius.LG}px;
                }}
            """
        
        self.setStyleSheet(stylesheet)
    
    def add_widget(self, widget: QWidget):
        """Adiciona widget ao conteúdo do card."""
        self.content_layout.addWidget(widget)
        self.content_widgets.append(widget)
    
    def add_layout(self, layout):
        """Adiciona layout ao conteúdo do card."""
        self.content_layout.addLayout(layout)
    
    def clear_content(self):
        """Remove todos os widgets do conteúdo."""
        while self.content_layout.count():
            self.content_layout.takeAt(0).widget()?.deleteLater()
        self.content_widgets.clear()


class KPICard(QWidget):
    """
    Card especializado para KPIs e métricas
    Mostra valor principal, descrição e mudança
    """
    
    def __init__(
        self,
        title: str,
        value: str,
        unit: str = "",
        change: Optional[str] = None,
        change_positive: bool = True,
        parent=None
    ):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.unit = unit
        self.change = change
        self.change_positive = change_positive
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Monta interface do KPI card."""
        layout = QVBoxLayout()
        layout.setContentsMargins(cw_theme.spacing.LG, cw_theme.spacing.LG, cw_theme.spacing.LG, cw_theme.spacing.LG)
        layout.setSpacing(cw_theme.spacing.MD)
        self.setLayout(layout)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
        title_label.setStyleSheet(f"color: {cw_theme.colors['text_secondary']}; background: transparent;")
        layout.addWidget(title_label)
        
        # Valor principal
        value_text = f"{self.value}{self.unit}"
        value_label = QLabel(value_text)
        value_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_2XL, bold=True))
        value_label.setStyleSheet(f"color: {cw_theme.colors['text_primary']}; background: transparent;")
        layout.addWidget(value_label)
        
        # Mudança (se fornecida)
        if self.change:
            change_color = cw_theme.colors['success'] if self.change_positive else cw_theme.colors['error']
            change_label = QLabel(self.change)
            change_label.setFont(cw_theme.get_font(cw_theme.typography.FONT_SIZE_SM))
            change_label.setStyleSheet(f"color: {change_color}; background: transparent;")
            layout.addWidget(change_label)
        
        layout.addStretch()
        
        # Aplicar styling de card
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {cw_theme.colors['card_bg']};
                border: 1px solid {cw_theme.colors['card_border']};
                border-radius: {cw_theme.radius.LG}px;
            }}
        """)
    
    def set_value(self, value: str):
        """Atualiza o valor exibido."""
        self.value = value
        # Encontrar label de valor e atualizar
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and cw_theme.typography.FONT_SIZE_2XL in str(widget.font().pointSize()):
                widget.setText(f"{value}{self.unit}")
                break
