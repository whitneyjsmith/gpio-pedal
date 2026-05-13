"""
gpio-pedal: Map Raspberry Pi GPIO pins to keyboard shortcuts.

Turn any foot pedal, footswitch, or button wired to GPIO into a
configurable keyboard shortcut — useful for hands-free control,
accessibility, live performance, transcription, and more.

Basic usage::

    from gpio_pedal import PedalController

    config = {
        17: "space",    # GPIO 17 → Spacebar
        22: "ctrl+c",   # GPIO 22 → Ctrl+C
        27: "m",        # GPIO 27 → M key
    }

    pedal = PedalController(config)
    pedal.run()
"""

from gpio_pedal.controller import PedalController
from gpio_pedal.config import load_config

__version__ = "0.1.0"
__all__ = ["PedalController", "load_config", "__version__"]
