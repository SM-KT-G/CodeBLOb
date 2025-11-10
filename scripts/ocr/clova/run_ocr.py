"""CLI entrypoint for sending images to Clova OCR."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from clova_client import ClovaOcrClient
from config_loader import ClovaConfig, load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send an image to Clova OCR")
    parser.add_argument("image", type=Path, help="분석할 이미지 경로")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="기본값은 scripts/ocr/clova/config.json",
    )
    parser.add_argument(
        "--dotenv",
        type=Path,
        default=None,
        help=".env 파일 경로 (기본값은 scripts/ocr/clova/.env)",
    )
    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="요청 언어를 덮어씁니다 (예: ko, en).",
    )
    parser.add_argument(
        "--format",
        dest="image_format",
        type=str,
        default=None,
        help="이미지 포맷을 덮어씁니다 (예: png).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="요청 타임아웃(초).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config: ClovaConfig = load_config(config_path=args.config, dotenv_path=args.dotenv)
    client = ClovaOcrClient(config=config, timeout=args.timeout)
    response = client.recognize(
        image_path=args.image,
        language=args.language,
        image_format=args.image_format,
    )
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
