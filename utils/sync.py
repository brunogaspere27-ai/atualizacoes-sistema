import json
import sqlite3
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Any

try:
    from psycopg2.extras import execute_values
except ImportError:  # pragma: no cover
    execute_values = None

from config.settings import settings
from utils.database import (
    DB_NAME,
    TABELAS_SYNC,
    criar_banco,
    get_connection_rows,
    tabela_existe_sqlite,
)
from utils.logger import get_logger
from utils.performance import sqlite_connection_factory
from utils.supabase_db import (
    conectar_supabase,
    supabase_habilitado,
    SupabaseNaoConfiguradoError,
    SupabaseOfflineError,
)

logger = get_logger(__name__)

DB_LOCAL = DB_NAME
ORDEM_SYNC = {tabela: indice for indice, tabela in enumerate(TABELAS_SYNC)}
COLUNAS_IGNORADAS_SYNC = set()


def agora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def conectar_local() -> sqlite3.Connection:
    conn = sqlite3.connect(
        DB_LOCAL,
        timeout=30,
        check_same_thread=False,
        factory=sqlite_connection_factory(),
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def resultado_sync(**kwargs) -> Dict[str, Any]:
    base = {
        "status": "ok",
        "offline": False,
        "mensagem": "",
        "ultima_sync": None,
        "enviados": 0,
        "baixados": 0,
        "erros": 0,
        "pendencias": 0,
    }
    base.update(kwargs)
    return base


def carregar_config_sync() -> Dict[str, str]:
    caminho = settings.sync_config_path
    if not caminho.exists():
        return {"ultima_sincronizacao": "2000-01-01 00:00:00"}

    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except Exception as erro:
        logger.error(f"Erro ao carregar configuração de sync: {erro}")
        return {"ultima_sincronizacao": "2000-01-01 00:00:00"}


def salvar_config_sync(data_sync: str) -> None:
    try:
        settings.sync_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(settings.sync_config_path, "w", encoding="utf-8") as arquivo:
            json.dump({"ultima_sincronizacao": data_sync}, arquivo, ensure_ascii=False, indent=4)
    except Exception as erro:
        logger.error(f"Erro ao salvar configuração de sync: {erro}")



def tabela_existe_supabase(cursor_cloud, tabela: str) -> bool:
    try:
        cursor_cloud.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = %s
        """, (tabela,))
        return cursor_cloud.fetchone() is not None
    except Exception as erro:
        logger.error(f"Erro ao verificar tabela {tabela} no Supabase: {erro}")
        return False


def colunas_sqlite(cursor: sqlite3.Cursor, tabela: str):
    cursor.execute(f"PRAGMA table_info({tabela})")
    return cursor.fetchall()


def colunas_supabase(cursor_cloud, tabela: str) -> List[Tuple]:
    try:
        cursor_cloud.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = %s
            ORDER BY ordinal_position
        """, (tabela,))
        return cursor_cloud.fetchall()
    except Exception as erro:
        logger.error(f"Erro ao obter colunas da tabela {tabela} no Supabase: {erro}")
        return []


def tipo_postgres(tipo_sqlite: str) -> str:
    tipo = str(tipo_sqlite or "").upper()
    if "INT" in tipo:
        return "INTEGER"
    if "REAL" in tipo or "FLOA" in tipo or "DOUB" in tipo or "NUMERIC" in tipo:
        return "DOUBLE PRECISION"
    return "TEXT"


def tipo_sqlite(tipo_postgres: str) -> str:
    tipo = str(tipo_postgres or "").upper()
    if "INT" in tipo:
        return "INTEGER"
    if "DOUBLE" in tipo or "REAL" in tipo or "NUMERIC" in tipo:
        return "REAL"
    return "TEXT"


def preparar_sync_log() -> None:
    conn = conectar_local()
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()


