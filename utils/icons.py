"""
Gerenciador de ícones.
"""
from PySide6.QtGui import QPixmap, QColor, QPainter
from PySide6.QtCore import Qt


def get_icon(name, size=24, color="#ffffff"):
    """Retorna ícone como QPixmap."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setPen(QColor(color))
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, name[0].upper())
    painter.end()
    
    return pixmap