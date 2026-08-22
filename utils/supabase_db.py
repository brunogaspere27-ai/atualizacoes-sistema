import os
from dotenv import load_dotenv
from config.settings import settings

try:
    import psycopg2
except ImportError:  # pragma: no cover
    psycopg2 = None

load_dotenv()

class SupabaseNaoConfiguradoError(RuntimeError):
    """Erro levantado quando a nuvem não está configurada."""


def supabase_habilitado() -> bool:
    return settings.supabase_enabled


def conectar_supabase():
    if not supabase_habilitado():
        raise SupabaseNaoConfiguradoError(
            "SUPABASE_URL não configurado. O sistema seguirá em modo local."
        )
    if psycopg2 is None:
        raise SupabaseNaoConfiguradoError(
            "psycopg2 não está instalado. O sistema seguirá em modo local."
        )

    return psycopg2.connect(
        settings.supabase_url,
        connect_timeout=10
    )