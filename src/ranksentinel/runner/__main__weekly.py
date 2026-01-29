#!/usr/bin/env python3
"""Entry point for weekly digest runner."""

import sys
from pathlib import Path

from ranksentinel.config import get_settings
from ranksentinel.lock import FileLock, LockError
from ranksentinel.runner.weekly_digest import run


def main() -> None:
    settings = get_settings()
    
    # Determine lock directory (same as DB location)
    db_path = Path(settings.RANKSENTINEL_DB_PATH)
    lock_dir = db_path.parent if db_path.is_absolute() else Path.cwd()
    
    # Acquire lock or exit
    try:
        with FileLock(str(lock_dir), "weekly"):
            run(settings)
    except LockError as e:
        print(f"ERROR: Weekly run failed (lock): {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Weekly run failed: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Success - exit 0 (implicit)


if __name__ == "__main__":
    main()