def preparar_sqlite_sync() -> None:
    preparar_sync_log()
    conn = conectar_local()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sync_log
        SET status = 'PENDENTE',
            tentativas = 0,
            erro = NULL
        WHERE status = 'ERRO'
          AND tentativas >= 10
    """)

    for tabela in TABELAS_SYNC:
        if not tabela_existe_sqlite(cursor, tabela):
            continue

        for coluna, tipo in [
            ("sync_id", "TEXT"),
            ("sincronizado", "INTEGER DEFAULT 0"),
            ("atualizado_em", "TEXT"),
            ("deletado", "INTEGER DEFAULT 0"),
        ]:
            try:
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}")
            except sqlite3.OperationalError:
                pass  # Coluna já existe

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
            """, (agora(),))
        except Exception as erro:
            logger.warning(f"Não foi possível preparar tabela {tabela} para sync: {erro}")

    conn.commit()
    conn.close()


def criar_ou_atualizar_tabela_supabase(cursor_cloud, tabela: str, colunas: List[sqlite3.Row]) -> None:
    campos = []
    for coluna in colunas:
        nome = coluna["name"]
        tipo = coluna["type"]
        if nome == "id":
            campos.append("id INTEGER PRIMARY KEY")
        else:
            campos.append(f"{nome} {tipo_postgres(tipo)}")

    cursor_cloud.execute(f"CREATE TABLE IF NOT EXISTS {tabela} ({', '.join(campos)})")
    for coluna in colunas:
        nome = coluna["name"]
        if nome == "id":
            continue
        cursor_cloud.execute(
            f"ALTER TABLE {tabela} ADD COLUMN IF NOT EXISTS {nome} {tipo_postgres(coluna['type'])}"
        )

    nomes = [coluna["name"] for coluna in colunas]
    if "sync_id" in nomes:
        cursor_cloud.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{tabela}_sync_id ON {tabela}(sync_id)"
        )


def ordenar_grupos_sync(grupos):
    return sorted(grupos.items(), key=lambda item: ORDEM_SYNC.get(item[0], 999))


def filtrar_colunas_sync(colunas: List[str]) -> List[str]:
    return [coluna for coluna in colunas if coluna not in COLUNAS_IGNORADAS_SYNC]


def _referencias_numericas(referencias: List[str]) -> List[str]:
    numericas = []
    for referencia in referencias:
        try:
            int(referencia)
            numericas.append(str(referencia))
        except (TypeError, ValueError):
            continue
    return numericas


def _referencias_sync_id(referencias: List[str]) -> List[str]:
    sync_ids = []
    for referencia in referencias:
        try:
            int(referencia)
        except (TypeError, ValueError):
            if referencia:
                sync_ids.append(str(referencia))
    return sync_ids


def buscar_registros_locais(cursor_local, tabela: str, referencias: List[str]) -> List[sqlite3.Row]:
    """Busca registros pelo id numérico ou pelo sync_id."""
    if not referencias:
        return []

    registros: Dict[str, sqlite3.Row] = {}
    ids = _referencias_numericas(referencias)
    sync_ids = _referencias_sync_id(referencias)

    if ids:
        placeholders = ",".join(["?"] * len(ids))
        cursor_local.execute(
            f"SELECT * FROM {tabela} WHERE id IN ({placeholders})",
            ids,
        )
        for row in cursor_local.fetchall():
            registros[str(row["id"])] = row

    if sync_ids:
        placeholders = ",".join(["?"] * len(sync_ids))
        cursor_local.execute(
            f"SELECT * FROM {tabela} WHERE sync_id IN ({placeholders})",
            sync_ids,
        )
        for row in cursor_local.fetchall():
            chave = str(row["sync_id"]) if row["sync_id"] else str(row["id"])
            registros[chave] = row

    return list(registros.values())


def _timestamp_mais_recente(valor_local: Any, valor_remoto: Any) -> bool:
    if not valor_remoto:
        return False
    if not valor_local:
        return True
    return str(valor_remoto) > str(valor_local)


