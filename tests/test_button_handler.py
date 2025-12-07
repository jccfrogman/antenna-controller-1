#!/usr/bin/env python3
"""
Unit tests for button_handler.py (2-antenna baseline)
Tests button cycling logic: A1 ↔ A2 toggle
"""

import unittest
from unittest.mock import Mock, patch
import sys

# Mock gpiozero before imports
sys.modules['gpiozero'] = Mock()
sys.modules['gpiozero.pins'] = Mock()
sys.modules['gpiozero.pins.lgpio'] = Mock()

from button_handler import ButtonHandler


class TestButtonHandler(unittest.TestCase):
    """Test ButtonHandler class"""
    
    @patch('button_handler.Button')
    @patch('button_handler.Device')
    def setUp(self, mock_device, mock_button):
        """Set up test fixtures with mocked button"""
        from button_handler import ButtonHandler
        
        # Create mock hardware
        self.mock_hw = Mock()
        self.mock_hw.get_current_antenna.return_value = 1
        
        # Create mock button
        self.mock_button_instance = Mock()
        mock_button.return_value = self.mock_button_instance
        
        # Create handler
        self.handler = ButtonHandler(self.mock_hw)
    
    def test_cycle_from_a1_to_a2(self):
        """Test cycling from A1 to A2"""
        self.mock_hw.get_current_antenna.return_value = 1
        
        self.handler.cycle_antenna()
        
        self.mock_hw.set_antenna.assert_called_with(2)
    
    def test_cycle_from_a2_to_a3(self):
        """Test cycling from A2 to A3"""
        self.mock_hw.get_current_antenna.return_value = 2
        
        self.handler.cycle_antenna()
        
        self.mock_hw.set_antenna.assert_called_with(3)
    
    def test_cycle_from_a3_to_a1(self):
        """Test cycling from A3 back to A1 (rotation behavior)"""
        self.mock_hw.get_current_antenna.return_value = 3
        
        self.handler.cycle_antenna()
        
        self.mock_hw.set_antenna.assert_called_with(1)
    
    def test_cycle_from_off_to_a1(self):
        """Test cycling from OFF state goes to A1"""
        self.mock_hw.get_current_antenna.return_value = 0
        
        self.handler.cycle_antenna()
        
        self.mock_hw.set_antenna.assert_called_with(1)
    
    def test_button_press_triggers_cycle(self):
        """Test button press callback triggers cycle"""
        self.mock_hw.get_current_antenna.return_value = 2
        
        # Simulate button press by calling the callback directly
        self.handler._on_button_press()
        
        # Should cycle from A2 to A3
        self.mock_hw.set_antenna.assert_called_with(3)
    
    def test_debounce_time_default(self):
        """Test default debounce time is 200ms"""
        self.assertEqual(self.handler.debounce_time, 0.2)
    
    def test_button_pin_default(self):
        """Test default button pin is GPIO 17"""
        self.assertEqual(self.handler.button_pin, 17)
    
    def test_cleanup(self):
        """Test cleanup closes button"""
        self.handler.cleanup()
        self.mock_button_instance.close.assert_called()


if __name__ == '__main__':
    unittest.main()
