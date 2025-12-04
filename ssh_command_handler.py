# src/ssh_command_handler.py
"""
SSH Command Handler - 2 Antenna System
Parses and executes antenna control commands via SSH
"""


class SSHCommandHandler:
    """Handles SSH command parsing and execution"""
    
    # Valid commands for 3-antenna system
    VALID_COMMANDS = ['A1', 'A2', 'A3', 'OFF', 'STAT']
    
    def __init__(self, hardware):
        """
        Initialize command handler with hardware reference
        
        Args:
            hardware: AntennaHardware instance
        """
        self.hardware = hardware
    
    def handle_command(self, command):
        """
        Parse and execute command, return status response
        
        Args:
            command (str): Command string from SSH input
            
        Returns:
            str: Response message with current state or error
        """
        # Strip whitespace and convert to uppercase
        cmd = command.strip().upper()
        
        # Handle empty command
        if not cmd:
            return "ERROR: Empty command"
        
        # Validate command
        if cmd not in self.VALID_COMMANDS:
            return f"ERROR: Invalid command '{command}'. Valid: A1, A2, A3, OFF, STAT"
        
        # Execute command
        if cmd == 'STAT':
            return self._get_status()
        elif cmd == 'OFF':
            self.hardware.set_antenna(0)
            return "Status: OFF"
        elif cmd == 'A1':
            self.hardware.set_antenna(1)
            return "Status: A1"
        elif cmd == 'A2':
            self.hardware.set_antenna(2)
            return "Status: A2"
        elif cmd == 'A3':
            self.hardware.set_antenna(3)
            return "Status: A3"
    
    def _get_status(self):
        """
        Get current antenna status without changing state
        
        Returns:
            str: Current antenna status
        """
        current = self.hardware.get_current_antenna()
        
        if current == 0:
            return "Status: OFF"
        else:
            return f"Status: A{current}"