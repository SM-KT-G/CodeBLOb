"""Client utilities for requesting current weather data from Open-Meteo."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass(frozen=True)
class WeatherQuery:
    """Query parameters describing a single weather lookup."""

    latitude: float
    longitude: float
    timezone: str = "auto"
    temperature_unit: str = "celsius"
    wind_speed_unit: str = "ms"

    def to_params(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "current_weather": True,
            "temperature_unit": self.temperature_unit,
            "wind_speed_unit": self.wind_speed_unit,
        }


class WeatherClient:
    """Thin wrapper around the Open-Meteo forecast endpoint."""

    def __init__(
        self,
        base_url: str = OPEN_METEO_URL,
        session: Optional[requests.Session] = None,
        timeout: int = 10,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._timeout = timeout

    def fetch_current_weather(self, query: WeatherQuery) -> Dict[str, Any]:
        """Return the parsed JSON body from Open-Meteo for the given query."""

        response = self._session.get(
            self._base_url,
            params=query.to_params(),
            timeout=self._timeout,
        )
        response.raise_for_status()
        payload: Dict[str, Any] = response.json()
        if "current_weather" not in payload:
            raise ValueError("API response did not include current_weather field")
        return payload
