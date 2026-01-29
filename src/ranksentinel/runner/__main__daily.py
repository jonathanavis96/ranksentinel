#!/usr/bin/env python3
"""Entry point for daily checks runner."""

import sys
from pathlib import Path

from ranksentinel.config import get_settings
from ranksentinel.lock import FileLock, LockError
from ranksentinel.operator_alert import send_operator_alert
from ranksentinel.runner.daily_checks import run


def main() -> None:
    settings = get_settings()
    
    # Determine lock directory (same as DB location)
    db_path = Path(settings.RANKSENTINEL_DB_PATH)
    lock_dir = db_path.parent if db_path.is_absolute() else Path.cwd()
    
    # Acquire lock or exit
    try:
        with FileLock(str(lock_dir), "daily"):
            run(settings)
    except LockError as e:
        error_msg = f"Daily run failed (lock): {e}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        send_operator_alert(
            settings=settings,
            run_type="daily",
            error_type="LockError",
            error_message=str(e),
            context={"lock_dir": str(lock_dir)},
        )
        sys.exit(1)
    except Exception as e:
        error_msg = f"Daily run failed: {type(e).__name__}: {e}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        send_operator_alert(
            settings=settings,
            run_type="daily",
            error_type=type(e).__name__,
            error_message=str(e),
        )
        sys.exit(1)
    
    # Success - exit 0 (implicit)


if __name__ == "__main__":
    main()
