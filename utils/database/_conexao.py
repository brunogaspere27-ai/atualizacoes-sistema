"""
Camada de conexao, schema e rastreamento de sincronizacao (sync_log).
"""

import os
import shutil
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Iterator
from pathlib import Path

from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

DB_NAME = str(settings.db_path)

TABELAS_SYNC = [
    "manifestos", "clientes", "funcionarios", "folha_funcionarios",
    "notas", "caminhoes", "viagens", "viagem_notas",
    "operacoes_sp", "contas", "abastecimentos", "manutencoes"
]


def migrar_banco_antigo() -> None:
    """Migra banco antigo para nova localizacao."""
    banco_antigo = "cw_transportadora.db"
    if os.path.exists(banco_antigo) and not os.path.exists(DB_NAME):
        try:
            shutil.copy2(banco_antigo, DB_NAME)
            logger.info(f"Banco antigo migrado para {DB_NAME}")
        except Exception as erro:
            logger.error(f"Erro ao migrar banco antigo: {erro}")


def _create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False,
    )
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = _create_connection()
    try:
        yield conn
    except Exception as e:
        logger.error(f"Erro na conexao com banco: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_connection_rows() -> Iterator[sqlite3.Connection]:
    conn = _create_connection()
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception as e:
        logger.error(f"Erro na conexao com banco: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def conectar() -> sqlite3.Connection:
    return _create_connection()


def agora_sync() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _coluna_existe(cursor, tabela, coluna):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return any(row[1] == coluna for row in cursor.fetchall())


def _tabela_existe(cursor, tabela):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (tabela,)
    )
    return cursor.fetchone() is not None


def _migrar_schema(cursor):
    """Migra schema antigo para novo automaticamente."""
    
    # --- MANIFESTOS: garantir nome_arquivo ---
    if _tabela_existe(cursor, "manifestos"):
        if not _coluna_existe(cursor, "manifestos", "nome_arquivo"):
            try:
                cursor.execute("ALTER TABLE manifestos ADD COLUMN nome_arquivo TEXT")
                logger.info("[MIGRACAO] Coluna nome_arquivo adicionada em manifestos")
            except Exception as e:
                logger.warning(f"[MIGRACAO] Erro ao adicionar nome_arquivo: {e}")
        
        if not _coluna_existe(cursor, "manifestos", "data_importacao"):
            try:
                cursor.execute("ALTER TABLE manifestos ADD COLUMN data_importacao TEXT DEFAULT CURRENT_TIMESTAMP")
                logger.info("[MIGRACAO] Coluna data_importacao adicionada em manifestos")
            except Exception as e:
                logger.warning(f"[MIGRACAO] Erro ao adicionar data_importacao: {e}")
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS manifestos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_arquivo TEXT,
                data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    # --- VIAGEM_NOTAS: renomear notas_viagem se existir, ou criar ---
    if _tabela_existe(cursor, "notas_viagem") and not _tabela_existe(cursor, "viagem_notas"):
        try:
            cursor.execute("ALTER TABLE notas_viagem RENAME TO viagem_notas")
            logger.info("[MIGRACAO] Tabela notas_viagem renomeada para viagem_notas")
        except Exception as e:
            logger.warning(f"[MIGRACAO] Erro ao renomear notas_viagem: {e}")
    
    if not _tabela_existe(cursor, "viagem_notas"):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS viagem_notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                viagem_id INTEGER,
                nota_id INTEGER,
                sync_id TEXT,
                sincronizado INTEGER DEFAULT 0,
                atualizado_em TEXT,
                deletado INTEGER DEFAULT 0
            )
        """)
        logger.info("[MIGRACAO] Tabela viagem_notas criada")

    # --- CLIENTES ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cnpj TEXT UNIQUE,
            cidade TEXT,
            uf TEXT,
            razao_social TEXT,
            fantasia TEXT,
            cpf TEXT,
            telefone TEXT,
            codigo TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    for col in [("razao_social","TEXT"), ("fantasia","TEXT"), ("cpf","TEXT"), 
                ("telefone","TEXT"), ("codigo","TEXT")]:
        if not _coluna_existe(cursor, "clientes", col[0]):
            try:
                cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col[0]} {col[1]}")
            except: pass

    # --- NOTAS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manifesto_id INTEGER,
            chave_nfe TEXT UNIQUE,
            numero_cte TEXT,
            remetente_id INTEGER,
            destinatario_id INTEGER,
            valor_mercadoria REAL,
            valor_frete REAL,
            peso REAL,
            origem TEXT,
            destino TEXT,
            status TEXT DEFAULT 'Disponivel',
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- CAMINHOES ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caminhoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT,
            modelo TEXT,
            motorista TEXT,
            capacidade_kg REAL,
            media_km_l REAL
        )
    """)

    # --- VIAGENS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS viagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caminhao_id INTEGER,
            data_saida TEXT,
            data_retorno TEXT,
            motorista TEXT,
            status TEXT,
            peso_total REAL DEFAULT 0,
            frete_total REAL DEFAULT 0,
            custo_total REAL DEFAULT 0,
            lucro_total REAL DEFAULT 0
        )
    """)

    # --- FUNCIONARIOS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cargo TEXT,
            status TEXT DEFAULT 'Ativo',
            salario REAL DEFAULT 0,
            telefone TEXT,
            data_admissao TEXT,
            vale_refeicao REAL DEFAULT 0,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    for col in [("salario","REAL DEFAULT 0"), ("telefone","TEXT"), 
                ("data_admissao","TEXT"), ("vale_refeicao","REAL DEFAULT 0")]:
        if not _coluna_existe(cursor, "funcionarios", col[0]):
            try:
                cursor.execute(f"ALTER TABLE funcionarios ADD COLUMN {col[0]} {col[1]}")
            except: pass

    # --- FOLHA_FUNCIONARIOS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folha_funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            mes TEXT,
            ano TEXT,
            salario REAL DEFAULT 0,
            vale_refeicao REAL DEFAULT 0,
            hora_extra REAL DEFAULT 0,
            outros REAL DEFAULT 0,
            total REAL DEFAULT 0,
            qtd_horas_extra REAL DEFAULT 0,
            valor_hora_extra REAL DEFAULT 0,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    for col in [("qtd_horas_extra","REAL DEFAULT 0"), ("valor_hora_extra","REAL DEFAULT 0")]:
        if not _coluna_existe(cursor, "folha_funcionarios", col[0]):
            try:
                cursor.execute(f"ALTER TABLE folha_funcionarios ADD COLUMN {col[0]} {col[1]}")
            except: pass

    # --- OPERACOES_SP ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operacoes_sp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_operacao TEXT,
            nome_caminhao TEXT,
            placa TEXT,
            motorista TEXT,
            valor_notas REAL DEFAULT 0,
            frete_carreta REAL DEFAULT 0,
            pedagio_carreta REAL DEFAULT 0,
            outros_custos REAL DEFAULT 0,
            custo_total REAL DEFAULT 0,
            liquido REAL DEFAULT 0,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- CONTAS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            descricao TEXT,
            pessoa TEXT,
            categoria TEXT,
            valor REAL DEFAULT 0,
            vencimento TEXT,
            pagamento TEXT,
            status TEXT DEFAULT 'Pendente',
            observacao TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- ABASTECIMENTOS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS abastecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_abastecimento TEXT,
            veiculo TEXT,
            motorista TEXT,
            km_atual REAL DEFAULT 0,
            litros REAL DEFAULT 0,
            valor_litro REAL DEFAULT 0,
            valor_total REAL DEFAULT 0,
            media_km_l REAL DEFAULT 0,
            custo_km REAL DEFAULT 0,
            posto TEXT,
            observacao TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- MANUTENCOES ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manutencoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_manutencao TEXT,
            veiculo TEXT,
            km_atual REAL DEFAULT 0,
            tipo TEXT,
            descricao TEXT,
            oficina TEXT,
            valor REAL DEFAULT 0,
            proxima_revisao_km REAL DEFAULT 0,
            status TEXT DEFAULT 'Pendente',
            observacao TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- SYNC_LOG ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_log (
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

    # --- USUARIOS ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_completo TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            senha_salt TEXT NOT NULL,
            nivel_acesso TEXT NOT NULL DEFAULT 'comum',
            ativo INTEGER NOT NULL DEFAULT 1,
            deve_alterar_senha INTEGER NOT NULL DEFAULT 0,
            tentativas_falhas INTEGER NOT NULL DEFAULT 0,
            bloqueado_ate TEXT,
            ultimo_login TEXT,
            criado_por INTEGER,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- PERMISSOES_USUARIO ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissoes_usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            modulo TEXT NOT NULL,
            pode_visualizar INTEGER DEFAULT 1,
            pode_criar INTEGER DEFAULT 0,
            pode_editar INTEGER DEFAULT 0,
            pode_excluir INTEGER DEFAULT 0,
            pode_exportar INTEGER DEFAULT 0,
            pode_sincronizar INTEGER DEFAULT 0,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
            UNIQUE(usuario_id, modulo)
        )
    """)

    # --- AUDITORIA ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            usuario_nome TEXT,
            acao TEXT NOT NULL,
            modulo TEXT,
            registro_afetado TEXT,
            detalhes TEXT,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- INDICES ---
    indices = [
        ("idx_clientes_nome", "clientes", "nome"),
        ("idx_clientes_cnpj", "clientes", "cnpj"),
        ("idx_notas_status", "notas", "status"),
        ("idx_notas_manifesto", "notas", "manifesto_id"),
        ("idx_notas_chave_nfe", "notas", "chave_nfe"),
        ("idx_viagens_caminhao", "viagens", "caminhao_id"),
        ("idx_viagens_status", "viagens", "status"),
        ("idx_viagem_notas_viagem", "viagem_notas", "viagem_id"),
        ("idx_viagem_notas_nota", "viagem_notas", "nota_id"),
        ("idx_caminhoes_placa", "caminhoes", "placa"),
        ("idx_sync_log_tabela", "sync_log", "tabela"),
        ("idx_sync_log_status", "sync_log", "status"),
        ("idx_usuarios_usuario", "usuarios", "usuario"),
        ("idx_auditoria_criado_em", "auditoria", "criado_em"),
    ]
    for idx_name, tabela, coluna in indices:
        try:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {tabela}({coluna})")
        except Exception:
            pass

    # --- COLUNAS SYNC EM TODAS AS TABELAS ---
    colunas_sync = [
        ("sync_id", "TEXT"),
        ("sincronizado", "INTEGER DEFAULT 0"),
        ("atualizado_em", "TEXT"),
        ("deletado", "INTEGER DEFAULT 0"),
    ]
    for tabela in TABELAS_SYNC:
        if not _tabela_existe(cursor, tabela):
            continue
        for coluna_nome, coluna_tipo in colunas_sync:
            if not _coluna_existe(cursor, tabela, coluna_nome):
                try:
                    cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna_nome} {coluna_tipo}")
                    logger.info(f"[MIGRACAO] Coluna {coluna_nome} adicionada em {tabela}")
                except sqlite3.OperationalError:
                    pass
        
        # Atualizar registros antigos sem sync_id
        try:
            cursor.execute(f"""
                UPDATE {tabela}
                SET sync_id = COALESCE(NULLIF(sync_id, ''), '{tabela}:' || CAST(id AS TEXT)),
                    atualizado_em = COALESCE(NULLIF(atualizado_em, ''), ?),
                    sincronizado = COALESCE(sincronizado, 0),
                    deletado = COALESCE(deletado, 0)
                WHERE sync_id IS NULL OR sync_id = ''
                   OR atualizado_em IS NULL OR atualizado_em = ''
            """, (agora_sync(),))
        except:
            pass

        try:
            cursor.execute(f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{tabela}_sync_id ON {tabela}(sync_id)")
        except:
            pass


def marcar_registro_para_sync(cursor, tabela, registro_id, operacao="UPSERT"):
    if tabela == "sync_log" or registro_id is None:
        return
    if str(registro_id).strip().lower() in ("", "none"):
        return
    timestamp = agora_sync()
    try:
        if operacao.upper() == "UPSERT":
            cursor.execute(f"""
                UPDATE {tabela}
                SET atualizado_em = ?, sincronizado = 0, deletado = 0,
                    sync_id = COALESCE(NULLIF(sync_id, ''), ?)
                WHERE id = ?
            """, (timestamp, str(uuid.uuid4()), registro_id))
        else:
            cursor.execute(f"""
                UPDATE {tabela}
                SET atualizado_em = ?, sincronizado = 0, deletado = 1
                WHERE id = ?
            """, (timestamp, registro_id))
    except sqlite3.OperationalError as erro:
        logger.debug(f"Tabela {tabela} sem colunas de sync: {erro}")


def obter_referencia_sync(cursor, tabela, registro_id, operacao="UPSERT"):
    try:
        cursor.execute(f"SELECT sync_id FROM {tabela} WHERE id = ?", (registro_id,))
        row = cursor.fetchone()
        if row and row[0]:
            return str(row[0])
    except:
        pass
    return str(registro_id)


def registrar_sync(cursor, tabela, registro_id, operacao="UPSERT"):
    if tabela == "sync_log":
        return
    if registro_id is None or str(registro_id).strip().lower() in ("", "none"):
        return
    try:
        marcar_registro_para_sync(cursor, tabela, registro_id, operacao)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tabela TEXT, registro_id TEXT, operacao TEXT DEFAULT 'UPSERT',
                status TEXT DEFAULT 'PENDENTE', tentativas INTEGER DEFAULT 0,
                erro TEXT, criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
                sincronizado_em TEXT
            )
        """)
        referencia_sync = obter_referencia_sync(cursor, tabela, registro_id, operacao)
        referencias = [referencia_sync, str(registro_id)]
        placeholders = ",".join(["?"] * len(referencias))
        cursor.execute(f"""
            UPDATE sync_log
            SET status = 'PENDENTE', operacao = ?, tentativas = 0, erro = NULL,
                registro_id = ?
            WHERE tabela = ? AND registro_id IN ({placeholders}) AND status = 'OK'
        """, [operacao, referencia_sync, tabela, *referencias])
        if cursor.rowcount > 0:
            return
        cursor.execute(f"""
            SELECT id FROM sync_log
            WHERE tabela = ? AND registro_id IN ({placeholders}) AND status = 'PENDENTE'
        """, [tabela, *referencias])
        if cursor.fetchone():
            return
        cursor.execute("""
            INSERT INTO sync_log (tabela, registro_id, operacao, status, tentativas)
            VALUES (?, ?, ?, 'PENDENTE', 0)
        """, (tabela, referencia_sync, operacao))
    except Exception as erro:
        logger.error(f"Erro ao registrar sync {tabela} {registro_id}: {erro}")


def criar_banco():
    """Cria/Atualiza o banco de dados com migrações automáticas."""
    logger.info("Verificando estrutura do banco de dados...")
    migrar_banco_antigo()
    
    conn = conectar()
    cursor = conn.cursor()
    
    # Executar migrações automáticas
    _migrar_schema(cursor)
    
    conn.commit()
    conn.close()
    logger.info("Banco de dados verificado com sucesso!")


def tabela_existe_sqlite(cursor, tabela):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
    return cursor.fetchone() is not None

