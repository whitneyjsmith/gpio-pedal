"""
Core GPIO pedal controller.

Wires Raspberry Pi GPIO input pins to keyboard key presses via pynput.
Each pin is set up with an internal pull-up resistor; pressing a connected
normally-open switch pulls the pin LOW and triggers the mapped key.
"""

from __future__ import annotations

import time
import logging
from typing import Dict, Optional, Union

import RPi.GPIO as GPIO
from pynput.keyboard import Controller, Key

from gpio_pedal.config import validate_config

logger = logging.getLogger(__name__)

# Type alias for a key string like "space", "ctrl+c", or "a"
KeyString = str


class PedalController:
    """Maps Raspberry Pi GPIO input pins to keyboard key presses.

    Each pin should be connected to a normally-open momentary switch (foot
    pedal, pushbutton, etc.) with the other side tied to GND.  An internal
    pull-up resistor is enabled automatically, so no external resistor is
    needed.

    Args:
        config: A dict mapping GPIO BCM pin numbers to key strings.
                Key strings can be single characters (``"a"``, ``"1"``),
                named special keys (``"space"``, ``"enter"``, ``"ctrl"``),
                or ``+``-separated combinations (``"ctrl+c"``, ``"shift+f1"``).
        bouncetime: Debounce time in milliseconds. Increase if you see phantom
                    key presses; decrease for faster response. Default: 300.

    Example::

        from gpio_pedal import PedalController

        controller = PedalController({
            17: "space",
            22: "ctrl+c",
            27: "m",
        })
        controller.run()
    """

    def __init__(
        self,
        config: Dict[int, KeyString],
        bouncetime: int = 300,
    ) -> None:
        self.config = validate_config(config)
        self.bouncetime = bouncetime
        self.keyboard = Controller()
        self._running = False

        GPIO.setmode(GPIO.BCM)
        for pin in self.config:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=self._handle_press,
                bouncetime=self.bouncetime,
            )
            logger.debug("Registered GPIO pin %d → '%s'", pin, self.config[pin])

        logger.info(
            "PedalController ready — monitoring %d pin(s): %s",
            len(self.config),
            sorted(self.config),
        )

    def _handle_press(self, channel: int) -> None:
        """GPIO interrupt callback: called when a pin goes LOW."""
        key = self.config.get(channel)
        if key:
            logger.debug("GPIO %d pressed → simulating '%s'", channel, key)
            self._simulate_keypress(key)

    def _simulate_keypress(self, key_string: KeyString) -> None:
        """Simulate a key press (and release) for the given key string.

        Handles single keys and ``+``-separated combinations.
        """
        try:
            if "+" in key_string:
                keys = [self._convert_key(k.strip()) for k in key_string.split("+")]
                with self.keyboard.pressed(*keys):
                    pass
            else:
                key = self._convert_key(key_string)
                self.keyboard.press(key)
                self.keyboard.release(key)
        except Exception:
            logger.exception("Failed to simulate keypress for '%s'", key_string)

    def _convert_key(self, key: str) -> Union[Key, str]:
        """Convert a string key name to a pynput ``Key`` object or bare char.

        Args:
            key: A key name like ``"space"``, ``"ctrl"``, or ``"a"``.

        Returns:
            A ``pynput.keyboard.Key`` for special keys, or the bare string
            for regular characters.
        """
        special = getattr(Key, key, None)
        if special is not None:
            return special
        if len(key) == 1:
            return key
        # Unknown multi-char string — pass through and let pynput handle/raise
        return key

    def stop(self) -> None:
        """Stop the run loop and clean up GPIO resources."""
        self._running = False

    def run(self) -> None:
        """Block and listen for pedal presses until Ctrl+C or ``stop()`` is called.

        Cleans up GPIO on exit.
        """
        self._running = True
        logger.info("Listening for pedal input — press Ctrl+C to quit.")
        try:
            while self._running:
                time.sleep(0.05)
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Shutting down — cleaning up GPIO.")
            print("\nShutting down pedal controller.")
            GPIO.cleanup()