def marcar_registros_sincronizados(cursor_local, tabela: str, registros: List[sqlite3.Row]) -> None:
    agora_atual = agora()
    for registro in registros:
        try:
            cursor_local.execute(
                f"""
                UPDATE {tabela}
                SET sincronizado = 1,
                    atualizado_em = COALESCE(NULLIF(atualizado_em, ''), ?)
                WHERE id = ?
                """,
                (agora_atual, registro["id"]),
            )
        except Exception as erro:
            logger.warning(f"Não foi possível marcar {tabela}:{registro['id']} como sincronizado: {erro}")


def reparar_e_enfileirar_fila() -> int:
    """
    Garante que registros locais pendentes estejam na fila de envio.
    Corrige entradas marcadas como OK sem envio real e registros nunca enfileirados.
    """
    from utils.database import registrar_sync

    preparar_sync_log()
    conn = conectar_local()
    cursor = conn.cursor()
    total = 0

    try:
        for tabela in TABELAS_SYNC:
            if not tabela_existe_sqlite(cursor, tabela):
                continue

            cursor.execute(
                f"""
                SELECT id, sync_id, atualizado_em
                FROM {tabela}
                WHERE COALESCE(deletado, 0) = 0
                """
            )
            registros = cursor.fetchall()

            for registro in registros:
                registro_id = registro["id"]
                sync_id = registro["sync_id"]
                atualizado_em = registro["atualizado_em"]
                referencias = [str(registro_id)]
                if sync_id:
                    referencias.append(str(sync_id))

                placeholders = ",".join(["?"] * len(referencias))
                cursor.execute(
                    f"""
                    SELECT status, sincronizado_em
                    FROM sync_log
                    WHERE tabela = ?
                      AND registro_id IN ({placeholders})
                    ORDER BY id DESC
                    LIMIT 1
                    """,
                    [tabela, *referencias],
                )
                ultimo_log = cursor.fetchone()

                precisa_enfileirar = False
                if ultimo_log is None:
                    precisa_enfileirar = True
                elif ultimo_log["status"] == "ERRO":
                    precisa_enfileirar = True
                elif ultimo_log["status"] == "OK":
                    cursor.execute(
                        f"SELECT sincronizado FROM {tabela} WHERE id = ?",
                        (registro_id,),
                    )
                    estado_local = cursor.fetchone()
                    if estado_local and not estado_local["sincronizado"]:
                        precisa_enfileirar = True
                    elif atualizado_em and ultimo_log["sincronizado_em"]:
                        if str(atualizado_em) > str(ultimo_log["sincronizado_em"]):
                            precisa_enfileirar = True

                if precisa_enfileirar:
                    registrar_sync(cursor, tabela, registro_id)
                    total += 1

        conn.commit()
    finally:
        conn.close()

    return total


