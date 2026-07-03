import argparse
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Minimal runner for Gemma3:12B (HF or local)")
    parser.add_argument("--repo-id", help="Hugging Face repo id for model (optional)", default=None)
    parser.add_argument("--local-path", help="Local directory with model files (optional)", default=None)
    parser.add_argument("--device", help="Device to use (cpu/cuda)", default=None)
    parser.add_argument("--download", action="store_true", help="If set, attempt to download model to local-path using huggingface_hub")
    parser.add_argument("--prompt", help="Prompt to run", default="Hello from Gemma3")
    args = parser.parse_args()

    model_source = args.local_path or args.repo_id
    if model_source is None:
        print("Provide --repo-id or --local-path to load the model.")
        sys.exit(1)

    device = args.device or ("cuda" if (os.environ.get("CUDA_VISIBLE_DEVICES") is not None or os.path.exists("/proc/driver/nvidia")) else "cpu")

    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    except Exception as e:
        print("Transformers not available. Install requirements and retry.")
        raise

    # Optional download flow
    if args.download and args.repo_id and args.local_path:
        try:
            from huggingface_hub import snapshot_download
            print(f"Downloading {args.repo_id} to {args.local_path} ...")
            snapshot_download(repo_id=args.repo_id, cache_dir=args.local_path, local_dir_use_symlinks=False)
            model_source = args.local_path
        except Exception as e:
            print("Failed to download model:", e)
            raise

    print(f"Loading tokenizer and model from {model_source} on {device}...")
    tokenizer = AutoTokenizer.from_pretrained(model_source, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(model_source, device_map="auto" if device.startswith("cuda") else None, torch_dtype=None)

    gen = pipeline("text-generation", model=model, tokenizer=tokenizer, device=0 if device.startswith("cuda") else -1)
    out = gen(args.prompt, max_new_tokens=128, do_sample=False)
    print(out[0]["generated_text"])  

if __name__ == "__main__":
    main()
