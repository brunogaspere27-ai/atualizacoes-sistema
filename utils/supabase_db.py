import os
import threading
import time
from dotenv import load_dotenv
from config.settings import settings
from utils.logger import get_logger

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None

logger = get_logger(__name__)

load_dotenv()

class SupabaseNaoConfiguradoError(RuntimeError):
    """Erro levantado quando a nuvem não está configurada."""


class SupabaseOfflineError(RuntimeError):
    """Conexão indisponível; a aplicação deve continuar em modo local."""


class _CircuitBreaker:
    """
    Evita repetição de tentativas DNS/conexão enquanto a rede está fora.
    
    Implementa circuit breaker com retry exponencial:
    - Base delay: 60 segundos
    - Max delay: 300 segundos (5 minutos)
    - Exponential backoff: 60s, 120s, 240s, 300s...
    """

    def __init__(self, base_delay: int = 60, max_delay: int = 300):
        self._lock = threading.Lock()
        self._failures = 0
        self._next_attempt = 0.0
        self._base_delay = base_delay
        self._max_delay = max_delay
        self._last_error: Exception | None = None

    def ensure_available(self) -> None:
        """Verifica se o circuit breaker permite tentativas de conexão."""
        with self._lock:
            remaining = self._next_attempt - time.monotonic()
        if remaining > 0:
            minutes = max(1, int(remaining // 60) + 1)
            raise SupabaseOfflineError(
                f"Sistema operando em modo offline. Próxima tentativa em {minutes} minuto(s)."
            )

    def success(self) -> None:
        """Reseta o circuit breaker após sucesso."""
        with self._lock:
            self._failures = 0
            self._next_attempt = 0.0
            self._last_error = None

    def failure(self, error: Exception) -> None:
        """Registra falha e calcula próximo delay com exponential backoff."""
        with self._lock:
            self._failures += 1
            delay = min(self._base_delay * (2 ** (self._failures - 1)), self._max_delay)
            self._next_attempt = time.monotonic() + delay
            self._last_error = error
        
        # Log apenas na primeira falha para evitar spam
        if self._failures == 1:
            error_str = str(error).lower()
            if "could not translate host name" in error_str or "name or service not known" in error_str:
                logger.info("✓ Sistema operando em modo offline (DNS não resolveu)")
            else:
                logger.warning(f"Supabase indisponível; modo offline ativado por {delay}s: {error}")

    def get_status(self) -> dict:
        """Retorna status atual do circuit breaker."""
        with self._lock:
            remaining = max(0, self._next_attempt - time.monotonic())
            return {
                "failures": self._failures,
                "next_attempt_seconds": remaining,
                "is_open": remaining > 0,
                "last_error": str(self._last_error) if self._last_error else None
            }


_circuit_breaker = _CircuitBreaker()


def supabase_habilitado() -> bool:
    return settings.supabase_enabled


def conectar_supabase():
    """
    Tenta conectar ao Supabase com circuit breaker e tratamento de erros robusto.
    
    Implementa:
    - Circuit breaker para evitar tentativas repetidas
    - Timeout configurável
    - SSL obrigatório
    - Logs detalhados sem spam
    - Tratamento específico para erros de DNS
    """
    if not supabase_habilitado():
        raise SupabaseNaoConfiguradoError(
            "SUPABASE_URL não configurado. O sistema seguirá em modo local."
        )
    if psycopg2 is None:
        raise SupabaseNaoConfiguradoError(
            "psycopg2 não está instalado. O sistema seguirá em modo local."
        )

    _circuit_breaker.ensure_available()
    
    try:
        logger.debug("Tentando conectar ao Supabase...")
        connection = psycopg2.connect(
            settings.supabase_url,
            connect_timeout=settings.sync_timeout_seconds,
            sslmode="require",
        )
        _circuit_breaker.success()
        logger.info("✓ Supabase conectado com sucesso")
        return connection
        
    except psycopg2.OperationalError as error:
        # Tratamento específico para erros de DNS
        error_str = str(error).lower()
        if "could not translate host name" in error_str or "name or service not known" in error_str:
            logger.warning(f"✗ DNS não resolveu: {settings.supabase_url}")
            _circuit_breaker.failure(error)
            raise SupabaseOfflineError(
                "DNS não resolveu. Sistema operando em modo offline."
            ) from error
        else:
            _circuit_breaker.failure(error)
            raise SupabaseOfflineError(
                f"Erro de conexão: {error}"
            ) from error
            
    except psycopg2.InterfaceError as error:
        logger.warning(f"✗ Erro de interface PostgreSQL: {error}")
        _circuit_breaker.failure(error)
        raise SupabaseOfflineError(
            "Erro na interface do banco. Sistema operando em modo offline."
        ) from error
        
    except Exception as error:
        _circuit_breaker.failure(error)
        raise SupabaseOfflineError(
            f"Erro ao conectar: {error}"
        ) from error


def get_circuit_breaker_status() -> dict:
    """Retorna status atual do circuit breaker para diagnóstico."""
    return _circuit_breaker.get_status()
