"""Componente de Busca Global Moderno - PySide6

Implementa busca inteligente estilo ERP profissional (Notion, Attio, Linear):
- Debounce de 300ms
- Pesquisa instantânea
- Loading durante busca
- Enter abre primeiro resultado
- Esc limpa pesquisa
- Seta ↑ ↓ navega resultados
- Resultados agrupados por categoria
"""

from __future__ import annotations

from typing import Callable, Optional, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
    QScrollArea, QFrame, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, Signal, QEvent
from PySide6.QtGui import QKeyEvent, QCursor

from services.search_service import search_service, SearchResult
from utils.icons import get_icon
from utils.logger import get_logger

logger = get_logger(__name__)


class ModernSearchWidget(QWidget):
    """Widget de busca global moderno com debounce e navegação por teclado."""
    
    # Sinais
    result_selected = Signal(str, str, int)  # tela, categoria, registro_id
    search_cleared = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._debounce_timer: Optional[QTimer] = None
        self._current_results: List[SearchResult] = []
        self._selected_index = -1
        self._is_loading = False
        
        self._setup_ui()
        self._setup_debounce()
        
    def _setup_ui(self):
        """Configura a interface do widget de busca."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Campo de busca
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar clientes, notas, operações, viagens...")
        self.search_input.setMinimumHeight(44)
        
        # Ícone de busca
        search_icon = get_icon("search", (20, 20), "#9CA3AF")
        self.search_input.setTextMargins(40, 0, 40, 0)
        
        # Botão de limpar
        self.clear_btn = QPushButton()
        self.clear_btn.setIcon(get_icon("close", (16, 16), "#9CA3AF"))
        self.clear_btn.setFixedSize(24, 24)
        self.clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.clear_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: #F3F4F6;
            }
        """)
        self.clear_btn.hide()
        self.clear_btn.clicked.connect(self._clear_search)
        
        # Layout do campo de busca
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(12, 0, 12, 0)
        search_layout.setSpacing(8)
        
        # Ícone de busca (fixo à esquerda)
        search_icon_label = QLabel()
        search_icon_label.setPixmap(search_icon.pixmap((20, 20)))
        search_icon_label.setStyleSheet("background: transparent;")
        
        search_layout.addWidget(search_icon_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.clear_btn)
        
        search_container = QFrame()
        search_container.setLayout(search_layout)
        search_container.setStyleSheet("""
            QFrame {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
        """)
        
        # Lista de resultados
        self.results_list = QListWidget()
        self.results_list.setMinimumHeight(200)
        self.results_list.setMaximumHeight(400)
        self.results_list.setStyleSheet("""
            QListWidget {
                background: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background: #F3F4F6;
            }
            QListWidget::item:selected {
                background: #E5E7EB;
            }
        """)
        self.results_list.hide()
        
        # Label de loading
        self.loading_label = QLabel("Buscando...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #6B7280;
                font-size: 14px;
                padding: 12px;
            }
        """)
        self.loading_label.hide()
        
        # Label de sem resultados
        self.no_results_label = QLabel("Nenhum resultado encontrado")
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setStyleSheet("""
            QLabel {
                color: #6B7280;
                font-size: 14px;
                padding: 12px;
            }
        """)
        self.no_results_label.hide()
        
        layout.addWidget(search_container)
        layout.addWidget(self.loading_label)
        layout.addWidget(self.no_results_label)
        layout.addWidget(self.results_list)
        
        self.setLayout(layout)
        
        # Conectar eventos
        self.search_input.textChanged.connect(self._on_text_changed)
        self.search_input.returnPressed.connect(self._on_return_pressed)
        self.results_list.itemClicked.connect(self._on_item_clicked)
        
        # Instalar filtro de eventos para navegação por teclado
        self.search_input.installEventFilter(self)
        
    def _setup_debounce(self):
        """Configura o timer de debounce."""
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._perform_search)
        
    def _on_text_changed(self, text: str):
        """Manipula mudanças no texto de busca com debounce."""
        if not text.strip():
            self._clear_search()
            return
            
        self.clear_btn.show()
        
        # Reiniciar timer de debounce
        self._debounce_timer.stop()
        self._debounce_timer.start(300)  # 300ms
        
    def _perform_search(self):
        """Executa a busca após o debounce."""
        query = self.search_input.text().strip()
        
        if not query:
            self._clear_search()
            return
            
        self._is_loading = True
        self.loading_label.show()
        self.results_list.hide()
        self.no_results_label.hide()
        
        # Executar busca
        try:
            results = search_service.search(query, limit_per_group=5)
            self._current_results = results
            self._display_results(results)
        except Exception as e:
            logger.error(f"Erro ao realizar busca: {e}")
            self.no_results_label.setText("Erro ao realizar busca")
            self.no_results_label.show()
        finally:
            self._is_loading = False
            self.loading_label.hide()
            
    def _display_results(self, results: List[SearchResult]):
        """Exibe os resultados da busca."""
        self.results_list.clear()
        self._selected_index = -1
        
        if not results:
            self.no_results_label.setText("Nenhum resultado encontrado")
            self.no_results_label.show()
            self.results_list.hide()
            return
            
        # Agrupar resultados por categoria
        grouped = {}
        for result in results:
            if result.categoria not in grouped:
                grouped[result.categoria] = []
            grouped[result.categoria].append(result)
            
        # Adicionar itens à lista
        for category, category_results in grouped.items():
            # Header da categoria
            category_item = QListWidgetItem()
            category_item.setText(f"  {category}")
            category_item.setFlags(Qt.ItemFlag.NoItemFlags)
            category_item.setBackground(Qt.GlobalColor.transparent)
            category_item.setForeground(Qt.GlobalColor.gray)
            font = category_item.font()
            font.setBold(True)
            font.setPointSize(10)
            category_item.setFont(font)
            self.results_list.addItem(category_item)
            
            # Resultados da categoria
            for result in category_results:
                item = QListWidgetItem()
                item.setText(f"  {result.titulo}")
                item.setData(Qt.ItemDataRole.UserRole, result)
                self.results_list.addItem(item)
                
        self.results_list.show()
        self.no_results_label.hide()
        
    def _clear_search(self):
        """Limpa a busca e reseta a interface."""
        self.search_input.clear()
        self.clear_btn.hide()
        self.results_list.clear()
        self.results_list.hide()
        self.loading_label.hide()
        self.no_results_label.hide()
        self._current_results = []
        self._selected_index = -1
        self.search_cleared.emit()
        
    def _on_return_pressed(self):
        """Manipula Enter pressionado - abre primeiro resultado."""
        if self._current_results:
            first_result = self._current_results[0]
            self.result_selected.emit(first_result.tela, first_result.categoria, first_result.registro_id)
            
    def _on_item_clicked(self, item: QListWidgetItem):
        """Manipula clique em um resultado."""
        result = item.data(Qt.ItemDataRole.UserRole)
        if result:
            self.result_selected.emit(result.tela, result.categoria, result.registro_id)
            
    def eventFilter(self, obj, event):
        """Filtro de eventos para navegação por teclado."""
        if obj == self.search_input and event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            
            if key_event.key() == Qt.Key.Key_Escape:
                self._clear_search()
                return True
                
            elif key_event.key() == Qt.Key.Key_Down:
                self._navigate_results(1)
                return True
                
            elif key_event.key() == Qt.Key.Key_Up:
                self._navigate_results(-1)
                return True
                
        return super().eventFilter(obj, event)
        
    def _navigate_results(self, direction: int):
        """Navega pelos resultados usando setas do teclado."""
        if not self._current_results:
            return
            
        total_items = self.results_list.count()
        if total_items == 0:
            return
            
        # Calcular novo índice
        new_index = self._selected_index + direction
        
        # Limites
        if new_index < 0:
            new_index = total_items - 1
        elif new_index >= total_items:
            new_index = 0
            
        # Selecionar item
        self._selected_index = new_index
        self.results_list.setCurrentRow(new_index)
        
        # Se houver um resultado válido, emitir sinal
        current_item = self.results_list.currentItem()
        if current_item:
            result = current_item.data(Qt.ItemDataRole.UserRole)
            if result:
                # Não emitir imediatamente, apenas selecionar
                pass
                
    def focus_search(self):
        """Foca no campo de busca."""
        self.search_input.setFocus()
        self.search_input.selectAll()
