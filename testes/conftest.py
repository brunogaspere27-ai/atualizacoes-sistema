"""
Fixtures compartilhadas para todos os testes do CW Transportadora.

Fornece:
- db_temp: banco SQLite temporário em memória para testes de banco
- mock_settings: mock do settings singleton para testes isolados
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def db_temp():
    """Cria banco SQLite temporário em memória para testes unitários."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


@pytest.fixture
def db_temp_file():
    """Cria banco SQLite temporário em arquivo para testes que precisam de path."""
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "teste.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn, db_path, temp_dir
    conn.close()


@pytest.fixture
def mock_settings():
    """Mock do settings singleton para testes que não devem acessar config real."""
    settings = MagicMock()
    settings.empresa = "Empresa Teste"
    settings.tema = "Escuro"
    settings.meta_lucro = 20.0
    settings.imposto_percentual = 6.0
    settings.supabase_enabled = False
    settings.dados_dir = Path(tempfile.mkdtemp())
    settings.db_path = settings.dados_dir / "cw_transportadora.db"
    settings.config_path = settings.dados_dir / "configuracoes.json"
    settings.sync_config_path = settings.dados_dir / "sync_config.json"
    return settings
