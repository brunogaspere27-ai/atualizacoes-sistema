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


migrar_banco_antigo()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Context manager para conexão com banco de dados.
    
    Yields:
        Conexão SQLite configurada com foreign keys habilitadas.
    """
    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False
    )
    
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
    conn = sqlite3.connect(DB_NAME, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
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
    conn = sqlite3.connect(
        DB_NAME,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


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


def buscar_cliente_por_cnpj(cnpj):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM clientes WHERE cnpj = ?",
        (cnpj,)
    )

    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return resultado[0]

    return None


def criar_cliente(nome, cnpj, cidade="", uf=""):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes
        (nome, cnpj, cidade, uf)
        VALUES (?, ?, ?, ?)
    """, (nome, cnpj, cidade, uf))

    cliente_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return cliente_id


def obter_ou_criar_cliente(nome, cnpj, cidade="", uf=""):

    if not cnpj:
        cnpj = nome

    cliente_id = buscar_cliente_por_cnpj(cnpj)

    if cliente_id:
        return cliente_id

    return criar_cliente(nome, cnpj, cidade, uf)


def salvar_nota(nota):

    chave_nfe = nota.get("chave_nfe") or nota.get("numero_cte")

    if nota_existe(chave_nfe):
        return False

    remetente_id = obter_ou_criar_cliente(
        nota.get("remetente_nome", ""),
        nota.get("remetente_cnpj", ""),
        nota.get("origem", ""),
        nota.get("uf_origem", "")
    )

    destinatario_id = obter_ou_criar_cliente(
        nota.get("destinatario_nome", ""),
        nota.get("destinatario_cnpj", ""),
        nota.get("destino", ""),
        nota.get("uf_destino", "")
    )

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO notas (
            manifesto_id,
            chave_nfe,
            numero_cte,
            remetente_id,
            destinatario_id,
            valor_mercadoria,
            valor_frete,
            peso,
            origem,
            destino,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        nota.get("manifesto_id"),
        chave_nfe,
        nota.get("numero_cte", ""),
        remetente_id,
        destinatario_id,
        nota.get("valor_mercadoria", 0),
        nota.get("valor_frete", 0),
        nota.get("peso", 0),
        nota.get("origem", ""),
        nota.get("destino", ""),
        nota.get("status", "Disponível")
    ))

    conn.commit()
    conn.close()

    return True


def listar_notas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notas.id,
            notas.chave_nfe,
            notas.numero_cte,
            remetente.nome,
            destinatario.nome,
            notas.origem,
            notas.destino,
            notas.valor_frete,
            notas.peso,
            notas.status
        FROM notas
        LEFT JOIN clientes remetente
            ON remetente.id = notas.remetente_id
        LEFT JOIN clientes destinatario
            ON destinatario.id = notas.destinatario_id
        ORDER BY notas.id DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    return dados

def nota_existe(chave_nfe):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM notas WHERE chave_nfe = ?",
        (chave_nfe,)
    )

    resultado = cursor.fetchone()
    conn.close()

    return resultado is not None


def criar_manifesto(nome_arquivo):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO manifestos (nome_arquivo)
        VALUES (?)
    """, (nome_arquivo,))

    manifesto_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return manifesto_id


def listar_manifestos(tipo_periodo="Geral", mes=None, ano=None):

    conn = conectar()
    cursor = conn.cursor()

    filtro = ""
    params = []

    if tipo_periodo == "Mês" and mes and ano:
        mes = str(mes).zfill(2)
        ano = str(ano)
        filtro = "WHERE substr(manifestos.data_importacao, 6, 2) = ? AND substr(manifestos.data_importacao, 1, 4) = ?"
        params = [mes, ano]

    elif tipo_periodo == "Ano" and ano:
        ano = str(ano)
        filtro = "WHERE substr(manifestos.data_importacao, 1, 4) = ?"
        params = [ano]

    cursor.execute(f"""
        SELECT
            manifestos.id,
            manifestos.nome_arquivo,
            manifestos.data_importacao,
            COUNT(notas.id) as total_notas,
            COALESCE(SUM(notas.valor_mercadoria), 0) as valor_total_notas,
            COALESCE(SUM(notas.valor_frete), 0) as frete_total,
            COALESCE(SUM(notas.peso), 0) as peso_total
        FROM manifestos
        LEFT JOIN notas ON notas.manifesto_id = manifestos.id
        {filtro}
        GROUP BY manifestos.id
        ORDER BY manifestos.id DESC
    """, params)

    dados = cursor.fetchall()
    conn.close()

    return dados


def listar_notas_por_manifesto(manifesto_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notas.id,
            notas.chave_nfe,
            notas.numero_cte,
            remetente.nome,
            destinatario.nome,
            notas.origem,
            notas.destino,
            notas.valor_mercadoria,
            notas.valor_frete,
            notas.peso,
            notas.status
        FROM notas
        LEFT JOIN clientes remetente
            ON remetente.id = notas.remetente_id
        LEFT JOIN clientes destinatario
            ON destinatario.id = notas.destinatario_id
        WHERE notas.manifesto_id = ?
        ORDER BY notas.id DESC
    """, (manifesto_id,))

    dados = cursor.fetchall()
    conn.close()

    return dados

