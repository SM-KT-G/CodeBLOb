"""CLI to poll disaster messages and push alerts."""
from __future__ import annotations

import argparse
import time

import schedule

from api_client import DisasterApiClient
from config_loader import AppConfig, FirebaseConfig, load_app_config
from notifier import FirebaseNotifier, NotifierConfig
from poller import DisasterPoller


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="재난 문자 API 모니터링")
    parser.add_argument("--config", type=str, help="config.json 경로", default=None)
    parser.add_argument("--dotenv", type=str, help=".env 경로", default=None)
    parser.add_argument("--interval", type=int, help="폴링 간격(초)", default=None)
    parser.add_argument("--last-id", type=str, help="초기 마지막 메시지 ID", default=None)
    parser.add_argument("--once", action="store_true", help="한 번만 조회하고 종료")
    parser.add_argument("--debug", action="store_true", help="API 원본 JSON을 출력")
    return parser.parse_args()


def build_components(args: argparse.Namespace) -> tuple[AppConfig, DisasterPoller]:
    config = load_app_config(
        config_path=_maybe_path(args.config),
        dotenv_path=_maybe_path(args.dotenv),
    )
    api_client = DisasterApiClient(api_config=config.api, parsing=config.parsing)
    notifier = _build_notifier(config.firebase)
    poller = DisasterPoller(api_client=api_client, notifier=notifier, last_message_id=args.last_id)
    return config, poller


def _build_notifier(firebase_cfg: FirebaseConfig) -> FirebaseNotifier:
    notifier_cfg = NotifierConfig(
        service_account=firebase_cfg.service_account,
        topic=firebase_cfg.topic,
    )
    return FirebaseNotifier(config=notifier_cfg)


def _maybe_path(path_str: str | None):
    if path_str is None:
        return None
    from pathlib import Path

    return Path(path_str)


def main() -> None:
    args = parse_args()
    config, poller = build_components(args)
    interval = args.interval or config.schedule.interval_seconds

    if args.once:
        poller.check_once(debug=args.debug)
        return

    print(f"{interval}초 간격으로 재난 문자를 모니터링합니다.")
    schedule.every(interval).seconds.do(poller.check_once, debug=args.debug)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("사용자 종료 요청을 받아 모니터링을 중단합니다.")


if __name__ == "__main__":
    main()
