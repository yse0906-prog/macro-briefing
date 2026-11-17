"""가장 최근 브리핑을 텔레그램 메시지로 출력한다. 깃허브 워크플로가 이 글을 보낸다."""
import sys
from pathlib import Path

from macro.data import load_site_data
from macro.notify import telegram_message

if __name__ == "__main__":
    text = telegram_message(load_site_data(Path("data")))
    if not text:
        print("[notify] 보낼 브리핑이 없습니다", file=sys.stderr)
        raise SystemExit(1)
    sys.stdout.write(text)
