"""Configuration loader for the disaster alert script."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv

_BASE_DIR = Path(__file__).parent
_DEFAULT_CONFIG_PATH = _BASE_DIR / "config.json"
_DEFAULT_ENV_PATH = _BASE_DIR / ".env"


@dataclass(frozen=True)
class ApiConfig:
    url: str
    params: Dict[str, str]
    service_key: str


@dataclass(frozen=True)
class ScheduleConfig:
    interval_seconds: int = 300


@dataclass(frozen=True)
class FirebaseConfig:
    service_account: str
    topic: str


@dataclass(frozen=True)
class ParsingConfig:
    items_path: List[str]
    id_field: str
    message_field: str
    location_field: str


@dataclass(frozen=True)
class AppConfig:
    api: ApiConfig
    schedule: ScheduleConfig
    firebase: FirebaseConfig
    parsing: ParsingConfig


def _read_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"config file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_app_config(
    config_path: Optional[Path] = None,
    dotenv_path: Optional[Path] = None,
) -> AppConfig:
    config_path = config_path or _DEFAULT_CONFIG_PATH
    dotenv_path = dotenv_path or _DEFAULT_ENV_PATH

    if dotenv_path.exists():
        load_dotenv(dotenv_path, override=False)

    raw = _read_json(config_path)

    api = _load_api_config(raw.get("api", {}))
    schedule = _load_schedule_config(raw.get("schedule", {}))
    firebase = _load_firebase_config(raw.get("firebase", {}))
    parsing = _load_parsing_config(raw.get("parsing", {}))

    return AppConfig(api=api, schedule=schedule, firebase=firebase, parsing=parsing)


def _load_api_config(raw: Dict[str, object]) -> ApiConfig:
    url = str(raw.get("url") or "").strip()
    if not url:
        raise ValueError("api.url is required")

    params = {str(k): str(v) for k, v in (raw.get("params") or {}).items()}
    service_key = os.getenv("DATA_GO_KR_API_KEY", "").strip()
    if not service_key:
        raise ValueError("DATA_GO_KR_API_KEY is required (set in .env or environment)")

    params.setdefault("serviceKey", service_key)
    return ApiConfig(url=url, params=params, service_key=service_key)


def _load_schedule_config(raw: Dict[str, object]) -> ScheduleConfig:
    interval = int(raw.get("interval_seconds", 300))
    if interval <= 0:
        raise ValueError("schedule.interval_seconds must be positive")
    return ScheduleConfig(interval_seconds=interval)


def _load_firebase_config(raw: Dict[str, object]) -> FirebaseConfig:
    service_account = os.getenv(
        "FIREBASE_CREDENTIALS", str(raw.get("service_account") or "")
    ).strip()
    topic = os.getenv("FIREBASE_TOPIC", str(raw.get("topic") or "")).strip()
    if not service_account:
        raise ValueError("Firebase service account path is required")
    if not topic:
        raise ValueError("Firebase topic is required")
    return FirebaseConfig(service_account=service_account, topic=topic)


def _load_parsing_config(raw: Dict[str, object]) -> ParsingConfig:
    items_path = [str(part) for part in raw.get("items_path", [])]
    if not items_path:
        raise ValueError("parsing.items_path must contain at least one key")
    id_field = str(raw.get("id_field") or "md101_sn")
    message_field = str(raw.get("message_field") or "msg_cn")
    location_field = str(raw.get("location_field") or "rcv_area_nm")
    return ParsingConfig(
        items_path=items_path,
        id_field=id_field,
        message_field=message_field,
        location_field=location_field,
    )
