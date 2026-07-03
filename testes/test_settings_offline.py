"""
Testes básicos para modo offline e caminhos centralizados.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from utils.sync import sincronizar


def test_paths_centralizados():
    assert settings.db_path.name == "cw_transportadora.db"
    assert settings.config_path.name == "configuracoes.json"
    assert settings.sync_config_path.name == "sync_config.json"
    print("✓ test_paths_centralizados passou")


def test_sync_offline_sem_quebrar():
    resultado = sincronizar()
    assert isinstance(resultado, dict)

    if not settings.supabase_enabled:
        assert resultado["offline"] is True
        assert resultado["status"] == "offline"

    print("✓ test_sync_offline_sem_quebrar passou")


if __name__ == "__main__":
    print("Executando testes de settings/offline...")
    print()

    test_paths_centralizados()
    test_sync_offline_sem_quebrar()

    print()
    print("Todos os testes de settings/offline passaram! ✓")
