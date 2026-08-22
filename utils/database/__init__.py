"""
Database utils - Criação e gerenciamento do banco SQLite.
"""
import os
import sqlite3
from pathlib import Path


def _get_connection():
    db_path = Path("data/cw_transportadora.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def criar_banco():
    """Cria banco de dados com TODAS as tabelas necessárias."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    # Tabela de operações/fretes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operacoes (
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
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de usuários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT,
            nome_completo TEXT,
            email TEXT,
            eh_mestre INTEGER DEFAULT 0,
            ativo INTEGER DEFAULT 1,
            foto_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de notas/manifestos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            manifesto_id TEXT,
            numero_nota TEXT,
            chave_acesso TEXT,
            remetente TEXT,
            destinatario TEXT,
            valor_mercadoria REAL DEFAULT 0,
            peso REAL DEFAULT 0,
            volumes INTEGER DEFAULT 1,
            data_emissao TEXT,
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de manifestos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manifestos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_manifesto TEXT UNIQUE,
            transportadora TEXT,
            data_manifesto TEXT,
            qtd_notas INTEGER DEFAULT 0,
            valor_total REAL DEFAULT 0,
            status TEXT DEFAULT 'aberto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de caminhões
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caminhoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            placa TEXT UNIQUE,
            modelo TEXT,
            ano INTEGER,
            capacidade_kg REAL DEFAULT 0,
            media_km_l REAL DEFAULT 0,
            motorista_principal TEXT,
            status TEXT DEFAULT 'ativo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de viagens
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS viagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caminhao_id INTEGER,
            motorista TEXT,
            data_saida TEXT,
            data_chegada TEXT,
            km_inicial REAL DEFAULT 0,
            km_final REAL DEFAULT 0,
            status TEXT DEFAULT 'em_andamento',
            valor_frete REAL DEFAULT 0,
            custo_total REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (caminhao_id) REFERENCES caminhoes(id)
        )
    """)
    
    # Tabela de notas_viagem (relacionamento)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas_viagem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            viagem_id INTEGER,
            nota_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (viagem_id) REFERENCES viagens(id),
            FOREIGN KEY (nota_id) REFERENCES notas(id)
        )
    """)
    
    # Tabela de combustível
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS combustivel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caminhao_id INTEGER,
            data_abastecimento TEXT,
            litros REAL DEFAULT 0,
            valor_litro REAL DEFAULT 0,
            valor_total REAL DEFAULT 0,
            km_atual REAL DEFAULT 0,
            posto TEXT,
            tipo_combustivel TEXT DEFAULT 'Diesel',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (caminhao_id) REFERENCES caminhoes(id)
        )
    """)
    
    # Tabela de manutenções
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manutencoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caminhao_id INTEGER,
            data_manutencao TEXT,
            tipo TEXT,
            descricao TEXT,
            oficina TEXT,
            valor REAL DEFAULT 0,
            km_atual REAL DEFAULT 0,
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (caminhao_id) REFERENCES caminhoes(id)
        )
    """)
    
    # Tabela de contas (receber/pagar)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            descricao TEXT,
            valor REAL DEFAULT 0,
            data_vencimento TEXT,
            data_pagamento TEXT,
            status TEXT DEFAULT 'pendente',
            categoria TEXT,
            observacoes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de funcionários
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT UNIQUE,
            cargo TEXT,
            salario REAL DEFAULT 0,
            data_admissao TEXT,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            status TEXT DEFAULT 'ativo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de folha de pagamento
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS folha_funcionarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            mes INTEGER,
            ano INTEGER,
            salario_base REAL DEFAULT 0,
            horas_extras REAL DEFAULT 0,
            valor_horas_extras REAL DEFAULT 0,
            adicionais REAL DEFAULT 0,
            descontos REAL DEFAULT 0,
            valor_liquido REAL DEFAULT 0,
            status TEXT DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id)
        )
    """)
    
    # Tabela de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            razao_social TEXT,
            nome_fantasia TEXT,
            cnpj TEXT UNIQUE,
            ie TEXT,
            endereco TEXT,
            cidade TEXT,
            estado TEXT,
            telefone TEXT,
            email TEXT,
            status TEXT DEFAULT 'ativo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabela de auditoria
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT,
            modulo TEXT,
            usuario TEXT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detalhes TEXT
        )
    """)
    
    # Tabela de configurações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chave TEXT UNIQUE,
            valor TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    print("[DB] Banco de dados criado/atualizado com sucesso!")


def criar_caminhoes_padrao():
    """Cria caminhões padrão se não existirem."""
    conn = _get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM caminhoes")
    if cursor.fetchone()[0] == 0:
        caminhoes_padrao = [
            ("ABC-1234", "Volvo FH 540", 2022, 45000, 3.5, "João Silva"),
            ("DEF-5678", "Scania R450", 2021, 42000, 3.2, "Pedro Santos"),
            ("GHI-9012", "Mercedes Actros", 2023, 48000, 3.8, "Carlos Oliveira"),
        ]
        for placa, modelo, ano, cap, media, mot in caminhoes_padrao:
            cursor.execute("""
                INSERT INTO caminhoes (placa, modelo, ano, capacidade_kg, media_km_l, motorista_principal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (placa, modelo, ano, cap, media, mot))
        conn.commit()
        print("[DB] Caminhões padrão criados!")
    
    conn.close()


