# Gemma3:12B local inference (scaffolding)

This folder contains helper scripts and a minimal runner to prepare local inference for Gemma3:12B.

Quick steps:

1. Create and activate the virtualenv (PowerShell):

```powershell
.\scripts\setup_gemma3.ps1
``` 

2. Edit `config/gemma3.json` to set `repo_id` (Hugging Face) or `local_path`.

3. To download the model (if allowed) and run a prompt:

```powershell
.
# activate the venv first
& .\venv_gemma3\Scripts\Activate.ps1
python models/gemma3_runner.py --repo-id <HF_REPO_ID> --local-path models/gemma3_local --download --prompt "Olá"
```

Notes:
- Downloading large models may require huggingface authentication and agreement to model license.
- For best performance use a GPU build of PyTorch and consider quantized/ggml weights.
