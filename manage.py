#!/usr/bin/env python
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Add apps folder to Python path
sys.path.insert(0, str(BASE_DIR / "apps"))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc
    execute_from_command_line(sys.argv)