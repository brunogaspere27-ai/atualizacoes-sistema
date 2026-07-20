from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import os

IGNORAR_PASTAS = {
    ".venv", "venv", "__pycache__", ".git",
    "build", "dist", "node_modules",
    ".pytest_cache", ".mypy_cache", ".idea", ".vscode",
    ".tox", "htmlcov", ".coverage"
}

IGNORAR_EXTENSOES = {
    ".pyc", ".pyo", ".log", ".egg-info"
}

IGNORAR_PREFIXOS = (".",)  # arquivos ocultos

TAMANHO_MAXIMO_MB = 50  # ignora arquivos maiores que 50MB

zip_name = "codigo_fonte.zip"
tamanho_maximo = TAMANHO_MAXIMO_MB * 1024 * 1024
arquivos_adicionados = 0
arquivos_ignorados = 0

with ZipFile(zip_name, "w", ZIP_DEFLATED) as zipf:
    for arquivo in Path(".").rglob("*"):
        # Ignora diretórios
        if not arquivo.is_file():
            continue

        # Ignora pastas específicas (parte exata do path)
        if any(parte in IGNORAR_PASTAS for parte in arquivo.parts):
            arquivos_ignorados += 1
            continue

        # Ignora extensões
        if arquivo.suffix in IGNORAR_EXTENSOES:
            arquivos_ignorados += 1
            continue

        # Ignora arquivos ocultos
        if any(parte.startswith(IGNORAR_PREFIXOS) for parte in arquivo.parts):
            arquivos_ignorados += 1
            continue

        # Ignora o próprio ZIP
        if arquivo.name == zip_name:
            continue

        # Ignora arquivos muito grandes
        tamanho = arquivo.stat().st_size
        if tamanho > tamanho_maximo:
            print(f"⚠️ Ignorado (muito grande): {arquivo} ({tamanho/1024/1024:.1f} MB)")
            arquivos_ignorados += 1
            continue

        zipf.write(arquivo, arquivo)
        arquivos_adicionados += 1

tamanho_final = os.path.getsize(zip_name)
print(f"\n✅ ZIP criado: {zip_name}")
print(f"   Arquivos adicionados: {arquivos_adicionados}")
print(f"   Arquivos ignorados: {arquivos_ignorados}")
print(f"   Tamanho final: {tamanho_final/1024/1024:.2f} MB")