def enviar_lote_tabela(cursor_local, cursor_cloud, tabela: str, itens: List[sqlite3.Row]):
    if not itens:
        return [], []

    itens_delete = [item for item in itens if str(item["operacao"]).upper() == "DELETE"]
    itens_upsert = [item for item in itens if str(item["operacao"]).upper() != "DELETE"]

    sucessos: List[int] = []
    erros: List[Tuple[int, str]] = []

    if itens_delete:
        ids_delete: List[int] = []
        sync_ids_delete: List[str] = []
        for item in itens_delete:
            try:
                ids_delete.append(int(item["registro_id"]))
            except (TypeError, ValueError):
                if item["registro_id"]:
                    sync_ids_delete.append(str(item["registro_id"]))
                else:
                    sucessos.append(item["id"])

        if ids_delete or sync_ids_delete:
            try:
                if tabela == "manifestos" and ids_delete:
                    cursor_cloud.execute("""
                        DELETE FROM viagem_notas
                        WHERE nota_id IN (
                            SELECT id FROM notas WHERE manifesto_id = ANY(%s)
                        )
                    """, (ids_delete,))
                    cursor_cloud.execute("DELETE FROM notas WHERE manifesto_id = ANY(%s)", (ids_delete,))

                if tabela == "notas" and ids_delete:
                    cursor_cloud.execute("DELETE FROM viagem_notas WHERE nota_id = ANY(%s)", (ids_delete,))

                if tabela == "viagens" and ids_delete:
                    cursor_cloud.execute("DELETE FROM viagem_notas WHERE viagem_id = ANY(%s)", (ids_delete,))

                if ids_delete:
                    cursor_cloud.execute(f"DELETE FROM {tabela} WHERE id = ANY(%s)", (ids_delete,))
                if sync_ids_delete:
                    cursor_cloud.execute(f"DELETE FROM {tabela} WHERE sync_id = ANY(%s)", (sync_ids_delete,))
                sucessos.extend([item["id"] for item in itens_delete if item["id"] not in sucessos])
            except Exception as erro:
                erros.extend([(item["id"], str(erro)) for item in itens_delete])

    if itens_upsert:
        referencias = [str(item["registro_id"]) for item in itens_upsert]
        rows = buscar_registros_locais(cursor_local, tabela, referencias)
        dados = [dict(row) for row in rows]

        if not dados:
            erros.extend([
                (item["id"], f"Registro não encontrado em {tabela}: {item['registro_id']}")
                for item in itens_upsert
            ])
            return sucessos, erros

        colunas_insert = filtrar_colunas_sync(list(dados[0].keys()))
        conflict_column = "sync_id" if "sync_id" in colunas_insert else "id"
        colunas_set = [coluna for coluna in colunas_insert if coluna != "id"]
        updates = ", ".join([f"{col} = EXCLUDED.{col}" for col in colunas_set])
        sql = f"""
            INSERT INTO {tabela} ({", ".join(colunas_insert)})
            VALUES %s
            ON CONFLICT ({conflict_column})
            DO UPDATE SET {updates}
        """
        valores = [tuple(dado[coluna] for coluna in colunas_insert) for dado in dados]

        try:
            execute_values(cursor_cloud, sql, valores, page_size=500)
            marcar_registros_sincronizados(cursor_local, tabela, rows)
            sucessos.extend([item["id"] for item in itens_upsert])
        except Exception as erro:
            erros.extend([(item["id"], str(erro)) for item in itens_upsert])

    return sucessos, erros


def processar_fila_envio() -> Tuple[int, int]:
    if execute_values is None:
        raise RuntimeError("psycopg2 não está instalado; sincronização com nuvem indisponível.")

    preparar_sync_log()
    conn_local = conectar_local()
    conn_cloud = conectar_supabase()
    cursor_local = conn_local.cursor()
    cursor_cloud = conn_cloud.cursor()

    total_enviados = 0
    total_erros = 0

    try:
        cursor_local.execute("""
            SELECT *
            FROM sync_log
            WHERE status IN ('PENDENTE', 'ERRO')
              AND tentativas < 10
            ORDER BY id
            LIMIT 1000
        """)
        pendencias = cursor_local.fetchall()
        if not pendencias:
            return 0, 0

        grupos = {}
        for item in pendencias:
            grupos.setdefault(item["tabela"], []).append(item)

        for tabela, itens in ordenar_grupos_sync(grupos):
            cursor_local.execute(f"PRAGMA table_info({tabela})")
            info_colunas = cursor_local.fetchall()
            if info_colunas:
                criar_ou_atualizar_tabela_supabase(cursor_cloud, tabela, info_colunas)

            sucesso_logs, erros_logs = enviar_lote_tabela(cursor_local, cursor_cloud, tabela, itens)

            if sucesso_logs:
                cursor_local.executemany("""
                    UPDATE sync_log
                    SET status = 'OK',
                        erro = NULL,
                        sincronizado_em = ?
                    WHERE id = ?
                """, [(agora(), log_id) for log_id in sucesso_logs])

            if erros_logs:
                cursor_local.executemany("""
                    UPDATE sync_log
                    SET status = 'ERRO',
                        tentativas = tentativas + 1,
                        erro = ?
                    WHERE id = ?
                """, [(mensagem, log_id) for log_id, mensagem in erros_logs])

            total_enviados += len(sucesso_logs)
            total_erros += len(erros_logs)
            conn_cloud.commit()
            conn_local.commit()
    finally:
        conn_cloud.close()
        conn_local.close()

    return total_enviados, total_erros


