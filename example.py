"""
gpio-pedal example — Python API usage.

Wire normally-open switches between each GPIO pin and GND.
The internal pull-up resistor is enabled automatically.

Run this script on your Raspberry Pi:
    python example.py
"""

from gpio_pedal import PedalController, load_config
from gpio_pedal.utils import describe_config

# ── Option 1: define the config inline ───────────────────────────────────────

config = {
    17: "space",    # GPIO 17 (pin 11) → Spacebar
    22: "ctrl+c",   # GPIO 22 (pin 15) → Ctrl+C
    27: "m",        # GPIO 27 (pin 13) → M key
}

# ── Option 2: load from a JSON file ──────────────────────────────────────────
# config = load_config("config.json")

# Preview what's mapped before starting
print(describe_config(config))
print()

# Start the controller — blocks until Ctrl+C
pedal = PedalController(config=config, bouncetime=300)
pedal.run()
