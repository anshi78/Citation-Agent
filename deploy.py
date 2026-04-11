"""
Deploy Citation-Agent to Hugging Face Space.

Usage:
    python deploy.py
"""

import os
from huggingface_hub import HfApi

SPACE_ID = "ruby56/Citation-Agent"

# Your HuggingFace token for uploading (NOT the Groq key)
# Set via: $env:HF_UPLOAD_TOKEN="hf_your_token_here"
HF_UPLOAD_TOKEN = os.environ.get("HF_UPLOAD_TOKEN", "")

# Files to upload to the HF Space
FILES_TO_UPLOAD = [
    # Core environment
    "environment.py",
    "tasks.py",
    # OpenEnv server
    "server/__init__.py",
    "server/app.py",
    "server/citation_environment.py",
    # Inference
    "inference.py",
    # Config & build
    "Dockerfile",
    "openenv.yaml",
    "requirements.txt",
    "pyproject.toml",
    "uv.lock",
    "README.md",
    ".gitattributes",
    ".dockerignore",
    ".gitignore",
    # Supporting files
    "database_builder.py",
    "generate_tasks.py",
    "citations_links.txt",
    "dataset_links.txt",
]

def main():
    api = HfApi(token=HF_UPLOAD_TOKEN)

    # Check which files actually exist locally
    existing = [f for f in FILES_TO_UPLOAD if os.path.exists(f)]
    missing = [f for f in FILES_TO_UPLOAD if not os.path.exists(f)]
    
    if missing:
        print(f"Note: Skipping {len(missing)} missing files: {missing}")

    print(f"Uploading {len(existing)} files to {SPACE_ID}...")
    
    api.upload_folder(
        folder_path=".",
        repo_id=SPACE_ID,
        repo_type="space",
        allow_patterns=existing,
    )
    
    print(f"\n✅ Deployed to https://huggingface.co/spaces/{SPACE_ID}")
    print("The Space will rebuild automatically. Wait ~5 minutes for it to be ready.")

if __name__ == "__main__":
    main()
