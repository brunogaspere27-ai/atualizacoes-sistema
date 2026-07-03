"""
Testes para funções auxiliares do sistema.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (
    formatar_moeda,
    formatar_peso,
    formatar_data,
    parse_numero,
    parse_inteiro,
    validar_cnpj,
    validar_placa,
    mascara_cnpj,
    mascara_placa
)


def test_formatar_moeda():
    """Testa formatação de moeda."""
    assert formatar_moeda(1000.50) == "R$ 1.000,50"
    assert formatar_moeda(0) == "R$ 0,00"
    assert formatar_moeda(None) == "R$ 0,00"
    assert formatar_moeda("1500") == "R$ 1.500,00"
    print("✓ test_formatar_moeda passou")


def test_formatar_peso():
    """Testa formatação de peso."""
    assert formatar_peso(5000.75) == "5.000,75 kg"
    assert formatar_peso(0) == "0,00 kg"
    assert formatar_peso(None) == "0,00 kg"
    print("✓ test_formatar_peso passou")


def test_parse_numero():
    """Testa parsing de números."""
    assert parse_numero("1.000,50") == 1000.50
    assert parse_numero("1000.50") == 1000.50
    assert parse_numero("") == 0.0
    assert parse_numero(None) == 0.0
    print("✓ test_parse_numero passou")


def test_parse_inteiro():
    """Testa parsing de inteiros."""
    assert parse_inteiro("100") == 100
    assert parse_inteiro("") == 0
    assert parse_inteiro(None) == 0
    print("✓ test_parse_inteiro passou")


def test_validar_cnpj():
    """Testa validação de CNPJ."""
    assert validar_cnpj("11.444.777/0001-61") == True
    assert validar_cnpj("11444777000161") == True
    assert validar_cnpj("") == False
    assert validar_cnpj("123") == False
    print("✓ test_validar_cnpj passou")


def test_validar_placa():
    """Testa validação de placa."""
    assert validar_placa("ABC-1234") == True
    assert validar_placa("ABC1234") == True
    assert validar_placa("ABC1D23") == True
    assert validar_placa("") == False
    print("✓ test_validar_placa passou")


def test_mascara_cnpj():
    """Testa máscara de CNPJ."""
    assert mascara_cnpj("11444777000161") == "11.444.777/0001-61"
    assert mascara_cnpj("") == ""
    print("✓ test_mascara_cnpj passou")


def test_mascara_placa():
    """Testa máscara de placa."""
    assert mascara_placa("ABC1234") == "ABC-1234"
    assert mascara_placa("abc1234") == "ABC-1234"
    assert mascara_placa("") == ""
    print("✓ test_mascara_placa passou")


if __name__ == "__main__":
    print("Executando testes de helpers...")
    print()
    
    test_formatar_moeda()
    test_formatar_peso()
    test_parse_numero()
    test_parse_inteiro()
    test_validar_cnpj()
    test_validar_placa()
    test_mascara_cnpj()
    test_mascara_placa()
    
    print()
    print("Todos os testes passaram! ✓")
