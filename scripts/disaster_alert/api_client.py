"""Client for the data.go.kr disaster message API."""
from __future__ import annotations

import json
import time
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

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
        session: Optional[requests.Session] = None,
    ) -> None:
        self._api_config = api_config
        self._parsing = parsing
        self._timeout = timeout
        self._logger = logging.getLogger(__name__)
        self._session = session or requests.Session()
        self._owns_session = session is None
        if self._owns_session:
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
            safe_params = dict(params)
            if "serviceKey" in safe_params:
                safe_params["serviceKey"] = "***REDACTED***"
            self._logger.debug("Disaster API request to %s with params %s", self._api_config.url, safe_params)
            pretty_payload = json.dumps(data, indent=2, ensure_ascii=False)
            self._logger.debug("Disaster API response snapshot at %s\n%s", time.ctime(), pretty_payload)

        items = self._extract_items(data)
        messages: List[DisasterMessage] = []
        seen_ids: Set[str] = set()
        for item in items:
            if not item:
                continue
            message = self._to_message(item)
            message_id = message.message_id
            if message_id in seen_ids:
                raise ValueError(f"Duplicate message_id '{message_id}' detected in API payload")
            seen_ids.add(message_id)
            messages.append(message)
        return messages, data

    def close(self) -> None:
        if self._owns_session:
            self._session.close()

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
        message_id = self._require_text_field(item, self._parsing.id_field, "message_id")
        content = self._require_text_field(item, self._parsing.message_field, "content")
        location = str(item.get(self._parsing.location_field, "")).strip()
        return DisasterMessage(message_id=message_id, content=content, location=location, raw=item)

    def _require_text_field(self, item: Dict[str, Any], field_name: str, label: str) -> str:
        if field_name not in item:
            raise ValueError(f"Missing '{field_name}' for {label} in disaster message payload")
        value = item[field_name]
        text = str(value).strip()
        if not text:
            raise ValueError(f"Field '{field_name}' resolved for {label} but is empty/blank")
        return text

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
