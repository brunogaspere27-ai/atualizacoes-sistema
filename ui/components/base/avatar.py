"""
Avatar Component - CW Transportadora
Componente reutilizável para avatares com suporte a fotos e iniciais
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QBrush, QPen
from PySide6.QtCore import Qt, QSize, QRect

from services.perfil_service import perfil_service
from ui.theme.cw_theme import cw_theme


class AvatarSize(Enum):
    """Tamanhos padrão para avatares."""
    XS = 32      # Header, listas compactas
    SM = 40      # Comentários, mentions
    MD = 56      # Default, cards
    LG = 80      # Perfil
    XL = 120     # Modal de perfil
    XXL = 160    # Hero section


class CWAvatar(QWidget):
    """
    Avatar reutilizável com suporte a:
    - Fotos de perfil (JPEG/PNG)
    - Iniciais com cor determinística
    - Dark Mode automático
    - Fallback inteligente
    """
    
    def __init__(
        self,
        usuario_id: Optional[int] = None,
        nome: str = "Usuário",
        size: AvatarSize = AvatarSize.MD,
        parent=None
    ):
        super().__init__(parent)
        self.usuario_id = usuario_id
        self.nome = nome
        self.size = size
        self.pixmap = None
        self.use_initials = False
        
        # Obter dimensões
        size_px = size.value
        self.setFixedSize(size_px, size_px)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
            }}
        """)
        
        # Tentar carregar foto, fallback para iniciais
        self._load_avatar()
    
    def _load_avatar(self):
        """Tenta carregar foto, fallback para iniciais com cor."""
        self.pixmap = None
        self.use_initials = False
        
        # 1. Tentar carregar foto do banco de dados
        if self.usuario_id:
            foto_path = perfil_service.get_avatar_path(self.usuario_id)
            if foto_path:
                try:
                    self.pixmap = QPixmap(foto_path)
                    if not self.pixmap.isNull():
                        # Redimensionar para o tamanho do avatar
                        self.pixmap = self.pixmap.scaledToWidth(
                            self.size.value,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.update()
                        return
                except Exception as e:
                    from utils.logger import get_logger
                    logger = get_logger(__name__)
                    logger.warning(f"Erro ao carregar foto de perfil: {e}")
        
        # 2. Fallback: usar iniciais com cor determinística
        self.use_initials = True
        self.update()
    
    def set_photo(self, image_path: str) -> bool:
        """Atualiza a foto de perfil e salva no banco."""
        if not self.usuario_id:
            return False
        
        # Salvar no banco via serviço
        if perfil_service.save_avatar(self.usuario_id, image_path):
            # Recarregar avatar
            self._load_avatar()
            return True
        return False
    
    def remove_photo(self) -> bool:
        """Remove a foto de perfil."""
        if not self.usuario_id:
            return False
        
        if perfil_service.remove_avatar(self.usuario_id):
            self._load_avatar()
            return True
        return False
    
    def paintEvent(self, event):
        """Renderiza o avatar (foto ou iniciais)."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        size_px = self.size.value
        rect = QRect(0, 0, size_px, size_px)
        
        # Se temos foto, desenhar
        if self.pixmap is not None and not self.pixmap.isNull():
            # Desenhar foto como circular
            painter.save()
            painter.setClipRect(rect)
            painter.drawPixmap(rect, self.pixmap)
            painter.restore()
        else:
            # Desenhar fundo colorido com iniciais
            bg_color = QColor(perfil_service.get_avatar_color(self.nome))
            painter.fillRect(rect, bg_color)
            
            # Desenhar iniciais
            initials = perfil_service.get_initials(self.nome)
            
            font_size = {
                AvatarSize.XS: 10,
                AvatarSize.SM: 12,
                AvatarSize.MD: 16,
                AvatarSize.LG: 24,
                AvatarSize.XL: 32,
                AvatarSize.XXL: 48,
            }.get(self.size, 16)
            
            font = QFont(cw_theme.typography.FONT_FAMILY_QT, font_size)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QColor("#FFFFFF"))  # Texto branco
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, initials)
        
        # Desenhar borda sutil (apenas em sizes maiores)
        if self.size.value > 40:
            border_color = QColor(cw_theme.colors['border_subtle'])
            painter.setPen(QPen(border_color, 1))
            painter.drawRect(0, 0, size_px - 1, size_px - 1)
    
    def sizeHint(self) -> QSize:
        """Retorna tamanho sugerido."""
        size_px = self.size.value
        return QSize(size_px, size_px)