def apagar_manifesto(manifesto_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, nome_arquivo FROM manifestos WHERE id = ?",
            (manifesto_id,)
        )

        manifesto = cursor.fetchone()

        if not manifesto:
            raise Exception("Manifesto não encontrado.")

        cursor.execute(
            "SELECT id FROM notas WHERE manifesto_id = ?",
            (manifesto_id,)
        )

        notas_ids = [linha[0] for linha in cursor.fetchall()]

        for nota_id in notas_ids:
            registrar_sync(cursor, "notas", nota_id, "DELETE")

        registrar_sync(cursor, "manifestos", manifesto_id, "DELETE")

        cursor.execute(
            """
            DELETE FROM viagem_notas
            WHERE nota_id IN (
                SELECT id
                FROM notas
                WHERE manifesto_id = ?
            )
            """,
            (manifesto_id,)
        )

        cursor.execute(
            "DELETE FROM notas WHERE manifesto_id = ?",
            (manifesto_id,)
        )

        cursor.execute(
            "DELETE FROM manifestos WHERE id = ?",
            (manifesto_id,)
        )

        conn.commit()

        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()

def listar_caminhoes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, placa, modelo, motorista, capacidade_kg
        FROM caminhoes
        ORDER BY modelo
    """)

    dados = cursor.fetchall()
    conn.close()

    return dados


def apagar_todos_caminhoes():
    """Remove todos os caminhões da tabela."""
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM caminhoes")
        conn.commit()
        conn.close()

        logger.info("Todos os caminhões foram apagados")
        return True

    except Exception as erro:
        logger.error(f"Erro ao apagar caminhões: {erro}")
        return False


def criar_caminhoes_padrao():

    conn = conectar()
    cursor = conn.cursor()

    caminhoes = [
        ("Renault Master", "Renault Master", "Motorista Master", 1500, 9),
        ("3/4 Branco", "Caminhão 3/4 Branco", "Motorista Branco", 3500, 7),
        ("3/4 Preto", "Caminhão 3/4 Preto", "Motorista Preto", 3500, 7),
        ("Toco", "Caminhão Toco", "Motorista Toco", 6000, 5),
    ]

    for placa, modelo, motorista, capacidade, media in caminhoes:
        cursor.execute("SELECT id FROM caminhoes WHERE placa = ?", (placa,))
        existe = cursor.fetchone()

        if not existe:
            cursor.execute("""
                INSERT INTO caminhoes
                (placa, modelo, motorista, capacidade_kg, media_km_l)
                VALUES (?, ?, ?, ?, ?)
            """, (placa, modelo, motorista, capacidade, media))

            registrar_sync(cursor, "caminhoes", cursor.lastrowid)

    conn.commit()
    conn.close()


def criar_viagem(caminhao_id, notas_ids, data_saida, motorista):

    if not notas_ids:
        raise ValueError("Nenhuma nota selecionada.")

    placeholders = ",".join(["?"] * len(notas_ids))

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT id, status
            FROM notas
            WHERE id IN ({placeholders})
        """, notas_ids)

        for nota_id, status in cursor.fetchall():
            if status != "Disponível":
                raise ValueError(
                    f"A nota #{nota_id} não está disponível (status: {status})."
                )

        cursor.execute(f"""
            SELECT
                COALESCE(SUM(peso), 0),
                COALESCE(SUM(valor_frete), 0)
            FROM notas
            WHERE id IN ({placeholders})
        """, notas_ids)

        peso_total, frete_total = cursor.fetchone()

        cursor.execute("""
            INSERT INTO viagens (
                caminhao_id,
                data_saida,
                motorista,
                status,
                peso_total,
                frete_total,
                custo_total,
                lucro_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            caminhao_id,
            data_saida,
            motorista,
            "Em viagem",
            peso_total,
            frete_total,
            0,
            frete_total
        ))

        viagem_id = cursor.lastrowid
        registrar_sync(cursor, "viagens", viagem_id)

        for nota_id in notas_ids:
            cursor.execute("""
                INSERT INTO viagem_notas (viagem_id, nota_id)
                VALUES (?, ?)
            """, (viagem_id, nota_id))

            viagem_nota_id = cursor.lastrowid
            registrar_sync(cursor, "viagem_notas", viagem_nota_id)

            cursor.execute("""
                UPDATE notas
                SET status = 'Em viagem'
                WHERE id = ?
            """, (nota_id,))

            registrar_sync(cursor, "notas", nota_id)

        conn.commit()

    return viagem_id


def apagar_viagem(viagem_id):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id FROM viagens WHERE id = ?",
            (viagem_id,)
        )

        if not cursor.fetchone():
            raise Exception("Viagem não encontrada.")

        cursor.execute(
            "SELECT id, nota_id FROM viagem_notas WHERE viagem_id = ?",
            (viagem_id,)
        )

        viagem_notas = cursor.fetchall()
        notas_ids = [nota_id for _, nota_id in viagem_notas]

        for viagem_nota_id, nota_id in viagem_notas:
            if viagem_nota_id:
                registrar_sync(cursor, "viagem_notas", viagem_nota_id, "DELETE")

        for nota_id in notas_ids:
            cursor.execute("""
                UPDATE notas
                SET status = 'Disponível'
                WHERE id = ?
            """, (nota_id,))

            registrar_sync(cursor, "notas", nota_id)

        cursor.execute(
            "DELETE FROM viagem_notas WHERE viagem_id = ?",
            (viagem_id,)
        )

        registrar_sync(cursor, "viagens", viagem_id, "DELETE")

        cursor.execute(
            "DELETE FROM viagens WHERE id = ?",
            (viagem_id,)
        )

        conn.commit()

        return len(notas_ids)

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def cadastrar_caminhao(placa, modelo, motorista, capacidade_kg, media_km_l):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO caminhoes (
            placa,
            modelo,
            motorista,
            capacidade_kg,
            media_km_l
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        placa,
        modelo,
        motorista,
        capacidade_kg,
        media_km_l
    ))

    registrar_sync(cursor, "caminhoes", cursor.lastrowid)

    conn.commit()
    conn.close()


def listar_viagens():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            viagens.id,
            viagens.data_saida,
            caminhoes.modelo,
            caminhoes.placa,
            viagens.motorista,
            viagens.status,
            viagens.peso_total,
            viagens.frete_total,
            COUNT(viagem_notas.nota_id) as total_notas
        FROM viagens
        LEFT JOIN caminhoes ON caminhoes.id = viagens.caminhao_id
        LEFT JOIN viagem_notas ON viagem_notas.viagem_id = viagens.id
        GROUP BY viagens.id
        ORDER BY viagens.id DESC
    """)

    dados = cursor.fetchall()
    conn.close()

    return dados

