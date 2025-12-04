# src/antenna_hardware.py
"""
Antenna Hardware Control - 2 Antenna System
Controls relays and LEDs for antenna selection on Pi Zero 2W
LEDs are wired in parallel with relay drivers (same GPIO pins)
"""

from gpiozero import OutputDevice


class AntennaHardware:
    """Hardware abstraction for antenna control system"""
    
    def __init__(self):
        """Initialize GPIO pins and set default state"""
        # GPIO pin mappings - 3 antenna system
        # Relays and LEDs share same pins (LEDs in parallel with relay drivers)
        self.relay_pins = {1: 27, 2: 22, 3: 4}
        self.led_pins = {1: 27, 2: 22, 3: 4}  # Same as relay pins (hardware parallel)
        
        # Initialize GPIO devices
        # Only create ONE device per pin (relay OutputDevice controls both relay and LED)
        self.relays = {}
        
        # Setup relays (active high) - this also drives the LEDs
        for antenna_num, pin in self.relay_pins.items():
            self.relays[antenna_num] = OutputDevice(pin, active_high=True, initial_value=False)
        
        # Set default state (A1 on startup)
        self.current_antenna = 0
        self.set_antenna(1)
    
    def set_antenna(self, antenna_num):
        """
        Set active antenna (1, 2, 3) or OFF (0)
        Ensures exclusive selection - only one antenna active at a time
        
        Args:
            antenna_num (int): Antenna to activate (1, 2, 3) or 0 for OFF
        """
        # Validate input - now 0, 1, 2, 3 valid
        if antenna_num not in [0, 1, 2, 3]:
            return
        
        # Turn off all relays (and LEDs) first
        for i in [1, 2, 3]:
            self.relays[i].off()
        
        # Turn on selected antenna (if not OFF)
        if antenna_num != 0:
            self.relays[antenna_num].on()
        
        # Update current state
        self.current_antenna = antenna_num
    
    def get_current_antenna(self):
        """
        Get currently selected antenna
        
        Returns:
            int: Current antenna (1, 2, 3) or 0 for OFF
        """
        return self.current_antenna
    
    def get_relay_state(self, antenna_num):
        """
        Get relay state for specific antenna
        
        Args:
            antenna_num (int): Antenna number (1, 2, 3)
            
        Returns:
            bool: True if relay is active, False otherwise
        """
        if antenna_num not in [1, 2, 3]:
            return False
        
        return self.relays[antenna_num].is_active
    
    def get_led_state(self, antenna_num):
        """
        Get LED state for specific antenna
        Since LEDs are wired parallel to relays, LED state = relay state
        
        Args:
            antenna_num (int): Antenna number (1, 2, 3)
            
        Returns:
            bool: True if LED is on, False otherwise
        """
        # LED state is same as relay state (hardware parallel connection)
        return self.get_relay_state(antenna_num)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        # Turn off all outputs
        for i in [1, 2, 3]:
            self.relays[i].off()
        
        # Close GPIO devices
        for relay in self.relays.values():
            relay.close()
