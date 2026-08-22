"""
Camada de conexao, schema e rastreamento de sincronizacao (sync_log).

Contem: criacao/abertura de conexao SQLite, criacao de tabelas e indices,
migracao de banco antigo e as funcoes de apoio ao offline-first
(marcar_registro_para_sync / registrar_sync).
"""

import os
import shutil
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any, Iterator
from pathlib import Path

from config.settings import settings
from utils.logger import get_logger
from utils.performance import sqlite_connection_factory

logger = get_logger(__name__)


PASTA_DADOS = str(settings.dados_dir)

os.makedirs(PASTA_DADOS, exist_ok=True)

DB_NAME = str(settings.db_path)

TABELAS_SYNC = [
    "manifestos",
    "clientes",
    "funcionarios",
    "folha_funcionarios",
    "notas",
    "caminhoes",
    "viagens",
    "viagem_notas",
    "operacoes_sp",
    "contas",
    "abastecimentos",
    "manutencoes"
]


def migrar_banco_antigo() -> None:
    """Migra banco antigo para nova localização."""
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
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Context manager para conexão com banco de dados.
    
    Yields:
        Conexão SQLite configurada com foreign keys habilitadas.
    """
    conn = _create_connection()
    
    try:
        conn.execute("PRAGMA busy_timeout = 30000")
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_connection_rows() -> Iterator[sqlite3.Connection]:
    """Conexão com row_factory ativado — permite row['coluna'] em vez de row[0]."""
    conn = _create_connection()
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def tabela_existe_sqlite(cursor: sqlite3.Cursor, tabela: str) -> bool:
    """Verifica se uma tabela existe no banco SQLite local."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (tabela,)
    )
    return cursor.fetchone() is not None


def conectar() -> sqlite3.Connection:
    """
    Cria conexão com banco de dados (legado, usar get_connection preferencialmente).
    
    Returns:
        Conexão SQLite configurada com foreign keys habilitadas.
    """
    return _create_connection()


def agora_sync() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def marcar_registro_para_sync(
    cursor: sqlite3.Cursor,
    tabela: str,
    registro_id: Any,
    operacao: str = "UPSERT"
) -> None:
    if tabela == "sync_log" or registro_id is None:
        return

    try:
        if str(registro_id).strip().lower() in ("", "none"):
            return
    except Exception:
        return

    timestamp = agora_sync()

    try:
        if operacao.upper() == "UPSERT":
            cursor.execute(f"""
                UPDATE {tabela}
                SET atualizado_em = ?,
                    sincronizado = 0,
                    deletado = 0,
                    sync_id = COALESCE(NULLIF(sync_id, ''), ?)
                WHERE id = ?
            """, (timestamp, str(uuid.uuid4()), registro_id))
        else:
            cursor.execute(f"""
                UPDATE {tabela}
                SET atualizado_em = ?,
                    sincronizado = 0,
                    deletado = 1
                WHERE id = ?
            """, (timestamp, registro_id))
    except sqlite3.OperationalError as erro:
        logger.debug(f"Tabela {tabela} não possui colunas de sync ainda: {erro}")


def obter_referencia_sync(
    cursor: sqlite3.Cursor,
    tabela: str,
    registro_id: Any,
    operacao: str = "UPSERT"
) -> str:
    try:
        cursor.execute(
            f"SELECT sync_id FROM {tabela} WHERE id = ?",
            (registro_id,)
        )
        row = cursor.fetchone()
        if row and row[0]:
            return str(row[0])
    except sqlite3.OperationalError:
        pass  # Tabela pode não ter coluna sync_id ainda

    if operacao.upper() == "DELETE":
        return str(registro_id)

    return str(registro_id)


def registrar_sync(
    cursor: sqlite3.Cursor,
    tabela: str,
    registro_id: Any,
    operacao: str = "UPSERT"
) -> None:
    """
    Registra operação para sincronização.
    
    Args:
        cursor: Cursor do banco de dados
        tabela: Nome da tabela
        registro_id: ID do registro
        operacao: Tipo de operação (UPSERT ou DELETE)
    """
    if tabela == "sync_log":
        return

    if registro_id is None or str(registro_id).strip().lower() in ("", "none"):
        return

    try:
        marcar_registro_para_sync(cursor, tabela, registro_id, operacao)

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

        referencia_sync = obter_referencia_sync(cursor, tabela, registro_id, operacao)
        referencias = [referencia_sync, str(registro_id)]

        placeholders = ",".join(["?"] * len(referencias))
        cursor.execute(f"""
            UPDATE sync_log
            SET status = 'PENDENTE',
                operacao = ?,
                tentativas = 0,
                erro = NULL,
                registro_id = ?
            WHERE tabela = ?
              AND registro_id IN ({placeholders})
              AND status = 'OK'
        """, [operacao, referencia_sync, tabela, *referencias])

        if cursor.rowcount > 0:
            return

        cursor.execute(f"""
            SELECT id
            FROM sync_log
            WHERE tabela = ?
            AND registro_id IN ({placeholders})
            AND status = 'PENDENTE'
        """, [tabela, *referencias])

        if cursor.fetchone():
            return

        cursor.execute("""
            INSERT INTO sync_log (
                tabela,
                registro_id,
                operacao,
                status,
                tentativas
            )
            VALUES (?, ?, ?, 'PENDENTE', 0)
        """, (tabela, referencia_sync, operacao))

    except Exception as erro:
        logger.error(f"Erro ao registrar sync {tabela} {registro_id}: {erro}")