def sqlite_connection_factory(db_path=None):
    """Factory de conexões SQLite."""
    if db_path is None:
        db_path = "data/cw_transportadora.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# Legacy function compatibility
def conectar():
    return _get_connection()


def get_connection():
    return _get_connection()


def get_connection_rows():
    return _get_connection()


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


def listar_caminhoes(conn=None):
    if conn is None:
        conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caminhoes")
    return [dict(row) for row in cursor.fetchall()]


def apagar_todos_caminhoes():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM caminhoes")
    conn.commit()
    conn.close()
    return True


def cadastrar_caminhao(placa, modelo, motorista, capacidade, media):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO caminhoes (placa, modelo, motorista_principal, capacidade_kg, media_km_l)
        VALUES (?, ?, ?, ?, ?)
    """, (placa, modelo, motorista, capacidade, media))
    conn.commit()
    conn.close()


def criar_viagem(cam_id, notas_ids, data_saida, motorista):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO viagens (caminhao_id, motorista, data_saida, status)
        VALUES (?, ?, ?, 'em_andamento')
    """, (cam_id, motorista, data_saida))
    viagem_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return viagem_id


def apagar_viagem(viagem_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM viagens WHERE id = ?", (viagem_id,))
    conn.commit()
    conn.close()


def listar_viagens():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM viagens")
    return [dict(row) for row in cursor.fetchall()]


def listar_notas_da_viagem(viagem_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.* FROM notas n
        JOIN notas_viagem nv ON n.id = nv.nota_id
        WHERE nv.viagem_id = ?
    """, (viagem_id,))
    return [dict(row) for row in cursor.fetchall()]


def finalizar_viagem(viagem_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE viagens SET status = 'concluida' WHERE id = ?", (viagem_id,))
    conn.commit()
    conn.close()


def buscar_detalhes_viagem(viagem_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM viagens WHERE id = ?", (viagem_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else {}


def salvar_nota(dados):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO notas (numero_nota, chave_acesso, remetente, destinatario, valor_mercadoria, peso, volumes, data_emissao)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (dados.get('numero_nota'), dados.get('chave_acesso'), dados.get('remetente'), 
          dados.get('destinatario'), dados.get('valor_mercadoria'), dados.get('peso'), 
          dados.get('volumes', 1), dados.get('data_emissao')))
    conn.commit()
    conn.close()


def listar_notas():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notas")
    return [dict(row) for row in cursor.fetchall()]


def nota_existe(chave):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM notas WHERE chave_acesso = ?", (chave,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def criar_manifesto(dados):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO manifestos (numero_manifesto, transportadora, data_manifesto, qtd_notas, valor_total)
        VALUES (?, ?, ?, ?, ?)
    """, (dados.get('numero_manifesto'), dados.get('transportadora'), dados.get('data_manifesto'),
          dados.get('qtd_notas', 0), dados.get('valor_total', 0)))
    conn.commit()
    conn.close()
    return cursor.lastrowid


def listar_manifestos(tipo=None, mes=None, ano=None):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM manifestos")
    return [dict(row) for row in cursor.fetchall()]


def listar_notas_por_manifesto(manifesto_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notas WHERE manifesto_id = ?", (manifesto_id,))
    return [dict(row) for row in cursor.fetchall()]


def apagar_manifesto(manifesto_id):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM manifestos WHERE id = ?", (manifesto_id,))
    conn.commit()
    conn.close()


def listar_notas_por_cliente(cliente_id, apenas_disponiveis=True, excluir_vinculadas=True):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notas WHERE destinatario LIKE ?", (f"%{cliente_id}%",))
    return [dict(row) for row in cursor.fetchall()]


def calcular_resumo_notas(notas_ids, conn=None):
    if conn is None:
        conn = _get_connection()
    cursor = conn.cursor()
    if not notas_ids:
        return {"quantidade": 0, "peso_total": 0, "frete_total": 0, "volumes": 0}
    
    placeholders = ','.join(['?'] * len(notas_ids))
    cursor.execute(f"SELECT SUM(peso), SUM(volumes), SUM(valor_mercadoria), COUNT(*) FROM notas WHERE id IN ({placeholders})", notas_ids)
    result = cursor.fetchone()
    return {
        "quantidade": result[3] or 0,
        "peso_total": result[0] or 0,
        "frete_total": result[2] or 0,
        "volumes": result[1] or 0
    }


def buscar_cliente_por_cnpj(cnpj):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE cnpj = ?", (cnpj,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def criar_cliente(dados):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clientes (razao_social, nome_fantasia, cnpj, ie, endereco, cidade, estado, telefone, email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (dados.get('razao_social'), dados.get('nome_fantasia'), dados.get('cnpj'),
          dados.get('ie'), dados.get('endereco'), dados.get('cidade'), dados.get('estado'),
          dados.get('telefone'), dados.get('email')))
    conn.commit()
    conn.close()
    return cursor.lastrowid


