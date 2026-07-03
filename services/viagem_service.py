"""
Serviço para gerenciamento de viagens.
Desacoplado da interface, contém lógica de negócio para criação de viagens.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from datetime import datetime

from utils.database import (
    buscar_clientes_por_nome,
    listar_notas_por_cliente,
    calcular_resumo_notas,
    criar_viagem,
    listar_caminhoes,
    apagar_todos_caminhoes
)
from utils.logger import get_logger
from utils.validators import (
    sanitize_string,
    validate_nome,
    ValidationError
)

logger = get_logger(__name__)


class ViagemService:
    """Serviço para gerenciar operações de viagens."""

    def buscar_clientes(self, termo: str) -> List[Tuple]:
        """
        Busca clientes pelo nome.
        
        Args:
            termo: Termo de busca
            
        Returns:
            Lista de tuplas (id, nome, cnpj, cidade, uf)
        """
        if not termo or len(termo) < 2:
            return []
        
        # Sanitiza o termo de busca
        termo = sanitize_string(termo, max_length=100)
        
        try:
            return buscar_clientes_por_nome(termo)
        except Exception as e:
            logger.error(f"Erro ao buscar clientes: {e}")
            return []

    def listar_notas_cliente(
        self,
        cliente_id: int,
        apenas_disponiveis: bool = True,
        excluir_vinculadas: bool = True
    ) -> List[Tuple]:
        """
        Lista notas de um cliente com filtros.
        
        Args:
            cliente_id: ID do cliente
            apenas_disponiveis: Filtrar apenas notas disponíveis
            excluir_vinculadas: Excluir notas já vinculadas a viagens
            
        Returns:
            Lista de tuplas com dados das notas
        """
        try:
            return listar_notas_por_cliente(
                cliente_id,
                apenas_disponiveis,
                excluir_vinculadas
            )
        except Exception as e:
            logger.error(f"Erro ao listar notas do cliente: {e}")
            return []

    def calcular_resumo_selecao(self, notas_ids: List[int]) -> Dict[str, float]:
        """
        Calcula resumo das notas selecionadas.
        
        Args:
            notas_ids: Lista de IDs das notas
            
        Returns:
            Dict com quantidade, peso_total, frete_total, volumes
        """
        try:
            return calcular_resumo_notas(notas_ids)
        except Exception as e:
            logger.error(f"Erro ao calcular resumo: {e}")
            return {
                "quantidade": 0,
                "peso_total": 0,
                "frete_total": 0,
                "volumes": 0
            }

    def criar_viagem_com_notas(
        self,
        caminhao_id: int,
        notas_ids: List[int],
        motorista: str,
        data_saida: Optional[str] = None
    ) -> int:
        """
        Cria uma nova viagem com as notas selecionadas.
        
        Args:
            caminhao_id: ID do caminhão
            notas_ids: Lista de IDs das notas
            motorista: Nome do motorista
            data_saida: Data de saída (opcional, usa atual se não informado)
            
        Returns:
            ID da viagem criada
        """
        if not notas_ids:
            raise ValueError("Nenhuma nota selecionada")
        
        if not motorista:
            raise ValueError("Motorista não informado")
        
        # Valida e sanitiza o nome do motorista
        motorista = sanitize_string(motorista, max_length=100)
        valido, erro = validate_nome(motorista)
        if not valido:
            raise ValueError(f"Nome do motorista inválido: {erro}")
        
        if data_saida is None:
            data_saida = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        try:
            viagem_id = criar_viagem(caminhao_id, notas_ids, data_saida, motorista)
            logger.info(f"Viagem #{viagem_id} criada com {len(notas_ids)} notas")
            return viagem_id
        except Exception as e:
            logger.error(f"Erro ao criar viagem: {e}")
            raise

    def listar_caminhoes_disponiveis(self) -> List[Tuple]:
        """
        Lista todos os caminhões disponíveis.
        
        Returns:
            Lista de tuplas (id, placa, modelo, motorista, capacidade)
        """
        try:
            return listar_caminhoes()
        except Exception as e:
            logger.error(f"Erro ao listar caminhões: {e}")
            return []

    def validar_capacidade(
        self,
        caminhao_id: int,
        notas_ids: List[int]
    ) -> Tuple[bool, str, float]:
        """
        Valida se as notas excedem a capacidade do caminhão.
        
        Args:
            caminhao_id: ID do caminhão
            notas_ids: Lista de IDs das notas
            
        Returns:
            Tuple (valido, mensagem, porcentagem_uso)
        """
        try:
            caminhoes = listar_caminhoes()
            caminhao = None
            
            for c in caminhoes:
                if c[0] == caminhao_id:
                    caminhao = c
                    break
            
            if not caminhao:
                return False, "Caminhão não encontrado", 0
            
            capacidade = caminhao[4] or 0  # capacidade_kg
            
            if capacidade == 0:
                return True, "Capacidade não definida", 0
            
            resumo = calcular_resumo_notas(notas_ids)
            peso_total = resumo["peso_total"]
            
            porcentagem_uso = (peso_total / capacidade) * 100 if capacidade > 0 else 0
            
            if peso_total > capacidade:
                return False, f"Peso excede capacidade ({peso_total:,.0f} kg > {capacidade:,.0f} kg)", porcentagem_uso
            
            return True, "Capacidade OK", porcentagem_uso
            
        except Exception as e:
            logger.error(f"Erro ao validar capacidade: {e}")
            return False, f"Erro na validação: {e}", 0
    def apagar_caminhoes(self) -> bool:
        """
        Apaga todos os caminhões do sistema.
        
        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            return apagar_todos_caminhoes()
        except Exception as e:
            logger.error(f"Erro ao apagar caminhões: {e}")
            return False


viagem_service = ViagemService()
