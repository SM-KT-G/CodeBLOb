"""Client for the data.go.kr disaster message API."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config_loader import ApiConfig, ParsingConfig


@dataclass(frozen=True)
class DisasterMessage:
    message_id: str
    content: str
    location: str
    raw: Dict[str, Any]


class DisasterApiClient:
    """Wraps the REST API and normalises results."""

    def __init__(
        self,
        api_config: ApiConfig,
        parsing: ParsingConfig,
        timeout: int = 10,
        retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self._api_config = api_config
        self._parsing = parsing
        self._timeout = timeout
        self._session = requests.Session()
        self._configure_retries(max(0, retries), backoff_factor)

    def fetch_messages(self, debug: bool = False) -> Tuple[List[DisasterMessage], Dict[str, Any]]:
        """Call the API and return normalised messages and raw payload."""

        params = dict(self._api_config.params)
        params.setdefault("pageNo", "1")
        params.setdefault("numOfRows", "10")
        params.setdefault("returnType", "json")
        params["serviceKey"] = self._api_config.service_key

        try:
            response = self._session.get(self._api_config.url, params=params, timeout=self._timeout)
        except requests.RequestException as exc:
            raise RuntimeError(f"Failed to reach disaster API at {self._api_config.url}") from exc

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
        traversed: List[str] = []

        for key in self._parsing.items_path:
            traversed.append(str(key))
            if not isinstance(node, dict):
                joined = " -> ".join(traversed[:-1]) or "<root>"
                raise ValueError(
                    f"items_path expects mapping at {joined}, "
                    f"got {type(node).__name__} while accessing '{key}'"
                )
            if key not in node or node[key] is None:
                raise ValueError(f"items_path missing key '{key}' after traversing {' -> '.join(traversed[:-1]) or '<root>'}")
            node = node[key]

        if isinstance(node, dict):
            # some APIs wrap list in dict under key such as "item"
            if "item" in node:
                node = node["item"]
            else:
                node = list(node.values())

        if not isinstance(node, list):
            raise ValueError(
                "items_path did not resolve to a list. "
                f"End node type: {type(node).__name__}"
            )

        return node

    def _to_message(self, item: Dict[str, Any]) -> DisasterMessage:
        message_id = str(item.get(self._parsing.id_field, "")).strip()
        content = str(item.get(self._parsing.message_field, "")).strip()
        location = str(item.get(self._parsing.location_field, "")).strip()
        return DisasterMessage(message_id=message_id, content=content, location=location, raw=item)

    def _configure_retries(self, retries: int, backoff_factor: float) -> None:
        if retries <= 0:
            return

        retry = Retry(
            total=retries,
            connect=retries,
            read=retries,
            status=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)
