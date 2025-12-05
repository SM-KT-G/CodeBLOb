"""Helpers to parse Clova OCR responses."""
from __future__ import annotations

from typing import Any, Dict, List


def extract_text_lines(response: Dict[str, Any]) -> List[str]:
    """Return a flattened list of inferred text segments."""

    lines: List[str] = []
    for image in response.get("images", []) or []:
        for field in image.get("fields", []) or []:
            text = field.get("inferText")
            if text:
                lines.append(str(text).strip())
    return [line for line in lines if line]


def summarize(response: Dict[str, Any]) -> Dict[str, Any]:
    """Extract small summary metadata for logging/printing."""

    images = response.get("images", []) or []
    field_count = sum(len(img.get("fields", []) or []) for img in images)
    return {
        "image_count": len(images),
        "field_count": field_count,
    }
