#!/usr/bin/env python3
"""Entry point for daily checks runner."""

import sys
from pathlib import Path

from ranksentinel.config import get_settings
from ranksentinel.lock import FileLock, LockError
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
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
