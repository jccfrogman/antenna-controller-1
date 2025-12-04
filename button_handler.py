# src/button_handler.py
"""
Button Handler - 3 Antenna System
Handles physical button input with debouncing for antenna cycling
Debounce: 200ms (optimized for 12mm domed pushbutton)
"""

from gpiozero import Button, Device
from gpiozero.pins.lgpio import LGPIOFactory

# Use modern lgpio pin factory
Device.pin_factory = LGPIOFactory()


class ButtonHandler:
    """Handles physical button control for antenna toggling"""
    
    def __init__(self, hardware, button_pin=17, debounce_time=0.2):
        """
        Initialize button handler with hardware reference
        
        Args:
            hardware: AntennaHardware instance
            button_pin: GPIO pin for button (GPIO 17 = Pin 11)
            debounce_time: Debounce delay in seconds (0.2s = 200ms)
                          Optimized for 12mm domed pushbutton
        """
        self.hardware = hardware
        self.button_pin = button_pin
        self.debounce_time = debounce_time
        
        # Initialize button with pull-up resistor and debouncing
        self.button = Button(
            button_pin,
            pull_up=True,
            bounce_time=debounce_time
        )
        
        # Register button press callback
        self.button.when_pressed = self._on_button_press
    
    def _on_button_press(self):
        """Callback for button press events"""
        self.cycle_antenna()
    
    def cycle_antenna(self):
        """
        Cycle through antennas: A1 → A2 → A3 → A1
        If currently OFF, go to A1
        
        Note: Button does NOT cycle through OFF state (OFF only via SSH)
        """
        current = self.hardware.get_current_antenna()
        
        # Use modulo arithmetic for clean rotation
        if current == 0:
            # From OFF → A1
            next_antenna = 1
        else:
            # Rotate: 1→2, 2→3, 3→1
            next_antenna = (current % 3) + 1
        
        self.hardware.set_antenna(next_antenna)
    
    def cleanup(self):
        """Clean up button resources"""
        if self.button:
            self.button.close()
