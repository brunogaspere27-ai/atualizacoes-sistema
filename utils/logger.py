"""
Sistema de logging estruturado para o projeto CW Transportadora.
Utiliza loguru para logging avançado e estruturado.
"""

import sys
from pathlib import Path
from typing import Optional
from config.settings import settings

try:
    from loguru import logger as _loguru_logger
except ImportError:  # pragma: no cover
    _loguru_logger = None
    import logging


def configurar_logging(
    nivel: str = "INFO",
    arquivo_log: Optional[str] = None,
    rotacao: str = "10 MB",
    retencao: str = "30 days"
) -> None:
    """
    Configura o sistema de logging do projeto.
    
    Args:
        nivel: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        arquivo_log: Caminho do arquivo de log (opcional)
        rotacao: Tamanho para rotação do arquivo de log
        retenção: Tempo de retenção dos logs
    """
    if _loguru_logger is None:
        log_path = Path(arquivo_log) if arquivo_log else None
        if log_path:
            log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            level=getattr(logging, nivel.upper(), logging.INFO),
            format="%(asctime)s | %(levelname)-8s | %(name)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)] + ([logging.FileHandler(log_path, encoding="utf-8")] if log_path else [])
        )
        return

    _loguru_logger.remove()
    console_sink = sys.stdout if sys.stdout is not None else sys.stderr
    if console_sink is not None:
        _loguru_logger.add(
            console_sink,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=nivel,
            colorize=True
        )

    if arquivo_log:
        log_path = Path(arquivo_log)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        _loguru_logger.add(
            arquivo_log,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=nivel,
            rotation=rotacao,
            retention=retencao,
            compression="zip"
        )

        error_log = str(Path(arquivo_log).parent / "errors.log")
        _loguru_logger.add(
            error_log,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="ERROR",
            rotation=rotacao,
            retention=retencao,
            compression="zip"
        )


def get_logger(nome: str):
    """
    Obtém um logger configurado para um módulo específico.
    
    Args:
        nome: Nome do módulo (geralmente __name__)
        
    Returns:
        Logger configurado
    """
    if _loguru_logger is None:
        import logging
        return logging.getLogger(nome)
    return _loguru_logger.bind(name=nome)


# Configuração padrão ao importar o módulo
configurar_logging(
    nivel="INFO",
    arquivo_log=str(settings.logs_dir / "cw_transportadora.log")
)
