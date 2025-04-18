import RPi.GPIO as GPIO
import time
from pynput.keyboard import Controller, Key


class PedalController:
    def __init__(self, config):
        """Initialize the GPIO pedal controller."""
        self.config = config
        self.keyboard = Controller()
        GPIO.setmode(GPIO.BCM)

        for pin in self.config:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, callback=self._handle_press, bouncetime=300)

    def _handle_press(self, channel):
        """Handles footswitch press event."""
        key = self.config.get(channel)
        if key:
            self._simulate_keypress(key)

    def _simulate_keypress(self, key):
        """Simulates a keyboard press."""
        try:
            if '+' in key:  # Handle key combinations like 'ctrl+c'
                keys = key.split('+')
                with self.keyboard.pressed(*[self._convert_key(k) for k in keys]):
                    pass
            else:
                self.keyboard.press(self._convert_key(key))
                self.keyboard.release(self._convert_key(key))
        except Exception as e:
            print(f"Error simulating keypress: {e}")

    def _convert_key(self, key):
        """Converts string key names to pynput Key objects."""
        return getattr(Key, key, key)  # Convert if it's a special key (e.g., 'ctrl')

    def run(self):
        """Keeps the script running to listen for pedal inputs."""
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down pedal controller.")
            GPIO.cleanup()