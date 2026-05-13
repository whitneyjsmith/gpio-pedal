"""
Utility helpers for gpio-pedal.

Provides key-string validation and introspection so users can
check their config before wiring it up to hardware.
"""

from __future__ import annotations

from typing import List, Optional
from pynput.keyboard import Key


# All named special keys that pynput understands.
# Key.__members__ is the standard Enum API for this — works with both
# the real pynput Key enum and test mocks.
SPECIAL_KEYS: List[str] = list(Key.__members__.keys())


def is_valid_key(key_string: str) -> bool:
    """Return True if *key_string* is a valid key that gpio-pedal can simulate.

    Accepts single characters (``"a"``, ``"1"``, ``"!"``) as well as named
    special keys (``"space"``, ``"ctrl"``, ``"enter"``) and combinations
    joined by ``+`` (``"ctrl+c"``, ``"shift+f1"``).

    Args:
        key_string: The key string to validate.

    Returns:
        True if the key string is valid, False otherwise.
    """
    if not isinstance(key_string, str) or not key_string.strip():
        return False

    parts = [p.strip() for p in key_string.split("+")]
    for part in parts:
        if len(part) == 1:
            continue  # single character — always valid
        if part not in SPECIAL_KEYS:
            return False
    return True


def validate_key(key_string: str) -> None:
    """Raise ``ValueError`` if *key_string* is not a valid key.

    Args:
        key_string: The key string to validate.

    Raises:
        ValueError: With a helpful message listing available special keys.
    """
    if not is_valid_key(key_string):
        invalid_parts = [
            p.strip()
            for p in key_string.split("+")
            if len(p.strip()) != 1 and p.strip() not in SPECIAL_KEYS
        ]
        raise ValueError(
            f"Invalid key name(s): {invalid_parts}. "
            f"Available special keys: {sorted(SPECIAL_KEYS)}"
        )


def list_special_keys() -> List[str]:
    """Return a sorted list of all special key names supported by pynput.

    Returns:
        Sorted list of special key name strings (e.g. ``["alt", "backspace", ...]``).
    """
    return sorted(SPECIAL_KEYS)


def describe_config(config: dict) -> str:
    """Return a human-readable summary of a pin→key mapping config.

    Args:
        config: Dict mapping GPIO pin numbers to key strings.

    Returns:
        A formatted multi-line string describing each mapping.
    """
    if not config:
        return "(empty config)"
    lines = ["GPIO pin → key mapping:"]
    for pin in sorted(config):
        lines.append(f"  GPIO {pin:>3}  →  {config[pin]}")
    return "\n".join(lines)
