"""
Command-line interface for gpio-pedal.

Usage::

    # Run with a JSON config file
    gpio-pedal config.json

    # Run with a YAML config file (requires PyYAML)
    gpio-pedal config.yaml

    # Show help
    gpio-pedal --help

    # Show version
    gpio-pedal --version
"""

from __future__ import annotations

import argparse
import logging
import sys

from gpio_pedal import __version__
from gpio_pedal.config import load_config
from gpio_pedal.utils import describe_config


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gpio-pedal",
        description=(
            "Map Raspberry Pi GPIO pins to keyboard shortcuts.\n\n"
            "CONFIG FILE FORMAT (JSON):\n"
            '  { "17": "space", "22": "ctrl+c", "27": "m" }\n\n'
            "YAML format is also supported (pip install gpio-pedal[yaml])."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "config",
        metavar="CONFIG_FILE",
        help="Path to a JSON or YAML config file mapping GPIO pins to keys.",
    )
    parser.add_argument(
        "--bouncetime",
        type=int,
        default=300,
        metavar="MS",
        help="Debounce time in milliseconds (default: 300).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose debug logging.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"gpio-pedal {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``gpio-pedal`` CLI command."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError, ImportError) as e:
        print(f"Error loading config: {e}", file=sys.stderr)
        sys.exit(1)

    print(describe_config(config))
    print()

    # Import here so the module fails gracefully if RPi.GPIO isn't available
    try:
        from gpio_pedal.controller import PedalController
    except ImportError as e:
        print(
            f"Error: {e}\n"
            "gpio-pedal requires RPi.GPIO, which only runs on a Raspberry Pi.",
            file=sys.stderr,
        )
        sys.exit(1)

    controller = PedalController(config, bouncetime=args.bouncetime)
    controller.run()


if __name__ == "__main__":
    main()
