"""
Testes para funções auxiliares do sistema.
"""

from utils.helpers import (
    formatar_moeda,
    formatar_peso,
    formatar_data,
    parse_numero,
    parse_inteiro,
    validar_cnpj,
    validar_placa,
    mascara_cnpj,
    mascara_placa,
)


def test_formatar_moeda():
    """Testa formatação de moeda."""
    assert formatar_moeda(1000.50) == "R$ 1.000,50"
    assert formatar_moeda(0) == "R$ 0,00"
    assert formatar_moeda(None) == "R$ 0,00"
    assert formatar_moeda("1500") == "R$ 1.500,00"


def test_formatar_peso():
    """Testa formatação de peso."""
    assert formatar_peso(5000.75) == "5.000,75 kg"
    assert formatar_peso(0) == "0,00 kg"
    assert formatar_peso(None) == "0,00 kg"


def test_parse_numero():
    """Testa parsing de números."""
    assert parse_numero("1.000,50") == 1000.50
    assert parse_numero("1000.50") == 1000.50
    assert parse_numero("") == 0.0
    assert parse_numero(None) == 0.0


def test_parse_inteiro():
    """Testa parsing de inteiros."""
    assert parse_inteiro("100") == 100
    assert parse_inteiro("") == 0
    assert parse_inteiro(None) == 0


def test_validar_cnpj():
    """Testa validação de CNPJ."""
    assert validar_cnpj("11.444.777/0001-61") is True
    assert validar_cnpj("11444777000161") is True
    assert validar_cnpj("") is False
    assert validar_cnpj("123") is False


def test_validar_placa():
    """Testa validação de placa."""
    assert validar_placa("ABC-1234") is True
    assert validar_placa("ABC1234") is True
    assert validar_placa("ABC1D23") is True
    assert validar_placa("") is False


def test_mascara_cnpj():
    """Testa máscara de CNPJ."""
    assert mascara_cnpj("11444777000161") == "11.444.777/0001-61"
    assert mascara_cnpj("") == ""


def test_mascara_placa():
    """Testa máscara de placa."""
    assert mascara_placa("ABC1234") == "ABC-1234"
    assert mascara_placa("abc1234") == "ABC-1234"
    assert mascara_placa("") == ""
