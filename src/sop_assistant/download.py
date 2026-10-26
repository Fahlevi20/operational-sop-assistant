"""Download EmbeddingGemma locally; does not load it or call an LLM."""

import argparse
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import snapshot_download
from huggingface_hub.errors import HfHubHTTPError

MODEL_ID = "google/embeddinggemma-300m"


def download_model(target: Path, downloader=snapshot_download, revision="main") -> str:
    """Use HF_TOKEN or cached Hugging Face login; never log credentials."""
    return downloader(
        repo_id=MODEL_ID,
        revision=revision,
        local_dir=str(target),
        allow_patterns=["*.json", "*.safetensors", "*.model", "*.txt", "*.md"],
        max_workers=2,
    )


def main():
    """Explicit user-run download with gated-model troubleshooting."""
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/models/embeddinggemma-300m"))
    parser.add_argument(
        "--revision", default="main", help="HF revision or commit for reproducibility"
    )
    args = parser.parse_args()
    print(f"Downloading {MODEL_ID} to {args.output}. Model weights are roughly 1.2 GB.")
    try:
        path = download_model(args.output, revision=args.revision)
    except HfHubHTTPError:
        parser.exit(
            1,
            "Download denied or unavailable. Accept Gemma terms at "
            "https://huggingface.co/google/embeddinggemma-300m, then use "
            "`uv run hf auth login` or set HF_TOKEN in your ignored .env. "
            "Check network/access and retry.\n",
        )
    except OSError:
        parser.exit(
            1, "Download failed. Check connectivity, free disk space, and directory permissions.\n"
        )
    print(f"Download complete: {path}")
    print("Keep this folder local. Downloading does not yet configure application inference.")


if __name__ == "__main__":
    main()
