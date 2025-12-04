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
    
    def __init__(self, hardware, button_pin=17, debounce_time=0.2, antenna_count=3):
        """
        Initialize button handler with hardware reference
        
        Args:
            hardware: AntennaHardware instance
            button_pin: GPIO pin for button (GPIO 17 = Pin 11)
            debounce_time: Debounce delay in seconds (0.2s = 200ms)
                          Optimized for 12mm domed pushbutton
            antenna_count: Number of antennas to cycle through (2 or 3)
        """
        self.hardware = hardware
        self.button_pin = button_pin
        self.debounce_time = debounce_time
        self.antenna_count = antenna_count
        
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
        Cycle through antennas based on antenna_count configuration
        - 2-antenna mode: Toggle A1 ↔ A2
        - 3-antenna mode: Rotate A1 → A2 → A3 → A1
        If currently OFF, go to A1
        
        Note: Button does NOT cycle through OFF state (OFF only via SSH)
        """
        current = self.hardware.get_current_antenna()
        
        # Use modulo arithmetic for clean cycling
        if current == 0:
            # From OFF → A1
            next_antenna = 1
        else:
            # Dynamic cycling based on antenna_count
            # 2-antenna: 1→2, 2→1
            # 3-antenna: 1→2, 2→3, 3→1
            next_antenna = (current % self.antenna_count) + 1
        
        self.hardware.set_antenna(next_antenna)
    
    def cleanup(self):
        """Clean up button resources"""
        if self.button:
            self.button.close()
