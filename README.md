# gpio-pedal

[![PyPI Version](https://img.shields.io/pypi/v/gpio-pedal.svg)](https://pypi.org/project/gpio-pedal/)
[![Python Versions](https://img.shields.io/pypi/pyversions/gpio-pedal.svg)](https://pypi.org/project/gpio-pedal/)
[![License](https://img.shields.io/pypi/l/gpio-pedal.svg)](LICENSE)

**Turn any Raspberry Pi GPIO pin into a keyboard shortcut.**

Wire a foot pedal, footswitch, or momentary button to a GPIO pin and `gpio-pedal` will simulate whatever key press you configure — space bar, Ctrl+C, a media key, anything. Works great for hands-free control, live performance, transcription, accessibility setups, or any situation where your hands are busy.

---

## Features

- Map any number of GPIO pins to individual keys or key combinations (`ctrl+c`, `shift+f1`, etc.)
- Configurable debounce time to eliminate phantom presses
- Load config from a JSON or YAML file, or pass a plain Python dict
- CLI command (`gpio-pedal config.json`) for running without writing any code
- Clean shutdown on Ctrl+C with automatic GPIO cleanup

---

## Requirements

- Raspberry Pi (any model with GPIO)
- Python 3.9 or higher
- A normally-open momentary switch wired between a GPIO pin and GND

---

## Installation

```bash
pip install gpio-pedal
```

For YAML config file support:

```bash
pip install gpio-pedal[yaml]
```

---

## Hardware Setup

Wire your switch between the GPIO pin and GND. `gpio-pedal` enables the internal pull-up resistor automatically, so no external resistor is needed.

```
GPIO pin ──── [switch] ──── GND
```

For example, to use GPIO 17:

```
Pin 11 (GPIO 17) ──── [foot pedal] ──── Pin 9 (GND)
```

Use BCM pin numbering (the number after "GPIO", not the physical pin number).

---

## Quick Start

```python
from gpio_pedal import PedalController

config = {
    17: "space",    # GPIO 17 → Spacebar
    22: "ctrl+c",   # GPIO 22 → Ctrl+C
    27: "m",        # GPIO 27 → M key
}

pedal = PedalController(config)
pedal.run()
```

---

## CLI Usage

Create a JSON config file:

```json
{
    "17": "space",
    "22": "ctrl+c",
    "27": "m"
}
```

Then run:

```bash
gpio-pedal config.json
```

Options:

```
gpio-pedal config.json --bouncetime 200   # faster debounce (ms)
gpio-pedal config.json --verbose          # debug logging
gpio-pedal --version
gpio-pedal --help
```

---

## Config File Format

| Format | Extension | Install |
|--------|-----------|---------|
| JSON   | `.json`   | built-in |
| YAML   | `.yaml` / `.yml` | `pip install gpio-pedal[yaml]` |

**JSON example:**
```json
{
    "17": "space",
    "22": "ctrl+z",
    "27": "shift+f5"
}
```

**YAML example:**
```yaml
17: space
22: ctrl+z
27: shift+f5
```

Keys can be single characters (`a`, `1`, `!`) or any key name from
[pynput's Key enum](https://pynput.readthedocs.io/en/latest/keyboard.html),
such as `space`, `enter`, `tab`, `ctrl`, `shift`, `alt`, `f1`–`f20`, etc.
Combine them with `+` for shortcuts.

---

## Python API

```python
from gpio_pedal import PedalController, load_config
from gpio_pedal.utils import list_special_keys, describe_config

# Load from a file
config = load_config("config.json")

# Or define inline
config = {17: "space", 22: "ctrl+c"}

# See all supported special key names
print(list_special_keys())

# Preview your config before running
print(describe_config(config))

# Start listening (blocks until Ctrl+C)
controller = PedalController(config, bouncetime=300)
controller.run()
```

---

## Development

```bash
git clone https://github.com/whitneyjsmith/gpio-pedal.git
cd gpio-pedal
pip install -e ".[dev]"
pytest
```

---

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.