def obter_ou_criar_cliente(dados):
    cliente = buscar_cliente_por_cnpj(dados.get('cnpj'))
    if cliente:
        return cliente['id']
    return criar_cliente(dados)


def buscar_clientes_por_nome(termo):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE nome_fantasia LIKE ? OR razao_social LIKE ?", (f"%{termo}%", f"%{termo}%"))
    return [dict(row) for row in cursor.fetchall()]


def dados_dashboard(tipo, mes, ano, conn=None):
    if conn is None:
        conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(liquido) FROM operacoes")
    result = cursor.fetchone()
    return {
        "total_fretes": result[0] or 0,
        "receita_bruta": result[1] or 0.0
    }


def top_destinos_dashboard(tipo, mes, ano, conn=None):
    return []


def criar_operacao_sp(dados):
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO operacoes (data_operacao, nome_caminhao, placa, motorista, valor_notas, frete_carreta, pedagio_carreta, outros_custos, custo_total, liquido, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (dados.get('data_operacao'), dados.get('nome_caminhao'), dados.get('placa'),
          dados.get('motorista'), dados.get('valor_notas'), dados.get('frete_carreta'),
          dados.get('pedagio_carreta'), dados.get('outros_custos'), dados.get('custo_total'),
          dados.get('liquido'), dados.get('status', 'pendente')))
    conn.commit()
    conn.close()
    return cursor.lastrowid


def listar_operacoes_sp():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM operacoes")
    return [dict(row) for row in cursor.fetchall()]


def gerar_ranking_clientes_v6(tipo, mes, ano, conn=None):
    return []


# Import from new modules to avoid conflicts with legacy functions
from .viagens import criar_viagem, apagar_viagem, listar_viagens, listar_notas_da_viagem, finalizar_viagem, buscar_detalhes_viagem
from .notas import salvar_nota, listar_notas, nota_existe, criar_manifesto, listar_manifestos, listar_notas_por_manifesto, apagar_manifesto, listar_notas_por_cliente, calcular_resumo_notas
