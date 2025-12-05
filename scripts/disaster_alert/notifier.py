"""Firebase Cloud Messaging helper."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging


@dataclass(frozen=True)
class NotifierConfig:
    service_account: str
    topic: str


class FirebaseNotifier:
    def __init__(self, config: NotifierConfig) -> None:
        self._config = config
        self._app: Optional[firebase_admin.App] = None

    def _ensure_app(self) -> None:
        if self._app is not None:
            return
        cred = credentials.Certificate(self._config.service_account)
        self._app = firebase_admin.initialize_app(cred)

    def send_alert(self, title: str, body: str, data: Optional[dict] = None) -> str:
        self._ensure_app()
        message = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            topic=self._config.topic,
            data=data or {},
        )
        return messaging.send(message)
