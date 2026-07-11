"""
Testes da lógica de sincronização.
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from utils.sync import (
    buscar_registros_locais,
    reparar_e_enfileirar_fila,
    _timestamp_mais_recente,
)


def _criar_banco_teste():
    temp_dir = Path(tempfile.mkdtemp())
    db_path = temp_dir / "teste_sync.db"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            sync_id TEXT,
            sincronizado INTEGER DEFAULT 0,
            atualizado_em TEXT,
            deletado INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabela TEXT,
            registro_id TEXT,
            operacao TEXT DEFAULT 'UPSERT',
            status TEXT DEFAULT 'PENDENTE',
            tentativas INTEGER DEFAULT 0,
            erro TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            sincronizado_em TEXT
        )
    """)
    cursor.execute(
        "INSERT INTO clientes (nome, sync_id, atualizado_em) VALUES (?, ?, ?)",
        ("Cliente A", "clientes:1", "2026-07-09 10:00:00"),
    )
    conn.commit()
    return conn, db_path, temp_dir


def test_buscar_registros_por_sync_id():
    conn, _, _ = _criar_banco_teste()
    cursor = conn.cursor()
    registros = buscar_registros_locais(cursor, "clientes", ["clientes:1"])
    assert len(registros) == 1
    assert registros[0]["nome"] == "Cliente A"
    conn.close()


def test_buscar_registros_por_id_numerico():
    conn, _, _ = _criar_banco_teste()
    cursor = conn.cursor()
    registros = buscar_registros_locais(cursor, "clientes", ["1"])
    assert len(registros) == 1
    assert registros[0]["id"] == 1
    conn.close()


def test_timestamp_mais_recente():
    assert _timestamp_mais_recente("2026-07-09 09:00:00", "2026-07-09 10:00:00") is True
    assert _timestamp_mais_recente("2026-07-09 11:00:00", "2026-07-09 10:00:00") is False
    assert _timestamp_mais_recente(None, "2026-07-09 10:00:00") is True


def test_reparar_enfileira_registro_sem_log():
    """Testa que reparar_e_enfileirar_fila enfileira registros sem log."""
    conn, db_path, temp_dir = _criar_banco_teste()

    with patch("utils.sync.DB_LOCAL", str(db_path)), patch(
        "utils.sync.settings"
    ) as mock_settings:
        mock_settings.dados_dir = temp_dir
        mock_settings.db_path = db_path
        mock_settings.sync_config_path = temp_dir / "sync_config.json"
        mock_settings.supabase_enabled = False

        with patch("utils.sync.conectar_local", return_value=conn), patch(
            "utils.sync.preparar_sync_log"
        ):
            total = reparar_e_enfileirar_fila()

    # A função fecha a conexão no finally; abrimos outra para verificar
    conn_verificacao = sqlite3.connect(str(db_path))
    cursor = conn_verificacao.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM sync_log WHERE tabela='clientes' AND status='PENDENTE'"
    )
    pendentes = cursor.fetchone()[0]
    conn_verificacao.close()

    assert total >= 1
    assert pendentes >= 1
