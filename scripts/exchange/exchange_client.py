"""Client utilities for requesting latest exchange rates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

import requests

EXCHANGE_RATE_HOST_URL = "https://api.exchangerate.host/latest"


@dataclass(frozen=True)
class ExchangeQuery:
    """Represents a single exchange-rate lookup."""

    base_currency: str
    symbols: Iterable[str]
    amount: float = 1.0

    def to_params(self) -> Dict[str, Any]:
        symbols_param = ",".join(currency.upper() for currency in self.symbols)
        return {
            "base": self.base_currency.upper(),
            "symbols": symbols_param,
            "amount": self.amount,
            "places": 6,
        }


class ExchangeClient:
    """Thin wrapper around the ExchangeRate.host API."""

    def __init__(
        self,
        base_url: str = EXCHANGE_RATE_HOST_URL,
        session: Optional[requests.Session] = None,
        timeout: int = 10,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout

    def fetch_rates(self, query: ExchangeQuery) -> Dict[str, Any]:
        response = self._session.get(
            self._base_url,
            params=query.to_params(),
            timeout=self._timeout,
        )
        response.raise_for_status()
        payload: Dict[str, Any] = response.json()
        success = payload.get("success", True)
        if not success:
            # API sometimes returns error info in 'error' field
            error_info = payload.get("error") or payload
            raise ValueError(f"API returned error: {error_info}")
        if "rates" not in payload:
            raise ValueError("API response missing 'rates' field")
        return payload
