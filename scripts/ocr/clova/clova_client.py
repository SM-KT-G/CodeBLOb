"""HTTP client for interacting with the Naver Clova OCR API."""
from __future__ import annotations

import json
import mimetypes
import time
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

import requests

from config_loader import ClovaConfig


class ClovaOcrClient:
    """Thin wrapper for the Clova OCR REST endpoint."""

    def __init__(self, config: ClovaConfig, timeout: int = 15) -> None:
        self._config = config
        self._timeout = timeout

    def recognize(
        self,
        image_path: Path,
        language: Optional[str] = None,
        image_format: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send the image to Clova OCR and return the parsed JSON response."""

        if not image_path.exists():
            raise FileNotFoundError(f"image file not found: {image_path}")

        lang = (language or self._config.default_language).strip() or "ko"
        fmt = (image_format or self._config.image_format).strip() or "jpg"
        payload = self._build_message(image_path, lang, fmt)

        mime_type, _ = mimetypes.guess_type(str(image_path))
        mime_type = mime_type or "application/octet-stream"

        with image_path.open("rb") as file_obj:
            files = {
                "file": (image_path.name, file_obj, mime_type),
            }
            response = requests.post(
                self._config.invoke_url,
                headers={**self._config.as_headers()},
                data={"message": json.dumps(payload, ensure_ascii=False)},
                files=files,
                timeout=self._timeout,
            )

        response.raise_for_status()
        return response.json()

    def _build_message(self, image_path: Path, language: str, image_format: str) -> Dict[str, Any]:
        return {
            "version": "V2",
            "requestId": str(uuid4()),
            "timestamp": int(time.time() * 1000),
            "lang": language,
            "images": [
                {
                    "format": image_format,
                    "name": image_path.stem,
                }
            ],
        }