def criar_tabela_sqlite_se_nao_existir(cursor_local, tabela: str, colunas: List[Tuple]):
    if tabela_existe_sqlite(cursor_local, tabela):
        return

    campos = []
    for nome, tipo in colunas:
        if nome == "id":
            campos.append("id INTEGER PRIMARY KEY")
        else:
            campos.append(f"{nome} {tipo_sqlite(tipo)}")
    cursor_local.execute(f"CREATE TABLE IF NOT EXISTS {tabela} ({', '.join(campos)})")


def garantir_colunas_sqlite(cursor_local, tabela: str, colunas: List[Tuple]):
    cursor_local.execute(f"PRAGMA table_info({tabela})")
    existentes = [coluna["name"] for coluna in cursor_local.fetchall()]
    for nome, tipo in colunas:
        if nome not in existentes:
            try:
                cursor_local.execute(f"ALTER TABLE {tabela} ADD COLUMN {nome} {tipo_sqlite(tipo)}")
            except sqlite3.OperationalError:
                pass  # Coluna já existe
    if "sync_id" in [coluna[0] for coluna in colunas]:
        try:
            cursor_local.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{tabela}_sync_id ON {tabela}(sync_id)"
            )
        except sqlite3.OperationalError:
            pass  # Índice já existe


def baixar_tabela(cursor_local, cursor_cloud, tabela: str) -> int:
    if not tabela_existe_supabase(cursor_cloud, tabela):
        return 0

    colunas = colunas_supabase(cursor_cloud, tabela)
    if not colunas:
        return 0

    criar_tabela_sqlite_se_nao_existir(cursor_local, tabela, colunas)
    garantir_colunas_sqlite(cursor_local, tabela, colunas)

    nomes = [coluna[0] for coluna in colunas]
    cursor_cloud.execute(f"SELECT * FROM {tabela}")
    registros = cursor_cloud.fetchall()
    if not registros:
        return 0

    total = 0
    for row in registros:
        row_dict = dict(zip(nomes, row))
        
        try:
            sync_id = row_dict.get("sync_id")
            registro_id = row_dict.get("id")
            atualizado_remoto = row_dict.get("atualizado_em")

            if sync_id and "sync_id" in nomes:
                cursor_local.execute(
                    f"SELECT id, atualizado_em FROM {tabela} WHERE sync_id = ?",
                    (sync_id,),
                )
                local = cursor_local.fetchone()
                if local and not _timestamp_mais_recente(local["atualizado_em"], atualizado_remoto):
                    continue

                placeholders = ", ".join(["?"] * len(nomes))
                updates = ", ".join([f"{col}=excluded.{col}" for col in nomes if col != "id"])
                sql = f"""
                    INSERT INTO {tabela} ({", ".join(nomes)})
                    VALUES ({placeholders})
                    ON CONFLICT(sync_id) DO UPDATE SET {updates}
                """
                cursor_local.execute(sql, list(row))
                total += 1
            else:
                cursor_local.execute(f"SELECT id, atualizado_em FROM {tabela} WHERE id = ?", (registro_id,))
                existe = cursor_local.fetchone()
                
                if existe:
                    if not _timestamp_mais_recente(existe["atualizado_em"], atualizado_remoto):
                        continue
                    set_clause = ", ".join([f"{col} = ?" for col in nomes if col != "id"])
                    sql = f"UPDATE {tabela} SET {set_clause} WHERE id = ?"
                    valores = [row_dict[col] for col in nomes if col != "id"] + [registro_id]
                    cursor_local.execute(sql, valores)
                    total += 1
                else:
                    placeholders = ", ".join(["?"] * len(nomes))
                    sql = f"INSERT INTO {tabela} ({', '.join(nomes)}) VALUES ({placeholders})"
                    cursor_local.execute(sql, list(row))
                    total += 1
        except Exception as erro:
            logger.error(f"Erro ao sincronizar registro em {tabela}: {erro}")
    
    return total


