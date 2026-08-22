"""
Serviço de gestão financeira.
"""
import threading
import time
from datetime import datetime
from utils.logger import Logger


class FinanceiroService:
    """Gerencia dados financeiros."""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.logger = Logger()
        self._lock = threading.Lock()
        self._cache = {}
        self._cache_ttl = 300
        self._last_update = None
        self._running = False
        self._update_interval = 30
        self._observers = []
        self._metrics = {}
    
    def get_resumo(self):
        """Retorna resumo financeiro."""
        try:
            with self._lock:
                if self._is_cache_valid():
                    return self._cache.get("resumo")
                
                # Simulação - em produção, consultar DB
                resumo = {
                    "receitas": 0.0,
                    "despesas": 0.0,
                    "saldo": 0.0,
                    "updated_at": datetime.now().isoformat()
                }
                self._cache["resumo"] = resumo
                self._last_update = time.time()
                return resumo
        except Exception as e:
            self.logger.log(f"Erro no resumo: {e}", "error")
            return {}
    
    def _is_cache_valid(self):
        if not self._last_update:
            return False
        return (time.time() - self._last_update) < self._cache_ttl
    
    def add_observer(self, callback):
        self._observers.append(callback)
    
    def _notify_observers(self, event, data):
        for obs in self._observers:
            try:
                obs(event, data)
            except Exception as e:
                self.logger.log(f"Erro no observer: {e}", "error")