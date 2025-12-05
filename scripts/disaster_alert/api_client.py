"""Client for the data.go.kr disaster message API."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

import requests

from config_loader import ApiConfig, ParsingConfig


@dataclass(frozen=True)
class DisasterMessage:
    message_id: str
    content: str
    location: str
    raw: Dict[str, Any]


class DisasterApiClient:
    """Wraps the REST API and normalises results."""

    def __init__(self, api_config: ApiConfig, parsing: ParsingConfig, timeout: int = 10) -> None:
        self._api_config = api_config
        self._parsing = parsing
        self._timeout = timeout
        self._session = requests.Session()

    def fetch_messages(self, debug: bool = False) -> Tuple[List[DisasterMessage], Dict[str, Any]]:
        """Call the API and return normalised messages and raw payload."""

        params = dict(self._api_config.params)
        params.setdefault("pageNo", "1")
        params.setdefault("numOfRows", "10")
        params.setdefault("returnType", "json")
        params["serviceKey"] = self._api_config.service_key

        response = self._session.get(self._api_config.url, params=params, timeout=self._timeout)
        response.raise_for_status()
        data = response.json()

        if debug:
            print("--- API 응답 (데이터 구조 확인용) ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print(f"--------------------------------------- ({time.ctime()})")

        items = self._extract_items(data)
        messages = [self._to_message(item) for item in items if item]
        return messages, data

    def _extract_items(self, data: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        node: Any = data
        for key in self._parsing.items_path:
            if isinstance(node, dict):
                node = node.get(key)
            else:
                return []
            if node is None:
                return []
        if isinstance(node, dict):
            # some APIs wrap list in dict under key such as "item"
            if "item" in node:
                node = node["item"]
            else:
                node = list(node.values())
        return node if isinstance(node, list) else []

    def _to_message(self, item: Dict[str, Any]) -> DisasterMessage:
        message_id = str(item.get(self._parsing.id_field, "")).strip()
        content = str(item.get(self._parsing.message_field, "")).strip()
        location = str(item.get(self._parsing.location_field, "")).strip()
        return DisasterMessage(message_id=message_id, content=content, location=location, raw=item)
