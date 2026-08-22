"""
Verificação de ambiente.
"""
import os
import sys


def check_environment():
    """Verifica se o ambiente está configurado corretamente."""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"❌ Variáveis ausentes: {', '.join(missing)}")
        return False
    
    print("✅ Ambiente OK")
    return True


if __name__ == "__main__":
    sys.exit(0 if check_environment() else 1)