def baixar_do_supabase() -> Tuple[int, int]:
    if execute_values is None:
        raise RuntimeError("psycopg2 não está instalado; sincronização com nuvem indisponível.")

    conn_local = conectar_local()
    conn_cloud = conectar_supabase()
    cursor_local = conn_local.cursor()
    cursor_cloud = conn_cloud.cursor()
    total_baixados = 0
    erros = 0

    try:
        for tabela in TABELAS_SYNC:
            try:
                total_baixados += baixar_tabela(cursor_local, cursor_cloud, tabela)
            except Exception as erro:
                erros += 1
                logger.error(f"Erro ao baixar {tabela}: {erro}")

        conn_local.commit()
    finally:
        conn_cloud.close()
        conn_local.close()

    return total_baixados, erros


_sync_banco_preparado = False


def sincronizar(reparar_fila: bool = True) -> Dict[str, Any]:
    global _sync_banco_preparado
    if not _sync_banco_preparado:
        criar_banco()
        preparar_sqlite_sync()
        _sync_banco_preparado = True

    if not supabase_habilitado():
        pendencias = contar_pendencias_sync()
        return resultado_sync(
            status="offline",
            offline=True,
            mensagem="Nuvem desabilitada. Sistema operando em modo local.",
            pendencias=pendencias,
        )

    if execute_values is None:
        pendencias = contar_pendencias_sync()
        return resultado_sync(
            status="offline",
            offline=True,
            mensagem="Dependências da nuvem não instaladas. Sistema operando em modo local.",
            pendencias=pendencias,
        )

    try:
        config = carregar_config_sync()
        inicio_sync = agora()
        if reparar_fila:
            reparar_e_enfileirar_fila()

        enviados = 0
        erros_envio = 0
        for _ in range(20):
            lote_enviados, lote_erros = processar_fila_envio()
            enviados += lote_enviados
            erros_envio += lote_erros
            if lote_enviados == 0 and lote_erros == 0:
                break

        baixados, erros_baixar = baixar_do_supabase()
        total_erros = erros_envio + erros_baixar
        pendencias = contar_pendencias_sync()

        if total_erros == 0:
            salvar_config_sync(inicio_sync)
            return resultado_sync(
                status="ok",
                mensagem="Sincronização concluída com sucesso.",
                ultima_sync=inicio_sync,
                enviados=enviados,
                baixados=baixados,
                erros=0,
                pendencias=pendencias,
            )

        return resultado_sync(
            status="partial",
            mensagem="Sincronização concluída com pendências.",
            ultima_sync=config.get("ultima_sincronizacao"),
            enviados=enviados,
            baixados=baixados,
            erros=total_erros,
            pendencias=pendencias,
        )
    except SupabaseNaoConfiguradoError:
        pendencias = contar_pendencias_sync()
        return resultado_sync(
            status="offline",
            offline=True,
            mensagem="Nuvem desabilitada. Sistema operando em modo local.",
            pendencias=pendencias,
        )
    except SupabaseOfflineError as erro:
        pendencias = contar_pendencias_sync()
        logger.info(str(erro))
        return resultado_sync(
            status="offline",
            offline=True,
            mensagem=str(erro),
            pendencias=pendencias,
        )
    except Exception as erro:
        logger.error(f"Erro geral na sincronização: {erro}")
        return resultado_sync(
            status="error",
            mensagem=str(erro),
            erros=1,
            pendencias=contar_pendencias_sync(),
        )


def sincronizar_em_segundo_plano():
    thread = threading.Thread(target=sincronizar, daemon=True)
    thread.start()


def contar_pendencias_sync() -> int:
    try:
        conn = conectar_local()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*)
            FROM sync_log
            WHERE status IN ('PENDENTE', 'ERRO')
        """)
        total = cursor.fetchone()[0]
        conn.close()
        return total
    except Exception:
        return 0
