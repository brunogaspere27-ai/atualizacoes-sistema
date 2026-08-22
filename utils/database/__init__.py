"""
Database utils - Criacao e gerenciamento do banco SQLite.
Delega toda a criacao de tabelas para _conexao.py (schema unico).
"""

from utils.database._conexao import (
    conectar, get_connection, get_connection_rows,
    criar_banco, tabela_existe_sqlite, registrar_sync, agora_sync
)
from utils.database.caminhoes import listar_caminhoes, apagar_todos_caminhoes, cadastrar_caminhao
from utils.database.clientes import buscar_cliente_por_cnpj, criar_cliente, obter_ou_criar_cliente, buscar_clientes_por_nome
from utils.database.notas import (
    salvar_nota, listar_notas, nota_existe,
    criar_manifesto, listar_manifestos, listar_notas_por_manifesto,
    apagar_manifesto, listar_notas_por_cliente, calcular_resumo_notas
)
from utils.database.viagens import (
    criar_viagem, apagar_viagem, listar_viagens,
    listar_notas_da_viagem, finalizar_viagem, buscar_detalhes_viagem
)
from utils.database.relatorios import dados_dashboard, top_destinos_dashboard


def sqlite_connection_factory(db_path=None):
    import sqlite3
    if db_path is None:
        db_path = "data/cw_transportadora.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def criar_caminhoes_padrao():
    """Cria caminhoes padrao se nao existirem."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM caminhoes")
    if cursor.fetchone()[0] == 0:
        caminhoes_padrao = [
            ("ABC-1234", "Volvo FH 540", 2022, 45000, 3.5, "Joao Silva"),
            ("DEF-5678", "Scania R450", 2021, 42000, 3.2, "Pedro Santos"),
            ("GHI-9012", "Mercedes Actros", 2023, 48000, 3.8, "Carlos Oliveira"),
        ]
        for placa, modelo, ano, cap, media, mot in caminhoes_padrao:
            cursor.execute("""
                INSERT INTO caminhoes (placa, modelo, capacidade_kg, media_km_l, motorista)
                VALUES (?, ?, ?, ?, ?)
            """, (placa, modelo, cap, media, mot))
        conn.commit()
        print("[DB] Caminhoes padrao criados!")
    conn.close()


def criar_operacao_sp(dados):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO operacoes_sp (data_operacao, nome_caminhao, placa, motorista,
            valor_notas, frete_carreta, pedagio_carreta, outros_custos, custo_total, liquido, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados.get('data_operacao'), dados.get('nome_caminhao'), dados.get('placa'),
        dados.get('motorista'), dados.get('valor_notas'), dados.get('frete_carreta'),
        dados.get('pedagio_carreta'), dados.get('outros_custos'), dados.get('custo_total'),
        dados.get('liquido'), dados.get('status', 'pendente')
    ))
    conn.commit()
    conn.close()
    return cursor.lastrowid


def listar_operacoes_sp():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operacoes_sp")
    return [dict(row) for row in cursor.fetchall()]


def gerar_ranking_clientes_v6(tipo, mes, ano, conn=None):
    return []
