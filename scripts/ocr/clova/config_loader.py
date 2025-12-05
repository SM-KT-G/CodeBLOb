"""Configuration helpers for the Clova OCR client."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

_CONFIG_DIR = Path(__file__).parent
_DEFAULT_CONFIG_PATH = _CONFIG_DIR / "config.json"
_DEFAULT_DOTENV_PATH = _CONFIG_DIR / ".env"


@dataclass(frozen=True)
class ClovaConfig:
    """Holds the settings required to call the Clova OCR API."""

    invoke_url: str
    secret_key: str
    default_language: str = "ko"
    image_format: str = "jpg"

    def as_headers(self) -> Dict[str, str]:
        return {
            "X-OCR-SECRET": self.secret_key,
        }


def _load_json_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(text)


def load_config(
    config_path: Optional[Path] = None,
    dotenv_path: Optional[Path] = None,
) -> ClovaConfig:
    """Load configuration from JSON and environment overrides."""

    if config_path is None:
        config_path = _DEFAULT_CONFIG_PATH
    if dotenv_path is None:
        dotenv_path = _DEFAULT_DOTENV_PATH

    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=False)

    raw = _load_json_config(config_path)
    invoke_url = os.getenv("CLOVA_OCR_INVOKE_URL", raw.get("invoke_url", "")).strip()
    secret_key = os.getenv("CLOVA_OCR_SECRET_KEY", raw.get("secret_key", "")).strip()
    default_language = os.getenv(
        "CLOVA_OCR_DEFAULT_LANG", raw.get("default_language", "ko")
    ).strip()
    image_format = os.getenv(
        "CLOVA_OCR_IMAGE_FORMAT", raw.get("image_format", "jpg")
    ).strip()

    if not invoke_url:
        raise ValueError("invoke_url is required (config or CLOVA_OCR_INVOKE_URL)")
    if not secret_key:
        raise ValueError("secret_key is required (config or CLOVA_OCR_SECRET_KEY)")

    return ClovaConfig(
        invoke_url=invoke_url,
        secret_key=secret_key,
        default_language=default_language or "ko",
        image_format=image_format or "jpg",
    )
