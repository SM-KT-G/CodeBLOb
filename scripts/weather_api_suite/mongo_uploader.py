"""Helpers for persisting weather data into MongoDB."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from pymongo import MongoClient
from pymongo.collection import Collection


class MongoUploader:
    """Simple wrapper that stores API responses with metadata."""

    def __init__(
        self,
        uri: str,
        db_name: str,
        collection_prefix: str = "weather_data",
        debug: bool = False,
    ) -> None:
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client[db_name]
        self.collection_prefix = collection_prefix
        self.debug = debug

    def _collection(self, service: str) -> Collection:
        suffix = service.replace("-", "_")
        name = f"{self.collection_prefix}_{suffix}"
        return self.db[name]

    def ping(self) -> None:
        """Verify connectivity up front."""
        self.client.admin.command("ping")
        if self.debug:
            print("[debug] MongoDB ping successful.")

    def insert(self, service: str, metadata: Dict[str, Any], payload: Any) -> None:
        document = {
            "service": service,
            "metadata": metadata,
            "payload": payload,
            "created_at": datetime.now(timezone.utc),
        }
        collection = self._collection(service)
        result = collection.insert_one(document)
        if self.debug:
            print(f"[debug] Inserted document into {collection.full_name} id={result.inserted_id}")

    def close(self) -> None:
        self.client.close()
