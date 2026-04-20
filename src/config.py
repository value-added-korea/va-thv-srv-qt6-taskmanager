#!/usr/bin/env python3
"""User configuration loader for La Toolhive Thv Ui.

Config file location: ~/.config/la-toolhive-thv-ui/config.ini
A default config is written on first run if absent.
Edit DEFAULTS to add application-specific settings.
"""
import configparser
import os
from pathlib import Path

APP_NAME = "la-toolhive-thv-ui"

CONFIG_DIR  = Path(os.environ.get("XDG_CONFIG_HOME",
                   Path.home() / ".config")) / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.ini"

DEFAULTS: dict[str, dict[str, str]] = {
    "general": {
        "autostart": "true",
    },
    # TODO: Add your application-specific config sections and keys here.
}


def load() -> configparser.ConfigParser:
    """Return a ConfigParser populated from disk (or defaults if absent)."""
    parser = configparser.ConfigParser()
    for section, values in DEFAULTS.items():
        parser[section] = values
    if CONFIG_FILE.exists():
        parser.read(CONFIG_FILE, encoding="utf-8")
    else:
        _write(parser)
    return parser


def save(parser: configparser.ConfigParser) -> None:
    """Persist *parser* to ~/.config/la-toolhive-thv-ui/config.ini."""
    _write(parser)


def _write(parser: configparser.ConfigParser) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as fh:
        parser.write(fh)
