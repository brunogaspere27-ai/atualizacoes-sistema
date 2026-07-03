"""
Utilitário para retry de operações com backoff exponencial.
"""

from __future__ import annotations

import time
from functools import wraps
from typing import Callable, Type, Tuple, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator para retry de funções com backoff exponencial.
    
    Args:
        max_attempts: Número máximo de tentativas
        delay: Delay inicial em segundos
        backoff: Fator de multiplicação do delay
        exceptions: Tupla de exceções que devem trigger retry
        on_retry: Callback executado em cada retry (recebe attempt, exception)
        
    Example:
        @retry(max_attempts=3, delay=1, exceptions=(ConnectionError,))
        def fetch_data():
            return requests.get(url)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"Função {func.__name__} falhou após {max_attempts} tentativas: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Tentativa {attempt}/{max_attempts} falhou para {func.__name__}: {e}. "
                        f"Retrying em {current_delay:.1f}s..."
                    )
                    
                    if on_retry:
                        on_retry(attempt, e)
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    return decorator


class RetryHandler:
    """Classe para gerenciar retries de forma mais flexível."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff: float = 2.0
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff = backoff
    
    def execute(
        self,
        func: Callable,
        *args,
        exceptions: Tuple[Type[Exception], ...] = (Exception,),
        **kwargs
    ) -> Any:
        """
        Executa função com retry.
        
        Args:
            func: Função a ser executada
            args: Argumentos posicionais
            exceptions: Exceções que trigger retry
            kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
        """
        current_delay = self.initial_delay
        
        for attempt in range(1, self.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if attempt == self.max_attempts:
                    logger.error(
                        f"Função {func.__name__} falhou após {self.max_attempts} tentativas: {e}"
                    )
                    raise
                
                logger.warning(
                    f"Tentativa {attempt}/{self.max_attempts} falhou: {e}. "
                    f"Retrying em {current_delay:.1f}s..."
                )
                
                time.sleep(min(current_delay, self.max_delay))
                current_delay *= self.backoff
        
        return None
    
    def execute_async(self, func: Callable, *args, **kwargs):
        """
        Executa função assíncrona com retry.
        
        Args:
            func: Função assíncrona a ser executada
            args: Argumentos posicionais
            kwargs: Argumentos nomeados
            
        Returns:
            Coroutine
        """
        import asyncio
        
        async def wrapper():
            current_delay = self.initial_delay
            
            for attempt in range(1, self.max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == self.max_attempts:
                        logger.error(
                            f"Função {func.__name__} falhou após {self.max_attempts} tentativas: {e}"
                        )
                        raise
                    
                    logger.warning(
                        f"Tentativa {attempt}/{self.max_attempts} falhou: {e}. "
                        f"Retrying em {current_delay:.1f}s..."
                    )
                    
                    await asyncio.sleep(min(current_delay, self.max_delay))
                    current_delay *= self.backoff
            
            return None
        
        return wrapper()
