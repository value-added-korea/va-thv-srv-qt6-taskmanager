#!/usr/bin/env python3
"""XDG user data and cache directory helpers for La Toolhive Thv Ui."""
import os
from pathlib import Path

APP_NAME = "la-toolhive-thv-ui"

DATA_DIR  = Path(os.environ.get("XDG_DATA_HOME",
                 Path.home() / ".local" / "share")) / APP_NAME
CACHE_DIR = Path(os.environ.get("XDG_CACHE_HOME",
                 Path.home() / ".cache")) / APP_NAME


def ensure_dirs() -> None:
    """Create user data and cache directories on first run."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
