"""Client utilities for requesting latest exchange rates."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import requests

OPEN_ER_API_URL = "https://open.er-api.com/v6/latest"


def _normalize_symbols(symbols: Iterable[str]) -> List[str]:
    normalized: List[str] = []
    for symbol in symbols:
        token = str(symbol).strip()
        if token:
            normalized.append(token.upper())
    return normalized


@dataclass(frozen=True)
class ExchangeQuery:
    """Represents a single exchange-rate lookup."""

    base_currency: str
    symbols: Iterable[str]
    amount: float = 1.0

    def normalized_base(self) -> str:
        return self.base_currency.upper()

    def normalized_symbols(self) -> List[str]:
        return _normalize_symbols(self.symbols)


class ExchangeClient:
    """Thin wrapper around the open.er-api.com latest endpoint."""

    def __init__(
        self,
        base_url: str = OPEN_ER_API_URL,
        session: Optional[requests.Session] = None,
        timeout: int = 10,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout

    def fetch_rates(self, query: ExchangeQuery) -> Dict[str, object]:
        """Return normalized payload containing requested symbol rates."""

        url = f"{self._base_url}/{query.normalized_base()}"
        response = self._session.get(url, timeout=self._timeout)
        response.raise_for_status()
        payload = response.json()
        if payload.get("result") != "success":
            error_info = payload.get("error-type") or payload
            raise ValueError(f"API returned error: {error_info}")
        rates = payload.get("rates")
        if not isinstance(rates, dict):
            raise ValueError("API response missing 'rates' field")

        matched: Dict[str, float] = {}
        missing: List[str] = []
        for symbol in query.normalized_symbols():
            rate = rates.get(symbol)
            if rate is None:
                missing.append(symbol)
                continue
            matched[symbol] = rate * query.amount

        return {
            "base_code": payload.get("base_code", query.normalized_base()),
            "amount": query.amount,
            "rates": matched,
            "missing_symbols": missing,
            "meta": {
                "provider": payload.get("provider"),
                "time_last_update_unix": payload.get("time_last_update_unix"),
                "time_last_update_utc": payload.get("time_last_update_utc"),
                "time_next_update_unix": payload.get("time_next_update_unix"),
                "time_next_update_utc": payload.get("time_next_update_utc"),
            },
            "raw_count": len(rates),
        }
