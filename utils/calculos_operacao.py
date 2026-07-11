"""
Cálculos operacionais do sistema CW Transportadora.

Todas as funções são puras (sem efeitos colaterais) e retornam
novos dicionários em vez de modificar os argumentos recebidos.
"""

from __future__ import annotations

from typing import Any, Dict, List


# Médias de consumo por veículo (km/L)
_MEDIAS_CONSUMO: Dict[str, float] = {
    "Renault Master": 9.0,
    "Caminhao 3/4 Branco": 7.0,
    "Caminhao 3/4 Preto": 7.0,
    "Caminhao Toco": 5.0,
}


def calcular_frete_cliente(valor_notas: float, percentual_frete: float) -> float:
    """
    Calcula o frete de um cliente com base no valor das notas e percentual.

    Args:
        valor_notas: Valor total das notas do cliente.
        percentual_frete: Percentual de frete a cobrar (ex: 3.5 para 3,5%).

    Returns:
        Valor do frete calculado.
    """
    if valor_notas < 0 or percentual_frete < 0:
        return 0.0
    return valor_notas * (percentual_frete / 100.0)


def calcular_operacao_v5(
    clientes: List[Dict[str, Any]],
    frete_carreta: float,
    pedagio_carreta: float,
    outros_custos_transferencia: float,
    veiculo_distribuicao: str,
    km_distribuicao: float,
    preco_combustivel: float,
    pedagio_regional: float,
    dias: int,
    diaria_motorista: float,
    alimentacao_dia: float,
    chapa_dia: float,
) -> Dict[str, Any]:
    """
    Calcula o resultado financeiro de uma operação completa.

    Não modifica os dicionários de `clientes` recebidos — retorna cópias
    com o campo `frete_calculado` adicionado.

    Args:
        clientes: Lista de dicts com 'valor_notas' e 'percentual_frete'.
        frete_carreta: Custo do frete da carreta SP→CWB.
        pedagio_carreta: Pedágio pago pela carreta.
        outros_custos_transferencia: Outros custos da transferência.
        veiculo_distribuicao: Nome do veículo de distribuição.
        km_distribuicao: Quilômetros rodados na distribuição.
        preco_combustivel: Preço do combustível por litro.
        pedagio_regional: Pedágio regional de distribuição.
        dias: Quantidade de dias da operação.
        diaria_motorista: Valor da diária do motorista.
        alimentacao_dia: Custo de alimentação por dia.
        chapa_dia: Custo de chapa por dia.

    Returns:
        Dict com todos os resultados financeiros e uma cópia da lista de
        clientes enriquecida com 'frete_calculado'.
    """
    faturamento_total = 0.0
    clientes_calculados: List[Dict[str, Any]] = []

    for cliente in clientes:
        valor_notas = float(cliente.get("valor_notas") or 0)
        percentual = float(cliente.get("percentual_frete") or 0)
        frete_calculado = calcular_frete_cliente(valor_notas, percentual)
        faturamento_total += frete_calculado
        # Cria uma cópia para não alterar o dict original (sem efeito colateral)
        clientes_calculados.append({**cliente, "frete_calculado": frete_calculado})

    consumo = _MEDIAS_CONSUMO.get(veiculo_distribuicao, 0.0)
    custo_combustivel = (
        (km_distribuicao / consumo) * preco_combustivel
        if consumo > 0 and km_distribuicao > 0
        else 0.0
    )

    custo_diarias = diaria_motorista * dias
    custo_alimentacao = alimentacao_dia * dias
    custo_chapa = chapa_dia * dias
    impostos = faturamento_total * 0.03

    custo_total = (
        frete_carreta
        + pedagio_carreta
        + outros_custos_transferencia
        + custo_combustivel
        + pedagio_regional
        + custo_diarias
        + custo_alimentacao
        + custo_chapa
        + impostos
    )

    lucro = faturamento_total - custo_total
    margem = (lucro / faturamento_total * 100) if faturamento_total > 0 else 0.0

    return {
        "faturamento_total_clientes": faturamento_total,
        "custo_combustivel": custo_combustivel,
        "custo_diarias": custo_diarias,
        "custo_alimentacao": custo_alimentacao,
        "custo_chapa": custo_chapa,
        "impostos": impostos,
        "custo_total": custo_total,
        "lucro": lucro,
        "margem": margem,
        "clientes": clientes_calculados,
    }
