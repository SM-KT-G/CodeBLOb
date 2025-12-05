"""
pytest 설정 파일
환경변수 로드 및 공통 픽스처
"""
import os
from pathlib import Path
from dotenv import load_dotenv


# .env 파일 로드
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✓ Loaded .env from {env_path}")
else:
    print(f"⚠ .env file not found at {env_path}")
