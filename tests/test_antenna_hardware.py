#!/usr/bin/env python3
"""
Unit tests for antenna_hardware.py (2-antenna baseline)
Tests basic hardware control functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys

# Mock gpiozero before any imports
sys.modules['gpiozero'] = Mock()
sys.modules['gpiozero.pins'] = Mock()
sys.modules['gpiozero.pins.lgpio'] = Mock()

from antenna_hardware import AntennaHardware


class TestAntennaHardware(unittest.TestCase):
    """Test AntennaHardware class"""
    
    @patch('antenna_hardware.OutputDevice')
    def setUp(self, mock_output):
        """Set up test fixtures with mocked GPIO"""
        # Mock OutputDevice to avoid actual GPIO access
        self.mock_relay_1 = Mock()
        self.mock_relay_2 = Mock()
        self.mock_relay_3 = Mock()
        
        # Return different mocks for each pin
        def output_device_side_effect(pin, **kwargs):
            if pin == 27:
                return self.mock_relay_1
            elif pin == 22:
                return self.mock_relay_2
            elif pin == 3:
                return self.mock_relay_3
            return Mock()
        
        mock_output.side_effect = output_device_side_effect
        
        # Instantiate hardware with mocked GPIO
        self.hw = AntennaHardware()
    
    def test_initialization_defaults_to_a1(self):
        """Test system initializes to A1 state"""
        self.assertEqual(self.hw.get_current_antenna(), 1)
        self.mock_relay_1.on.assert_called()
    
    def test_set_antenna_a1(self):
        """Test selecting antenna 1"""
        self.hw.set_antenna(1)
        self.assertEqual(self.hw.get_current_antenna(), 1)
        self.mock_relay_1.on.assert_called()
    
    def test_set_antenna_a2(self):
        """Test selecting antenna 2"""
        self.hw.set_antenna(2)
        self.assertEqual(self.hw.get_current_antenna(), 2)
        self.mock_relay_2.on.assert_called()
    
    def test_set_antenna_a3(self):
        """Test selecting antenna 3"""
        self.hw.set_antenna(3)
        self.assertEqual(self.hw.get_current_antenna(), 3)
        self.mock_relay_3.on.assert_called()
    
    def test_set_antenna_off(self):
        """Test setting all antennas OFF"""
        self.hw.set_antenna(0)
        self.assertEqual(self.hw.get_current_antenna(), 0)
        self.mock_relay_1.off.assert_called()
        self.mock_relay_2.off.assert_called()
        self.mock_relay_3.off.assert_called()
    
    def test_exclusive_selection(self):
        """Test only one antenna active at a time"""
        # Start at A1, switch to A3
        self.hw.set_antenna(3)
        
        # All should be turned off first, then A3 turned on
        self.mock_relay_1.off.assert_called()
        self.mock_relay_2.off.assert_called()
        self.mock_relay_3.off.assert_called()
        self.mock_relay_3.on.assert_called()
    
    def test_invalid_antenna_number(self):
        """Test invalid antenna numbers are ignored"""
        self.hw.set_antenna(1)
        self.assertEqual(self.hw.get_current_antenna(), 1)
        
        # Try invalid antenna (4 is beyond our 3-antenna system)
        self.hw.set_antenna(5)
        
        # Should still be at A1
        self.assertEqual(self.hw.get_current_antenna(), 1)
    
    def test_get_relay_state(self):
        """Test querying relay state"""
        self.mock_relay_1.is_active = True
        self.mock_relay_2.is_active = False
        self.mock_relay_3.is_active = False
        
        self.assertTrue(self.hw.get_relay_state(1))
        self.assertFalse(self.hw.get_relay_state(2))
        self.assertFalse(self.hw.get_relay_state(3))
    
    def test_get_led_state(self):
        """Test LED state matches relay state"""
        self.mock_relay_1.is_active = True
        self.mock_relay_2.is_active = False
        self.mock_relay_3.is_active = False
        
        # LED state should equal relay state (parallel wiring)
        self.assertTrue(self.hw.get_led_state(1))
        self.assertFalse(self.hw.get_led_state(2))
        self.assertFalse(self.hw.get_led_state(3))
    
    def test_cleanup(self):
        """Test cleanup turns off all relays"""
        self.hw.cleanup()
        
        self.mock_relay_1.off.assert_called()
        self.mock_relay_2.off.assert_called()
        self.mock_relay_3.off.assert_called()
        self.mock_relay_1.close.assert_called()
        self.mock_relay_2.close.assert_called()
        self.mock_relay_3.close.assert_called()


if __name__ == '__main__':
    unittest.main()