def criar_indices(cursor: sqlite3.Cursor) -> None:
    """Cria índices para melhorar performance de consultas."""
    indices = [
        # Índices para clientes
        ("idx_clientes_nome", "clientes", "nome"),
        ("idx_clientes_cnpj", "clientes", "cnpj"),
        ("idx_clientes_cidade", "clientes", "cidade"),
        
        # Índices para notas
        ("idx_notas_status", "notas", "status"),
        ("idx_notas_destinatario", "notas", "destinatario_id"),
        ("idx_notas_remetente", "notas", "remetente_id"),
        ("idx_notas_manifesto", "notas", "manifesto_id"),
        ("idx_notas_chave_nfe", "notas", "chave_nfe"),
        ("idx_notas_criado_em", "notas", "criado_em"),
        
        # Índices para viagens
        ("idx_viagens_caminhao", "viagens", "caminhao_id"),
        ("idx_viagens_status", "viagens", "status"),
        ("idx_viagens_data_saida", "viagens", "data_saida"),
        
        # Índices para viagem_notas
        ("idx_viagem_notas_viagem", "viagem_notas", "viagem_id"),
        ("idx_viagem_notas_nota", "viagem_notas", "nota_id"),
        
        # Índices para caminhoes
        ("idx_caminhoes_placa", "caminhoes", "placa"),
        
        # Índices para funcionarios
        ("idx_funcionarios_status", "funcionarios", "status"),
        
        # Índices para sync_log
        ("idx_sync_log_tabela", "sync_log", "tabela"),
        ("idx_sync_log_status", "sync_log", "status"),
    ]
    
    for idx_name, tabela, coluna in indices:
        try:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {idx_name}
                ON {tabela}({coluna})
            """)
            logger.debug(f"Índice {idx_name} criado/verificado")
        except Exception as e:
            logger.warning(f"Erro ao criar índice {idx_name}: {e}")


def _criar_tabelas_auth(cursor: sqlite3.Cursor) -> None:
    """Cria tabelas de autenticação, permissões e auditoria (locais, sem sync)."""

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

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_usuarios_usuario ON usuarios(usuario)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_auditoria_criado_em ON auditoria(criado_em)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria(usuario_id)
    """)