def listar_notas_da_viagem(viagem_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            notas.id,
            notas.numero_cte,
            remetente.nome,
            destinatario.nome,
            notas.origem,
            notas.destino,
            notas.valor_frete,
            notas.peso,
            notas.status
        FROM viagem_notas
        INNER JOIN notas ON notas.id = viagem_notas.nota_id
        LEFT JOIN clientes remetente ON remetente.id = notas.remetente_id
        LEFT JOIN clientes destinatario ON destinatario.id = notas.destinatario_id
        WHERE viagem_notas.viagem_id = ?
        ORDER BY notas.id DESC
    """, (viagem_id,))

    dados = cursor.fetchall()
    conn.close()

    return dados

def finalizar_viagem(viagem_id, data_retorno):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE viagens
        SET status = 'Finalizada',
            data_retorno = ?
        WHERE id = ?
    """, (data_retorno, viagem_id))

    cursor.execute("""
        UPDATE notas
        SET status = 'Entregue'
        WHERE id IN (
            SELECT nota_id
            FROM viagem_notas
            WHERE viagem_id = ?
        )
    """, (viagem_id,))

    registrar_sync(cursor, "viagens", viagem_id)

    cursor.execute(
        "SELECT nota_id FROM viagem_notas WHERE viagem_id = ?",
        (viagem_id,)
    )

    for (nota_id,) in cursor.fetchall():
        registrar_sync(cursor, "notas", nota_id)

    conn.commit()
    conn.close()

    return True

