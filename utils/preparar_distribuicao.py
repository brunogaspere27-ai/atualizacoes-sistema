"""
Prepara pacote para distribuição.
"""
import os
import shutil
import zipfile


def preparar_distribuicao():
    """Cria pacote de distribuição."""
    output = "dist/sistema_atualizacoes"
    if os.path.exists(output):
        shutil.rmtree(output)
    os.makedirs(output, exist_ok=True)
    
    files = ["main.py", "main_pyside6.py", "versao.json"]
    dirs = ["services", "utils", "ui", "config"]
    
    for f in files:
        if os.path.exists(f):
            shutil.copy2(f, output)
    
    for d in dirs:
        if os.path.exists(d):
            shutil.copytree(d, os.path.join(output, d), dirs_exist_ok=True)
    
    # Criar ZIP
    zip_path = "dist/sistema_atualizacoes.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(output):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, "dist")
                zf.write(filepath, arcname)
    
    print(f"✅ Distribuição criada: {zip_path}")
    return zip_path


if __name__ == "__main__":
    preparar_distribuicao()