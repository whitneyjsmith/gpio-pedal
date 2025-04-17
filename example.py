#Basic Usage Example

from gpio_pedal import PedalController

# Define switch-to-key mappings
pedal_config = {
    17: "space",   # GPIO 17 triggers Spacebar
    22: "ctrl+c",  # GPIO 22 triggers Ctrl+C
    27: "m",       # GPIO 27 triggers "M" key
}

# Initialize the pedal controller
pedal = PedalController(config=pedal_config)

# Start listening for footswitch presses
pedal.run()