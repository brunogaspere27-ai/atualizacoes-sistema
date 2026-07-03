from __future__ import annotations

import threading
from typing import Any, Dict

from config.settings import settings
from utils.sync import sincronizar, contar_pendencias_sync


class SyncService:
    def __init__(self):
        self._lock = threading.Lock()
        self._sincronizando = False
        self._ultimo_resultado: Dict[str, Any] = {
            "status": "idle",
            "mensagem": "Sincronização ainda não executada.",
            "pendencias": 0,
            "offline": not settings.supabase_enabled,
        }

    @property
    def sincronizando(self) -> bool:
        return self._sincronizando

    @property
    def ultimo_resultado(self) -> Dict[str, Any]:
        resultado = dict(self._ultimo_resultado)
        resultado["pendencias"] = contar_pendencias_sync()
        return resultado

    def executar(self) -> Dict[str, Any]:
        with self._lock:
            if self._sincronizando:
                return {
                    "status": "busy",
                    "mensagem": "Sincronização já está em andamento.",
                    "pendencias": contar_pendencias_sync(),
                    "offline": not settings.supabase_enabled,
                }
            self._sincronizando = True

        try:
            self._ultimo_resultado = sincronizar()
            self._ultimo_resultado["pendencias"] = contar_pendencias_sync()
            return dict(self._ultimo_resultado)
        finally:
            self._sincronizando = False


sync_service = SyncService()
