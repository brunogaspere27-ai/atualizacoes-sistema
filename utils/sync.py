"""
Gerenciador de sincronização (utilitário).
"""
import threading
from utils.logger import Logger


class SyncManager:
    """Gerencia sincronização de dados."""
    
    def __init__(self, db_manager, auth_service):
        self.db = db_manager
        self.auth = auth_service
        self.logger = Logger()
        self._sync_queue = []
        self._sync_lock = threading.Lock()
        self._running = False
        self._last_sync = None
        self._conflicts = []
        self._observers = []