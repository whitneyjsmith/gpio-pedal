"""
Config loading for gpio-pedal.

Supports loading pin→key mappings from JSON or YAML files,
or validating a plain Python dict before passing to PedalController.

Config file format (JSON example)::

    {
        "17": "space",
        "22": "ctrl+c",
        "27": "m"
    }

YAML format (requires ``pip install gpio-pedal[yaml]``)::

    17: space
    22: ctrl+c
    27: m
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def load_config(path: str | Path) -> Dict[int, str]:
    """Load a pin→key mapping from a JSON or YAML config file.

    Args:
        path: Path to a ``.json`` or ``.yaml`` / ``.yml`` config file.

    Returns:
        A dict mapping GPIO pin numbers (int) to key strings (str).

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is unsupported or the config is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".json":
        with path.open() as f:
            raw = json.load(f)
    elif suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError as e:
            raise ImportError(
                "PyYAML is required for YAML config files. "
                "Install it with: pip install gpio-pedal[yaml]"
            ) from e
        with path.open() as f:
            raw = yaml.safe_load(f)
    else:
        raise ValueError(
            f"Unsupported config file format: '{suffix}'. Use .json or .yaml"
        )

    return validate_config(raw)


def validate_config(config: dict) -> Dict[int, str]:
    """Validate and normalise a raw pin→key mapping dict.

    Accepts string keys (e.g. from JSON) and converts them to ints.

    Args:
        config: Raw mapping of pin numbers to key strings.

    Returns:
        A validated dict with integer keys and string values.

    Raises:
        ValueError: If any pin or key value is invalid.
        TypeError: If the config is not a dict.
    """
    if not isinstance(config, dict):
        raise TypeError(f"Config must be a dict, got {type(config).__name__}")

    validated: Dict[int, str] = {}
    for pin, key in config.items():
        try:
            pin_int = int(pin)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid GPIO pin number: {pin!r} (must be an integer)")

        if not isinstance(key, str) or not key.strip():
            raise ValueError(
                f"Key for pin {pin_int} must be a non-empty string, got {key!r}"
            )

        validated[pin_int] = key.strip()

    if not validated:
        raise ValueError("Config must contain at least one pin mapping")

    return validated
