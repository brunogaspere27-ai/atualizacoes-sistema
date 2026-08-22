"""
Camada de acesso a dados (SQLite) - versão simplificada.
"""
import sqlite3
from pathlib import Path

DB_NAME = "cw_transportadora.db"
PASTA_DADOS = Path(".")
TABELAS_SYNC = []


def conectar():
    return sqlite3.connect(DB_NAME)


def criar_banco():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, nome TEXT)")
    conn.commit()
    conn.close()


def get_connection():
    return conectar()


def get_connection_rows():
    return conectar()


def tabela_existe_sqlite(cursor, tabela):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabela}'")
    return cursor.fetchone() is not None


def agora_sync():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def registrar_sync(cursor, tabela, registro_id, operacao="UPSERT"):
    pass


def criar_indices():
    pass


def criar_caminhoes_padrao():
    pass


def listar_caminhoes(conn=None):
    return []


def apagar_todos_caminhoes():
    return True


def cadastrar_caminhao(placa, modelo, motorista, capacidade, media):
    pass


def criar_viagem(cam_id, notas_ids, data_saida, motorista):
    return 1


def apagar_viagem(viagem_id):
    pass


def listar_viagens():
    return []


def listar_notas_da_viagem(viagem_id):
    return []


def finalizar_viagem(viagem_id):
    pass


def buscar_detalhes_viagem(viagem_id):
    return {}


def salvar_nota(dados):
    pass


def listar_notas():
    return []


def nota_existe(chave):
    return False


def criar_manifesto(dados):
    return 1


def listar_manifestos(tipo=None, mes=None, ano=None):
    return []


def listar_notas_por_manifesto(manifesto_id):
    return []


def apagar_manifesto(manifesto_id):
    pass


def listar_notas_por_cliente(cliente_id, apenas_disponiveis=True, excluir_vinculadas=True):
    return []


def calcular_resumo_notas(notas_ids, conn=None):
    return {"quantidade": 0, "peso_total": 0, "frete_total": 0, "volumes": 0}


def buscar_cliente_por_cnpj(cnpj):
    return None


def criar_cliente(dados):
    return 1


def obter_ou_criar_cliente(dados):
    return 1


def buscar_clientes_por_nome(termo):
    return []


def dados_dashboard(tipo, mes, ano, conn=None):
    return {}


def top_destinos_dashboard(tipo, mes, ano, conn=None):
    return []


def criar_operacao_sp(dados):
    return 1


def listar_operacoes_sp():
    return []


def gerar_ranking_clientes_v6(tipo, mes, ano, conn=None):
    return []

