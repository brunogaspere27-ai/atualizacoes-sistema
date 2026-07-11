"""
Testes básicos para modo offline e caminhos centralizados.
"""

import pytest

from config.settings import settings
from utils.sync import sincronizar

pytestmark = pytest.mark.integration


def test_paths_centralizados():
    assert settings.db_path.name == "cw_transportadora.db"
    assert settings.config_path.name == "configuracoes.json"
    assert settings.sync_config_path.name == "sync_config.json"


def test_sync_offline_sem_quebrar():
    resultado = sincronizar()
    assert isinstance(resultado, dict)

    if not settings.supabase_enabled:
        assert resultado["offline"] is True
        assert resultado["status"] == "offline"
