"""Pre-download the Whisper model to local cache.

Run once before your first meeting:
    uv run download-model
    # or
    python -m meeting_summarizer.download_model
"""

import os

import whisper
from dotenv import load_dotenv


load_dotenv()

MODEL_INFO: dict[str, dict[str, str]] = {
    "tiny":   {"params": "39M", "size": "~75 MB"},
    "base":   {"params": "74M", "size": "~145 MB"},
    "small":  {"params": "244M", "size": "~480 MB"},
    "medium": {"params": "769M", "size": "~1.5 GB"},
    "large":  {"params": "1.5B", "size": "~3 GB"},
}


def download(model_size: str | None = None) -> None:
    model_size = model_size or os.getenv("WHISPER_MODEL", "medium")
    info = MODEL_INFO.get(model_size, {})

    print(f"Downloading Whisper model: '{model_size}'")
    if info:
        print(f"  Parameters : {info['params']}")
        print(f"  Disk size  : {info['size']}")
    print("  Cache dir  : ~/.cache/whisper/")
    print()

    whisper.load_model(model_size)

    cache_dir = os.path.expanduser("~/.cache/whisper")
    if os.path.exists(cache_dir):
        print("✓ Cached files:")
        for fname in os.listdir(cache_dir):
            path = os.path.join(cache_dir, fname)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            print(f"  {fname}  ({size_mb:.1f} MB)")

    print("\nAll done — run `meeting-summarizer <audio_file>` to process a meeting.")


if __name__ == "__main__":
    download()
