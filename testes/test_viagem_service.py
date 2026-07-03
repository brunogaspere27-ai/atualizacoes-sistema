"""
Testes para o serviço de viagens.
"""

import pytest
from unittest.mock import Mock, patch
from services.viagem_service import ViagemService


@pytest.fixture
def viagem_service():
    """Fixture para criar instância do ViagemService."""
    return ViagemService()


def test_buscar_clientes_termo_curto(viagem_service):
    """Testa busca com termo muito curto."""
    result = viagem_service.buscar_clientes("a")
    assert result == []


@patch('services.viagem_service.buscar_clientes_por_nome')
def test_buscar_clientes_sucesso(mock_buscar, viagem_service):
    """Testa busca de clientes com sucesso."""
    mock_buscar.return_value = [
        (1, "Cliente A", "123456789", "Cascavel", "PR"),
        (2, "Cliente B", "987654321", "Foz do Iguaçu", "PR")
    ]
    
    result = viagem_service.buscar_clientes("Cliente")
    
    assert len(result) == 2
    assert result[0][1] == "Cliente A"
    mock_buscar.assert_called_once_with("Cliente")


@patch('services.viagem_service.buscar_clientes_por_nome')
def test_buscar_clientes_erro(mock_buscar, viagem_service):
    """Testa busca de clientes com erro."""
    mock_buscar.side_effect = Exception("Database error")
    
    result = viagem_service.buscar_clientes("Cliente")
    
    assert result == []


@patch('services.viagem_service.listar_notas_por_cliente')
def test_listar_notas_cliente_sucesso(mock_listar, viagem_service):
    """Testa listagem de notas de cliente com sucesso."""
    mock_listar.return_value = [
        (1, "CTE001", "chave123", "Cliente A", "Cascavel", 100.0, 500.0, "2024-01-01", "Disponível")
    ]
    
    result = viagem_service.listar_notas_cliente(1)
    
    assert len(result) == 1
    assert result[0][0] == 1
    mock_listar.assert_called_once_with(1, True, True)


@patch('services.viagem_service.calcular_resumo_notas')
def test_calcular_resumo_selecao_sucesso(mock_calcular, viagem_service):
    """Testa cálculo de resumo com sucesso."""
    mock_calcular.return_value = {
        "quantidade": 5,
        "peso_total": 500.0,
        "frete_total": 2500.0,
        "volumes": 5
    }
    
    result = viagem_service.calcular_resumo_selecao([1, 2, 3, 4, 5])
    
    assert result["quantidade"] == 5
    assert result["peso_total"] == 500.0
    mock_calcular.assert_called_once()


@patch('services.viagem_service.calcular_resumo_notas')
def test_calcular_resumo_selecao_erro(mock_calcular, viagem_service):
    """Testa cálculo de resumo com erro."""
    mock_calcular.side_effect = Exception("Database error")
    
    result = viagem_service.calcular_resumo_selecao([1, 2, 3])
    
    assert result["quantidade"] == 0
    assert result["peso_total"] == 0


@patch('services.viagem_service.criar_viagem')
def test_criar_viagem_com_notas_sucesso(mock_criar, viagem_service):
    """Testa criação de viagem com sucesso."""
    mock_criar.return_value = 10
    
    result = viagem_service.criar_viagem_com_notas(
        caminhao_id=1,
        notas_ids=[1, 2, 3],
        motorista="João Silva"
    )
    
    assert result == 10
    mock_criar.assert_called_once()


def test_criar_viagem_com_notas_sem_notas(viagem_service):
    """Testa criação de viagem sem notas."""
    with pytest.raises(ValueError, match="Nenhuma nota selecionada"):
        viagem_service.criar_viagem_com_notas(
            caminhao_id=1,
            notas_ids=[],
            motorista="João Silva"
        )


def test_criar_viagem_com_notas_sem_motorista(viagem_service):
    """Testa criação de viagem sem motorista."""
    with pytest.raises(ValueError, match="Motorista não informado"):
        viagem_service.criar_viagem_com_notas(
            caminhao_id=1,
            notas_ids=[1, 2, 3],
            motorista=""
        )


@patch('services.viagem_service.listar_caminhoes')
def test_listar_caminhoes_disponiveis_sucesso(mock_listar, viagem_service):
    """Testa listagem de caminhões com sucesso."""
    mock_listar.return_value = [
        (1, "ABC1234", "Volvo", "João", 5000),
        (2, "DEF5678", "Scania", "Maria", 6000)
    ]
    
    result = viagem_service.listar_caminhoes_disponiveis()
    
    assert len(result) == 2
    assert result[0][1] == "ABC1234"


@patch('services.viagem_service.listar_caminhoes')
@patch('services.viagem_service.calcular_resumo_notas')
def test_validar_capacidade_sucesso(mock_calcular, mock_listar, viagem_service):
    """Testa validação de capacidade com sucesso."""
    mock_listar.return_value = [
        (1, "ABC1234", "Volvo", "João", 5000)
    ]
    mock_calcular.return_value = {
        "quantidade": 2,
        "peso_total": 3000,
        "frete_total": 1500,
        "volumes": 2
    }
    
    valido, mensagem, porcentagem = viagem_service.validar_capacidade(
        caminhao_id=1,
        notas_ids=[1, 2]
    )
    
    assert valido is True
    assert "OK" in mensagem
    assert porcentagem == 60.0


@patch('services.viagem_service.listar_caminhoes')
@patch('services.viagem_service.calcular_resumo_notas')
def test_validar_capacidade_excedida(mock_calcular, mock_listar, viagem_service):
    """Testa validação de capacidade excedida."""
    mock_listar.return_value = [
        (1, "ABC1234", "Volvo", "João", 5000)
    ]
    mock_calcular.return_value = {
        "quantidade": 2,
        "peso_total": 6000,
        "frete_total": 3000,
        "volumes": 2
    }
    
    valido, mensagem, porcentagem = viagem_service.validar_capacidade(
        caminhao_id=1,
        notas_ids=[1, 2]
    )
    
    assert valido is False
    assert "excede" in mensagem.lower()
    assert porcentagem == 120.0


@patch('services.viagem_service.listar_caminhoes')
def test_validar_capacidade_caminhao_nao_encontrado(mock_listar, viagem_service):
    """Testa validação com caminhão não encontrado."""
    mock_listar.return_value = []
    
    valido, mensagem, porcentagem = viagem_service.validar_capacidade(
        caminhao_id=999,
        notas_ids=[1, 2]
    )
    
    assert valido is False
    assert "não encontrado" in mensagem.lower()
