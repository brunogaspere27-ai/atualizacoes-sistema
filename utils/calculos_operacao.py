def calcular_frete_cliente(valor_notas, percentual_frete):
    return valor_notas * (percentual_frete / 100)


def calcular_operacao_v5(
    clientes,
    frete_carreta,
    pedagio_carreta,
    outros_custos_transferencia,
    veiculo_distribuicao,
    km_distribuicao,
    preco_combustivel,
    pedagio_regional,
    dias,
    diaria_motorista,
    alimentacao_dia,
    chapa_dia
):

    medias = {
        "Renault Master": 9.0,
        "Caminhao 3/4 Branco": 7.0,
        "Caminhao 3/4 Preto": 7.0,
        "Caminhao Toco": 5.0
    }

    faturamento_total_clientes = 0

    for cliente in clientes:
        valor_notas = float(cliente["valor_notas"])
        percentual = float(cliente["percentual_frete"])

        frete_calculado = calcular_frete_cliente(valor_notas, percentual)
        cliente["frete_calculado"] = frete_calculado

        faturamento_total_clientes += frete_calculado

    consumo = medias.get(veiculo_distribuicao, 0)

    if consumo > 0:
        custo_combustivel = (km_distribuicao / consumo) * preco_combustivel
    else:
        custo_combustivel = 0

    custo_diarias = diaria_motorista * dias
    custo_alimentacao = alimentacao_dia * dias
    custo_chapa = chapa_dia * dias

    impostos = faturamento_total_clientes * 0.03

    custo_total = (
        frete_carreta +
        pedagio_carreta +
        outros_custos_transferencia +
        custo_combustivel +
        pedagio_regional +
        custo_diarias +
        custo_alimentacao +
        custo_chapa +
        impostos
    )

    lucro = faturamento_total_clientes - custo_total

    margem = 0
    if faturamento_total_clientes > 0:
        margem = (lucro / faturamento_total_clientes) * 100

    return {
        "faturamento_total_clientes": faturamento_total_clientes,
        "custo_combustivel": custo_combustivel,
        "custo_diarias": custo_diarias,
        "custo_alimentacao": custo_alimentacao,
        "custo_chapa": custo_chapa,
        "impostos": impostos,
        "custo_total": custo_total,
        "lucro": lucro,
        "margem": margem,
        "clientes": clientes
    }
