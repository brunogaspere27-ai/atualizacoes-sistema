import os
import shutil
import sqlite3
from datetime import datetime

from config.settings import settings
from utils.database import DB_NAME, criar_banco, criar_caminhoes_padrao
from utils.logger import get_logger
from utils.supabase_db import conectar_supabase, supabase_habilitado

logger = get_logger(__name__)


TABELAS_LIMPAR = [
    "sync_log",
    "viagem_notas",
    "viagens",
    "notas",
    "manifestos",
    "operacoes_sp",
    "contas",
    "abastecimentos",
    "manutencoes",
    "folha_funcionarios",
    "funcionarios",
    "clientes"
]


def backup_antes_limpar():
    pasta_backup = settings.backup_distribuicao_dir

    nome_backup = f"backup_antes_zerar_{datetime.now().strftime('%d%m%Y_%H%M%S')}.db"
    destino = pasta_backup / nome_backup

    if os.path.exists(DB_NAME):
        shutil.copy2(DB_NAME, destino)

    return str(destino)


def limpar_sqlite_local():
    criar_banco()

    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False
    )
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA busy_timeout = 30000")

        for tabela in TABELAS_LIMPAR:
            try:
                cursor.execute(f"DELETE FROM {tabela}")
            except Exception as erro:
                logger.warning(f"Erro ao limpar {tabela}: {erro}")

        try:
            cursor.execute("DELETE FROM sqlite_sequence")
        except sqlite3.OperationalError:
            pass  # sqlite_sequence pode não existir se não houver AUTOINCREMENT

        conn.commit()

    finally:
        conn.close()

    criar_banco()
    criar_caminhoes_padrao()


def limpar_supabase():
    if not supabase_habilitado():
        logger.info("Supabase desabilitado. Limpeza da nuvem ignorada.")
        return

    conn = conectar_supabase()
    cursor = conn.cursor()

    tabelas_nuvem = [
        tabela for tabela in TABELAS_LIMPAR
        if tabela != "sync_log"
    ]

    for tabela in tabelas_nuvem:
        try:
            cursor.execute(f"DELETE FROM {tabela}")
        except Exception as erro:
            logger.warning(f"Erro ao limpar Supabase {tabela}: {erro}")

    conn.commit()
    conn.close()


def resetar_sync_config():
    try:
        if settings.sync_config_path.exists():
            settings.sync_config_path.unlink()
    except Exception:
        pass


def preparar_base_para_distribuicao(criar_backup=True):
    backup = None

    if criar_backup:
        backup = backup_antes_limpar()

    limpar_sqlite_local()
    limpar_supabase()
    resetar_sync_config()

    return backup
