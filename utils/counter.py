"""utils/counter.py — simple file-based usage counter."""

import os

COUNTER_FILE = "usage_count.txt"


def get_count() -> int:
    """Get the current total analysis count."""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, "r") as f:
                return int(f.read().strip() or 0)
        return 0
    except Exception:
        return 0


def increment_count() -> int:
    """Increment counter by 1 and return new count."""
    try:
        count = get_count() + 1
        with open(COUNTER_FILE, "w") as f:
            f.write(str(count))
        return count
    except Exception:
        return 0