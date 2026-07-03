from pathlib import Path

from telas.criar_viagem import (
    atualizar_marcacao_nota,
    carregar_rascunho_viagem,
    limpar_rascunho_viagem,
    salvar_rascunho_viagem,
    adicionar_historico_viagem,
    listar_historico_viagem,
)


def test_adicionar_nota_na_selecao():
    notas = set()

    notas = atualizar_marcacao_nota(notas, 10, True)

    assert notas == {10}


def test_remover_nota_da_selecao():
    notas = {10}

    notas = atualizar_marcacao_nota(notas, 10, False)

    assert notas == set()


def test_salvar_e_carregar_rascunho_viagem(tmp_path):
    caminho = tmp_path / "rascunho.json"
    dados = {"cliente_id": 7, "notas": [1, 2, 3], "motorista": "João"}

    salvar_rascunho_viagem(dados, caminho)
    carregado = carregar_rascunho_viagem(caminho)

    assert carregado["cliente_id"] == 7
    assert carregado["notas"] == [1, 2, 3]
    assert carregado["motorista"] == "João"

    limpar_rascunho_viagem(caminho)
    assert carregar_rascunho_viagem(caminho) is None


def test_adicionar_e_listar_historico_viagem(tmp_path):
    caminho = tmp_path / "historico.json"
    entrada = {
        "viagem_id": 99,
        "motorista": "Maria",
        "caminhao": "ABC-1234",
        "quantidade": 2,
        "peso_total": 1250.5,
        "frete_total": 320.0,
    }

    adicionar_historico_viagem(entrada, caminho, limite=3)
    historico = listar_historico_viagem(caminho)

    assert len(historico) == 1
    assert historico[0]["viagem_id"] == 99
    assert historico[0]["motorista"] == "Maria"
