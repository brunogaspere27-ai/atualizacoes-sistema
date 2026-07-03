Param()

Write-Host "Instalando dependências de desenvolvimento..."
python -m pip install --upgrade pip
python -m pip install -r "$(Resolve-Path (Join-Path $PSScriptRoot "..\requirements-dev.txt"))"

Write-Host "Instalando hooks do pre-commit..."
if (Test-Path ".git") {
    pre-commit install
    Write-Host "Hooks instalados. Rode 'pre-commit run --all-files' para checar o repositório." 
} else {
    Write-Host "Pasta .git não encontrada. Inicialize um repositório git antes de instalar hooks."
}
