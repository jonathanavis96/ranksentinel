"""File-based locking to prevent concurrent cron runs."""

import fcntl
import os
import sys
from pathlib import Path
from typing import Optional


class LockError(Exception):
    """Raised when lock cannot be acquired."""


class FileLock:
    """Context manager for exclusive file locks."""

    def __init__(self, lock_path: str, lock_name: str):
        """Initialize lock.

        Args:
            lock_path: Directory where lock file will be created
            lock_name: Name of the lock file (e.g., 'daily', 'weekly')
        """
        self.lock_dir = Path(lock_path)
        self.lock_file = self.lock_dir / f"{lock_name}.lock"
        self.fd: Optional[int] = None

    def __enter__(self) -> "FileLock":
        """Acquire the lock."""
        # Ensure lock directory exists
        self.lock_dir.mkdir(parents=True, exist_ok=True)

        # Open lock file
        self.fd = os.open(self.lock_file, os.O_CREAT | os.O_WRONLY, 0o600)

        # Try to acquire exclusive lock (non-blocking)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(self.fd)
            self.fd = None
            raise LockError(f"Another instance is already running (lock: {self.lock_file})")

        # Write PID to lock file
        os.ftruncate(self.fd, 0)
        os.write(self.fd, f"{os.getpid()}\n".encode())
        os.fsync(self.fd)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Release the lock."""
        if self.fd is not None:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                os.close(self.fd)
            except Exception:
                pass
            finally:
                self.fd = None
                # Clean up lock file
                try:
                    self.lock_file.unlink(missing_ok=True)
                except Exception:
                    pass


def acquire_lock_or_exit(lock_path: str, lock_name: str) -> FileLock:
    """Acquire lock or exit with error code.

    This is a convenience function for scripts that should exit
    if they cannot acquire the lock.

    Args:
        lock_path: Directory where lock file will be created
        lock_name: Name of the lock file

    Returns:
        FileLock context manager

    Exits:
        With code 1 if lock cannot be acquired
    """
    try:
        lock = FileLock(lock_path, lock_name)
        lock.__enter__()
        return lock
    except LockError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