def buscar_detalhes_viagem(viagem_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            viagens.id,
            viagens.data_saida,
            viagens.data_retorno,
            viagens.motorista,
            viagens.status,
            viagens.peso_total,
            viagens.frete_total,
            caminhoes.modelo,
            caminhoes.placa,
            caminhoes.capacidade_kg
        FROM viagens
        LEFT JOIN caminhoes ON caminhoes.id = viagens.caminhao_id
        WHERE viagens.id = ?
    """, (viagem_id,))

    dados = cursor.fetchone()
    conn.close()

    return dados

def dados_dashboard(tipo_periodo="Geral", mes=None, ano=None):

    conn = conectar()
    cursor = conn.cursor()

    filtro_viagens = ""
    params_viagens = []

    filtro_manifestos = ""
    params_manifestos = []

    filtro_notas = ""
    params_notas = []

    if tipo_periodo == "Mês" and mes and ano:
        filtro_viagens = "WHERE substr(data_saida, 4, 2) = ? AND substr(data_saida, 7, 4) = ?"
        params_viagens = [mes, ano]

        filtro_manifestos = "WHERE substr(data_importacao, 6, 2) = ? AND substr(data_importacao, 1, 4) = ?"
        params_manifestos = [mes, ano]

        filtro_notas = "WHERE substr(criado_em, 6, 2) = ? AND substr(criado_em, 1, 4) = ?"
        params_notas = [mes, ano]

    elif tipo_periodo == "Ano" and ano:
        filtro_viagens = "WHERE substr(data_saida, 7, 4) = ?"
        params_viagens = [ano]

        filtro_manifestos = "WHERE substr(data_importacao, 1, 4) = ?"
        params_manifestos = [ano]

        filtro_notas = "WHERE substr(criado_em, 1, 4) = ?"
        params_notas = [ano]

    cursor.execute(f"SELECT COUNT(*) FROM manifestos {filtro_manifestos}", params_manifestos)
    total_manifestos = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM notas {filtro_notas}", params_notas)
    total_notas = cursor.fetchone()[0]

    separador_notas = "AND" if filtro_notas else "WHERE"
    separador_viagens = "AND" if filtro_viagens else "WHERE"

    cursor.execute(
        f"SELECT COUNT(*) FROM notas {filtro_notas} {separador_notas} status = 'Disponível'",
        params_notas,
    )
    notas_disponiveis = cursor.fetchone()[0]

    cursor.execute(
        f"SELECT COUNT(*) FROM notas {filtro_notas} {separador_notas} status = 'Em viagem'",
        params_notas,
    )
    notas_em_viagem = cursor.fetchone()[0]

    cursor.execute(
        f"SELECT COUNT(*) FROM notas {filtro_notas} {separador_notas} status = 'Entregue'",
        params_notas,
    )
    notas_entregues = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM viagens {filtro_viagens}", params_viagens)
    total_viagens = cursor.fetchone()[0]

    cursor.execute(
        f"SELECT COUNT(*) FROM viagens {filtro_viagens} {separador_viagens} status = 'Em viagem'",
        params_viagens,
    )
    viagens_em_andamento = cursor.fetchone()[0]

    cursor.execute(
        f"SELECT COUNT(*) FROM viagens {filtro_viagens} {separador_viagens} status = 'Finalizada'",
        params_viagens,
    )
    viagens_finalizadas = cursor.fetchone()[0]

    cursor.execute(f"SELECT COALESCE(SUM(frete_total), 0) FROM viagens {filtro_viagens}", params_viagens)
    frete_total = cursor.fetchone()[0]

    cursor.execute(f"SELECT COALESCE(SUM(peso_total), 0) FROM viagens {filtro_viagens}", params_viagens)
    peso_total = cursor.fetchone()[0]

    conn.close()

    return {
        "total_manifestos": total_manifestos,
        "total_notas": total_notas,
        "notas_disponiveis": notas_disponiveis,
        "notas_em_viagem": notas_em_viagem,
        "notas_entregues": notas_entregues,
        "total_viagens": total_viagens,
        "viagens_em_andamento": viagens_em_andamento,
        "viagens_finalizadas": viagens_finalizadas,
        "frete_total": frete_total,
        "peso_total": peso_total
    }

def top_destinos_dashboard(tipo_periodo="Geral", mes=None, ano=None):

    conn = conectar()
    cursor = conn.cursor()

    filtro = ""
    params = []

    if tipo_periodo == "Mês" and mes and ano:
        filtro = "WHERE substr(notas.criado_em, 6, 2) = ? AND substr(notas.criado_em, 1, 4) = ?"
        params = [mes, ano]

    elif tipo_periodo == "Ano" and ano:
        filtro = "WHERE substr(notas.criado_em, 1, 4) = ?"
        params = [ano]

    cursor.execute(f"""
        SELECT
            notas.destino,
            COUNT(notas.id) as total_notas,
            COALESCE(SUM(notas.peso), 0) as peso_total
        FROM notas
        {filtro}
        GROUP BY notas.destino
        ORDER BY total_notas DESC
        LIMIT 4
    """, params)

    dados = cursor.fetchall()
    conn.close()

    return dados

def criar_operacao_sp(dados):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO operacoes_sp (
                data_operacao,
                nome_caminhao,
                placa,
                motorista,
                valor_notas,
                frete_carreta,
                pedagio_carreta,
                outros_custos,
                custo_total,
                liquido
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados.get("data_operacao"),
            dados.get("nome_caminhao"),
            dados.get("placa"),
            dados.get("motorista"),
            dados.get("valor_notas", 0),
            dados.get("frete_carreta", 0),
            dados.get("pedagio_carreta", 0),
            dados.get("outros_custos", 0),
            dados.get("custo_total", 0),
            dados.get("liquido", 0)
        ))
        operacao_id = cursor.lastrowid
        registrar_sync(cursor, "operacoes_sp", operacao_id)
        conn.commit()
    finally:
        conn.close()
    return True


def listar_operacoes_sp():
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                id,
                data_operacao,
                nome_caminhao,
                placa,
                motorista,
                valor_notas,
                frete_carreta,
                pedagio_carreta,
                outros_custos,
                custo_total,
                liquido
            FROM operacoes_sp
            ORDER BY id DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()

def gerar_ranking_clientes_v6(tipo_periodo="Geral", mes=None, ano=None):

    conn = conectar()
    cursor = conn.cursor()

    filtro = ""
    params = []

    if tipo_periodo == "Mês" and mes and ano:
        filtro = "WHERE substr(notas.criado_em, 6, 2) = ? AND substr(notas.criado_em, 1, 4) = ?"
        params = [mes, ano]

    elif tipo_periodo == "Ano" and ano:
        filtro = "WHERE substr(notas.criado_em, 1, 4) = ?"
        params = [ano]

    cursor.execute(f"""
        SELECT
            destinatario.nome as cliente,
            COUNT(notas.id) as total_notas,
            COALESCE(SUM(notas.valor_mercadoria), 0) as valor_notas,
            COALESCE(SUM(notas.valor_frete), 0) as frete_total,
            COALESCE(SUM(notas.peso), 0) as peso_total
        FROM notas
        LEFT JOIN clientes destinatario
            ON destinatario.id = notas.destinatario_id
        {filtro}
        GROUP BY destinatario.nome
        ORDER BY frete_total DESC
    """, params)

    dados = cursor.fetchall()
    conn.close()

    ranking = []

    for linha in dados:
        cliente, total_notas, valor_notas, frete_total, peso_total = linha

        percentual_medio = 0

        if valor_notas and valor_notas > 0:
            percentual_medio = (frete_total / valor_notas) * 100

        ranking.append({
            "cliente": cliente or "Cliente não informado",
            "total_notas": total_notas or 0,
            "valor_notas": valor_notas or 0,
            "frete": frete_total or 0,
            "peso": peso_total or 0,
            "percentual_medio": percentual_medio
        })

    return ranking


def buscar_clientes_por_nome(termo_busca: str):
    """
    Busca clientes pelo nome (destinatários).
    
    Args:
        termo_busca: Termo para busca (pode ser parcial)
        
    Returns:
        Lista de tuplas (id, nome, cnpj, cidade, uf)
    """
    conn = conectar()
    cursor = conn.cursor()
    
    termo = f"%{termo_busca}%"
    
    cursor.execute("""
        SELECT id, nome, cnpj, cidade, uf
        FROM clientes
        WHERE nome LIKE ?
        ORDER BY nome
        LIMIT 50
    """, (termo,))
    
    dados = cursor.fetchall()
    conn.close()
    
    return dados


def listar_notas_por_cliente(
    cliente_id: int,
    apenas_disponiveis: bool = True,
    excluir_vinculadas: bool = True
):
    """
    Lista notas filtradas por cliente.
    
    Args:
        cliente_id: ID do cliente (destinatário)
        apenas_disponiveis: Se True, retorna apenas notas com status 'Disponível'
        excluir_vinculadas: Se True, exclui notas já vinculadas a alguma viagem
        
    Returns:
        Lista de tuplas com dados das notas
    """
    conn = conectar()
    cursor = conn.cursor()
    
    query = """
        SELECT
            notas.id,
            notas.numero_cte,
            notas.chave_nfe,
            destinatario.nome as cliente_nome,
            notas.destino as cidade,
            notas.peso,
            notas.valor_frete,
            notas.criado_em as data,
            notas.status
        FROM notas
        LEFT JOIN clientes destinatario
            ON destinatario.id = notas.destinatario_id
        WHERE notas.destinatario_id = ?
    """
    
    params = [cliente_id]
    
    if apenas_disponiveis:
        query += " AND notas.status = 'Disponível'"
    
    if excluir_vinculadas:
        query += """
            AND notas.id NOT IN (
                SELECT nota_id
                FROM viagem_notas
            )
        """
    
    query += " ORDER BY notas.id DESC"
    
    cursor.execute(query, params)
    dados = cursor.fetchall()
    conn.close()
    
    return dados


def calcular_resumo_notas(notas_ids: list):
    """
    Calcula resumo das notas selecionadas.
    
    Args:
        notas_ids: Lista de IDs das notas
        
    Returns:
        Dict com quantidade, peso_total, frete_total, volumes
    """
    if not notas_ids:
        return {
            "quantidade": 0,
            "peso_total": 0,
            "frete_total": 0,
            "volumes": 0
        }
    
    conn = conectar()
    cursor = conn.cursor()
    
    placeholders = ",".join(["?"] * len(notas_ids))
    
    cursor.execute(f"""
        SELECT
            COUNT(*) as quantidade,
            COALESCE(SUM(peso), 0) as peso_total,
            COALESCE(SUM(valor_frete), 0) as frete_total
        FROM notas
        WHERE id IN ({placeholders})
    """, notas_ids)
    
    quantidade, peso_total, frete_total = cursor.fetchone()
    
    # Volumes é estimado como 1 volume por nota (pode ser ajustado no futuro)
    volumes = quantidade
    
    conn.close()
    
    return {
        "quantidade": quantidade or 0,
        "peso_total": peso_total or 0,
        "frete_total": frete_total or 0,
        "volumes": volumes or 0
    }
