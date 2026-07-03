Param()

# PowerShell setup script for Gemma3:12B local inference
# Creates a Python virtual environment and installs required packages.

$venvPath = "$PSScriptRoot\..\venv_gemma3"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
}

$activate = "$venvPath\Scripts\Activate.ps1"
Write-Host "Activating virtualenv: $activate"
& $activate

Write-Host "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r "$(Resolve-Path (Join-Path $PSScriptRoot "..\requirements.txt"))"

Write-Host "Setup complete. To use the virtualenv run:`n& $activate`"
Write-Host "Notes:`n - You will likely need GPU drivers, CUDA, and compatible PyTorch.`n - For large models, prefer loading quantized weights or using GGML runners.`n - To download model weights, run the provided Python runner with `--download` (if enabled)."