def criar_banco() -> None:
    """Cria todas as tabelas do banco de dados se não existirem."""
    logger.info("Criando/verificando estrutura do banco de dados...")
    
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS manifestos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_arquivo TEXT,
        data_importacao TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        cnpj TEXT UNIQUE,
        cidade TEXT,
        uf TEXT,
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Evolução do schema (instalações antigas) — campos necessários para busca profissional.
    # Mantém o app compatível e permite pesquisa por CPF/CNPJ/telefone/código sem falhas.
    for coluna_nome, coluna_tipo in [
        ("razao_social", "TEXT"),
        ("fantasia", "TEXT"),
        ("cpf", "TEXT"),
        ("telefone", "TEXT"),
        ("codigo", "TEXT"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {coluna_nome} {coluna_tipo}")
            logger.info(f"Coluna '{coluna_nome}' adicionada à tabela clientes")
        except sqlite3.OperationalError:
            pass  # Coluna já existe — esperado em instalações existentes

    # Índices para busca rápida (LIKE ainda pode ser pesado, mas isso já reduz latência em bases reais)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes(nome)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_cnpj ON clientes(cnpj)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_cpf ON clientes(cpf)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_telefone ON clientes(telefone)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_codigo ON clientes(codigo)")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cargo TEXT,
        status TEXT DEFAULT 'Ativo',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    for coluna_nome, coluna_tipo in [
        ("salario", "REAL DEFAULT 0"),
        ("telefone", "TEXT"),
        ("data_admissao", "TEXT"),
        ("vale_refeicao", "REAL DEFAULT 0"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE funcionarios ADD COLUMN {coluna_nome} {coluna_tipo}")
            logger.info(f"Coluna '{coluna_nome}' adicionada à tabela funcionarios")
        except sqlite3.OperationalError:
            pass  # Coluna já existe — esperado em instalações existentes

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
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

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
        status TEXT DEFAULT 'Disponível',
        criado_em TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS viagem_notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        viagem_id INTEGER,
        nota_id INTEGER
    )
    """)

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

    for coluna_nome, coluna_tipo in [
        ("qtd_horas_extra", "REAL DEFAULT 0"),
        ("valor_hora_extra", "REAL DEFAULT 0"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE folha_funcionarios ADD COLUMN {coluna_nome} {coluna_tipo}")
            logger.info(f"Coluna '{coluna_nome}' adicionada à tabela folha_funcionarios")
        except sqlite3.OperationalError:
            pass  # Coluna já existe — esperado em instalações existentes

    # Criar índices para melhorar performance
    criar_indices(cursor)

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

    colunas_sync = [
        ("sync_id", "TEXT"),
        ("sincronizado", "INTEGER DEFAULT 0"),
        ("atualizado_em", "TEXT"),
        ("deletado", "INTEGER DEFAULT 0"),
    ]
    for tabela in TABELAS_SYNC:
        for coluna_nome, coluna_tipo in colunas_sync:
            try:
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna_nome} {coluna_tipo}")
                logger.info(f"Coluna sync '{coluna_nome}' adicionada à tabela {tabela}")
            except sqlite3.OperationalError:
                pass  # Coluna já existe — esperado em instalações existentes

        try:
            cursor.execute(f"""
                UPDATE {tabela}
                SET sync_id = COALESCE(NULLIF(sync_id, ''), '{tabela}:' || CAST(id AS TEXT)),
                    atualizado_em = COALESCE(NULLIF(atualizado_em, ''), ?),
                    sincronizado = COALESCE(sincronizado, 0),
                    deletado = COALESCE(deletado, 0)
                WHERE sync_id IS NULL
                   OR sync_id = ''
                   OR atualizado_em IS NULL
                   OR atualizado_em = ''
            """, (agora_sync(),))
        except sqlite3.OperationalError as erro:
            logger.debug(f"Tabela {tabela} sem colunas de sync para atualizar: {erro}")

        try:
            cursor.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{tabela}_sync_id ON {tabela}(sync_id)"
            )
        except sqlite3.OperationalError as erro:
            logger.debug(f"Não foi possível criar índice sync_id para {tabela}: {erro}")

    # ── Tabelas de Autenticação e Auditoria (locais, não sincronizadas) ──
    _criar_tabelas_auth(cursor)

    corrigir_tabela_viagem_notas(cursor)
    registrar_caminhoes_para_sync(cursor)

    conn.commit()
    conn.close()
    
    logger.info("Estrutura do banco de dados verificada com sucesso")


def corrigir_tabela_viagem_notas(cursor):
    cursor.execute("PRAGMA table_info(viagem_notas)")
    colunas = cursor.fetchall()
    pk_cols = [coluna[1] for coluna in colunas if coluna[5]]

    if pk_cols:
        return

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS viagem_notas_nova (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viagem_id INTEGER,
            nota_id INTEGER,
            sync_id TEXT,
            sincronizado INTEGER DEFAULT 0,
            atualizado_em TEXT,
            deletado INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        INSERT INTO viagem_notas_nova (
            viagem_id,
            nota_id,
            sync_id,
            sincronizado,
            atualizado_em,
            deletado
        )
        SELECT
            viagem_id,
            nota_id,
            sync_id,
            sincronizado,
            atualizado_em,
            deletado
        FROM viagem_notas
    """)

    cursor.execute("DROP TABLE viagem_notas")
    cursor.execute("ALTER TABLE viagem_notas_nova RENAME TO viagem_notas")

    cursor.execute("SELECT id FROM viagem_notas")
    for (viagem_nota_id,) in cursor.fetchall():
        registrar_sync(cursor, "viagem_notas", viagem_nota_id)


def registrar_caminhoes_para_sync(cursor):
    cursor.execute("SELECT id FROM caminhoes")

    for (caminhao_id,) in cursor.fetchall():
        cursor.execute("""
            SELECT id
            FROM sync_log
            WHERE tabela = 'caminhoes'
            AND registro_id = ?
            AND status = 'OK'
        """, (str(caminhao_id),))

        if not cursor.fetchone():
            registrar_sync(cursor, "caminhoes", caminhao_id)

