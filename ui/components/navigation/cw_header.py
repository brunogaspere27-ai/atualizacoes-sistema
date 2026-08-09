"""
CW Header - Header profissional para CW Transportadora
Design System baseado em Linear, Stripe, Attio

Características:
- Breadcrumb de navegação
- Título da página
- Busca global
- Notificações
- Perfil do usuário
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional

from ui.theme.cw_theme import cw_theme, CWSpacing, CWRadius
from utils.avatar import AvatarWidget
from services.auth_service import auth_service


class CWHeader(QWidget):
    """Header profissional CW Transportadora"""
    
    # Sinais
    search_requested = Signal(str)
    profile_requested = Signal()
    settings_requested = Signal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._section = ""
        self._page = ""
        self._user_name = ""
        
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        """Configura layout do header"""
        self.setFixedHeight(64)
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(
            cw_theme.spacing._2XL,
            cw_theme.spacing.LG,
            cw_theme.spacing._2XL,
            cw_theme.spacing.LG
        )
        self.layout.setSpacing(cw_theme.spacing.XL)
        self.setLayout(self.layout)
        
        # Breadcrumb
        self._add_breadcrumb()
        
        # Spacer
        self.layout.addStretch()
        
        # Search
        self._add_search()
        
        # Actions
        self._add_actions()
    
    def _add_breadcrumb(self):
        """Adiciona breadcrumb"""
        breadcrumb_container = QWidget()
        breadcrumb_layout = QVBoxLayout()
        breadcrumb_layout.setContentsMargins(0, 0, 0, 0)
        breadcrumb_layout.setSpacing(cw_theme.spacing.XS)
        breadcrumb_container.setLayout(breadcrumb_layout)
        
        # Section
        self._section_label = QLabel()
        self._section_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_XS,
            bold=True
        ))
        self._section_label.setStyleSheet(f"""
            QLabel {{
                color: {cw_theme.colors['text_tertiary']};
                background: transparent;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
        """)
        breadcrumb_layout.addWidget(self._section_label)
        
        # Page title
        self._page_label = QLabel()
        self._page_label.setFont(cw_theme.get_font(
            cw_theme.typography.FONT_SIZE_LG,
            bold=True
        ))
        self._page_label.setStyleSheet(f"""
            QLabel {{
                color: {cw_theme.colors['text_primary']};
                background: transparent;
            }}
        """)
        breadcrumb_layout.addWidget(self._page_label)
        
        self.layout.addWidget(breadcrumb_container)
    
    def _add_search(self):
        """Adiciona campo de busca"""
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Buscar (Ctrl+K)")
        self._search_input.setFixedWidth(300)
        self._search_input.setMinimumHeight(36)
        self._search_input.setMaximumHeight(36)
        
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {cw_theme.colors['bg_secondary']};
                border: 1px solid {cw_theme.colors['border_subtle']};
                border-radius: {cw_theme.radius.MD}px;
                padding: 0 {cw_theme.spacing.MD}px;
                font-size: {cw_theme.typography.FONT_SIZE_SM}px;
                color: {cw_theme.colors['text_primary']};
            }}
            QLineEdit:focus {{
                border: 1px solid {cw_theme.colors['border_focus']};
            }}
        """)
        
        self._search_input.returnPressed.connect(
            lambda: self.search_requested.emit(self._search_input.text())
        )
        
        self.layout.addWidget(self._search_input)
    
    def _add_actions(self):
        """Adiciona ações (notificações, perfil)"""
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(cw_theme.spacing.MD)
        
        # Notifications button
        self._notif_btn = QPushButton("🔔")
        self._notif_btn.setFixedSize(36, 36)
        self._notif_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._notif_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {cw_theme.colors['text_secondary']};
                border: none;
                border-radius: {cw_theme.radius.MD}px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {cw_theme.colors['bg_tertiary']};
                color: {cw_theme.colors['text_primary']};
            }}
        """)
        actions_layout.addWidget(self._notif_btn)
        
        # Profile avatar - uses AvatarWidget for photo or initials
        self._profile_avatar = AvatarWidget(
            usuario_id=None,  # Will be set in set_user
            nome=self._user_name or "Usuário",
            tamanho=40,
            parent=self
        )
        self._profile_avatar.setCursor(Qt.CursorShape.PointingHandCursor)
        self._profile_avatar.mousePressEvent = lambda e: self.profile_requested.emit()
        actions_layout.addWidget(self._profile_avatar)
        
        self.layout.addLayout(actions_layout)
    
    def set_breadcrumb(self, section: str, page: str):
        """Define breadcrumb"""
        self._section = section
        self._page = page
        self._section_label.setText(section)
        self._page_label.setText(page)
    
    def set_user(self, name: str):
        """Define nome do usuário e atualiza avatar com foto ou iniciais"""
        self._user_name = name
        
        # Get current user from auth service to get user ID
        usuario = auth_service.usuario_atual or {}
        usuario_id = usuario.get("id")
        
        # Update avatar with user ID and name
        if hasattr(self, '_profile_avatar'):
            self._profile_avatar.update_user(usuario_id, name or "Usuário")
    
    def _apply_style(self):
        """Aplica estilos ao header (Dark Mode)"""
        c = cw_theme.colors
        
        self.setStyleSheet(f"""
            CWHeader {{
                background-color: {c['bg_primary']};
                border-bottom: 1px solid {c['border_subtle']};
            }}
        """)
