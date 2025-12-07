#!/usr/bin/env python3
"""
Unit tests for ssh_command_handler.py (2-antenna baseline)
Tests command parsing and execution
"""

import unittest
from unittest.mock import Mock
import sys

# Mock gpiozero (needed by antenna_hardware which we'll mock anyway)
sys.modules['gpiozero'] = Mock()
sys.modules['gpiozero.pins'] = Mock()
sys.modules['gpiozero.pins.lgpio'] = Mock()

from ssh_command_handler import SSHCommandHandler


class TestSSHCommandHandler(unittest.TestCase):
    """Test SSHCommandHandler class"""
    
    def setUp(self):
        """Set up test fixtures"""
        from ssh_command_handler import SSHCommandHandler
        
        # Create mock hardware
        self.mock_hw = Mock()
        self.mock_hw.get_current_antenna.return_value = 1
        
        # Create handler with mock hardware
        self.handler = SSHCommandHandler(self.mock_hw)
    
    def test_command_a1(self):
        """Test A1 command selects antenna 1"""
        response = self.handler.handle_command("A1")
        
        self.mock_hw.set_antenna.assert_called_with(1)
        self.assertEqual(response, "Status: A1")
    
    def test_command_a2(self):
        """Test A2 command selects antenna 2"""
        response = self.handler.handle_command("A2")
        
        self.mock_hw.set_antenna.assert_called_with(2)
        self.assertEqual(response, "Status: A2")
    
    def test_command_a3(self):
        """Test A3 command selects antenna 3"""
        response = self.handler.handle_command("A3")
        
        self.mock_hw.set_antenna.assert_called_with(3)
        self.assertEqual(response, "Status: A3")
    
    def test_command_off(self):
        """Test OFF command deactivates all antennas"""
        response = self.handler.handle_command("OFF")
        
        self.mock_hw.set_antenna.assert_called_with(0)
        self.assertEqual(response, "Status: OFF")
    
    def test_command_stat(self):
        """Test STAT command returns current status"""
        self.mock_hw.get_current_antenna.return_value = 2
        
        response = self.handler.handle_command("STAT")
        
        # Should not change antenna
        self.mock_hw.set_antenna.assert_not_called()
        self.assertEqual(response, "Status: A2")
    
    def test_command_stat_when_off(self):
        """Test STAT command when system is OFF"""
        self.mock_hw.get_current_antenna.return_value = 0
        
        response = self.handler.handle_command("STAT")
        
        self.assertEqual(response, "Status: OFF")
    
    def test_case_insensitive(self):
        """Test commands are case insensitive"""
        response = self.handler.handle_command("a1")
        self.mock_hw.set_antenna.assert_called_with(1)
        
        response = self.handler.handle_command("oFf")
        self.mock_hw.set_antenna.assert_called_with(0)
    
    def test_whitespace_handling(self):
        """Test commands with whitespace are handled"""
        response = self.handler.handle_command("  A2  ")
        self.mock_hw.set_antenna.assert_called_with(2)
    
    def test_invalid_command(self):
        """Test invalid command returns error"""
        response = self.handler.handle_command("INVALID")
        
        self.assertIn("ERROR", response)
        self.assertIn("Invalid command", response)
        self.mock_hw.set_antenna.assert_not_called()
    
    def test_empty_command(self):
        """Test empty command returns error"""
        response = self.handler.handle_command("")
        
        self.assertIn("ERROR", response)
        self.assertIn("Empty command", response)
    
    def test_valid_commands_list(self):
        """Test VALID_COMMANDS contains correct commands for 3-antenna system"""
        expected = ['A1', 'A2', 'A3', 'OFF', 'STAT']
        self.assertEqual(self.handler.VALID_COMMANDS, expected)


if __name__ == '__main__':
    unittest.main()
