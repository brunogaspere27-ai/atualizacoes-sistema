"""
CW Sidebar - Sidebar profissional para CW Transportadora
Design System baseado em Linear, Stripe, Attio, Plane

Características:
- Logo CW Transportadora
- Menu agrupado por seções
- Item ativo claramente identificado
- Hover elegante
- Ícones profissionais
- Largura adequada (260px)
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional, List, Callable

from ui.theme.cw_theme import cw_theme, CWSpacing, CWRadius


class SidebarSection:
    """Seção do sidebar com itens"""
    
    def __init__(self, title: str, items: List[dict]):
        self.title = title
        self.items = items  # [{'id': 'dashboard', 'label': 'Dashboard', 'icon': 'home'}]


class CWSidebar(QWidget):
    """Sidebar profissional CW Transportadora"""
    
    # Sinal quando um item é clicado
    item_clicked = Signal(str)  # item_id
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._sections: List[SidebarSection] = []
        self._active_item: Optional[str] = None
        self._bottom_widgets: List[QWidget] = []
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Configura layout do sidebar"""
        self.setFixedWidth(260)
        
        c = cw_theme.colors
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        # Logo container
        logo_container = QFrame()
        logo_container.setFixedHeight(64)
        logo_container.setStyleSheet(f"""
            QFrame {{
                background-color: {c['sidebar_bg']};
                border: none;
            }}
        """)
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(
            cw_theme.spacing.XL,
            cw_theme.spacing.LG,
            cw_theme.spacing.XL,
            cw_theme.spacing.LG
        )
        logo_container.setLayout(logo_layout)
        
        # Logo text
        logo_label = QLabel("CW")
        logo_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_XL,
            bold=True
        ))
        logo_label.setStyleSheet(f"""
            QLabel {{
                color: {c['sidebar_active']};
                background: transparent;
            }}
        """)
        logo_layout.addWidget(logo_label)
        
        subtitle_label = QLabel("Transportadora")
        subtitle_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_SM
        ))
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {c['sidebar_text_muted']};
                background: transparent;
            }}
        """)
        logo_layout.addWidget(subtitle_label)
        
        logo_layout.addStretch()
        
        self.layout.addWidget(logo_container)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"""
            QFrame {{
                background-color: {c['sidebar_border']};
            }}
        """)
        self.layout.addWidget(separator)
        
        # Scroll area for menu items
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(f"background: {c['sidebar_bg']};")
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(
            cw_theme.spacing.MD,
            cw_theme.spacing.XL,
            cw_theme.spacing.MD,
            cw_theme.spacing.MD
        )
        self.scroll_layout.setSpacing(cw_theme.spacing.LG)
        self.scroll_content.setLayout(self.scroll_layout)
        
        self.scroll.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll, 1)
        
        # Bottom area (user info, settings)
        self._add_bottom_area()
    
    def add_bottom_widget(self, widget: QWidget):
        """Adiciona widget à área inferior do sidebar"""
        self._bottom_widgets.append(widget)
        # Recriar área inferior com novos widgets
        self._rebuild_bottom_area()
    
    def _add_bottom_area(self):
        """Adiciona área inferior (configurações, usuário)"""
        c = cw_theme.colors
        
        self.bottom_container = QFrame()
        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.setContentsMargins(
            cw_theme.spacing.MD,
            cw_theme.spacing.MD,
            cw_theme.spacing.MD,
            cw_theme.spacing.MD
        )
        self.bottom_layout.setSpacing(cw_theme.spacing.SM)
        self.bottom_container.setLayout(self.bottom_layout)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"""
            QFrame {{
                background-color: {c['sidebar_border']};
            }}
        """)
        self.bottom_layout.addWidget(separator)
        
        # Settings button
        settings_btn = QPushButton("⚙ Configurações")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c['sidebar_text_muted']};
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: {cw_theme.spacing.SM}px {cw_theme.spacing.MD}px;
                text-align: left;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
            }}
            QPushButton:hover {{
                background-color: {c['sidebar_hover']};
                color: {c['sidebar_text']};
            }}
        """)
        settings_btn.clicked.connect(lambda: self.item_clicked.emit('configuracoes'))
        self.bottom_layout.addWidget(settings_btn)
        
        self.layout.addWidget(self.bottom_container)
    
    def _rebuild_bottom_area(self):
        """Reconstrói área inferior com widgets adicionados"""
        c = cw_theme.colors
        
        # Remove bottom container existente
        if hasattr(self, 'bottom_container'):
            self.layout.removeWidget(self.bottom_container)
            self.bottom_container.deleteLater()
        
        # Criar nova área inferior
        self.bottom_container = QFrame()
        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.setContentsMargins(
            cw_theme.spacing.MD,
            cw_theme.spacing.MD,
            cw_theme.spacing.MD,
            cw_theme.spacing.MD
        )
        self.bottom_layout.setSpacing(cw_theme.spacing.SM)
        self.bottom_container.setLayout(self.bottom_layout)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet(f"""
            QFrame {{
                background-color: {c['sidebar_border']};
            }}
        """)
        self.bottom_layout.addWidget(separator)
        
        # Settings button
        settings_btn = QPushButton("⚙ Configurações")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {c['sidebar_text_muted']};
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                padding: {cw_theme.spacing.SM}px {cw_theme.spacing.MD}px;
                text-align: left;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
            }}
            QPushButton:hover {{
                background-color: {c['sidebar_hover']};
                color: {c['sidebar_text']};
            }}
        """)
        settings_btn.clicked.connect(lambda: self.item_clicked.emit('configuracoes'))
        self.bottom_layout.addWidget(settings_btn)
        
        # Adicionar widgets customizados
        for widget in self._bottom_widgets:
            self.bottom_layout.addWidget(widget)
        
        self.layout.addWidget(self.bottom_container)
    
    def add_section(self, title: str, items: List[dict]):
        """Adiciona seção ao sidebar"""
        section = SidebarSection(title, items)
        self._sections.append(section)
        self._render_section(section)
    
    def _render_section(self, section: SidebarSection):
        """Renderiza seção no sidebar"""
        c = cw_theme.colors
        
        # Section title
        title_label = QLabel(section.title.upper())
        title_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_XS,
            bold=True
        ))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {c['sidebar_text_muted']};
                background: transparent;
                padding: {cw_theme.spacing.SM}px 0;
            }}
        """)
        self.scroll_layout.addWidget(title_label)
        
        # Menu items
        for item in section.items:
            item_btn = QPushButton(item['label'])
            item_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            item_btn.setProperty('item_id', item['id'])
            
            # Default style
            item_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                color: {c['sidebar_text_muted']};
                    border: none;
                    border-radius: {cw_theme.radius.MD}px;
                    padding: {cw_theme.spacing.SM}px {cw_theme.spacing.MD}px;
                    text-align: left;
                    font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                }}
                QPushButton:hover {{
                    background-color: {c['sidebar_hover']};
                    color: {c['sidebar_text']};
                }}
            """)
            
            # Click handler
            item_btn.clicked.connect(
                lambda checked, item_id=item['id']: self.item_clicked.emit(item_id)
            )
            
            self.scroll_layout.addWidget(item_btn)
    
    def set_active_item(self, item_id: str):
        """Define item ativo"""
        self._active_item = item_id
        self._update_active_styles()
    
    def _update_active_styles(self):
        """Atualiza estilos do item ativo"""
        c = cw_theme.colors
        
        # Encontrar todos os botões de item
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if isinstance(widget, QPushButton) and widget.property('item_id'):
                item_id = widget.property('item_id')
                
                if item_id == self._active_item:
                    # Active style
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background-color: {c['sidebar_active_bg']};
                            color: {c['sidebar_active']};
                            border: none;
                            border-radius: {cw_theme.radius.MD}px;
                            padding: {cw_theme.spacing.SM}px {cw_theme.spacing.MD}px;
                            text-align: left;
                            font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                            font-weight: 600;
                        }}
                    """)
                else:
                    # Default style
                    widget.setStyleSheet(f"""
                        QPushButton {{
                            background: transparent;
                            color: {c['sidebar_text_muted']};
                            border: none;
                            border-radius: {cw_theme.radius.MD}px;
                            padding: {cw_theme.spacing.SM}px {cw_theme.spacing.MD}px;
                            text-align: left;
                            font-size: {cw_theme.typography.FONT_SIZE_MD}px;
                        }}
                        QPushButton:hover {{
                            background-color: {c['sidebar_hover']};
                            color: {c['sidebar_text']};
                        }}
                    """)
    
    def _apply_style(self):
        """Aplica estilos ao sidebar (Dark Mode)"""
        c = cw_theme.colors
        
        self.setStyleSheet(f"""
            CWSidebar {{
                background-color: {c['sidebar_bg']};
                border: none;
            }}
        """)
