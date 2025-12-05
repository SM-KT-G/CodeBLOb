"""Polling logic for disaster messages."""
from __future__ import annotations

import time
from typing import Optional

from api_client import DisasterApiClient, DisasterMessage
from notifier import FirebaseNotifier


class DisasterPoller:
    def __init__(
        self,
        api_client: DisasterApiClient,
        notifier: FirebaseNotifier,
        last_message_id: Optional[str] = None,
    ) -> None:
        self._api_client = api_client
        self._notifier = notifier
        self._last_message_id = last_message_id

    def check_once(self, debug: bool = False) -> None:
        print(f"\n[{time.ctime()}] 재난 문자 확인 시작...")

        try:
            messages, _ = self._api_client.fetch_messages(debug=debug)
        except Exception as exc:  # requests and parsing errors bubble up
            print(f"API 호출 오류: {exc}")
            return

        if not messages:
            print("수신된 메시지가 없습니다.")
            return

        latest = messages[0]
        if not latest.message_id or not latest.content:
            print("오류: API 응답에서 메시지 ID 또는 내용을 찾을 수 없습니다.")
            return

        print(f"최신 메시지 ID: {latest.message_id}")
        if latest.message_id == self._last_message_id:
            print("새로운 재난 문자가 없습니다.")
            return

        print(f"!!! 새로운 재난 문자 발견: {latest.content}")
        self._send_notification(latest)
        self._last_message_id = latest.message_id

    def _send_notification(self, message: DisasterMessage) -> None:
        title = message.location or "재난 문자"
        body = message.content
        data = {
            "message_id": message.message_id,
            "location": message.location,
        }
        try:
            response_id = self._notifier.send_alert(title=title, body=body, data=data)
            print(f"FCM 푸시 전송 성공: {response_id}")
        except Exception as exc:
            print(f"FCM 전송 오류: {exc}")
